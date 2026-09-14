# Output 9 — Integration requirements

> **RoT-1 revision 4 — PROPOSED, pending fresh independent reviews; not approved, not implemented.**
> Normative keywords: MUST, MUST NOT, SHOULD. Requirement IDs are referenced by `02` and `12`. Mechanisms are in `04`,
> `05`, `17`–`20` and `23`–`27`. This file states obligations per ingress and catalogues codes.
>
> Revision 4 revises R-INIT-3, R-UPD-6, R-UPD-7, R-RI-1, R-ART-2, R-ENV-3, R-ANCH-1…4, R-GATE-3, R-SURF-1, R-SURF-3,
> R-SURF-7, R-MIG-3, R-MIG-5, R-REL-6, R-CERT-4, R-TS-5, R-TS-6, R-TS-8, R-FS-7, R-FMT-1, R-FMT-5, R-USE-7, R-BOOT-2 and
> R-AUTH-1.
>
> It adds R-ART-5…7, R-ANCH-5…9, R-GATE-7, R-SURF-8…12, R-MIG-7, R-REL-9, R-TS-10…12, R-CONF-1…3 and R-FMT-6…7. The
> error catalogue and the doctor checks gain the revision-4 codes.

## 1. Common order of evaluation (every command)

1. Read `governance/trust/FORMAT`, including `layout`. An unsupported format or layout stops here
   (`TRUST_FORMAT_UNSUPPORTED`).
2. Determine the installation state, including occupation entries, `LEGACY`, and honoured or foreign journals
   (`18` §9).
3. Build knowledge and effective state (`17` §5), inclusion-satisfied anchors, and the freshness and currency axes (`24` §3.4, §4.1).
4. Load the KernelSnapshot or EmbeddedSnapshot; compute the verdict, E7 surface and effective policy (`18` §6,
   `19` §5–§6).
5. Check the project-strength vector over the effective policy and overlay (`26` §6).
6. Apply the operation-class gate (C0–C3) from trust state × freshness × OP-7 (`24` §4.3), then pause/freeze guards and the
   kernel-trust guard with remedy exemptions (`04` §5).
7. For ingress: `authenticate` (`04` V0–V12, including V11s).
8. For ingress: eligibility, currency proof, trust-gate requirement and local confirmation, install-authority floor, migration whitelist and computed weakenings, downgrade policy (`04` §4). Only after every trust decision of the unit of work may a repository- or plugin-supplied command run, and only confined (R-CONF-1).
   downgrade policy (`04` §4).
9. For ingress: install transaction (`18` §5), including union trust record, layout migration, post-commit equality,
   strength vector.
10. Ledger entry, checkpoint, typed result.

Every trust failure MUST return `ok: false` (API-0002 exit code 1) with a code from §4. Trust refusals are never
`ok: true, applied: false`.

## 2. Requirements by ingress

### init — I-01, I-02

| ID | Requirement |
|---|---|
| R-INIT-1 | `init` MUST authenticate its source and complete authorisation before creating any Protected Path or occupation entry. |
| R-INIT-2 | Required authority MUST come from the install-authority floor, and the actor level from the effective ROLES (`19` §8), never from the release being installed. |
| R-INIT-3 | Production `init` MUST require E1–E8: the E7 surface (presence, YAML profile, exact precedence, migration whitelist), freshness `ANCHORED` or `WITNESSED`, and a currency proof (`24` §4.4). |
| R-INIT-4 | Production `init` MUST require an `init_ack` trust gate confirmed locally (`27`). |
| R-INIT-5 | `init` MUST create the layout of `26` §2 inside the transaction, lock last. |
| R-INIT-6 | `init --force` on an installed project MUST be treated as reinstall or update/downgrade. |
| R-INIT-7 | `init` MUST apply OP-6 confirmation and state anchoring before any trusted write (`06` §3). |
| R-INIT-8 | `release_commit` and `source` labels MUST come from the statement and `SourceRef.kind`. |

### adopt — I-03, I-30, I-34, I-36

| ID | Requirement |
|---|---|
| R-ADOPT-1 | Batch 0 MUST use the `init` pipeline (operation `adopt_install`) and create the layout. |
| R-ADOPT-2 | When protected or legacy paths exist, batch 0 MUST evaluate them through the installation state machine. |
| R-ADOPT-3 | Pre-install stages MUST read policy from EmbeddedSnapshot ⊔ floors. |
| R-ADOPT-4 | The planner MUST classify PPS paths and occupation entries as `GOVERNANCE_CURRENT`. RoT-1 adoption evidence MUST be written to `spec/audits/ADOPTION/` and batch snapshots to `.governance-runtime/adoption/`. |
| R-ADOPT-5 | A7 and A11 MUST use the snapshot verdict. |

### update — I-04, I-05, I-31

| ID | Requirement |
|---|---|
| R-UPD-1 | `update --check` MUST report E7, eligibility, trust state, freshness, certification view, computed weakenings, computed policy reductions, gate requirement and authority. |
| R-UPD-2 | Every reported value MUST come from signed statements, the effective state, anchors and the snapshot. |
| R-UPD-3 | Dry-run migrations MUST come from ARO blobs. |
| R-UPD-4 | `update --apply` MUST re-authenticate. |
| R-UPD-5 | The `framework_update` trust gate MUST be satisfied only by a local confirmation bound to both statement digests (`27` §3). A repository gate record MUST NOT authorise. |
| R-UPD-6 | Gate requirement per OP-3 mode. Migration operations MUST be checked against the Overlay Surface whitelist before any write. Computed weakenings over the recorded strength vector MUST need the `weakening` trust gate in every mode. |
| R-UPD-7 | Trust state MUST be `KNOWN`, with anchors satisfied by inclusion, freshness `ANCHORED` or `WITNESSED`, a currency proof present, and the target's release-local references met. `TRUST_STATE_HINT_MISMATCH` is a warning only. |
| R-UPD-8 | Migrations from the ARO, unique chain, no lock operation. |
| R-UPD-9 | The transaction MUST snapshot overlay and views into `.governance-runtime/trust-tx/<TX>/overlay.prev/` and write `.governance-runtime/snapshots/<CI>/`. |
| R-UPD-10 | Registries and adapters MUST be regenerated from the new snapshot with CI and policy digest; adapter rendering digests MUST be recorded in the VTS. |
| R-UPD-11 | Post-commit verification MUST include snapshot CI equality, E7, eligibility, doctor D030–D038 and the audit families. |
| R-UPD-12 | The ledger MUST record previous and new CI, signer key ids, purpose, eligibility, surface result, certification view, trust state, freshness and anchor epoch, TPS version, trust-gate confirmation digest, and source. |
| R-UPD-13 | An update to an eligible target MAY run while the installed kernel is `UNAUTHENTICATED`, `TAMPERED`, `INELIGIBLE`, `PARTIAL` or `LEGACY`. Freshness and trust-gate requirements still apply. |
| R-UPD-14 | Known REJECTED or WITHDRAWN finals MUST be refused when TPS `gating.refuse_known_*`. |
| R-UPD-15 | The first RoT-1 update of a legacy project MUST perform the layout migration of `26` §7 inside the transaction. |

### kernel reinstall — I-08

| ID | Requirement |
|---|---|
| R-RI-1 | The source MUST authenticate to the installed statement digest **recorded in the VTS per-project record** where one exists; the lock is a hint. A different identity is an update or a downgrade under `20` §4 (CR-09). |
| R-RI-2 | Source order: explicit `--source`; a user-cache bundle (untrusted); the EmbeddedSnapshot if the digest matches. Never `lock.source`. |
| R-RI-3 | A re-signed envelope of the same payload MAY replace `release.dsse.json`. |
| R-RI-4 | Reinstall MUST restore occupation entries, and MUST NOT clear `PROJECT_STRENGTH_WEAKENED`. |

### rollback — I-06, I-07

| ID | Requirement |
|---|---|
| R-RB-1 | Every restore MUST run the restore pipeline (`20` §2). |
| R-RB-2 | A downgrade MUST require the `downgrade` trust gate, confirmed on the local terminal (`27`). |
| R-RB-3 | Targets below the minimum sequence, revoked, historical, candidates in production, or with an unregistered surface MUST be refused without override. |
| R-RB-4 | Kernel, release statement and lock MUST be exchanged together; `state/` and `root/` MUST be the union. |
| R-RB-5 | No rollback MUST remove a verified trust statement (`18` §5.2). |

### override — I-09

| ID | Requirement |
|---|---|
| R-OV-1 | `kernel override` MUST require the `override_kernel_integrity` trust gate (local terminal only), and MUST NOT change authenticity, eligibility, surface result or policy root. |
| R-OV-2 | Override MUST NOT be available for `refuse_operation` revocations, `TRUST_STATE_REGRESSION`/`EQUIVOCATION`, `BINARY_BELOW_TRUST_POLICY`, `BINARY_T0_ROLLBACK` or lineage mismatch. |

### recovery — I-10, I-41

| ID | Requirement |
|---|---|
| R-REC-1 | Every invocation MUST detect honoured journals (VTS registry) and refuse mutations with `INSTALL_IN_PROGRESS`. |
| R-REC-2 | `gov recover` MUST follow `20` §5. A journal not registered in the VTS, or tracked by Git, MUST be reported as `FOREIGN_TRANSACTION_ARTEFACT` and ignored. |
| R-REC-3 | Recovery MUST NOT write Protected Paths except through the install transaction. |
| R-REC-4 | CIT and adoption recovery MUST go through GovernedFs. |
| R-REC-5 | Restoring `overlay.prev` MUST run the computed-weakening check; a non-empty list needs the `weakening` trust gate. |

### embedded payload and binaries — I-11, I-12, I-22, I-54, I-55

| ID | Requirement |
|---|---|
| R-EMB-1 | The EmbeddedSnapshot MUST be verified against the compiled statement named in the TBM, once per process. |
| R-EMB-2 | The embedded payload MUST NOT be materialised for trust; `GOV_KERNEL_CACHE` is removed. |
| R-EMB-3 | The fail-closed baseline MUST be EmbeddedSnapshot ⊔ floors. |
| R-EMB-4 | `build.rs` MUST compile the Trust Base Manifest (`25` §4) and no unsigned provenance. |
| R-ART-1 | `gov trust verify-artifact` MUST implement A1–A10 of `25` §5. |
| R-ART-2 | A binary MUST refuse trusted operations when its TBM is below the VTS **accepted-TBM** high-water (`BINARY_T0_ROLLBACK`). It MUST NOT compare with the TSS knowledge high-water (RV3-M8). |
| R-ART-3 | The release pipeline MUST produce a reproducible build with published build inputs, at least the threshold of build attestations, an `artifact-final.v2` statement at `release-artifact` threshold, and a TSS reference before a binary is announced. |
| R-ART-4 | `gov version --trust` MUST print the TBM and its digest. |
| R-ART-5 | `verify-artifact` MUST require the attested-source binding of `25` §5.1 (A4a, A4b), and every verifier MUST apply V8 source equality. |
| R-ART-6 | `verify-artifact --stage rebuilder|custodian|publisher` MUST implement the custodial pre-checks of `05` §7 rules 6 and 7. `gov trust publish` MUST refuse a TSS that references an artefact failing A4a/A4b, or that drops a lower `artifacts[]` reference. |
| R-ART-7 | A9 MUST require a currency proof (`24` §4.4). If OP-2 (S1) is registered, A4b MUST require the source in `eligibility.production_sources[]`. |

### environment, anchors and pins — I-13, I-14, I-39, I-44, I-48…I-52

| ID | Requirement |
|---|---|
| R-ENV-1 | `GOV_CANONICAL_ROOT` MUST select a source only. |
| R-ENV-2 | `GOV_KERNEL_SOURCE` and `GOV_KERNEL_CACHE` MUST be removed. |
| R-ENV-3 | The VTS MUST be resolved from the account database. Pins MUST be resolved from the system pin directory or the account location (`24` §3.5 (1)). |
| R-ENV-4 | No environment variable, flag or repository file may add keys, roots, policies, trust state, certification, confirmation, anchors, trust-gate confirmations or eligibility. |
| R-ANCH-1 | Anchors MUST be established only by protected, valid state pins, `gov trust confirm-state` with a typed fingerprint, in-gate state confirmations, or retained VTS anchors. Witnesses give currency only under OP-7 (c) (`24` §3). |
| R-ANCH-2 | Anchors MUST be satisfied only by inclusion (`24` §3.4), and statements outside the anchored chain MUST NOT be effective. The freshness axis and operation classes MUST follow `24` §4.1 and the single decision rule of §4.3 with the TPS `bootstrap`. |
| R-ANCH-3 | Anchors, high-water components and witness `issued_at` MUST be monotonic (`24` §8). Only witnesses raise `clock_high_water`. Pin anchors MUST be recomputed per process and never persisted. |
| R-ANCH-4 | No surface MUST contain the word `current` for trust state; `CURRENT_KNOWN` and `CERTIFIED_CURRENT` MUST NOT appear. |
| R-ANCH-5 | A state pin MUST carry `valid_until`, with `valid_until − provisioned_at ≤ pin_max_validity_days`. Outside that window it is not an anchor (`PIN_OUTSIDE_VALIDITY`). |
| R-ANCH-6 | Pins and decision pins MUST be ignored unless the integrity predicate of `24` §3.5 (2) holds (`PIN_WRITABLE_IGNORED`). |
| R-ANCH-7 | C3 and binary acceptance MUST require a currency proof: P1, P2 or P3 of `24` §4.4 (`TRUST_STATE_CURRENCY_UNPROVEN`). |
| R-ANCH-8 | Witnesses MUST be `freshness-witness` statements naming the effective TSS. C3 MUST require at least 2 distinct witness keys (KS-11). |
| R-ANCH-9 | Two anchors on different chains MUST give `ANCHOR_CONFLICT`. Unchained statements above an anchor MUST be reported (`TRUST_STATE_UNCHAINED_ABOVE_ANCHOR`). |

### trust gates — I-51, I-52

| ID | Requirement |
|---|---|
| R-GATE-1 | The trust-gate kinds of `27` §2 MUST be compiled. |
| R-GATE-2 | Confirmations MUST be recorded in the VTS bound to kind, `project_trust_id` and digests, and consumed once. |
| R-GATE-3 | `gov trust confirm` MUST use the controlling terminal, a typed digest prefix and, for C3 kinds, a typed state fingerprint naming the effective TSS. It MUST refuse without a terminal. |
| R-GATE-4 | Operator decision pins MUST NOT approve kinds listed in TPS `gating.local_terminal_only[]`. |
| R-GATE-5 | `gov decide` MUST refuse trust gates. No code path MUST read a repository record's answer for a trust decision. |
| R-GATE-6 | Consumers of non-trust human gates MUST require `by_kind: human` computed at answer time. |
| R-GATE-7 | Operator decision pins MUST carry `expires_at` and `approved_under_state`. An expired pin, a state outside the effective chain, or a C3 kind without a P1 or P3 currency proof MUST authorise nothing. |

### Constitutional Surface — I-19, I-53

| ID | Requirement |
|---|---|
| R-SURF-1 | The binary MUST implement `floor_schema_version: 3` exactly (`23` §3–§4, §11) and refuse unknown vocabulary (`BINARY_BELOW_TRUST_POLICY`). |
| R-SURF-2 | E7 MUST be evaluated at ingress and at use (`19` §6). |
| R-SURF-3 | The effective policy MUST be produced per `19` §5: registered precedence only (joined with the held registration), the directed project join, and exceptions after the join, relaxable only when registered. |
| R-SURF-4 | `gov release build` and canonical CI MUST run the surface checker and fail on non-zero. |
| R-SURF-5 | `gov trust draft-policy` MUST list classification, registration and computed-reduction changes. |
| R-SURF-6 | The compiled consumer and decision-point registers MUST exist; the build fails on an unclassified consumed key or a security decision point reading a `project_tunable` or `informational` key (`23` §6.5). |
| R-SURF-7 | The architecture reference (`constitutional-surface/csi_check.py selftest`, 56 cases) MUST yield the same exit classes against the implementation's evaluator. It is a conformance oracle, not an expected count (`12` §8). |
| R-SURF-8 | E7 MUST refuse a kernel whose POLICY_PRECEDENCE differs from the named TPS registration (`precedence_unregistered`). The kernel's rules MUST NOT be an input to effective policy. |
| R-SURF-9 | E7 MUST refuse a kernel missing a registered file or leaf (`surface_required_missing`). A missing or unregistered pinned value MUST resolve to the registered EmbeddedSnapshot value, or to `SURFACE_VALUE_UNAVAILABLE` at its decision point. |
| R-SURF-10 | The producer checker, canonical CI, the surface evaluator and every consumer MUST use the single YAML profile of `23` §3.6 (`SURFACE_STRUCTURE(yaml_profile)`). |
| R-SURF-11 | The project-strength vector MUST be recorded and checked over the effective policy and every Overlay Surface input (`26` §6). Computed reductions MUST cover precedence in both directions and the non-surface TPS fields (`19` §10.6). |
| R-SURF-12 | Owner constitutional files MUST be registered in owner-domain slots. Absence on a confirmed machine MUST give `OWNER_CONSTITUTIONAL_FILE_MISSING`, and on an unconfirmed machine `OWNER_CONSTITUTIONAL_FILE_UNCONFIRMED`. Both are fail-closed for the dependent decision point (`23` §7.2). |

### use time — I-15, I-16, I-17, I-31, I-37, I-46, I-58, I-59

| ID | Requirement |
|---|---|
| R-USE-1 | Every process reading kernel content MUST build a snapshot per `18` §6. |
| R-USE-2 | All consumers MUST read kernel content from the snapshot API. |
| R-USE-3 | The effective policy MUST be applied in policy loading (`19` §5). |
| R-USE-4 | V-H2 behaviour MUST be preserved. |
| R-USE-5 | Derived artefacts MUST record CI and effective-policy digest; unbound or mismatched artefacts MUST NOT be served (VU-8). |
| R-USE-6 | Context packets and `gov status` MUST surface all verdict axes, including `surface` and `freshness`. |
| R-USE-7 | Doctor checks D030–D038 (§5) MUST be implemented. |
| R-USE-8 | The VTS per-project record MUST be updated after verified snapshots and install transactions. |
| R-USE-9 | Every unit of work MUST apply the generation check of VU-11. The MCP server MUST adopt it before shipping. |
| R-USE-10 | Staged and installed kernel and trust files MUST have `st_nlink == 1` (VU-12). |
| R-AGENT-1 | Adapters MUST carry pointers and CI, not constitutional text. `gov kernel show` and `gov skills show` MUST serve snapshot bytes. Adapter rendering digests MUST be recorded in the VTS and compared (`18` §12). |

### migrations — I-18

| ID | Requirement |
|---|---|
| R-MIG-1 | Migrations MUST be loaded only from ARO blobs or the KernelSnapshot. |
| R-MIG-2 | No `stage_payload` parent fallback on consumer paths. |
| R-MIG-3 | No migration lock operation. The 4.1.6 chain MUST be re-issued without the historical `set_lock_field` operations (`11` WP-18). |
| R-MIG-4 | Unique chain. |
| R-MIG-5 | Every migration operation MUST target a migration-writable Overlay Surface target, otherwise `MIGRATION_OPERATION_NOT_PERMITTED` before any write. Computed weakenings MUST need the `weakening` trust gate. |
| R-MIG-6 | Operations remain declarative. |
| R-MIG-7 | No migration operation may resolve outside `governance/overlay/`. |

### producer, verification, certification — I-19…I-21, I-47

| ID | Requirement |
|---|---|
| R-REL-1 | `release build` MUST emit an unsigned candidate naming the TPS and never sign. |
| R-REL-2 | It MUST refuse private key material. |
| R-REL-3 | It MUST validate with compiled schemas and run the surface checker (R-SURF-4). |
| R-REL-4 | `attach-signature` MUST verify before attaching. |
| R-REL-5 | `release verify` MUST be `authenticate` in report mode. |
| R-REL-6 | `promote` MUST require a verified ACCEPTED attestation, identical content and an identical `release.source`; every verifier re-checks it (V8). |
| R-REL-7 | Statement inputs MUST be deterministic. |
| R-REL-8 | The pipeline MUST refuse a binary whose compiled TPS version is lower than the previous binary's (`FLOOR_REGRESSION_IN_BUILD`) or whose TBM `trust_profile` is not `production`. |
| R-REL-9 | `release build` MUST fill `release.source`. The verifier MUST attest `source` only after reproducing the candidate from it. |
| R-CERT-1 | Certification MUST be a signed statement. |
| R-CERT-2 | CERTIFIED MUST reference a verified ACCEPTED attestation. |
| R-CERT-3 | A CERTIFIED view MUST require an admissible TSS reference to both the certification and the attestation. |
| R-CERT-4 | Negative facts MUST be lifted only per `17` MS-2, with a verification attestation naming the negative in `lifts_negative_statement_digest`. |
| R-CERT-5 | Certification MAY name artefact statements (informational under mode A). |

### trust state — I-39, I-42, I-43, I-60

| ID | Requirement |
|---|---|
| R-TS-1 | Only verified statements enter knowledge. |
| R-TS-2 | The effective state MUST be computed per `17` S1–S12. |
| R-TS-3 | Non-admissible, equivocating and fork statements MUST NOT be used; anchored forks are orphaned. |
| R-TS-4 | The negative set MUST follow S5 and MS-2. |
| R-TS-5 | C3 MUST refuse on `INCOMPLETE`, `REGRESSION`, `EQUIVOCATION`, `BELOW_ANCHOR`, `UNANCHORED`, `ANCHOR_CONFLICT` and `CURRENCY_UNPROVEN`, with no override. |
| R-TS-6 | TPS acceptance MUST compute reductions against the strongest held values, including precedence in both directions and the non-surface fields of `19` §10.6, and MUST require a cumulative `lowering_history`. |
| R-TS-7 | `gov trust refresh` MUST write the PTR only through a transaction, as a union. |
| R-TS-8 | Currency proofs MUST follow `24` §4.4, and clock use `17` §13. |
| R-TS-9 | References in non-trust-state statements MUST be release-local (S7). Lock and VTS-record hints MUST be warnings. |
| R-TS-10 | A statement whose `issued_at` exceeds the local clock plus the compiled skew MUST be refused at ingest and never recorded (SV-11). |
| R-TS-11 | `clock_high_water` MUST be raised only by verified witnesses, and lowered only by a root-signed `bootstrap.clock_reset`. |
| R-TS-12 | Artefact-compromise remedies MUST revoke and never un-reference. Rotation MUST ship re-signed retained statements with root N+1 (`05` §8–§9). |

### filesystem and protected paths — I-34, I-35, I-45, I-57

| ID | Requirement |
|---|---|
| R-FS-1 | All runtime file mutations MUST go through GovernedFs. |
| R-FS-2 | GovernedFs MUST refuse PPS targets, including occupation entries and the transaction area, without `InstallTxToken`. |
| R-FS-3 | GovernedFs MUST refuse link crossings. |
| R-FS-4 | CIT planning MUST refuse PPS targets. |
| R-FS-5 | `gov`-run git arguments MUST be pre-validated. |
| R-FS-6 | Conformance MUST prove no PPS mutation outside `install_tx` for every command: interception for the builder, OS-level tracing for the verifier. |
| R-FS-7 | The production profile MUST refuse platforms lacking the primitives, and a transaction area on another device with `TRUST_PLATFORM_UNSUPPORTED(cross_device_tx)` before any write (C-2). |

### confined execution — I-46, I-63

| ID | Requirement |
|---|---|
| R-CONF-1 | Every repository- or plugin-supplied command MUST be started only through `confine::spawn`. That covers product and test commands, tool install, uninstall and health commands, plugin processes and adapter hooks. Writes to pin locations, the VTS, `governance/trust/**`, occupation entries and the transaction area MUST be denied. |
| R-CONF-2 | Where confinement is unavailable, `gov` MUST refuse to run the command (`REPOSITORY_COMMAND_CONFINEMENT_UNAVAILABLE`). |
| R-CONF-3 | Every trust decision of a unit of work MUST be made before any such child starts. The next unit of work MUST re-read pins with the integrity predicate. |

### partial install and layout — I-38, I-40, I-56, I-57

| ID | Requirement |
|---|---|
| R-PART-1 | Every process MUST evaluate the installation state machine before reading policy. |
| R-PART-2 | `PARTIAL`, `LEGACY`, `IN_TRANSACTION` and `ABSENT` MUST use EmbeddedSnapshot ⊔ floors. |
| R-PART-3 | `PARTIAL` MUST refuse mutations except remedies; `PARTIAL(occupation)` MUST be reported CRITICAL. |
| R-FMT-1 | Every RoT-1 install MUST write the layout of `26` §2 exactly: FORMAT with layout; lock 3.0.0 under `governance/trust/`; occupation entries with their types; `.governance-runtime/migration` force-added; and the ignore rule `/.governance-runtime/*` with `!/.governance-runtime/migration` (RV3-L7). |
| R-FMT-2 | RoT-1 binaries MUST NOT read occupation entry content. |
| R-FMT-3 | Unknown formats or layouts MUST stop with `TRUST_FORMAT_UNSUPPORTED`. |
| R-FMT-4 | The first RoT-1 transaction on a machine MUST quarantine legacy runtime residue (`26` §3.1). |
| R-FMT-5 | The acceptance suite MUST run LP-1 over the full registers of the real 4.1.2–4.1.5 binaries on a genuine 4.1.6 install, with type-aware digests and a `governance/trust` digest (`12` RT-50, C-5), and MUST run the occupation-absent register RT-50b. |
| R-FMT-6 | Doctor D033 MUST name mixed layouts and stray artefacts: `governance/framework.lock~legacy`, `governance/kernel/KERNEL_MANIFEST.json`, legacy overlay files (C-3). |
| R-FMT-7 | Occupation entry types MUST be checked by `st_mode` or `GetFileInformationByHandle`, never by name (C-4). |

### bootstrap — I-22, I-44

| ID | Requirement |
|---|---|
| R-BOOT-1 | The trust-root id and every state fingerprint MUST be published in at least two channels independent of the release host. |
| R-BOOT-2 | OP-6, OP-7 and the pin-currency parameters MUST be implemented as the TPS `bootstrap` block says. |
| R-BOOT-3 | Lineage mismatch MUST fail closed. |
| R-BOOT-4 | Subsequent binaries MUST be accepted only by `verify-artifact` (R-ART-1). |

### transport and bundles — I-23, I-24

| ID | Requirement |
|---|---|
| R-NET-1 | `gov release fetch` is transport only. |
| R-NET-2 | Credentials come from the platform store. |
| R-NET-3 | Network failure never changes a trust decision. |
| R-BUN-1 | Archives are streamed into buffers. |

### plugins, tools, profiles — I-25…I-28

| ID | Requirement |
|---|---|
| R-PLG-1 | The plugin authority floor and permission classes MUST come from the effective policy. |
| R-PLG-2 | Profile-bound registry entries MUST record `profile_statement_digest`. |
| R-TOOL-1 | Kernel tool descriptors MUST be served only when their member digest is registered. |
| R-PRF-1…7 | Per `10` §4–§5. |

### schemas, lock, development path

| ID | Requirement |
|---|---|
| R-AUTH-1 | The statement, lock, FORMAT, TBM, state-pin, decision-pin, witness and confirmation schemas used for trust decisions MUST be compiled. |
| R-AUTH-2 | Floor vocabulary MUST be compiled. |
| R-LOCK-1 | Lock identity fields MUST be cross-checked. |
| R-LOCK-2 | Lock references MUST be hints. |
| R-LOCK-3 | Only the install transaction MUST write the lock. |
| R-DEV-1…5 | As revision 2, with the override trust gate. |

## 3. Install transaction

Normative in `18` §5 (layout, VTS registry, union, phases, locking) and `20` §5 (recovery).

## 4. Error catalogue (`error.code`, `error.details.stage`, `error.details.*`)

| Code | Stage | Meaning | Key details |
|---|---|---|---|
| `KERNEL_SOURCE_NOT_FOUND` | V0 | no kernel at the source | `source_reference` |
| `RELEASE_TREE_INVALID` | V1 | link, special file, traversal, non-ASCII, case collision, limits | `path`, `rule` |
| `RELEASE_STATEMENT_MISSING` / `UNSIGNED_SOURCE_REFUSED` | V2 | statement absent | `looked_in[]` |
| `STATEMENT_MALFORMED` / `STATEMENT_TYPE_UNKNOWN` / `STATEMENT_TYPE_MISMATCH` | V3/V6/V7 | envelope, schema, withdrawn or mismatched type | `reason`, `payload_type` |
| `STATEMENT_LINEAGE_MISMATCH` / `TRUST_PROFILE_MISMATCH` | V7/V8 | lineage or profile | `expected`, `observed` |
| `TRUST_ROOT_INVALID` / `PURPOSE_SEPARATION_VIOLATION` | V4 | root chain; whitelist | `constraint`, `pair` |
| `TRUST_ROOT_ROLLBACK` / `TRUST_ROOT_LINEAGE_MISMATCH` / `TRUST_ROOT_UNCONFIRMED` | V4/use/bootstrap | root high-water, lineage, OP-6 | `binary`, `pinned` |
| `SIGNER_UNKNOWN` / `PURPOSE_NOT_GRANTED` / `SIGNER_REVOKED` / `SIGNATURE_INVALID` / `THRESHOLD_NOT_MET` | V5 / A2 | signatures | `key_id`, `purpose`, `valid`, `threshold` |
| **`TRUST_POLICY_EQUIVOCATION`** | V4 | two TPS of one version, or a fork | `versions` |
| **`TRUST_POLICY_UNDECLARED_LOWERING`** | V4 | computed reduction missing from `lowering_history` | `keys[]` |
| **`TRUST_STATE_EQUIVOCATION`** / `TRUST_STATE_REGRESSION` / **`TRUST_STATE_INCOMPLETE`** | V4/use | `17` S4 | `sequences`, `violation`, `unresolved` |
| **`TRUST_STATE_FORK_ORPHANS`** | V4 (warning, doctor CRITICAL) | statements outside the anchored chain | `orphans[]` |
| **`TRUST_STATE_UNANCHORED`** / **`TRUST_STATE_BELOW_ANCHOR`** / **`TRUST_ANCHOR_EXPIRED`** | class gate | `24` §4.3 | `held`, `required`, `op7_mode`, `remedy` |
| `TRUST_STATE_HINT_MISMATCH` | warning | hint above effective state | `hint`, `effective` |
| **`TRUST_STATE_CURRENCY_UNPROVEN`** | class gate / A9 | C3 or binary acceptance without a currency proof (`24` §4.4) | `last_proof_age`, `op7_mode`, `remedy` |
| **`TRUST_STATE_UNCHAINED_ABOVE_ANCHOR`** | V4 (doctor CRITICAL) | resolved TSSs above the anchor that do not descend from it | `statements[]` |
| **`ANCHOR_CONFLICT`** | class gate | two anchors on different chains | `anchors[]` |
| **`PIN_OUTSIDE_VALIDITY`** / **`PIN_WRITABLE_IGNORED`** | anchor | pin outside `[provisioned_at, valid_until]`; pin failing the integrity predicate | `path`, `valid_until`, `writable_by` |
| **`STATEMENT_ISSUED_IN_FUTURE`** | ingest (SV-11) | `issued_at` beyond the local clock plus skew | `issued_at`, `local_clock` |
| **`REPOSITORY_COMMAND_CONFINEMENT_UNAVAILABLE`** | command spawn | no OS write confinement | `command`, `platform` |
| **`RELEASE_REFERENCES_UNKNOWN_STATE`** | ingress | release-local requirement unmet (`17` S7) | `required`, `held` |
| `BINARY_BELOW_TRUST_POLICY` | V4/use | binary version or vocabulary | `min_binary_version`, `floor_schema_version` |
| **`BINARY_T0_ROLLBACK`** / **`BINARY_T0_UNVERIFIED`** | A6/A7, first run | TBM below high-water, or components not resolving | `component`, `high_water` |
| **`ARTIFACT_DIGEST_MISMATCH`** / **`ARTIFACT_IDENTITY_MISMATCH`** / **`ARTIFACT_BUILD_UNATTESTED`** / **`ARTIFACT_UNREFERENCED`** / **`ARTIFACT_REVOKED`** | A1–A8 | binary acceptance | `artifact_digest` |
| **`ARTIFACT_SOURCE_UNVERIFIED`** / **`ARTIFACT_SOURCE_REJECTED`** / **`ARTIFACT_SOURCE_UNREGISTERED`** | A4b | no ACCEPTED attestation for the source; a REJECTED attestation or a negative; source not in `production_sources[]` | `source`, `candidate_statement_digest` |
| `TRUST_FORMAT_UNSUPPORTED` | pre-V0 | format or layout | `trust_format`, `layout`, `minimum_reader` |
| `TRUST_PLATFORM_UNSUPPORTED` | any | primitives or cross-device transaction area | `primitive` |
| `RELEASE_IDENTITY_MISMATCH` (including `(source)`) / `RELEASE_REPLAY_DETECTED` / `RELEASE_DIGEST_MISMATCH` | V8/V9 | identity, source equality, content | `modified[]`, `field` |
| `MIGRATION_NOT_IN_STATEMENT` / `MIGRATION_DIGEST_MISMATCH` / `MIGRATION_CHAIN_AMBIGUOUS` / `MIGRATION_FAILED` | V10/tx | migrations | `migration` |
| `RELEASE_INCOMPATIBLE` | V11 | compatibility | `requirement` |
| `RELEASE_INELIGIBLE` / `KERNEL_INELIGIBLE` | auth/use | `reason` per `19` §6, including **`surface_unclassified`, `surface_required_missing`, `surface_structure`, `surface_unregistered`, `surface_membership`, `floor_violation`, `floor_not_registered`, `precedence_unregistered`, `migration_operation_not_permitted`, `currency_unproven`** | `reason`, `details` |
| **`SURFACE_UNCLASSIFIED` / `SURFACE_UNREGISTERED` / `FLOOR_VIOLATION` / `FLOOR_NOT_REGISTERED` / `PRECEDENCE_UNREGISTERED` / `SURFACE_REQUIRED_MISSING` / `SURFACE_STRUCTURE(yaml_profile)` / `SURFACE_CONSUMER_UNCLASSIFIED`** | producer / pipeline | surface checker (`23` §6) | `file`, `key` |
| `FLOOR_REGRESSION_IN_BUILD` | pipeline | compiled TPS older than previous binary's | `previous`, `candidate` |
| `HUMAN_GATE_REQUIRED` | auth | a gate is required | `gate`, `kind` |
| **`TRUST_GATE_LOCAL_CONFIRMATION_REQUIRED`** | auth | the trust gate lacks a local confirmation: a repository record is only a request, or the decision pin is writable, expired, out of chain or unproven | `gate`, `kind`, `bound_digests`, `detail` |
| **`TRUST_GATE_NEEDS_TERMINAL`** | `gov trust confirm` | no controlling terminal | — |
| `OVERLAY_WEAKENING_GATE_REQUIRED` | auth | computed weakenings | `weakenings[]`, `list_digest` |
| **`MIGRATION_OPERATION_NOT_PERMITTED`** | tx (before any write) | operation or target outside the Overlay Surface whitelist | `op`, `target` |
| **`SURFACE_VALUE_UNAVAILABLE`** | use | a missing or unregistered pinned value with no registered embedded value | `key`, `decision_point` |
| **`OVERRIDE_COMPONENT_REFUSED`** | use (report) | a weakening component of a project override not admitted by the registered rule | `key`, `component` |
| **`OWNER_CONSTITUTIONAL_FILE_MISSING`** / **`OWNER_CONSTITUTIONAL_FILE_UNCONFIRMED`** | use | owner constitutional file absent on a confirmed machine; slot unconfirmed | `path`, `consumers` |
| **`PROJECT_STRENGTH_WEAKENED`** | use | a recorded strength requirement fails over the effective policy or overlay outside a gated transaction | `failures[]`, `recorded_vector_digest` |
| `AUTHORITY_DENIED` | auth | actor below floor | `operation`, `required`, `actual` |
| `DEVELOPMENT_TRUST_DOWNGRADE_REFUSED` | auth | development transition without gate | — |
| `STAGED_CONTENT_CHANGED` / `INSTALL_TRANSACTION_CONFLICT` / `INSTALL_IN_PROGRESS` | tx/use | transaction | `transaction_id`, `phase` |
| **`FOREIGN_TRANSACTION_ARTEFACT`** | use (warning, doctor HIGH) | journal not VTS-registered or tracked | `path` |
| `INSTALL_STATE_PARTIAL` | use | partial state, including **`occupation`** | `present[]`, `missing[]`, `retyped[]` |
| **`INSTALL_STATE_LEGACY`** | use | legacy layout | `historical_identity` |
| `SNAPSHOT_UNAUTHENTICATED` / `SNAPSHOT_INELIGIBLE` | rollback | restore | nested |
| **`SNAPSHOT_GENERATION_STALE`** | use | unit-of-work generation mismatch (VU-11) | `snapshot_ci`, `installed_ci` |
| `KERNEL_UNAUTHENTICATED` / `KERNEL_TAMPERED` / `LOCK_IDENTITY_MISMATCH` | use | as revision 2 | … |
| `PROTECTED_PATH_WRITE_REFUSED` / `CIT_PROTECTED_PATH` / `PATH_SUBSTITUTION_DETECTED` | any | protected paths, links, link counts | `path`, `component` |
| **`ADAPTER_BODY_UNRECORDED` / `ADAPTER_BODY_MODIFIED`** | use (doctor) | adapter body differs from VTS rendering record | `adapter` |
| `PROFILE_STATEMENT_INVALID` / `PROFILE_DIGEST_MISMATCH` / `MODEL_DIGEST_MISMATCH` / `PROFILE_INCOMPATIBLE` | profile | `10` | `profile_id` |
| `PRIVATE_KEY_MATERIAL_DETECTED` | producer | key material | `path` |
| `TRANSPORT_FAILED` | fetch | never a trust verdict | `reference` |

**Withdrawn from revision 2:**
- `TRUST_STATE_STALE`, replaced by `RELEASE_REFERENCES_UNKNOWN_STATE`, `TRUST_STATE_INCOMPLETE` and the freshness codes;
- `TRUST_ROOT_STALE`, replaced by `TRUST_STATE_INCOMPLETE`;
- `STATEMENT_SOURCE_NOT_PERMITTED`, since the historical-identity type is withdrawn;
- revision 3's `PRECEDENCE_WEAKENED` and the reason `precedence_weakened`, replaced by `PRECEDENCE_UNREGISTERED` and `precedence_unregistered`.

## 5. Doctor checks

| Check | Severity | Condition |
|---|---|---|
| D003 kernel payload integrity | CRITICAL | `integrity = TAMPERED` |
| D004 lock present and schema-valid | CRITICAL | lock 3.0.0 missing or invalid on a RoT-1 project |
| D029 constitutional policy from a verified, eligible kernel | CRITICAL | `verified = false` (names the axis) |
| D030 authenticity, eligibility and surface | CRITICAL for `UNAUTHENTICATED`, `TAMPERED`, `INELIGIBLE(revoked, historical, below_min_release_sequence, downgrade_without_transaction, lineage_mismatch, surface_*, floor_*, precedence_unregistered, migration_operation_not_permitted)`; HIGH for `DEVELOPMENT_UNSIGNED`, `ELIGIBLE_EVALUATION`, `binary_below_policy`; MEDIUM for `NOT_CERTIFIED` | verdict axes |
| D031 lock identity consistent | CRITICAL | `LOCK_IDENTITY_MISMATCH` |
| D032 trust metadata | CRITICAL for `REGRESSION`, `EQUIVOCATION`, `FORK_ORPHANS`, `UNCHAINED_ABOVE_ANCHOR`; HIGH for `INCOMPLETE`, `HINT_MISMATCH`; MEDIUM when the OP-5 age since the last anchoring event is exceeded | `17` §5 |
| D033 installation state | CRITICAL for `PARTIAL` (including occupation), `LEGACY`, honoured `IN_TRANSACTION` outside a running transaction, `FORMAT_UNSUPPORTED`; names mixed layouts and stray artefacts (C-3); HIGH for `FOREIGN_TRANSACTION_ARTEFACT` | `18` §9 |
| D034 lineage confirmation | MEDIUM | `unconfirmed` (OP-6 b) |
| **D035 freshness and currency** | HIGH for `UNANCHORED`, `BELOW_ANCHOR`, `ANCHOR_CONFLICT`, `PIN_OUTSIDE_VALIDITY`, `WITNESS_EXPIRED`; MEDIUM for `CURRENCY_UNPROVEN`, a pin within 7 days of `valid_until`, or `ANCHORED` with age above OP-5 | `24` §4 |
| **D036 agent-facing content** | HIGH | `ADAPTER_BODY_UNRECORDED` / `ADAPTER_BODY_MODIFIED` |
| **D037 project strength** | CRITICAL | `PROJECT_STRENGTH_WEAKENED` over effective policy |
| **D038 anchor integrity and confinement** | CRITICAL | a pin or decision pin ignored by the integrity predicate (`PIN_WRITABLE_IGNORED`, `DECISION_PIN_WRITABLE_IGNORED`); `REPOSITORY_COMMAND_CONFINEMENT_UNAVAILABLE` on a project with repository-supplied commands |
