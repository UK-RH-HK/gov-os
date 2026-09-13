# Output 6 — TOCTOU and Transaction-Safety Review

## 1. Ingress TOCTOU (source → quarantine → staging)

| Mechanism (`04` V1, `09` §3) | Assessment |
|---|---|
| Single read of each file into a private 0700 directory or memory | A same-uid process (A3) can still write a 0700 directory it owns. Safety therefore rests on the next two steps, which are present. |
| Re-digest of staged copies before swap (`SOURCE_CHANGED_DURING_INSTALL`) | sound |
| Post-commit `kernel_trust` v2 with the target digest; failure → journal rollback | sound |
| Migrations and templates during the transaction | must be read from the `AuthenticatedRelease` **memory**, not from `governance/.kernel.next-<TX>` or the swapped directory. `add_overlay_file_from_template` and `reconcile_overlay_defaults` read template files by path today (`migrations/framework.rs:91-106`, `:339-382`). Not specified (AC-F4). |

**Verdict:** ingress TOCTOU is **COVERED**, subject to AC-F4.

## 2. Use-time TOCTOU — verified bytes versus used bytes (RV-H3)

RoT-1 specifies a “`TrustedKernel` read handle over installed dir or embedded in-memory map” (`04` §2) and one
verification per process (`04` §5). Nothing binds the bytes that enforcement later reads to the bytes that were digested.
4.1.5 has the same shape: `kernel_trust::compute` hashes the tree (`kernel_trust.rs:134`), then `PolicySet::load` re-opens
the policy files from `policy_root` (`policy.rs:98-101`). RT-22 tests only source-side racing.

### Executed evidence against the 4.1.5 binary (`evidence/R2b-use-time-toctou.{py,json}`)

A same-user process watches `governance/kernel/policies/SECURITY_POLICY.yaml` with inotify. On the first
`IN_CLOSE_NOWRITE` (kernel_trust's hash read) it rewrites the file in place without `restricted` in
`never_index_classes`. It restores the original bytes when `gov` exits.

| Step | Observation |
|---|---|
| Scope check (unclassified) | `spec/decisions/D-9001.yaml` and `product/restricted-plan.md` are indexed and retrievable (`docs/` is outside the contract scope) |
| Control, intact kernel, both classified `restricted` | both **excluded** (`sensitivity:restricted`), not indexed, not retrievable |
| Raced `rebuild-memory`, trial 1 | swap landed **0.11 ms** after kernel_trust's read; both files **indexed** with `sensitivity = restricted` in `artifacts`; `excluded` empty |
| Afterwards, **unraced** processes on the byte-identical restored kernel | `memory query` returns **both** restricted files; `kernel trust` → `verified: true`; doctor D003, D004, D029 → ok |

A preliminary run (`evidence/R2-preliminary-probes.py`) used `customer/**`, which is outside the index scope. There the
swapped floor was consumed in **5/5** trials: the restricted exclusion disappeared, although nothing was indexed because
of scope.

**Consequence.** An in-scope adversary (A3, the same class the pack uses for E3 and E5) causes persistent removal of a
constitutional floor with no residual evidence, while every integrity attestation stays green. RoT-1 as written
reproduces this, so post-install integrity (review area 3) is not established.

### Required design (CD-4)

1. `TrustedKernel` is an **immutable in-memory snapshot**: each kernel file is read once into memory, digested from that
   buffer, compared with the statement, and parsed from the **same buffer**. No component re-opens kernel paths after
   verification.
2. Installed-tree rules at use time equal the quarantine rules. Refuse symlinks and non-regular files, **including
   ancestors** `governance/`, `governance/kernel/`, `governance/trust/`. Open without following links (e.g.
   `openat2(RESOLVE_NO_SYMLINKS)` or `O_NOFOLLOW` on each component, with a fallback that `lstat`s each component and
   compares device and inode before and after).
3. A long-lived process (a future MCP server) holds the snapshot or re-verifies before each constitutional read; it
   never mixes snapshot generations.
4. Acceptance: RV-A25 (race after hash read), RV-A38 (symlinked ancestor), both with harm assertions.

## 3. Symlink and path substitution during staged install

| Vector | Pack | Required |
|---|---|---|
| A3 pre-creates `governance/.kernel.next-<TX>` or `.trust.next-<TX>` as a symlink to another directory | not addressed | create staging directories exclusively (fail if they exist); `<TX>` unpredictable; verify with `lstat` and a no-follow open; write files with `O_EXCL \| O_NOFOLLOW` |
| A2 commits `governance`, `governance/kernel` or `governance/trust` as a symlink (Git stores symlinks) | not addressed | refuse before any read or write (`RELEASE_TREE_INVALID` at install; `KERNEL_UNAUTHENTICATED` at use) |
| Symlink inside quarantine source | `07` §5.1 refuses | sound |
| Archive members with links, `..` or absolute paths | `07` §6 refuses | sound |

## 4. Swap atomicity and reader windows

The swap is four renames over two directories (`kernel`→`.kernel.prev`, `.kernel.next`→`kernel`, then the same for
`trust`). Between them a concurrent reader can see: no kernel; new kernel with old statement; old kernel with new
statement.

- Mixed kernel and statement: v2 reports a mismatch → fail closed. Acceptable.
- **No kernel directory:** in 4.1.5 this takes the `uninstalled` branch, where the guard passes and the policy root is the
  (missing) installed directory (`kernel_trust.rs:128-130, 289-291`). v2 must classify “lock or journal present, kernel or
  trust missing” as UNAUTHENTICATED, with the embedded baseline and mutations refused (RV-M2).
- Readers must check for an incomplete journal **before** reading kernel content and take a shared lock that the
  transaction's exclusive lock excludes (AC-F2).

## 5. Crash consistency

| Point | Pack | Required |
|---|---|---|
| File data durability in staging | fsync mentioned | also fsync the **directory entries** after each rename, and the parent of the lock after its rename (AC-F3) |
| Lock commit point | temp + rename | sound |
| Ledger write after commit | `install_evidence.ledger_entry` must exist in the ledger (`08` §3) | a crash after lock commit and before the ledger append would make a genuine install fail its own cross-check. Recovery must write the ledger entry idempotently from the journal (AC-F5). |
| Windows non-atomic directory replace | journal swap-back | acknowledged; acceptable |

## 6. Journal as adversarial input (RV-A15)

`.governance-runtime/install/<TX>/journal.json` and `.kernel.prev-<TX>` are writable by A3.

- **A3 alone:** forge phase `swapped` and plant an older **genuine** kernel + trust set as `.prev`. `gov recover` swaps
  back, but the lock still records the current identity → `LOCK_IDENTITY_MISMATCH` → fail closed. Availability impact
  only.
- **A2 + A3** (edit the lock too), or **A3 via adoption batch restore** (I-34, which restores the lock too): the older
  genuine release verifies and becomes the policy root. This is a currency failure (RV-H1).
- Required: recovery re-authenticates every restored set **and** applies the same currency and downgrade rules as an
  explicit rollback. A trust-level or sequence decrease requires the gate, unless the current state is already
  unverified (AC-C4).

## 7. Concurrency

| Case | Assessment |
|---|---|
| Two install transactions | exclusive lock file (`INSTALL_TRANSACTION_CONFLICT`); advisory, so A3 can delete it, but it protects honest concurrency |
| Install transaction versus CIT execution, adoption executor, `rebuild-memory` | not specified. These writers and readers must take the same lock (shared for readers, refusal for writers) (RV-M1, AC-F2) |
| Concurrent `update --apply` from two sessions for different statement digests | gate binding per digest plus exclusive lock: sound |

## 8. Summary

| Area | Verdict |
|---|---|
| Source TOCTOU | COVERED (AC-F4) |
| Use-time TOCTOU | **NOT COVERED — RV-H3 (executed)** |
| Symlink/path substitution in staging and ancestors | NOT SPECIFIED |
| Swap reader windows | PARTIAL (RV-M2) |
| Crash consistency | PARTIAL (directory fsync, ledger idempotence) |
| Journal integrity | PARTIAL (RV-H1 coupling) |
| Concurrency with non-install writers | NOT SPECIFIED (RV-M1) |
