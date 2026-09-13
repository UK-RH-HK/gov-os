# Output 18 — Verify-and-use transaction model

> **RoT-1 revision 2 — PROPOSED, pending a fresh independent review; not approved, not implemented.**
> New in revision 2. Addresses RV-H3 (CD-4), the writer guard of RV-M1 (CD-5, with `02`) and RV-M2 (CD-6).
> Normative keywords: MUST, MUST NOT, SHOULD.

## 1. Exactly what is authenticated, installed and enforced

| Object | Definition | Produced by | Consumed by |
|---|---|---|---|
| **Statement bytes `P`** | canonical GOV-JCS-1 payload bytes decoded once from the DSSE envelope | source, read once | signature verification (PAE) and parsing — **from the same buffer** |
| **Statement digest `D`** | `sha256:` + hex(SHA-256(`P`)) | computed | identity of everything below |
| **Release Content Set `RCS(D)`** | inside `P`: `kernel.files` (relpath → content digest), `tree_digest`, `manifest_digest`, component and migration digests | release signer | V9; snapshot comparison |
| **Content identity `CI`** | the pair (`D`, `tree_digest`) | computed | the identity recorded in the lock, journal, index manifests, adapter manifests, generated registries, context packets |
| **VerifiedBlob** | `{digest, bytes}` for one file: an immutable shared buffer whose SHA-256 equals `RCS(D)[path]` | secure reader (§3) | install staging writes; migration and template reads during the transaction |
| **AuthenticatedRelease (ARO)** | `{P, D, verified signers, RCS, VerifiedBlob per path, eligibility inputs}`, in memory only; no public constructor; not serialisable | `authenticate` (`04`) | authorisation (`19`), install transaction (§5) |
| **StagedTree** | files written **from VerifiedBlob buffers** into `governance/.tx/<TX>/kernel.next/` and `trust.next/` | install transaction | read-back verification; commit |
| **KernelSnapshot** | immutable in-memory map relpath → VerifiedBlob, loaded from the installed tree by the secure reader, whose digests equal `RCS(D_installed)` | `kernel_trust` at process start or explicit reload (§6) | **every** consumer of kernel content |
| **EmbeddedSnapshot** | the same shape built from bytes compiled into the binary and verified against the compiled statement | the binary | fail-closed baseline; `init` with no `--source` |

**What installation consumes:** the VerifiedBlob buffers that were digested. Installation never reads the source path
again.

**What runtime enforces:** KernelSnapshot buffers, or the EmbeddedSnapshot. Enforcement never reads a kernel path again
after it was digested.

## 2. Invariants (normative)

| ID | Invariant |
|---|---|
| VU-1 | Every source file is opened through the secure reader (§3) and read **once**, in full, into a buffer. The digest is computed over that buffer. |
| VU-2 | After a buffer is digested, no code path re-opens the source path or the installed path to obtain content for a trust or enforcement decision. |
| VU-3 | Staging files are created exclusively (they must not exist) and written only from VerifiedBlob buffers. |
| VU-4 | Immediately before commit, every staged file is re-read through no-follow handles relative to the held staging directory handle and re-digested. Any difference aborts with `STAGED_CONTENT_CHANGED`. |
| VU-5 | Commit replaces the installed kernel and trust directories atomically per directory, under the exclusive transaction lock. The lock file is the commit point and is written last. |
| VU-6 | After commit, the transaction loads a KernelSnapshot through the normal use-time path (§6) and requires `snapshot.CI == ARO.CI` and the same eligibility verdict. Otherwise: automatic journal rollback. |
| VU-7 | At run time all kernel content comes from the KernelSnapshot API: policies, precedence, roles, schemas, skills, adapter templates, tool registry, migrations, overlay templates, invariants, command contract. No other module can open `governance/kernel/**` (GovernedFs read guard, §8). |
| VU-8 | Every derived artefact whose correctness depends on kernel content records the CI it was built from: index manifest, adapter manifest, generated tool and plugin registries, context packet. A consumer that finds a different current CI treats the artefact as stale. |
| VU-9 | No cache, materialised directory or on-disk snapshot is read back into a trust decision without passing through the secure reader and a digest comparison against a verified statement. |
| VU-10 | Writes, creations, renames, deletions, permission changes and link creation under the Protected Path Set (§8) happen only inside the install transaction. |

## 3. Secure reader and secure directory primitives

All access to sources, staging, kernel and trust content goes through a `SecureDir` abstraction. It holds an open
directory handle to the repository root (or to the source root) obtained once.

| Platform | Opening, component by component | Commit | Locking |
|---|---|---|---|
| Linux ≥ 5.6 | `openat2(dirfd, rel, RESOLVE_BENEATH \| RESOLVE_NO_SYMLINKS \| RESOLVE_NO_MAGICLINKS \| RESOLVE_NO_XDEV)`; directories with `O_DIRECTORY`, files with `O_NOFOLLOW`; `fstat` must report the expected type | `renameat2(RENAME_EXCHANGE)` for `kernel` ↔ `.tx/<TX>/kernel.next` and `trust` ↔ `.tx/<TX>/trust.next`; `fsync` of files and of every affected parent directory | `flock` on `governance/.tx/LOCK` through a held descriptor |
| Other POSIX | `openat(parent_fd, name, O_NOFOLLOW \| O_DIRECTORY \| O_CLOEXEC)` per component, `fstat` type check; files `openat(…, O_NOFOLLOW)` | two `renameat` calls under the journal (§5.4) | `flock` or `fcntl` locks |
| Windows | `CreateFileW` with `FILE_FLAG_OPEN_REPARSE_POINT \| FILE_FLAG_BACKUP_SEMANTICS`; any reparse point on any component is refused | handle-based rename (`SetFileInformationByHandle`, `FileRenameInfoEx`) under the journal | `LockFileEx` |

The following are refused: a symlink or reparse point on any component (including ancestors such as `governance/` and
`governance/kernel/`), a device, FIFO or socket, an unexpected file type, and any path that escapes the root. Codes:
`PATH_SUBSTITUTION_DETECTED` at use time; `RELEASE_TREE_INVALID` with a `rule` detail at ingress.

Platforms offering none of these primitives are unsupported for production-profile operation (`TRUST_PLATFORM_UNSUPPORTED`).

## 4. Ingress pipeline (byte flow)

```text
SourceRef ─► SecureDir(source root)                        no-follow, beneath, regular files only
   │  V1  enumerate + gov-tree-v2 path rules + limits (07 §5)
   │  V1  read each file once → buffer + SHA-256            ← the source may change after this point: irrelevant
   ▼
envelope read once → P → V3–V7 (strict parse, purpose, signature, compiled schema)       05 SV-1…SV-10
   ▼
V8 identity (KERNEL.yaml version taken from its buffer) · V9 every buffer digest = RCS(D) · V10 migrations from buffers
   ▼
ARO (memory only) ─► authorisation: eligibility, trust state, gates, authority floor (17, 19, 21)
   ▼                                                                               journal: prepared
install_tx: take exclusive lock; create governance/.tx/<TX>/ exclusively (random 128-bit TX);
            write buffers → kernel.next/, trust.next/ (envelope bytes, TSS/TPS/certification/attestation statements);
            fsync files and directories                                            journal: staged
   ▼
VU-4 read-back: re-read every staged file via held handles, re-digest               journal: verified-staged
   ▼
RENAME_EXCHANGE kernel ; RENAME_EXCHANGE trust ; fsync governance/                  journal: swapped
   ▼
migrations interpreted from ARO buffers; overlay writes through GovernedFs (overlay is not protected);
computed-weakening check (19 §9); gate check if non-empty                          journal: migrated
   ▼
framework.lock written to .tx/<TX>/framework.lock.next, fsync, renameat over governance/framework.lock, fsync dir
                                                                                     journal: committed
   ▼
KernelSnapshot load + CI equality + eligibility + doctor/audit on the snapshot (VU-6)  journal: verified
   ▼
ledger entry (idempotent from the journal); remove .tx/<TX>/ (including kernel.prev, trust.prev); release lock
```

Rev 1's on-disk quarantine directory is replaced by in-memory VerifiedBlobs, bounded by the tree limits (`07` §5: at
most 64 MiB total). Archives are read by streaming members into buffers under the same rules; nothing is extracted to
disk.

## 5. Install transaction

### 5.1 Layout (entirely inside the Protected Path Set)

```text
governance/.tx/LOCK                         advisory lock file, held through a descriptor
governance/.tx/<TX>/journal.json            operation, phase, ARO CI, previous CI, gate ids, overlay snapshot digest
governance/.tx/<TX>/kernel.next/            staged kernel; becomes governance/kernel
governance/.tx/<TX>/trust.next/             staged trust record; becomes governance/trust
governance/.tx/<TX>/kernel.prev/ trust.prev/   the previous directories after the exchange
governance/.tx/<TX>/framework.lock.next     staged lock
governance/.tx/<TX>/overlay.prev/           snapshot of governance/project/ and governance/generated/ (project state)
```

### 5.2 Phases, visible state and recovery

| Phase | Installed state a reader could observe | Recovery (`20` §5) |
|---|---|---|
| `prepared`, `staged`, `verified-staged` | previous, unchanged | delete `.tx/<TX>` |
| `swapped` | new kernel and trust with the **old lock** → identity mismatch → `INSTALL_IN_PROGRESS` | evaluate the exchange-back target; exchange back; delete |
| `migrated` | as `swapped`, plus overlay changes | as `swapped`, plus restore the overlay from `overlay.prev/` through GovernedFs |
| `committed` | new kernel, trust and lock | re-run verification; if it fails, evaluate `kernel.prev`/`trust.prev` as a restore (`20` §2) |
| `verified` | new | delete `.tx/<TX>` |

### 5.3 Locking

- An install transaction holds the exclusive lock from `prepared` until cleanup.
- These processes take the **shared** lock: every process loading a KernelSnapshot (for the duration of the load), and
  every writer of project state that depends on kernel content (CIT execution, adoption executor, `rebuild-memory`,
  adapter and registry generation) for the duration of its operation. Honest processes therefore never observe a
  mid-exchange state and never write project state against a kernel that is being replaced.
- Locks are advisory. A3 can ignore them but cannot make an unverified or mixed state verify (`04` §5 identity checks).
  Ignoring the lock only produces refusals.

### 5.4 Platforms without atomic exchange

Each directory is replaced by two renames under the journal. Between them the path is absent, and the installation
state machine (§9) classifies the project `IN_TRANSACTION` because the journal exists. It fails closed.

## 6. Use-time snapshot (normative)

Once per process, and on explicit reload:

1. Take the shared lock with a bounded wait. On timeout: `INSTALL_IN_PROGRESS`, EmbeddedSnapshot, read-only.
2. Determine the installation state (§9). Unless it is `COMPLETE`, stop here: the policy root is the EmbeddedSnapshot
   joined with the effective floor (`19` §5).
3. Read `governance/trust/release.dsse.json` once through the secure reader and verify it under T0 (`04` V3–V8,
   `05` SV-1…SV-10).
4. Enumerate `governance/kernel/` through held directory handles. Refuse any non-regular entry or path-rule violation
   anywhere in the tree or its ancestors. Read each file once into a buffer and digest it.
5. Compare with `RCS(D)`. Any modified, missing or added path → `KERNEL_TAMPERED`.
6. Evaluate trust state (`17` §5) and eligibility (`19` §6).
7. Release the shared lock. Build `KernelSnapshot {CI, blobs, statement, verdict}` and publish it as an immutable shared
   handle. From here on the process never opens `governance/kernel/` again.
8. Long-lived processes keep the snapshot for their lifetime. `reload` repeats steps 1–7 and swaps the handle
   atomically. A unit of work keeps the handle it started with, so snapshot generations never mix.

Consumers never receive paths into `governance/kernel/`. When an external program needs kernel content (for example,
rendered adapter files), it receives bytes from the snapshot, written through GovernedFs into its own non-protected
location, with the CI recorded (VU-8).

Cost: the 4.1.5 kernel is 121 files, about 1 MiB. Reading and hashing it per process already happens today.

## 7. Embedded baseline and caches

- The EmbeddedSnapshot is built from compiled bytes. Its compiled statement is verified at first use, and its CI is
  compared with that statement.
- It is never materialised for any trust purpose. `init` without `--source` feeds EmbeddedSnapshot buffers directly
  into the ARO path; they are already VerifiedBlobs once the compiled statement check passes.
- **`GOV_KERNEL_CACHE` is removed. No cache exists on any trust path**, so cache substitution has nothing to substitute.
  A developer command that exports the embedded kernel (`gov kernel export <dir>`) writes a plain copy that is only
  ever an untrusted *source* afterwards.

## 8. Protected Path Set and GovernedFs

**Protected Path Set (PPS)** — relative to the repository root, compared after secure resolution, never by string
prefix of a user-supplied path:
- `governance/kernel/**`
- `governance/trust/**`
- `governance/framework.lock`
- `governance/.tx/**`
- the directory entries `governance`, `governance/kernel`, `governance/trust` and `governance/.tx` themselves
  (creation, removal, rename, replacement by a link)

**GovernedFs** is the only file-mutation API in the runtime. Every write, create, rename, delete, permission change,
link creation and directory removal:
1. resolves its target relative to the held repository-root handle with the no-follow rules of §3;
2. refuses a PPS target unless the call carries an `InstallTxToken`, which only `install_tx` can construct →
   `PROTECTED_PATH_WRITE_REFUSED` (details: operation, path, caller);
3. refuses targets whose resolution crosses a link or leaves the repository → `PATH_SUBSTITUTION_DETECTED`.

GovernedFs also guards **reads** of `governance/kernel/**` and `governance/trust/**`: only `kernel_trust` and
`install_tx` may open them (VU-7).

Subprocesses that `gov` starts to perform its own mutations (such as `git mv` and `git rm` in the adoption executor)
receive only arguments that GovernedFs has pre-validated by the same rules. Subprocesses that are not `gov` mutations —
plugins, tools, test commands, user shells — are outside GovernedFs. They are A3-equivalent, and VU-1…VU-8 are the
backstop.

Mechanisms constrained by this rule (full inventory in `02` §3):
- CIT `write_file`, `move_file`, `delete_file`, `append_record`, and CIT snapshot restore;
- adoption executor moves, deletions, `git mv`/`git rm`, and batch rollback restores;
- migration overlay operations and recovery;
- memory indexer outputs; adapter and registry generation;
- tool installer file writes; upstream packaging; lesson clustering writes.

**Enforcement proof (conformance).** A filesystem interception layer in the test build records every mutation by every
command in the command register. The suite asserts that no PPS mutation happens outside `install_tx` for every command.
Cases include CIT manifests and adoption plans naming PPS paths, `../` spellings, case variants on case-insensitive
filesystems, and symlinked parents.

## 9. Installation state machine (partial-install fail-closed)

Evaluated first in every process, including commands that do not require an installation (such as `doctor` and
`capabilities`).

| State | Condition | Policy root | Allowed |
|---|---|---|---|
| `ABSENT` | none of `governance/framework.lock`, `governance/kernel/`, `governance/trust/`, `governance/.tx/` exists | EmbeddedSnapshot ⊔ effective floor | commands not requiring an installation; `init`; adoption stages before batch 0 |
| `IN_TRANSACTION` | a `governance/.tx/<TX>/journal.json` exists | EmbeddedSnapshot ⊔ floor | read-only diagnostics; `gov recover` |
| `COMPLETE` | lock, kernel directory, `trust/FORMAT` and either `trust/release.dsse.json` or `trust/development.json` are all present and readable through the secure reader; no journal | KernelSnapshot if verified and eligible (`19` §6); otherwise EmbeddedSnapshot ⊔ floor | per verdict |
| `PARTIAL` | any other combination (lock without kernel, kernel without trust, trust without lock, and so on) | EmbeddedSnapshot ⊔ floor | read-only diagnostics; remedies (`20` §8) |
| `FORMAT_UNSUPPORTED` | `trust/FORMAT` names a format this binary does not implement | none | `gov version`; `gov doctor` reporting `TRUST_FORMAT_UNSUPPORTED` |

No state uses an on-disk kernel directory as policy root unless the state is `COMPLETE` and the snapshot is verified and
eligible. This closes the 4.1.5 `uninstalled` branch, where a missing manifest or lock made the guard pass with the
installed directory as policy root (`runtime/src/kernel_trust.rs:128-130, 289-291`).

`KERNEL_MANIFEST.json` is a compatibility tombstone for older binaries (`13` §3). It plays no role in any state or
decision.

## 10. Closure table

| Threat | Mechanism | Test (`12`) |
|---|---|---|
| Source file swapped after verification | VU-1…VU-3: installation writes the digested buffers; the source is never read again | RT-40 |
| Staged file swapped before commit | VU-4 read-back via held handles immediately before the exchange; exclusive `.tx/<TX>` | RT-40 |
| Installed file swapped after commit, before or during use | VU-6 post-commit snapshot; VU-7 runtime reads only snapshot bytes | RT-42 |
| Symlink or path substitution in the source | secure reader refuses links; `RESOLVE_BENEATH` | RT-41 |
| Symlink or path substitution in staging | exclusive creation of `.tx/<TX>` with a random name; handle-relative writes | RT-41 |
| Symlink or path substitution in the installed tree or its ancestors (e.g. committed through Git) | §6 step 4 refuses; PPS includes the directory entries | RT-41 |
| Concurrent source mutation | single read into buffers | RT-22 |
| Concurrent installs; readers mid-swap | exclusive and shared locks; identity-mismatch detection | RT-59 |
| Partial install (deletion, interrupted copy) | §9 state machine; EmbeddedSnapshot; remedies only | RT-43 |
| Crash in any phase | journal + §5.2 recovery with re-authentication and eligibility | RT-16 |
| Same-user races on journal or `.prev` directories | recovery re-authenticates and applies eligibility and the downgrade policy (`20` §5) | RT-58 |
| Cache replacement | no cache on any trust path; embedded content never materialised for trust | RT-45 |
| Mixed files from two authentic releases | V9 per-file digests at ingress; §6 step 5 at use | RT-10, RT-51 |
| Derived index built under a different or tampered kernel | VU-8 CI binding; floors only from the snapshot | RT-71 |

## 11. Residuals

| ID | Residual | Bound |
|---|---|---|
| VR-1 | A3 can modify installed files after a process built its snapshot. | That process is unaffected; the next process detects `KERNEL_TAMPERED`. |
| VR-2 | A3 can ignore advisory locks. | Produces refusals only. |
| VR-3 | Subprocesses that are not `gov` mutations can write protected paths. | Detected at the next snapshot; never enforced. |
| VR-4 | Plugin runtimes and model files are consumed by external processes through paths (`10`). | Host verification before and after use; kernel-enforced immutability (fs-verity) where available; index writes rejected on a post-use mismatch. |
