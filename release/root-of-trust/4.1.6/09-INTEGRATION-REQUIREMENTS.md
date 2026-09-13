# Output 9 — Integration requirements

> **RoT-1 revision 2 — PROPOSED, pending a fresh independent review; not approved, not implemented.**
> Normative keywords: MUST, MUST NOT, SHOULD. Requirement IDs are referenced by `02` and `12`. Mechanisms are defined in
> `04`, `05`, `17`, `18`, `19` and `20`; this file states obligations per ingress and catalogues codes.

## 1. Common order of evaluation (every command)

1. Read `governance/trust/FORMAT`; an unsupported format stops here (`TRUST_FORMAT_UNSUPPORTED`).
2. Determine the installation state (`18` §9).
3. Build the knowledge set and effective trust state (`17` §5).
4. Load the KernelSnapshot or EmbeddedSnapshot and compute the verdict and effective floor (`18` §6, `19` §5–§6).
5. `control::guard_write` (pause/freeze) and the kernel-trust guard, with the remedy exemptions of `04` §5.
6. For ingress: `authenticate` (`04` V0–V12).
7. For ingress: eligibility, trust-state requirement, gates, install-authority floor, computed weakenings, downgrade
   policy (`04` §4).
8. For ingress: install transaction (`18` §5), including post-commit snapshot equality and eligibility.
9. Ledger entry (idempotent from the journal), checkpoint, typed result.

Every trust failure MUST return `ok: false` (API-0002 exit code 1) with a code from §4. Trust refusals are never
`ok: true, applied: false`.

## 2. Requirements by ingress

### init — I-01, I-02

| ID | Requirement |
|---|---|
| R-INIT-1 | `init` MUST authenticate its source (explicit `--source`, canonical checkout, or EmbeddedSnapshot) and complete authorisation before creating any Protected Path. |
| R-INIT-2 | Required authority MUST come from the install-authority floor (`19` §8) — TPS and EmbeddedSnapshot for an `ABSENT` project — never from the release being installed. |
| R-INIT-3 | Production `init` MUST require an eligible final release (`19` E1–E8), or an eligible candidate with the evaluation flag. |
| R-INIT-4 | Production `init` MUST record an init-acknowledgement Human Decision Gate bound to the statement digest, showing authenticity, eligibility, certification view with its sequence, and trust state (`21` OP-3). |
| R-INIT-5 | `init` MUST write `governance/trust/` (FORMAT, release envelope, lineage candidate, PTR state) and lock 2.0.0 inside the transaction, lock last. |
| R-INIT-6 | `init --force` on an installed project MUST be treated as reinstall (same statement digest) or update/downgrade (different digest), with the corresponding rules. |
| R-INIT-7 | `init` MUST print the trust-root id and apply OP-6 confirmation before any trusted write (`06` §3). |
| R-INIT-8 | `release_commit` and `source` labels MUST come from the statement and `SourceRef.kind`, never from `manifest.json`, `git rev-parse` or path text. |

### adopt — I-03, I-30, I-34, I-36

| ID | Requirement |
|---|---|
| R-ADOPT-1 | `adopt migrate --batch 0` MUST use the `init` pipeline with operation `adopt_install`. |
| R-ADOPT-2 | When protected paths already exist, batch 0 MUST evaluate them through the installation state machine and refuse to proceed unless the state is `ABSENT` or `COMPLETE`, verified and eligible. |
| R-ADOPT-3 | Pre-install stages (A1 scanner, A3 `ARCHIVE_POLICY`) MUST read policy from the EmbeddedSnapshot ⊔ floor, never from `GOV_CANONICAL_ROOT` or `GOV_KERNEL_SOURCE`. |
| R-ADOPT-4 | The planner MUST classify all PPS paths as `GOVERNANCE_CURRENT` and never include them in moves, deletions or snapshots. Batch 0 rollback MUST be `install_tx::uninstall`; rollback of batches ≥ 1 MUST go through GovernedFs (`20` §6). |
| R-ADOPT-5 | A7 migration verification and A11 audit MUST use the snapshot verdict, not a self-manifest check (I-36). |

### update — I-04, I-05, I-31

| ID | Requirement |
|---|---|
| R-UPD-1 | `update --check` MUST run `authenticate` in report mode and report eligibility, trust state, certification view, computed weakenings, gate requirement and authority. |
| R-UPD-2 | Every value in the check result MUST come from signed statements, the effective state and the snapshot. `manifest.json` MUST NOT be read. |
| R-UPD-3 | Dry-run migrations MUST be interpreted from ARO blobs only. |
| R-UPD-4 | `update --apply` MUST re-authenticate and never reuse a check result from another process. |
| R-UPD-5 | The `framework_update` gate MUST record `release_statement_digest` (and, for downgrade, both digests; for weakenings, the list digest). Only an exactly matching presented, answered-A gate authorises. |
| R-UPD-6 | Gate requirement per OP-3 mode (TPS `gating`); certification MUST NOT remove a gate in mode A; computed weakenings MUST gate in every mode (`19` §9). |
| R-UPD-7 | Trust state MUST NOT be `STALE`; `HINT_MISMATCH` MUST add a gate (`17` §7). |
| R-UPD-8 | Migrations MUST come from the ARO, form a unique chain, and have no lock operation (`08` §4). |
| R-UPD-9 | The transaction MUST snapshot overlay and generated views into `.tx/<TX>/overlay.prev/` and write `.governance-runtime/snapshots/<CI>/` for the previous identity (`20` §3). |
| R-UPD-10 | Tool registry, plugin registry and adapters MUST be regenerated from the new snapshot after commit and record the new CI. |
| R-UPD-11 | Post-commit verification MUST include snapshot CI equality, eligibility, doctor D030–D034 and the audit families. Any critical finding triggers automatic rollback. |
| R-UPD-12 | The ledger entry MUST record previous and new CI, signer key ids, purpose, eligibility, certification view, trust-state status, TPS version, gate ids and source reference. |
| R-UPD-13 | An update whose target authenticates and is eligible MAY run while the installed kernel is `UNAUTHENTICATED`, `TAMPERED`, `INELIGIBLE` or `PARTIAL`; gates and authority use the floor. |
| R-UPD-14 | Known REJECTED or WITHDRAWN finals MUST be refused when TPS `gating.refuse_known_*` is true. |

### kernel reinstall — I-08

| ID | Requirement |
|---|---|
| R-RI-1 | The source MUST authenticate, and its statement digest MUST equal the installed `release.dsse.json` payload digest. |
| R-RI-2 | Source order: explicit `--source`; a bundle in the user release cache (an untrusted source); the EmbeddedSnapshot if its statement digest matches. `lock.source` MUST NOT be treated as a path. |
| R-RI-3 | A re-signed envelope of the same payload digest MAY replace `release.dsse.json` (re-attestation). |

### rollback — I-06, I-07

| ID | Requirement |
|---|---|
| R-RB-1 | Every restore MUST run the restore pipeline (`20` §2): authenticate, eligibility under the current policy, downgrade policy, authority floor, transaction. |
| R-RB-2 | A downgrade MUST require a Human Decision Gate bound to both statement digests (`20` §4). |
| R-RB-3 | Targets below `min_release_sequence`, revoked, historical, or candidates in production MUST be refused without override. |
| R-RB-4 | Kernel, trust record, overlay, generated views and lock MUST be restored as one transaction. |
| R-RB-5 | Accepted trust metadata MUST NOT be removed by any rollback. |

### override — I-09

| ID | Requirement |
|---|---|
| R-OV-1 | `kernel override` MUST remain a fingerprint-bound L4+ gate permitting governed mutations on an untrusted kernel. It MUST NOT change authenticity, eligibility, the certification view or the policy root. |
| R-OV-2 | Override MUST NOT be available for `refuse_operation` revocations, `TRUST_STATE_REGRESSION`, `BINARY_BELOW_TRUST_POLICY` or `TRUST_ROOT_LINEAGE_MISMATCH`. |

### recovery — I-10, I-41

| ID | Requirement |
|---|---|
| R-REC-1 | Every invocation MUST detect `IN_TRANSACTION` and refuse mutations with `INSTALL_IN_PROGRESS` (read-only diagnostics and `gov recover` remain available). |
| R-REC-2 | `gov recover` MUST follow `20` §5 and treat the journal and `.prev` directories as hints only. |
| R-REC-3 | Recovery MUST NOT write Protected Paths except through the install transaction. |
| R-REC-4 | CIT and adoption recovery MUST go through GovernedFs. |
| R-REC-5 | Adoption A0 classification of an existing `governance/` MUST consult the installation state machine first. |

### embedded payload — I-11, I-12, I-22

| ID | Requirement |
|---|---|
| R-EMB-1 | The EmbeddedSnapshot MUST be verified against its compiled statement and digested in memory once per process. |
| R-EMB-2 | The embedded payload MUST NOT be materialised for any trust purpose; `GOV_KERNEL_CACHE` is removed. |
| R-EMB-3 | The fail-closed baseline MUST be the EmbeddedSnapshot joined with the effective floor. |
| R-EMB-4 | `build.rs` MUST NOT derive provenance from unsigned files. It embeds the root chain, TPS, TSS and referenced statements, historical registry and final statement bytes, and makes no trust decision. |

### environment — I-13, I-14, I-39, I-44

| ID | Requirement |
|---|---|
| R-ENV-1 | `GOV_CANONICAL_ROOT` MUST select a source only; `Project::schemas` MUST NOT fall back to it. |
| R-ENV-2 | `GOV_KERNEL_SOURCE` and `GOV_KERNEL_CACHE` MUST be removed. |
| R-ENV-3 | The VTS and pin-file locations MUST be resolved from the account database, never from `HOME`, `XDG_*` or `GOV_*`. |
| R-ENV-4 | No environment variable may add keys, roots, policies, trust state, certification, confirmation or eligibility. |
| R-ENV-5 | Lineage confirmation MUST come from a human command, an explicit flag or a pin file (`06` §3). |

### use time — I-15, I-16, I-17, I-31, I-37, I-46

| ID | Requirement |
|---|---|
| R-USE-1 | Every process that reads kernel content MUST build a KernelSnapshot or EmbeddedSnapshot per `18` §6. |
| R-USE-2 | All consumers MUST read kernel content from the snapshot API; GovernedFs MUST refuse other opens of `governance/kernel/**` and `governance/trust/**`. |
| R-USE-3 | The effective floor MUST be applied in policy loading from the snapshot (`19` §5). |
| R-USE-4 | V-H2 behaviour (substitution, `KERNEL_TAMPERED`, fingerprint-bound override) MUST be preserved. |
| R-USE-5 | Derived artefacts MUST record the CI and be treated as stale on mismatch (`18` VU-8). |
| R-USE-6 | Context packets and `gov status` MUST surface all verdict axes (`19` §6). |
| R-USE-7 | Doctor checks D030–D034 (§5) MUST be implemented; D003, D004 and D029 wording MUST distinguish integrity, authenticity and eligibility. |
| R-USE-8 | The VTS per-project record MUST be updated after verified snapshots and install transactions, and compared per E10. |

### migrations — I-18

| ID | Requirement |
|---|---|
| R-MIG-1 | Migrations MUST be loaded only from ARO blobs (ingress) or the KernelSnapshot (use). |
| R-MIG-2 | The `stage_payload` parent-directory fallback MUST NOT exist on consumer paths. |
| R-MIG-3 | There MUST be no migration lock operation; informational keys only through the compiled allowlist (`08` §4). |
| R-MIG-4 | The migration set MUST form a unique chain (`MIGRATION_CHAIN_AMBIGUOUS`). |
| R-MIG-5 | Computed weakenings MUST gate (`19` §9). |
| R-MIG-6 | Migration operations remain declarative; any executable step requires its own statement binding and a new decision. |

### producer, verification, certification — I-19, I-20, I-21, I-47

| ID | Requirement |
|---|---|
| R-REL-1 | `release build` MUST emit an unsigned candidate payload and never sign. |
| R-REL-2 | `release build` MUST refuse private key material. |
| R-REL-3 | `release build` MUST validate with compiled schemas and enforce `FLOOR_NOT_REGISTERED` / `FLOOR_VIOLATION`. |
| R-REL-4 | `release attach-signature` MUST verify (purpose, lineage, profile) before attaching. |
| R-REL-5 | `release verify` MUST be `authenticate` in report mode plus views. |
| R-REL-6 | `release promote` MUST require a verified ACCEPTED attestation for the candidate and produce identical content with `stage: final`. |
| R-REL-7 | Statement inputs MUST be deterministic (`05` §7). |
| R-REL-8 | The release pipeline MUST refuse a binary whose compiled `policy_version` is lower than the previous published binary's (`FLOOR_REGRESSION_IN_BUILD`), and a shipped binary not reporting `trust_profile: production`. |
| R-CERT-1 | Certification MUST be a signed certification-status statement; the manifest block is descriptive only. |
| R-CERT-2 | CERTIFIED MUST reference a verified ACCEPTED attestation for the promoted-from candidate. |
| R-CERT-3 | A CERTIFIED view MUST additionally require an admissible TSS reference (`17` §6). |
| R-CERT-4 | Negative certification states MUST be sticky (`17` MS-2). |
| R-CERT-5 | `VERDICT.md` continues. The verifier signs the attestation; the certification owner signs the certification; the publisher references both in the TSS. |

### trust state — I-39, I-42, I-43

| ID | Requirement |
|---|---|
| R-TS-1 | Only verified statements MAY enter the knowledge set (`17` §4). |
| R-TS-2 | The effective state MUST be computed per `17` S1–S10. |
| R-TS-3 | Non-admissible TSS MUST raise `TRUST_STATE_REGRESSION` and MUST NOT be used. |
| R-TS-4 | The negative set MUST be the union of all known negative facts minus TPS `unrevokes`. |
| R-TS-5 | Ingress MUST refuse on `STALE`, with no override. |
| R-TS-6 | TPS acceptance MUST be monotonic. Lowering MUST follow `19` §10 step 6. |
| R-TS-7 | `gov trust refresh` MUST write the PTR only through the install transaction area. |
| R-TS-8 | OP-3 mode B freshness proofs MUST follow `17` §13 exactly. |

### filesystem and protected paths — I-34, I-35, I-45

| ID | Requirement |
|---|---|
| R-FS-1 | All runtime file mutations MUST go through GovernedFs (`18` §8). |
| R-FS-2 | GovernedFs MUST refuse PPS targets without `InstallTxToken` (`PROTECTED_PATH_WRITE_REFUSED`). |
| R-FS-3 | GovernedFs MUST resolve targets through the secure primitives and refuse link crossings (`PATH_SUBSTITUTION_DETECTED`). |
| R-FS-4 | CIT planning MUST refuse PPS targets (`CIT_PROTECTED_PATH`) for every file operation. |
| R-FS-5 | `gov`-run git subprocess arguments MUST be pre-validated. |
| R-FS-6 | The conformance suite MUST prove no PPS mutation outside `install_tx` for every command, by interception (`02` §5). |
| R-FS-7 | Production-profile operation MUST refuse platforms lacking the `18` §3 primitives (`TRUST_PLATFORM_UNSUPPORTED`). |

### partial install — I-38

| ID | Requirement |
|---|---|
| R-PART-1 | Every process MUST evaluate the installation state machine before reading policy (`18` §9). |
| R-PART-2 | `PARTIAL`, `IN_TRANSACTION` and `ABSENT` MUST use the EmbeddedSnapshot ⊔ floor, including for commands not requiring an installation. |
| R-PART-3 | `PARTIAL` MUST refuse mutations except the remedies of `20` §8. |

### format boundary — I-40

| ID | Requirement |
|---|---|
| R-FMT-1 | Every RoT-1 install MUST write `governance/trust/FORMAT`, the lock sentinels and the tombstone `KERNEL_MANIFEST.json` exactly as `13` §3. |
| R-FMT-2 | RoT-1 binaries MUST NOT read the sentinel fields or the tombstone. |
| R-FMT-3 | Unknown formats or `minimum_reader` above the binary version MUST stop with `TRUST_FORMAT_UNSUPPORTED`. |
| R-FMT-4 | A project modified by a pre-RoT binary MUST be detected (`KERNEL_TAMPERED` / `INSTALL_STATE_PARTIAL`) and remediable by reinstall. |
| R-FMT-5 | The acceptance suite MUST run the real 4.1.5 binary against a genuine 4.1.6 project (`12` RT-50). |

### bootstrap — I-22, I-44

| ID | Requirement |
|---|---|
| R-BOOT-1 | The trust-root id MUST be published in at least two channels not sharing an attacker with the release host (`06` §2 step 2). |
| R-BOOT-2 | OP-6 confirmation MUST be implemented as chosen, and recorded in the VTS and lock. |
| R-BOOT-3 | Lineage mismatch MUST fail closed with no re-pin (`06` §4). |
| R-BOOT-4 | `gov trust verify-artifact` MUST verify `artifact-final` statements under the pinned lineage and root high-water. |

### transport and bundles — I-23, I-24

| ID | Requirement |
|---|---|
| R-NET-1 | `gov release fetch <reference>` is transport into memory or scratch only; it MUST NOT install. |
| R-NET-2 | Credentials for private hosting MUST come from the platform credential store and never enter locks, ledgers or statements. |
| R-NET-3 | Network failure MUST never change a trust decision on material already present. |
| R-BUN-1 | Archive members MUST be streamed into buffers under `07` §5.1 and §6 before authentication. |

### plugins, tools, profiles — I-25…I-28

| ID | Requirement |
|---|---|
| R-PLG-1 | Plugin authority floor and permission classes MUST come from the effective floor. |
| R-PLG-2 | Profile-bound registry entries MUST record `profile_statement_digest`; descriptors from `$GOV_PLUGINS_DIR` MUST never be profile-bound. |
| R-TOOL-1 | Kernel tool descriptors MUST come from the snapshot; project descriptors remain governed by TOOL_POLICY; hash-pinned package installation SHOULD be added. |
| R-PRF-1…7 | Per `10` §4–§5 (host-side verification; plugin-reported digests informational; CAS store; index writes rejected on post-use mismatch; compatibility re-check on kernel update; pins bind the profile digest). |

### schemas, lock, development path

| ID | Requirement |
|---|---|
| R-AUTH-1 | Statement, lock and FORMAT schemas used for trust decisions MUST be compiled into the binary. |
| R-AUTH-2 | Floor operators and `floor_schema_version` MUST be compiled (`19` §4). |
| R-LOCK-1 | Lock identity fields MUST be cross-checked against the statement (`LOCK_IDENTITY_MISMATCH`). |
| R-LOCK-2 | Lock reference fields MUST be treated as hints (`17` S8). |
| R-LOCK-3 | Only the install transaction MUST write the lock (`08` §4). |
| R-DEV-1 | Production: unsigned sources require `--allow-unsigned-development` per command. |
| R-DEV-2 | The acknowledgement MUST be written to `governance/trust/development.json` and the ledger. |
| R-DEV-3 | Floors MUST come from the EmbeddedSnapshot ⊔ floor; mutations need the override gate. |
| R-DEV-4 | A development install MUST NOT be reported as authenticated, eligible or certified by any command. |
| R-DEV-5 | Any transition to `DEVELOPMENT_UNSIGNED` MUST raise a gate (`DEVELOPMENT_TRUST_DOWNGRADE_REFUSED` without one). |

## 3. Install transaction

Defined normatively in `18` §5 (layout, phases, locking, platforms) and `20` §5 (recovery). Not duplicated here.

## 4. Error catalogue (`error.code`, `error.details.stage`, `error.details.*`)

| Code | Stage | Meaning | Key details |
|---|---|---|---|
| `KERNEL_SOURCE_NOT_FOUND` | V0 | no kernel at the source | `source_reference` |
| `RELEASE_TREE_INVALID` | V1 | link, special file, traversal, non-ASCII path, case collision, limits | `path`, `rule` |
| `RELEASE_STATEMENT_MISSING` | V2 | required statement absent | `looked_in[]` |
| `UNSIGNED_SOURCE_REFUSED` | V2 | production, no statement, no development flag | `remediation` |
| `STATEMENT_MALFORMED` | V3/V6 | envelope, canonical form, schema, empty signatures | `reason` |
| `STATEMENT_TYPE_UNKNOWN` | V3 | payloadType not in the compiled table | `payload_type` |
| `STATEMENT_SOURCE_NOT_PERMITTED` | V3 | statement type not accepted from this source (historical identity outside the binary) | `source` |
| `STATEMENT_TYPE_MISMATCH` | V7 | `_type`, `signing.purpose` or `stage` inconsistent with the payloadType | `field` |
| `STATEMENT_LINEAGE_MISMATCH` | V8 / SV-10 | `trust_root_id` differs from the binary lineage | `expected`, `observed` |
| `TRUST_PROFILE_MISMATCH` | V7 | test material on production, or vice versa | `profile` |
| `TRUST_ROOT_INVALID` | V4 | root chain, key id recomputation, duplicate public key, corrupt compiled root/TPS/registry | `root_version`, `reason` |
| `PURPOSE_SEPARATION_VIOLATION` | V4 | root grants violate KS-1…KS-7 | `constraint` |
| `TRUST_ROOT_ROLLBACK` | V4 / bootstrap | older root presented as current to `verify-artifact` | `root_version`, `high_water` |
| `TRUST_ROOT_STALE` | V4 / ingress | a signed reference names a newer root than known | `required`, `effective` |
| `TRUST_ROOT_LINEAGE_MISMATCH` | use / bootstrap | binary lineage differs from the project or VTS pin | `binary`, `pinned` |
| `TRUST_ROOT_UNCONFIRMED` | ingress | lineage not confirmed per OP-6 | `trust_root_id` |
| `SIGNER_UNKNOWN` | V5 | key id not in the effective root | `key_id` |
| `PURPOSE_NOT_GRANTED` | V5 | key lacks the purpose of the payloadType | `key_id`, `purpose` |
| `SIGNER_REVOKED` | V5 | key revoked in the effective root | `key_id` |
| `SIGNATURE_INVALID` | V5 | signature does not verify | `key_id` |
| `THRESHOLD_NOT_MET` | V5 | too few valid distinct signatures, or a required algorithm missing | `valid`, `threshold` |
| `TRUST_STATE_STALE` | V4 / ingress | effective state below a signed required minimum | `required`, `effective` |
| `TRUST_STATE_HINT_MISMATCH` | V4 | effective state below a hint; adds a gate | `hint`, `effective` |
| `TRUST_STATE_REGRESSION` | V4 / use | higher TSS not admissible | `sequence`, `violation` |
| `BINARY_BELOW_TRUST_POLICY` | V4 / use | TPS needs a newer binary or unknown floor operators | `min_binary_version`, `operator` |
| `TRUST_FORMAT_UNSUPPORTED` | pre-V0 / use | `FORMAT` unknown or `minimum_reader` above this binary | `trust_format`, `minimum_reader` |
| `TRUST_PLATFORM_UNSUPPORTED` | any | secure primitives unavailable | `primitive` |
| `RELEASE_IDENTITY_MISMATCH` | V8 | framework, version, release id, promotion content | `expected`, `observed` |
| `RELEASE_REPLAY_DETECTED` | V8 | statement for another identity; equivocation; reinstall digest differs | `statement_digest`, `installed_digest` |
| `RELEASE_DIGEST_MISMATCH` | V9 | content ≠ statement | `modified[]`, `missing[]`, `added[]`, `component` |
| `MIGRATION_NOT_IN_STATEMENT` / `MIGRATION_DIGEST_MISMATCH` | V10 | migration binding | `migration`, `path` |
| `MIGRATION_CHAIN_AMBIGUOUS` | V10 | duplicate `from_version` | `from_version` |
| `MIGRATION_FAILED` | tx | operation failed; `lock_key_not_allowed` | `reason` |
| `RELEASE_INCOMPATIBLE` | V11 | CLI, contract, floor schema, supported-from | `requirement` |
| `RELEASE_INELIGIBLE` | auth | eligibility failure at ingress | `reason` (`19` §6), `condition` |
| `KERNEL_INELIGIBLE` | use | installed release not eligible | `reason` |
| `HUMAN_GATE_REQUIRED` | auth | a gate is required | `gate`, `kind` (`framework_update`, `init_ack`, `downgrade`, `weakening`, `hint_mismatch`) |
| `OVERLAY_WEAKENING_GATE_REQUIRED` | auth | computed weakenings need a gate | `weakenings[]`, `list_digest` |
| `AUTHORITY_DENIED` | auth | actor below the install-authority floor | `operation`, `required`, `actual` |
| `DEVELOPMENT_TRUST_DOWNGRADE_REFUSED` | auth | move to `DEVELOPMENT_UNSIGNED` without a gate | — |
| `STAGED_CONTENT_CHANGED` | tx | read-back digest differs from the buffer | `path` |
| `INSTALL_TRANSACTION_CONFLICT` | tx | another transaction holds the lock | `transaction_id` |
| `INSTALL_IN_PROGRESS` | use | journal present or lock wait timed out | `transaction_id`, `phase` |
| `INSTALL_STATE_PARTIAL` | use | partial protected-path state | `present[]`, `missing[]` |
| `SNAPSHOT_UNAUTHENTICATED` | rollback | snapshot fails authentication | nested code |
| `SNAPSHOT_INELIGIBLE` | rollback | authentic snapshot not eligible | nested reason |
| `KERNEL_UNAUTHENTICATED` | use | installed statement missing, invalid or of unknown identity | nested code |
| `KERNEL_TAMPERED` | use | installed files ≠ statement | `modified[]`… |
| `LOCK_IDENTITY_MISMATCH` | use | lock identity ≠ statement, or a better verdict than recomputed | `field` |
| `PROTECTED_PATH_WRITE_REFUSED` | any | mutation of a Protected Path outside the transaction | `operation`, `path`, `caller` |
| `CIT_PROTECTED_PATH` | CIT planning | manifest targets a Protected Path | `op`, `path` |
| `PATH_SUBSTITUTION_DETECTED` | any | link or special file on a resolved path | `path`, `component` |
| `FLOOR_NOT_REGISTERED` / `FLOOR_VIOLATION` | producer / E7 | release floor values stronger / weaker than the referenced TPS | `key`, `release`, `policy` |
| `FLOOR_REGRESSION_IN_BUILD` | pipeline | compiled TPS older than the previous binary's | `previous`, `candidate` |
| `PROFILE_STATEMENT_INVALID` / `PROFILE_DIGEST_MISMATCH` / `MODEL_DIGEST_MISMATCH` / `PROFILE_INCOMPATIBLE` | profile | profile trust | `profile_id`, `path` |
| `PRIVATE_KEY_MATERIAL_DETECTED` | producer | key material in the tree | `path` |
| `TRANSPORT_FAILED` | fetch | download failed (never a trust verdict) | `reference` |

## 5. Doctor checks

| Check | Severity | Condition |
|---|---|---|
| D003 kernel payload integrity | CRITICAL | `integrity = TAMPERED` (wording: integrity only) |
| D004 lock present and schema-valid | CRITICAL | lock missing or not 2.0.0 for a RoT-1 project |
| D029 constitutional policy read from a verified, eligible kernel | CRITICAL | `verified = false` (wording names the failing axis) |
| **D030** authenticity and eligibility | CRITICAL for `UNAUTHENTICATED`, `TAMPERED`, `INELIGIBLE(revoked, historical, below_min_release_sequence, downgrade_without_transaction, lineage_mismatch)`; HIGH for `DEVELOPMENT_UNSIGNED`, `ELIGIBLE_EVALUATION`, `INELIGIBLE(binary_below_policy)`; MEDIUM for `NOT_CERTIFIED` on a final | verdict axes |
| **D031** lock identity consistent | CRITICAL | `LOCK_IDENTITY_MISMATCH` |
| **D032** trust metadata | CRITICAL for `REGRESSION`; HIGH for `STALE`, `HINT_MISMATCH`; MEDIUM when OP-5 age exceeded | `17` §5 |
| **D033** installation state | CRITICAL | `PARTIAL`, `IN_TRANSACTION` outside a running transaction, `FORMAT_UNSUPPORTED` |
| **D034** lineage confirmation | MEDIUM | lineage `unconfirmed` (OP-6 mode b) |
