# Output 18 — Verify-and-use transaction model

> **RoT-1 revision 4 — PROPOSED, pending fresh independent reviews; not approved, not implemented.**
> Revision 4 keeps the byte-binding proof, the transaction area, union records, VU-1…VU-13 and the installation state
> machine (CD3-0). It adds:
> - VU-14, confined children (CR-03);
> - a typed, pre-write cross-device refusal (C-2);
> - doctor naming mixed layouts (C-3);
> - occupation type by `st_mode` (C-4);
> - the ignore rule in the layout migration (RV3-L7);
> - the recorded strength vector over effective policy, and the held registration, in the per-project record;
> - reinstall identity from the VTS record (CR-09, `20`).
>
> Normative keywords: MUST, MUST NOT, SHOULD.

## 1. Exactly what is authenticated, installed and enforced

| Object | Definition | Produced by | Consumed by |
|---|---|---|---|
| **Statement bytes `P`** | canonical GOV-JCS-1 payload decoded once from the DSSE envelope | source, read once | signature verification (PAE) and parsing, from the same buffer |
| **Statement digest `D`** | `sha256:` + hex(SHA-256(`P`)) | computed | identity |
| **Release Content Set `RCS(D)`** | `kernel.files`, `tree_digest`, `manifest_digest`, component and migration digests inside `P` | release signer | V9; snapshot comparison |
| **Content identity `CI`** | (`D`, `tree_digest`) | computed | lock, journal, VTS records, index and adapter manifests, context packets |
| **VerifiedBlob** | `{digest, bytes}`: an immutable buffer whose SHA-256 equals `RCS(D)[path]` | secure reader (§3) | staging writes; transaction reads |
| **AuthenticatedRelease (ARO)** | `{P, D, verified signers, RCS, blobs, eligibility inputs}`, in memory only | `authenticate` (`04`) | authorisation, install transaction |
| **StagedTree** | files written from VerifiedBlob buffers into `.governance-runtime/trust-tx/<TX>/trust.next/` | install transaction | read-back; commit |
| **KernelSnapshot** | immutable in-memory map relpath → VerifiedBlob, loaded from `governance/trust/kernel/` by the secure reader, whose digests equal `RCS(D_installed)`, with its generation `(CI, TSS sequence, TPS version, anchor epoch, negative-set digest)` | `kernel_trust` (§6) | **every** consumer of kernel content |
| **EmbeddedSnapshot** | the same shape built from compiled bytes verified against the compiled statement named in the TBM (`25` §4) | the binary | fail-closed baseline |

Installation consumes the digested buffers and never re-reads the source path. Enforcement reads KernelSnapshot or
EmbeddedSnapshot bytes and never re-reads a kernel path after digesting it.

## 2. Invariants (normative)

| ID | Invariant |
|---|---|
| VU-1 | Every source file is opened through the secure reader and read **once** into a buffer; the digest is computed over that buffer. |
| VU-2 | After a buffer is digested, no code path re-opens the source or installed path for a trust or enforcement decision. |
| VU-3 | Staging files are created exclusively and written only from VerifiedBlob buffers. |
| VU-4 | Immediately before commit, every staged file is re-read through no-follow handles relative to the held staging directory and re-digested; any difference aborts (`STAGED_CONTENT_CHANGED`). |
| VU-5 | Commit replaces `governance/trust` atomically under the exclusive transaction lock. The RoT-1 lock `governance/trust/framework.lock` is written last, inside the staged tree, and is the commit point. |
| VU-6 | After commit, a KernelSnapshot loaded through §6 MUST have `snapshot.CI == ARO.CI` and the same eligibility; otherwise automatic journal rollback. |
| VU-7 | All kernel content at run time comes from the KernelSnapshot API. No other module opens `governance/trust/**` (GovernedFs read guard). |
| VU-8 | Every derived artefact records the CI **and the effective-policy digest** it was built from: index manifest, adapter manifest, registries, context packets. A consumer finding a different current value treats it as stale; artefacts without the binding (for example written by a legacy binary) are never served. |
| VU-9 | No cache, materialised directory or on-disk snapshot enters a trust decision without the secure reader and a digest comparison. |
| VU-10 | Writes, creations, renames, deletions, permission changes and link creation under the Protected Path Set (§8) happen only inside the install transaction. |
| **VU-11** | **Generation discipline** (R2-M7). Every unit of work (a CLI command, an MCP request, a scheduled job step) that reads policy or performs a governed mutation MUST, under the shared lock, compare its snapshot generation with the installed statement digest, lock and effective trust state (`17` S1–S10). On any difference it MUST reload, if the new state is verified and eligible, or refuse (`SNAPSHOT_GENERATION_STALE`). A long-lived process MUST NOT keep a snapshot beyond `snapshot_max_age` (compiled: 60 seconds, or one unit of work, whichever is shorter) without repeating that comparison. |
| **VU-12** | **Link count** (R2-L2). Every staged and installed kernel or trust file MUST have `st_nlink == 1` when read and when read back; otherwise `PATH_SUBSTITUTION_DETECTED` before the exchange (staging) or at use. |
| **VU-13** | **Agent consumption** (R2-M8). Agents receive kernel content only as bytes served by `gov` from the snapshot, with the CI (§12). Direct agent reads of `governance/trust/kernel/**` are T4. |
| **VU-14** | **Confined children** (CR-03). A repository- or plugin-supplied command runs only through `confine::spawn`, after every trust decision of the unit of work. Its writes to pin locations, the VTS, `governance/trust/**`, occupation entries and the transaction area are denied (`24` §3.5). |

## 3. Secure reader and secure directory primitives

All access to sources, staging, kernel and trust content goes through `SecureDir`, which holds an open directory handle
to the repository root obtained once.

| Platform | Opening, component by component | Commit | Locking |
|---|---|---|---|
| Linux ≥ 5.6 | `openat2(dirfd, rel, RESOLVE_BENEATH \| RESOLVE_NO_SYMLINKS \| RESOLVE_NO_MAGICLINKS \| RESOLVE_NO_XDEV)`; `fstat` type and `st_nlink == 1` for files | `renameat2(RENAME_EXCHANGE)` of `governance/trust` ↔ `.governance-runtime/trust-tx/<TX>/trust.next` (same filesystem, checked by `st_dev`); `fsync` files and parents | `flock` on `.governance-runtime/trust-tx/LOCK` |
| Other POSIX | per-component `openat(O_NOFOLLOW)`, `fstat` type and link count | two `renameat` under the journal | `flock`/`fcntl` |
| Windows | `CreateFileW` with `FILE_FLAG_OPEN_REPARSE_POINT`; refuse reparse points; `GetFileInformationByHandle` link count | handle-based rename under the journal | `LockFileEx` |

Refused:
- a symlink or reparse point on any component, including ancestors;
- a device, FIFO or socket;
- an unexpected type, including an occupation entry of the wrong type (§9), decided by `st_mode` or `GetFileInformationByHandle`, never by name or extension (C-4);
- a link count above 1;
- a path escaping the root.

A staging directory on a different filesystem from `governance/` gives `TRUST_PLATFORM_UNSUPPORTED(cross_device_tx)` **before any write** (C-2): `st_dev` of `.governance-runtime/trust-tx` and `governance/` is compared at `prepared`. A `PARTIAL` install on such a machine stays repairable by a same-digest `kernel reinstall` once the runtime directory shares the device.

## 4. Ingress pipeline (byte flow)

```text
SourceRef ─► SecureDir(source) · V1 enumerate + tree rules · read once → buffers + SHA-256
   ▼  V3–V7 strict parse, purposes, signatures, compiled schemas (05 SV-1…SV-10)
   ▼  V8 identity · V9 buffers = RCS(D) · V10 migrations · V11 compatibility · E7 surface (23) against named/effective TPS
ARO (memory) ─► authorisation: eligibility E1–E9, trust state + freshness (17, 24), trust gates (27), install authority (19 §8)
   ▼                                                                               VTS open-transaction registry: TX registered
install_tx: exclusive lock; create .governance-runtime/trust-tx/<TX>/ exclusively (random 128-bit TX); journal: prepared
            write buffers → trust.next/kernel/…, release.dsse.json, lineage/; trust.next/state and root = UNION(current PTR,
            ARO bundle statements, VTS knowledge)  (never a subset of the current PTR); trust.next/framework.lock last
            fsync                                                                   journal: staged
   ▼  VU-4 read-back + VU-12 link counts                                           journal: verified-staged
   ▼  first RoT-1 install on a legacy layout only: layout migration steps of 26 §7 (quarantine, moves, occupation entries, ignore rule)
RENAME_EXCHANGE governance/trust ↔ trust.next ; fsync governance/                  journal: swapped
   ▼  migrations from ARO buffers: Overlay Surface whitelist first (MIGRATION_OPERATION_NOT_PERMITTED before any write); overlay writes through GovernedFs; recorded strength vector over the post-transaction effective policy (19 §9) → `weakening` trust gate
                                                                                    journal: migrated
   ▼  KernelSnapshot + CI equality + eligibility + doctor/audit (VU-6); strength vector re-recorded over effective policy; held registration recorded (26 §6, 19 §10.6)
                                                                                    journal: verified
ledger entry (idempotent); VTS per-project record updated; TX deregistered; trust-tx/<TX> moved to trust-tx/done/<TX>
```

## 5. Install transaction

### 5.1 Transaction area (outside Git; registered locally)

```text
.governance-runtime/trust-tx/LOCK                      advisory lock file
.governance-runtime/trust-tx/<TX>/journal.json         operation, phase, ARO CI, previous CI, gate confirmations, overlay snapshot digest
.governance-runtime/trust-tx/<TX>/trust.next/          staged governance/trust (kernel, statements, lock)
.governance-runtime/trust-tx/<TX>/trust.prev/          the previous governance/trust after the exchange
.governance-runtime/trust-tx/<TX>/overlay.prev/        snapshot of governance/overlay and governance/views
```

- `.governance-runtime/` is ignored by the installer's `.gitignore` entry.
- A journal is honoured **only if** (a) the VTS per-project record lists `<TX>` as an open transaction for this
  `project_trust_id` and repository path, and (b) the journal path is not tracked by Git.
- Anything else is `FOREIGN_TRANSACTION_ARTEFACT`: reported (doctor HIGH), never `IN_TRANSACTION`, never recovered from.
- A committed or copied journal therefore affects no clone (review RV2-A24).

### 5.2 Union trust record

`trust.next/state` and `trust.next/root` are the union of three sources:
- the current `governance/trust/state` and `root`, after verification;
- the ARO's bundle statements;
- VTS knowledge.

**Consequences:**
- Exchange-back (automatic rollback, recovery) uses `trust.prev` for **kernel, release statement and lock**, but MUST
  write `state/` and `root/` as the union of `trust.prev`, `trust.next` and VTS knowledge.
- A verified statement is never removed from `governance/trust/` by any transaction (review RV2-A26).

### 5.3 Phases, visible state and recovery

| Phase | Installed state a reader could observe | Recovery (`20` §5) |
|---|---|---|
| `prepared`, `staged`, `verified-staged` | previous, unchanged | move `trust-tx/<TX>` to `trust-tx/abandoned/`; deregister |
| `swapped` | new `governance/trust` with lock inside; the VTS registry marks the TX open → `IN_TRANSACTION` | evaluate the exchange-back target; exchange back with union state |
| `migrated` | as `swapped`, plus overlay changes | as `swapped`, plus the `overlay.prev` restore through the computed-weakening check and `weakening` trust gate |
| `verified` | new | clean up |

### 5.4 Locking

- An install transaction holds the exclusive lock from `prepared` until cleanup.
- Every snapshot load, and every writer of project state that depends on kernel content, takes the shared lock for the
  duration of its unit of work (VU-11).
- Locks are advisory. A3 ignoring them produces refusals, never trust.

## 6. Use-time snapshot (normative)

### 6.1 Load

1. Take the shared lock with a bounded wait (`INSTALL_IN_PROGRESS` on timeout, EmbeddedSnapshot, read-only).
2. Determine the installation state (§9). Unless `COMPLETE`, the policy root is EmbeddedSnapshot ⊔ floor (`19` §5).
3. Read `governance/trust/release.dsse.json` once and verify it (`04` V3–V8).
4. Enumerate `governance/trust/kernel/` through held handles. Refuse non-regular entries, link count > 1 and path-rule
   violations. Read each file once and digest it.
5. Compare with `RCS(D)` (`KERNEL_TAMPERED` on any difference).
6. Evaluate trust state, anchors by inclusion, freshness and currency (`17`, `24`); eligibility including E7 (`19` §6); the
   project-strength vector over the effective policy (`26` §6); and the negative set.
7. Build `KernelSnapshot {CI, generation, blobs, statement, verdict}`. Release the shared lock.

### 6.2 Consumers

Consumers never receive paths into `governance/trust/kernel/`. External programs receive snapshot bytes written through
GovernedFs into their own non-protected location, with CI and policy digest (VU-8, §12).

### 6.3 Units of work and long-lived processes (VU-11)

| Process | Rule |
|---|---|
| CLI command | one unit of work; generation compared at start and before the first governed mutation |
| MCP server, daemon or watcher (planned; `cli/src/main.rs:234`) | each request is a unit of work. Take the shared lock, compare the generation, reload or refuse, and never serve a request from a snapshot older than `snapshot_max_age`. A `refuse_operation` revocation, a TPS raise, a new anchor or an update applies to the next request. |
| Scheduler (for example G0–G6) | each job step is a unit of work |

The MCP server design MUST adopt this rule before it ships.

## 7. Embedded baseline and caches

- The EmbeddedSnapshot is built from compiled bytes, verified against the compiled statement named in the TBM, and never
  materialised for trust.
- **`GOV_KERNEL_CACHE` is removed. No cache exists on any trust path.**
- `gov kernel export <dir>` writes an untrusted source.

## 8. Protected Path Set and GovernedFs

**Protected Path Set (PPS)**, relative to the repository root and compared after secure resolution:
- `governance/trust/**` and the directory entries `governance`, `governance/trust`;
- the occupation entries (`26` §2): `governance/kernel` (regular file), `governance/project` (regular file),
  `governance/generated` (regular file), `governance/framework.lock` (directory) and its sentinel file,
  `spec/audits/GOVERNANCE-ADOPTION` (regular file), `.governance-runtime/migration` (regular file);
- the transaction area `.governance-runtime/trust-tx/**`. It is not tracked, and journals are hints (§5.1), but only
  `install_tx` writes it through GovernedFs.

**GovernedFs** is the only file-mutation API in the runtime. It:
1. resolves targets relative to the held root handle with §3 rules;
2. refuses PPS targets without an `InstallTxToken` (`PROTECTED_PATH_WRITE_REFUSED`);
3. refuses link crossings (`PATH_SUBSTITUTION_DETECTED`).

It also guards reads of `governance/trust/**`: only `kernel_trust` and `install_tx` may open it.

**Enforcement proof.**
- **Builder conformance:** a filesystem interception layer across every command in the command register.
- **Independent verification:** OS-level tracing by the verifier (`strace -f -e trace=%file,%process`, fanotify or
  eBPF), never an instrumentation layer the builder compiled in (review r2 `07` §2).

Subprocesses `gov` starts (plugins, tool commands, product and test commands) run confined (VU-14). Their remaining writes
are A3-equivalent (VR-3), and are detected by the next unit of work (VU-11) and by the project-strength vector.

## 9. Installation state machine

Evaluated first in every process, including commands that need no installation.

| State | Condition | Policy root | Allowed |
|---|---|---|---|
| `ABSENT` | no `governance/trust/`, no occupation entries, no legacy entries (`governance/framework.lock` file, `governance/kernel` directory) | EmbeddedSnapshot ⊔ floor | `init`; commands needing no installation |
| `LEGACY` | a legacy layout (`governance/framework.lock` is a file or `governance/kernel` is a directory) and no `governance/trust/` | EmbeddedSnapshot ⊔ floor; tree digest checked against `historical_releases` | read-only diagnostics; `update --apply` to an eligible release (layout migration, `26` §7) |
| `IN_TRANSACTION` | an honoured journal (§5.1) | EmbeddedSnapshot ⊔ floor | read-only diagnostics; `gov recover` |
| `COMPLETE` | `governance/trust/{FORMAT, framework.lock, kernel/, release.dsse.json or development.json}` present and readable, **every occupation entry present with its exact type**, and no honoured journal | KernelSnapshot if verified and eligible; otherwise EmbeddedSnapshot ⊔ floor | per verdict and freshness (`24` §4.3) |
| `PARTIAL` | any other combination, including a missing or retyped occupation entry (`PARTIAL(occupation)`), or legacy and RoT-1 entries mixed. Doctor D033 names the mixed layout and stray artefacts such as `governance/framework.lock~legacy` and `governance/kernel/KERNEL_MANIFEST.json` (C-3). | EmbeddedSnapshot ⊔ floor | read-only diagnostics; remedies (`20` §8) |
| `FORMAT_UNSUPPORTED` | `governance/trust/FORMAT` names an unimplemented format or layout | none | `gov version`; `gov doctor` |

A foreign transaction artefact (§5.1) is reported and ignored; the state is computed as if it were absent.

Evidence: `evidence/LR2-installation-state-and-strength-reference.json` applies this state machine to the trees left by
review r3's legacy probes. Every removed, restored, sparse or merged tree with legacy entries is `PARTIAL(occupation)` or
`LEGACY`. Intact trees, reviewer C's clean clone, checkout, merge and archive trees, and a fresh clone after the
untracking idiom under the revision-4 ignore rule are `COMPLETE`.

## 10. Closure table

| Threat | Mechanism | Test (`12`) |
|---|---|---|
| Source file swapped after verification | VU-1…VU-3 | RT-40 |
| Staged file swapped before commit; hard link to a staged file | VU-4, VU-12 | RT-40, RV2-A23 |
| Installed file swapped after commit | VU-6, VU-7 | RT-42 |
| Symlink or path substitution anywhere | §3 | RT-41 |
| Concurrent installs; readers mid-swap | locks, identity checks | RT-59 |
| Long-lived process across an update, TPS raise, revocation or anchor change | VU-11 | RV2-A21 |
| Partial install, missing occupation | §9 | RT-43, RT-81 |
| Crash in any phase | journal + VTS registry + §5.3 | RT-16 |
| Committed or copied journal | §5.1 foreign artefact | RV2-A24 |
| Exchange dropping trust statements | §5.2 union | RV2-A26 |
| Forged `overlay.prev` weakening | computed weakening + trust gate (`20` §5) | RV2-A25 |
| Cache replacement | no cache | RT-45 |
| Derived artefact built under another kernel or policy, or by a legacy binary | VU-8 CI and policy digest | RT-71 |
| Agent reads kernel or adapter content from disk | VU-13, §12 | RV2-A22 |
| Repository command writes pins or trust paths before a trust decision | VU-14 | RT-103 |
| Cross-device transaction area | §3 | RT-123 |
| Occupation entry presented with the wrong type | §3 | RT-125 |

## 11. Residuals

| ID | Residual | Bound |
|---|---|---|
| VR-1 | A3 modifies installed files between two units of work. | The current unit is unaffected; the next unit detects it (VU-11). There is no "never re-checked" process. |
| VR-2 | A3 ignores advisory locks. | Refusals only. |
| VR-3 | Processes outside `gov` (editors, shells, unconfined agents) write PPS, the overlay, records or the VTS; confined children write the overlay or records. | PPS: detected by the next unit of work. Overlay: project-strength vector over effective policy (`26` §6). Records: never authorise trust decisions (`27`). VTS: same-user boundary (RS-3); protected pins are out of reach. |
| VR-4 | Plugin runtimes and model files consumed by path. | `10` §5. |

## 12. Agent consumption of kernel content (R2-M8)

1. **Adapters carry pointers, not constitutional text.** Rendered adapter files contain the framework and project
   identity, the CI, and instructions to obtain content from `gov`:
   - `gov context compile`;
   - `gov kernel show <path>`, which serves snapshot bytes with the CI;
   - `gov skills show <id>`.

   Invariant statements in adapters are served, not copied. Where a harness requires inline text, the text is rendered
   per context packet from the snapshot.
2. **Rendering record outside A2's reach.** When `gov adapters generate` writes an adapter body, it records the body
   digest and the CI in the VTS per-project record. `gov status`, context packets and doctor D036 report
   `ADAPTER_BODY_UNRECORDED` or `ADAPTER_BODY_MODIFIED` when the on-disk body differs. A2 rewriting both the body and
   `adapter-manifest.json` cannot match the local record.
3. **Direct reads are T4.** The generic adapter's "Canonical sources: governance/kernel/" line
   (`framework/adapters/generic/template.md:4`) is replaced by a pointer to `gov kernel show`. Agents reading
   `governance/trust/kernel/**` or adapter files directly act on T4 material. The context packet carries a CI stamp an
   agent can compare with `gov status`.
4. **Bound.** An agent that ignores `gov` and follows an arbitrary repository file is outside every design (A2 can write
   any instruction file). `gov` enforcement is unaffected, and the acceptance plan asserts that governed operations use
   snapshot bytes only.
