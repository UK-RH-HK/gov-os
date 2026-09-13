# Output 9 — Integration requirements (init, adopt, update, reinstall, rollback, recovery and adjacent ingress)

Normative keywords: MUST / MUST NOT / SHOULD. Requirement IDs are referenced by `02-INGRESS-MAP.md` and
`12-ACCEPTANCE-TEST-PLAN.md`.

## 1. Common order of evaluation (every ingress command)

1. `control::guard_write` (pause/freeze) and kernel_trust v2 guard, with the remedy exemptions of `04` §5;
2. authority check for the operation (levels read from the authenticated kernel; for a first install, from the
   authenticated target release after step 3, before any write);
3. `authenticate(SourceRef)` → `AuthenticatedRelease`;
4. authorisation (`04` §8): certification policy, gates bound to `release_statement_digest`, downgrade, minimum trust;
5. install transaction (§3);
6. post-commit kernel_trust v2 must return the same statement digest with `verified: true` (production) — else automatic
   journal rollback;
7. ledger entry, checkpoint, typed result.

Every trust failure in steps 1–6 MUST return `ok: false` (API-0002 exit code 1) with a code from §4, never
`ok: true, applied: false` (closes V-L2 for trust refusals).

## 2. Per-ingress requirements

### init — I-01, I-02

| ID | Requirement |
|---|---|
| R-INIT-1 | `init` MUST authenticate its source (explicit `--source`, canonical checkout, or embedded payload) before creating `governance/`. |
| R-INIT-2 | The embedded payload MUST be authenticated via the embedded statement and in-memory digests (R-EMB-1); a development binary's embedded kernel is `DEVELOPMENT_UNSIGNED` and follows R-DEV. |
| R-INIT-3 | `init` MUST write `governance/trust/release.dsse.json` (and certification if present) inside the transaction and the lock last. |
| R-INIT-4 | A `release_commit` or `source` label MUST come from the statement and `SourceRef.kind`, never from `manifest.json`, `git rev-parse` or path text. |
| R-INIT-5 | If authority validation fails after install (today's `remove_file(framework.lock)` pattern), the transaction MUST roll back kernel, trust files and lock together. |
| R-INIT-6 | `init --force` on an installed project MUST be treated as reinstall (same identity) or update (different identity): downgrade, gate and identity rules apply. |
| R-INIT-7 | `init` MUST print the trust-root id and record it in the lock; OP-6 decides whether confirmation is mandatory. |

### adopt — I-03, I-30

| ID | Requirement |
|---|---|
| R-ADOPT-1 | `adopt migrate --batch 0` MUST use the same authenticate → transaction path as init. |
| R-ADOPT-2 | When a lock already exists, batch 0 MUST run kernel_trust v2 and refuse on `UNAUTHENTICATED`/`TAMPERED` instead of reading the existing manifest. |
| R-ADOPT-3 | Pre-install adoption stages (A1 inventory secret scanner, A3 `ARCHIVE_POLICY`) MUST read policy from the authenticated embedded baseline, never from `GOV_CANONICAL_ROOT`/`GOV_KERNEL_SOURCE`. |

### update — I-04, I-05, I-31

| ID | Requirement |
|---|---|
| R-UPD-1 | `update --check` MUST run `authenticate` (report mode) and report the trust verdict, trust level, signer, certification and any refusal code. |
| R-UPD-2 | Every value in the check result (target version, compatibility, migration path, breaking changes, human gates, certification) MUST come from the authenticated statement and certification statements. `manifest.json` MUST NOT be read. |
| R-UPD-3 | Dry-run migrations MUST be loaded from the authenticated quarantine tree only (no `migrations_for_source` parent-directory search). |
| R-UPD-4 | `update --apply` MUST re-authenticate (never reuse a check result from another process). |
| R-UPD-5 | The `framework_update` gate MUST record `release_statement_digest`; only a gate whose digest equals the authenticated statement digest authorises the apply. |
| R-UPD-6 | Gate requirement MUST be computed per `04` §8 (certification ≠ CERTIFIED, breaking changes, declared human gates, trust-level decrease). |
| R-UPD-7 | The snapshot MUST include `governance/trust/` and the journal of the previous authenticated identity. |
| R-UPD-8 | Migrations MUST be loaded from the `AuthenticatedRelease`, validated against the authenticated kernel's migration schema, and restricted by the `set_lock_field` allowlist (`08` §4). |
| R-UPD-9 | Tool registry, plugin registry checks and adapters MUST be regenerated from `TrustedKernel` after commit. |
| R-UPD-10 | Post-update doctor/audit MUST include the new trust checks (§5); a critical trust finding triggers rollback. |
| R-UPD-11 | The ledger entry MUST record `release_id`, `release_statement_digest`, signer key ids, trust level, certification, gate id and source reference. |
| R-UPD-12 | An update whose target authenticates MAY run while the installed kernel is `UNAUTHENTICATED`/`TAMPERED` (strictly trust-increasing); gates and authority for it are evaluated with floors from the embedded baseline. |

### kernel reinstall — I-08

| ID | Requirement |
|---|---|
| R-RI-1 | Reinstall restores the **installed identity**: the source MUST authenticate and its statement digest MUST equal `governance/trust/release.dsse.json`'s digest (or, for legacy installs, its tree digest MUST equal the legacy-identity entry of the installed version). |
| R-RI-2 | Source resolution order: explicit `--source`; bundle in the user release cache; embedded payload if its statement digest matches. `lock.source` MUST NOT be treated as a filesystem path. |
| R-RI-3 | A reinstall MAY replace `governance/trust/release.dsse.json` with a re-signed envelope of the same payload digest (re-attestation). |

### rollback — I-06, I-07

| ID | Requirement |
|---|---|
| R-RB-1 | A snapshot restore MUST authenticate the snapshot's kernel against the snapshot's statement (or legacy identity) before any byte is restored (`SNAPSHOT_UNAUTHENTICATED`). |
| R-RB-2 | Explicit rollback MAY lower the version only to the identity recorded as `from` in the matching ledger `update` entry, and MUST be refused if that identity is now revoked with `refuse_install`. |
| R-RB-3 | Explicit rollback that lowers the trust level (e.g. `CERTIFIED` → `AUTHENTICATED_REJECTED`) MUST raise a Human Decision Gate bound to both statement digests. |
| R-RB-4 | Kernel, `governance/trust/`, overlay, generated views and lock are restored as one transaction. |

### override — I-09

| ID | Requirement |
|---|---|
| R-OV-1 | `kernel override` remains a fingerprint-bound L4+ gate permitting operation on an untrusted kernel; it MUST NOT change `authenticated`, `trust_level` or the policy root (floors stay on the authenticated baseline), and MUST NOT be available for revoked releases. |

### recovery — I-10

| ID | Requirement |
|---|---|
| R-REC-1 | Every `gov` invocation MUST detect an incomplete install journal and refuse mutating operations with `INSTALL_INTERRUPTED` (read-only diagnostics and `gov recover` remain available). |
| R-REC-2 | `gov recover` MUST complete or roll back the transaction per §3.3 and write a recovery report. |
| R-REC-3 | Recovery MUST NOT restore kernel, trust files or lock except through the journal-bound authenticated restore. |
| R-REC-4 | Adoption A0 classification of `governance/` without a lock MUST consult the install journal first. |

### embedded payload — I-11, I-12, I-22

| ID | Requirement |
|---|---|
| R-EMB-1 | The embedded statement MUST be authenticated and the embedded bytes digested in memory once per process. |
| R-EMB-2 | Materialised directories MUST be re-digested before use; `.complete` markers are never evidence. |
| R-EMB-3 | The fail-closed policy baseline MUST be served from `KernelFs::Embedded` (memory). |
| R-EMB-4 | `build.rs` MUST NOT derive provenance from unsigned files; it embeds statement bytes and lets the runtime decide. |

### environment — I-13, I-14

| ID | Requirement |
|---|---|
| R-ENV-1 | `GOV_CANONICAL_ROOT` selects a source only; `Project::schemas` MUST NOT fall back to it. |
| R-ENV-2 | `GOV_KERNEL_SOURCE` MUST be removed. |
| R-ENV-3 | `GOV_KERNEL_CACHE` may relocate materialisation only. |
| R-ENV-4 | No environment variable may add keys, roots, revocation data or trust levels. |

### use-time — I-15, I-16, I-17

| ID | Requirement |
|---|---|
| R-USE-1 | kernel_trust v2 per `04` §5 on every process that reads kernel content. |
| R-USE-2 | New doctor checks: **D030** installed kernel authenticated (CRITICAL when `UNAUTHENTICATED`/`TAMPERED`/`REVOKED`; HIGH for `DEVELOPMENT_UNSIGNED` or legacy; MEDIUM for `AUTHENTICATED_UNCERTIFIED`); **D031** lock identity consistent (CRITICAL); **D032** trust metadata freshness (MEDIUM, OP-5); **D033** no incomplete install journal (CRITICAL). D003/D004/D029 wording distinguishes integrity from authenticity. |
| R-USE-3 | Context packets and `gov status` surface `trust_level`, `release_id`, certification. |
| R-USE-4 | V-H2 behaviour (substitution, `KERNEL_TAMPERED`, fingerprint-bound override) is preserved. |
| R-USE-5 | All kernel reads go through `TrustedKernel`; the architecture test forbids `Project::kernel_dir()` outside the trust module. |

### migrations — I-18

| ID | Requirement |
|---|---|
| R-MIG-1 | Migration files are loaded only from an `AuthenticatedRelease` or `TrustedKernel`. |
| R-MIG-2 | `stage_payload`'s parent-directory fallback for `migrations`/`tools` MUST be removed from consumer paths (producer only). |
| R-MIG-3 | `set_lock_field` allowlist (`08` §4). |
| R-MIG-4 | Migration operations remain declarative; any future executable migration step requires its own statement binding and a new decision. |

### producer, verification, certification — I-19, I-20, I-21

| ID | Requirement |
|---|---|
| R-REL-1 | `release build` emits `release.statement.json` (unsigned canonical payload) and never signs. |
| R-REL-2 | `release build` refuses private key material (`PRIVATE_KEY_MATERIAL_DETECTED`). |
| R-REL-3 | `release build` validates the statement with the compiled-in schema. |
| R-REL-4 | `release attach-signature` verifies before attaching. |
| R-REL-5 | `release verify` = authenticate in report mode. |
| R-CERT-1 | Certification is a signed certification statement; the `certification` block in `manifest.{json,yaml}` becomes descriptive only. |
| R-CERT-2 | `VERDICT.md` convention continues; the release owner signs the certification statement referencing the verifier report digest instead of editing a trusted field. |

### transport and bundles — I-23, I-24

| ID | Requirement |
|---|---|
| R-NET-1 | `gov release fetch <reference>` is a transport into the user release cache or a scratch directory; it MUST NOT install. |
| R-NET-2 | Credentials for private hosting are read from the platform credential store or environment, never written to locks, ledgers or statements. |
| R-NET-3 | Nothing fetched is trusted before `authenticate`; network failure never changes a trust decision on already-present material. |
| R-BUN-1 | Archive extraction rules per `07` §6 run in quarantine before authentication. |

### plugins, tools, profiles — I-25, I-26, I-27, I-28, I-32, I-33

| ID | Requirement |
|---|---|
| R-PLG-1 | The plugin authority floor and permission classes are read via `TrustedKernel`. |
| R-PLG-2 | Profile-bound registry entries record `profile_statement_digest`; descriptors discovered via `$GOV_PLUGINS_DIR` can never be profile-bound. |
| R-TOOL-1 | Kernel-shipped tool descriptors are trusted only through the authenticated kernel; project descriptors remain governed by TOOL_POLICY. Hash-pinned package installation SHOULD be added to TOOL_POLICY (non-blocking). |
| R-PRF-1…6 | Per `10-RETRIEVAL-PROFILE-TRUST.md` §4–§5; R-PRF-6: memory-select pins of a reference profile record the profile statement digest. |
| R-AUTH-7 | Statement and lock schemas used for trust decisions are compiled into the binary. |
| R-LOCK-1 | Lock identity cross-check per `08` §3; `LOCK_IDENTITY_MISMATCH` on any disagreement. |

### development path — R-DEV

| ID | Requirement |
|---|---|
| R-DEV-1 | Production profile: unsigned sources require `--allow-unsigned-development` per command. |
| R-DEV-2 | The acknowledgement (actor, role, session, time, file map) is written to `governance/trust/development.json`, and the ledger records it. |
| R-DEV-3 | Floors are read from the authenticated embedded baseline; mutations require the fingerprint-bound override gate. |
| R-DEV-4 | A development install MUST NOT be reported as authenticated or certified by any command. |
| R-DEV-5 | Any transition from a higher trust level to `DEVELOPMENT_UNSIGNED` raises a gate (`DEVELOPMENT_TRUST_DOWNGRADE_REFUSED` without one). |

## 3. Install transaction

### 3.1 Journal

`.governance-runtime/install/<TX>/journal.json` (local, derived) with phases and the statement digests of the previous and
target identities. An exclusive lock file prevents concurrent transactions (`INSTALL_TRANSACTION_CONFLICT`).

### 3.2 Phases

| Phase | Action | Writes to trust locations |
|---|---|---|
| `prepared` | ARO produced; authorisation recorded; previous identity + snapshot (kernel, trust, overlay, generated, lock) captured | none |
| `staged` | `governance/.kernel.next-<TX>/` and `governance/.trust.next-<TX>/` built from quarantine bytes, fsynced, re-digested (`SOURCE_CHANGED_DURING_INSTALL`) | staging dirs only |
| `swapped` | rename `kernel`→`.kernel.prev-<TX>`, `.kernel.next`→`kernel`; same for `trust` | kernel, trust |
| `migrated` | migrations from the ARO applied to overlay/generated; overlay preservation check | overlay, generated |
| `committed` | lock written via temp + rename (**commit point**) | lock |
| `verified` | kernel_trust v2 authenticated with the target digest; doctor/audit; ledger; `.prev` removed | ledger |

### 3.3 Recovery rules

| Journal phase found | Recovery |
|---|---|
| `prepared` or `staged` | delete staging; nothing else changed |
| `swapped` or `migrated` | swap back `.kernel.prev`/`.trust.prev`; restore overlay/generated from snapshot; lock untouched |
| `committed` but not `verified` | re-run verification; on failure, authenticated restore of the previous identity (R-RB-1) |

Invariant: kernel files of one identity are never paired with a trust directory or lock of another identity in any state
that kernel_trust v2 reports as verified (both are checked against the same statement digest). Directory rename is
atomic on POSIX filesystems; on platforms without atomic directory replacement, the journal-driven swap-back is the
guarantee.

## 4. Error catalogue (machine-readable; `error.code`, `error.details.stage`, `error.details.*`)

| Code | Stage | Meaning | Key details |
|---|---|---|---|
| `KERNEL_SOURCE_NOT_FOUND` | V0 | no kernel at the source | `source_reference` |
| `RELEASE_TREE_INVALID` | V1 | symlink, traversal, collision, limits | `path`, `rule` |
| `RELEASE_STATEMENT_MISSING` | V2 | required statement absent | `looked_in[]` |
| `UNSIGNED_SOURCE_REFUSED` | V2 | production binary, no statement, no dev flag | `remediation` |
| `RELEASE_STATEMENT_MALFORMED` | V3/V7 | envelope/payload/schema/canonical-form error | `reason` |
| `TRUST_ROOT_INVALID` / `TRUST_ROOT_ROLLBACK` / `TRUST_ROOT_THRESHOLD_NOT_MET` | V4 | root chain problems | `root_version`, `high_water` |
| `REVOCATION_LIST_ROLLBACK` | V4 | older revocation sequence | `sequence`, `floor` |
| `RELEASE_SIGNER_UNKNOWN` | V5 | key id not in root | `key_id` |
| `RELEASE_SIGNER_NOT_AUTHORISED` | V5 | key lacks role for payloadType | `key_id`, `role_required` |
| `RELEASE_SIGNATURE_INVALID` | V5 | signature does not verify | `key_id` |
| `RELEASE_ALGORITHM_MISMATCH` | V5/V7 | declared algorithm ≠ key algorithm | |
| `RELEASE_THRESHOLD_NOT_MET` | V5/V6 | too few valid signatures | `valid`, `threshold` |
| `TRUST_PROFILE_MISMATCH` | V5 | test material on production binary (or vice versa for locks) | `profile` |
| `RELEASE_SIGNER_REVOKED` / `RELEASE_REVOKED` | V6 / use | revoked key or release | `revocation_sequence` |
| `RELEASE_IDENTITY_MISMATCH` | V8 | framework/version/release_id disagreement | `expected`, `observed` |
| `RELEASE_REPLAY_DETECTED` | V8/V12 | statement for another identity, or equivocation | `statement_digest`, `installed_digest` |
| `RELEASE_DIGEST_MISMATCH` | V9 | content ≠ statement | `modified[]`, `missing[]`, `added[]`, `component` |
| `MIGRATION_NOT_IN_STATEMENT` / `MIGRATION_DIGEST_MISMATCH` | V10 | migration binding | `migration`, `path` |
| `RELEASE_INCOMPATIBLE` | V11 | CLI/contract/supported-from | `requirement` |
| `RELEASE_DOWNGRADE_REFUSED` | V12 | lower version/sequence | `installed`, `target` |
| `CERTIFICATION_STATEMENT_INVALID` / `CERTIFICATION_MISMATCH` | V13 | certification problems | `statement` |
| `DEVELOPMENT_TRUST_DOWNGRADE_REFUSED` | auth | trust decrease without gate | |
| `SOURCE_CHANGED_DURING_INSTALL` | tx | staged bytes ≠ authenticated bytes | `path` |
| `INSTALL_TRANSACTION_CONFLICT` / `INSTALL_INTERRUPTED` | tx / use | concurrent or incomplete transaction | `transaction_id`, `phase` |
| `SNAPSHOT_UNAUTHENTICATED` | rollback | snapshot fails authentication | nested code |
| `EMBEDDED_BASELINE_CORRUPT` / `EMBEDDED_BASELINE_UNAVAILABLE` | use | materialised embedded bytes ≠ compiled digests | `path` |
| `KERNEL_UNAUTHENTICATED` | use | installed statement missing/invalid/unknown identity | nested code |
| `KERNEL_TAMPERED` | use | installed files ≠ authenticated statement (unchanged meaning) | `modified[]`… |
| `LOCK_IDENTITY_MISMATCH` | use | lock ≠ statement | `field` |
| `PROFILE_STATEMENT_INVALID` / `PROFILE_DIGEST_MISMATCH` / `MODEL_DIGEST_MISMATCH` / `PROFILE_INCOMPATIBLE` | profile | profile trust | `profile_id`, `path` |
| `PRIVATE_KEY_MATERIAL_DETECTED` | producer | key material in tree | `path` |
| `TRANSPORT_FAILED` | fetch | download failed (never a trust verdict) | `reference` |
