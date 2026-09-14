# Output 35 — The certified production profile CP-1

> **RoT-1 revision 7 — PROPOSED, pending fresh independent reviews; not approved, not active, not implemented.**
> New in revision 7. D-0008 stays `PROVISIONAL` / `PROPOSED`, `human_approved: false`, `in_effect: false`; D-0007 stays ACTIVE.
> The owner's selections are **binding design inputs** recorded in `release/orchestration/phase-1/GATES/OWNER-DESIGN-REQUIREMENTS-0001.md`
> (verbatim text governs). They are not approval of D-0008.
> This file names the one certified production profile, every selected parameter, every exclusion, and where each is
> enforced. The machine-readable form is `profile/CP-1.yaml`; the executable check is `evidence/r7/PROF7-profile-conformance.py`.
> Normative keywords: MUST, MUST NOT, SHOULD.

## 1. What CP-1 is

**CP-1** (`profile_id: governance-os.rot1/CP-1`) is D-0008 Option C (RoT-1) with owner parameters OP-1…OP-16 fixed as the
owner selected them, the first-contact composer and signer requirement, the build-environment manifest authority requirement,
and the initial certified scope. It has no option tree:
- **One value per parameter.** There is no Trust Policy field that selects a trust mode. Parameters are compiled constants, or
  schema constants and maxima, or root grants whose shape the verifier checks exactly.
- **Excluded modes are absent or refused.** Every alternative the owner did not select is either absent from the certified
  schemas, executable surface and calculator, or refused by a typed code when presented (§4; PROF7).
- **Profile identity is bound.** `profile_id` is a constant of the root (`trust-root.schema.json`), the Trust Policy, the
  first-contact authority record and the Trust Base Manifest's `compiled_rules`. A statement of another profile is
  `PROFILE_NONCONFORMANT`.
- **Extension is a new profile.** A later mode is added only through a separately governed, independently reviewed and
  registered release with a new `profile_id` (owner text: "extensible later through a separately governed/verified release").

Options A, B, D, E and F of D-0008 are not supported production alternatives (EX-22). The revision-6 option analysis is history
at `4106885` and in `21` §9 (non-production).

## 2. Selected parameters and where each is enforced

"Schema" names a JSON pointer of `schemas/`; "compiled" names a constant or function of the certified executor model
(`evidence/r7/gov_admit_reference_r7.py`, which `gov` and `gov-admit` implement); refusal codes are the executor's.

| Owner selection | CP-1 value | Enforced by | Evidence |
|---|---|---|---|
| **OP-1** root keys 3, threshold 2-of-3; three custodial roles (product owner, independent security, recovery); offline hardware-backed devices | `root` purpose exactly 3 keys, threshold 2; root keys hold only `root`, `trust-policy`, `first-contact-authority`; roles named in the root ceremony record (`05` §7) | schema `trust-root#/properties/purposes/properties/root` (3 keys, const 2); compiled `PURPOSE_SHAPE`, `WHITELIST`, `root_conforms`; `05` KS-1″, KS-14; `PROFILE_NONCONFORMANT` / `ROOT_CHAIN_INVALID` | FA7 S5 `root_threshold_1`; PROF7 EX-09, EX-10 |
| **OP-2 (b)** delegated registration quorum 2-of-3, single-purpose keys | `release-registration` exactly 3 keys, threshold 2; its keys hold no other purpose | schema `…/release-registration` (3 keys, const 2); compiled `PURPOSE_SHAPE`, `WHITELIST` (no pair holds `release-registration`); `05` KS-10″ | FA7 S4 R14; PROF7 EX-09 |
| **OP-3** Mode A `always_gate` | every adoption, installation, update, rollback, downgrade and recovery needs the local human trust gate; decision pins never approve them | schema `trust-policy-statement#/properties/gating/properties/mode` const `always_gate`; `trust-decision-pin#/properties/gate_kind` enum excludes those kinds; `27` §3; `PROFILE_NONCONFORMANT:trust_policy` | FA7 S4 R13; PROF7 EX-06 |
| **OP-4** separate candidate key | `release-candidate` shares no key with any other purpose; evaluation candidates only | compiled `WHITELIST` (no pair); `05` KS-15 | FA7 S4 R15b |
| **OP-4** production release final identity: threshold protection | `release-final` ≥ 2 keys, threshold ≥ 2 | schema `…/release-final` (≥ 2, ≥ 2); compiled `PURPOSE_SHAPE`; KS-15 | FA7 S4 R15; BA12r7 |
| **OP-4** trust state 2-of-3 dedicated | `trust-state` exactly 3 keys, threshold 2 | schema `…/trust-state` (3, const 2); KS-17 | FA7 S2 P `genuine_authority_state_signed_by_one_trust_state_key`; BA12r7 |
| **OP-4** certification: two independently produced records (OP-8) | `certification-status` ≥ 2 keys, threshold ≥ 2, negatives only; production eligibility needs two verification records | schema `…/certification-status`; OP-8 row below | PROF7 schema checks |
| **OP-4** revocation 2-of-3, root-threshold emergency | `revocation` exactly 3 keys, threshold 2; `revocation-statement#/properties/authority` ∈ {`revocation-quorum`, `root-emergency`} | schema; compiled (a revocation counts at the revocation or root threshold) | FA7 S4 R1 |
| **OP-4** retrieval profile separate | `retrieval-profile` single purpose; signs only `retrieval-profile` | compiled `TYPE_PURPOSE`, `WHITELIST` | PROF7 compiled checks |
| **OP-4** witness: none | no `freshness-witness` purpose, statement or acceptance path | EX-01 | PROF7 EX-01 |
| **OP-5** 30-day age warning, informational | shown with every admission and status; read by no decision | compiled `METADATA_AGE_WARNING_DAYS`, read only by `display_age_warning`, used only as `age_note` | PROF7 EX-07 (compiled) |
| **OP-6 (a)** lineage confirmation once per verifier trust store | after the first admission of a store, the operator confirms the lineage fingerprint once; a new lineage needs re-admission and re-confirmation | `06` §3 step 5; `24` §3.2; confirmation at every `init` is absent (EX-11) | PROF7 EX-11 |
| **OP-7 (a)** anchored only; workstation anchor ≤ 90 days; CI anchor ≤ 7 days; production installation, update and rollback need state and currency ≤ 24 hours; expiry → C0 | decision rule `24` §4.3; admission-state age ≤ 24 h (`32` FC-9); clock high-water (R-CLK-1) | schema `trust-policy-statement#/properties/bootstrap/properties/admission_ceilings` (maxima 90, 7, 24, 24); compiled `ANCHOR_VALIDITY`, `C3_CURRENCY`, `ADMISSION_STATE_MAX_AGE`; `TRUST_STATE_UNANCHORED`, `TRUST_ANCHOR_EXPIRED`, `TRUST_STATE_CURRENCY_UNPROVEN`, `FIRST_CONTACT_STATE_TOO_OLD`, `TRUST_CLOCK_BELOW_HIGH_WATER` | ADM7 X7, CLK; CUR7; BA11r7; PROF7 EX-08, EX-12 |
| **OP-8** = 2 independent verification records | two `ACCEPTED` attestations bound to the registered candidate and kernel, from distinct keys, distinct `verifier_execution_id` and distinct report digests | schema `trust-policy-statement#/…/min_verification_records` const 2; `release-registration#/properties/verification_records` minItems 2; compiled `MIN_VERIFICATION_RECORDS`; `VERIFICATION_RECORDS_BELOW_MINIMUM` | FA7 S4 R6; S7 `count_attestation_signatures`; PROF7 EX-13 |
| **OP-9 (b) + (d)** three reproducer roles, any two matching; binary digests registered | `reproducer` 3 keys, `quorums.reproducer` 2; registration carries `binary_digests`; custodians register only digests of their own reproduction; a mismatching valid reproduction blocks | schema `trust-root#/properties/quorums/properties/reproducer` const 2, `release-registration#/required` `binary_digests`; `30` R-REG-3 (f), R-REP-5′; `REPRODUCTION_QUORUM_NOT_MET`, `REPRODUCTION_CONFLICT`, `BINARY_NOT_REGISTERED` | FA7 S4 R10, S5 conflict; PROF7 EX-14 |
| **OP-10 (b)** diverse, independently bootstrapped compiler agreement; independence by provenance | matching reproductions from at least two toolchain lineages independent by `bootstrap_root`, `package_source`, `build_system`, `signing_infrastructure`, at least one not rooted in an upstream binary compiler archive; a target without it is not certified | `33` R-BENV-6″; compiled `TOOLCHAIN_ATTRS`, `independent_classes`; schema `input-manifest#/properties/toolchains` minItems 2; `TOOLCHAIN_DIVERSITY_NOT_MET`; `35` CC-3 | FA7 S4 R9; ENV7 T2; PROF7 EX-15 |
| **OP-11 (b)** raise the minimum release sequence at every security-relevant content change; no grace; transport never chooses among eligible releases | effective minimum = max(Trust Policy `min_release_sequence`, sequence of every referenced registration with `security_relevant_change`), never below the held minimum; a project's release is selected at the local trust gate | `19` E3′; compiled in `accept`; schema `release-registration#/required` `security_relevant_change`; `RELEASE_BELOW_SECURITY_MINIMUM`; `29` DR-25 | FA7 S4 R11; CUR7 A02; PROF7 EX-16 |
| **OP-12 (a)** separate compiled admitter, registered and reproduced | `gov-admit`; its digest per certified target is listed in the first-contact authority record; admission records name it | `32` FC-8′; `31` R-ADM-1″, GB-1″; schema `admission-record#/properties/admitter_kind` const `compiled-gov-admit`; `ADMITTER_NOT_LISTED`, `RECORD_ADMITTER_NOT_LISTED` | FA7 S1; ADM7 EX02_EX03; PROF7 EX-02, EX-03 |
| **OP-13 (b)** two owner-controlled sources under separate custody, byte-identical, both required | sources `authenticated-private-release-channel` and `immutable-release-mirror`; compiled quorum 2 over the trust code, the state code and the procedure digest | `32` FC-1′, FC-4′, R-FCS-3; schema `first-contact-authority#/properties/sources` exactly 2 of those kinds; compiled `FIRST_CONTACT_QUORUM`; `FIRST_CONTACT_SOURCES_BELOW_QUORUM`, `FIRST_CONTACT_DISAGREEMENT` | FA7 S1, S2 X; PROF7 EX-17, EX-18 |
| **OP-14 (b)** all admission records expire (OP-7 limits); re-admission preserves the high-water | workstation records ≤ 90 days, CI image records ≤ 7 days; re-admission applies the stores' floors (AP-R1…AP-R6) | compiled `RECORD_VALIDITY`; schema `admission-record#/properties/valid_until` a string; `31` R-ADM-7″, AP-R1…AP-R6; `ADMISSION_RECORD_EXPIRED`, `READMISSION_*_BELOW_HELD`, `BINARY_REVOKED_IN_HELD_STATE`, `BINARY_T0_ROLLBACK` | ADM7 X14, A09; CUR7 A02, A04; PROF7 EX-19 |
| **OP-15 (a)** revoked genuine binary: read-only diagnostics | C0-R: `version`, `doctor`, `status`, `kernel-trust-report`, `trust-show`; nothing else | `31` GB-3′; compiled `C0_R`; `BINARY_REVOKED_SELF` | ADM7 X15; PROF7 EX-20 |
| **OP-16 (b)** matching builds from two supplier classes independent by provenance; static, self-contained linking | acceptance needs matching reproductions from two supplier classes independent by `base_image_lineage`, `package_source`, `build_system`, `signing_infrastructure` with disjoint pinned checksum keys; static self-contained targets only (CC-4) | `33` R-BENV-5″; compiled `SUPPLIER_ATTRS`, `independent_classes`; schema `release-registration#/properties/environments` minItems 2; `ENVIRONMENT_DIVERSITY_NOT_MET` | FA7 S4 R7, R8; ENV7 A08; PROF7 EX-21 |
| **First-contact composer/signer** | the first-contact authority record (lineage, admitter per certified target, the two sources, the procedure digest, admitter evidence) is signed at root threshold 2-of-3 after the admitter's registration, reproduction and two verification records; the trust-state publisher composes nothing; each source custodian publishes codes only for statements it verified first-hand | `32` R-FCA-1…R-FCA-4, R-FCS-1…R-FCS-3, FC-5′, FC-10; purpose `first-contact-authority` on the root keys only (KS-18); `FIRST_CONTACT_AUTHORITY_UNVERIFIED`, `FIRST_CONTACT_AUTHORITY_MISMATCH` | FA7 S2 P, S3, S4 R16; PROF7 EX-23 |
| **Build-environment manifest author/signer** | no author: the manifest is derived by `gov-envmanifest/1` from the environment lock in the registered source and the pinned supplier registry; authoritative only with ≥ 2 agreeing environment reproductions **and** the 2-of-3 registration over that exact `environment_id` | `33` R-BENV-2″, R-BENV-3″, R-BENV-7″; schemas `environment-lock`, `environment-manifest` v2 (`assembly_function` const); `ENVIRONMENT_MANIFEST_NOT_DERIVED`, `ENVIRONMENT_ASSEMBLY_NONCONFORMANT`, `ENVIRONMENT_NOT_REPRODUCED` | ENV7 A07a/b/c, A09 |
| **Initial certified scope** | CP-1 only; exclusions EX-01…EX-24; narrow target set (§5) | `profile/CP-1.yaml`; PROF7 | PROF7 |

## 3. Unavoidable core (owner text, OP-7)

A machine that has never received newer metadata cannot be claimed to know it. CP-1 bounds, and never hides, what such a
machine does:
- **Admission.** A first or repeated admission uses a state at most 24 hours old, read from both sources. A revocation issued
  inside those 24 hours and not yet in the state the sources publish is not seen: residual **CUR-R1** (`32` §8; computed set
  `{win}` in the CP-REVOKED block).
- **Running machines.** A workstation anchored within 90 days (CI: 7 days) runs C1–C2 at its anchored chain; it never shows the
  word `current`; C3 (installation, update, rollback, ingress) needs currency of at most 24 hours naming the effective state;
  an expired or missing anchor leaves C0 (`24` §4.3, residual RS-1).
- **Clock.** A clock set back below what the machine has recorded leaves C0-R (R-CLK-1). A machine without any store, given
  stored codes and a clock set back, is residual **RS-2** (computed set `{stored_old, clockback}`).

## 4. Exclusions and where each is enforced

Each row is checked by PROF7 under every mechanism kind the profile file declares for it (`per_exclusion`), and each has an
`excluded` input row in the decision register (`29` §4.3).

| ID | Owner text | Removed from the certified surface | Mechanism (schema · compiled · refusal · calculator · register) | Tests |
|---|---|---|---|---|
| EX-01 | witness service | OP-7 (c) witnesses; purpose and statement `freshness-witness` | schema: purpose absent, witness fields absent, schema withdrawn · compiled: no statement type · refusal: root granting it `PROFILE_NONCONFORMANT`, offered witness `PROFILE_MODE_EXCLUDED` · calculator: no WR victim, no witness atoms | RT-190; PROF7 EX-01 |
| EX-02 | helper-machine admission | OP-12 (c) | schema: `admitter_kind` const · compiled: records honoured only with a listed admitter · refusal `RECORD_ADMITTER_NOT_LISTED` | RT-190; PROF7 EX-02 |
| EX-03 | script-based certified admission | OP-12 (b) | schema as EX-02; admitters map to registered digests · refusal `RECORD_ADMITTER_NOT_LISTED`, `ADMITTER_NOT_LISTED` | RT-190; PROF7 EX-03 |
| EX-04 | OP-13 (c) "either suffices" | the second authentication path in all variants; compiled first-contact manifests | schema: no `channel_quorum`; exactly two sources · compiled: quorum 2, no platform-signature identifier · refusal `PROFILE_MODE_EXCLUDED`, `FIRST_CONTACT_SOURCES_BELOW_QUORUM` · calculator: no `alt` atom | RT-184; PROF7 EX-04 |
| EX-05 | platform package signing as an alternate independent root | platform code-signing roots; the package submitter | compiled: no platform verification or submitter function · refusal `PROFILE_MODE_EXCLUDED` (admission and procedure) · calculator: no `alt`, `submit` atoms | RT-184; PROF7 EX-05 |
| EX-06 | Mode-B no-human-gate updates | OP-3 mode B | schema: `gating.mode` const · refusal `PROFILE_NONCONFORMANT:trust_policy` | RT-190; PROF7 EX-06 |
| EX-07 | clock/grace-period trust | OP-11 (c) `eligible_until`; OP-7 (d) compiled epoch; any clock that grants | schema: fields absent · compiled: the OP-5 warning is informational; clocks only expire · refusal `PROFILE_NONCONFORMANT`, `TRUST_STATE_UNANCHORED` | RT-190; PROF7 EX-07 |
| EX-08 | unanchored governed mutation | every C1–C3 row of an unanchored machine | compiled decision rule · refusal `TRUST_STATE_UNANCHORED`, `TRUST_ANCHOR_EXPIRED` | RT-189; PROF7 EX-08 |
| EX-09 | OP-2 (b) selected | OP-2 (a) registration at root threshold | schema: registration purpose shape · compiled whitelist · refusal `PROFILE_NONCONFORMANT` | RT-190; PROF7 EX-09 |
| EX-10 | separate candidate key YES | OP-4 "no" (one everyday key) | compiled whitelist and release-final threshold · refusal `PROFILE_NONCONFORMANT` | RT-190; PROF7 EX-10 |
| EX-11 | OP-6 (a) once per machine | OP-6 (c) confirmation at every `init` | schema: `op6_mode` absent · refusal `PROFILE_NONCONFORMANT` | PROF7 EX-11 |
| EX-12 | OP-7 (a); do not implement OP-7 (b), (c), (d) | OP-7 (b) maximum anchor age as a mode | schema: `max_anchor_age_days` absent; ceilings as maxima · compiled constants 90 / 7 / 24 · refusal `TRUST_ANCHOR_EXPIRED`, `TRUST_STATE_CURRENCY_UNPROVEN` | PROF7 EX-12 |
| EX-13 | OP-8 = 2 | OP-8 = 1 | schema const 2 · compiled `MIN_VERIFICATION_RECORDS` · refusal `VERIFICATION_RECORDS_BELOW_MINIMUM` | RT-190; PROF7 EX-13 |
| EX-14 | OP-9 (b) plus (d) | OP-9 (a), (c); registration without binary digests | schema: quorum const 2, `binary_digests` required · refusal `REPRODUCTION_QUORUM_NOT_MET`, `BINARY_NOT_REGISTERED`, `PROFILE_NONCONFORMANT` | RT-190; PROF7 EX-14 |
| EX-15 | OP-10 (b); no silent fallback to OP-10 (a) | OP-10 (a), (c) as production answers | compiled provenance lineages · refusal `TOOLCHAIN_DIVERSITY_NOT_MET` · calculator: no toolchain axis, `V_TOOLCHAIN_DIVERSITY` on | RT-187; PROF7 EX-15 |
| EX-16 | OP-11 (b); no grace periods | OP-11 (a) keep superseded releases eligible | compiled computed minimum · refusal `RELEASE_BELOW_SECURITY_MINIMUM` | RT-188; PROF7 EX-16 |
| EX-17 | neither source alone is sufficient | OP-13 (a) one source | compiled quorum 2 · refusal `FIRST_CONTACT_SOURCES_BELOW_QUORUM`, `FIRST_CONTACT_DISAGREEMENT` | RT-184; PROF7 EX-17 |
| EX-18 | do NOT support OP-13 (d) as the sole generic admission route | provisioning media as the only source | compiled quorum 2 and 24 h state age · refusal `FIRST_CONTACT_SOURCES_BELOW_QUORUM`, `FIRST_CONTACT_STATE_TOO_OLD` | RT-184; PROF7 EX-18 |
| EX-19 | all admission records expire | OP-14 (a) | schema: `valid_until` never null · refusal `ADMISSION_RECORD_EXPIRED` | RT-185; PROF7 EX-19 |
| EX-20 | read-only only | OP-15 (b) C0–C2 for a revoked binary | schema: `revoked_self_scope` absent · compiled `C0_R` · refusal `BINARY_REVOKED_SELF` | RT-185; PROF7 EX-20 |
| EX-21 | OP-16 (b) | OP-16 (a), (c) as production answers | schema: environments ≥ 2, no diversity switch · compiled provenance classes · refusal `ENVIRONMENT_DIVERSITY_NOT_MET` · calculator: no environment axis | RT-186; PROF7 EX-21 |
| EX-22 | A, B, D, E and F are not supported production alternatives | D-0008 options A, B, D, E, F | register: D-0008 marks them not supported; no chosen option | PROF7 EX-22 |
| EX-23 | first-contact trust base must NOT be composed by the ordinary trust-state publisher | revision 6's first-contact manifest composed per Trust State | schema withdrawn · compiled: codes are digests of root-threshold and trust-state-threshold statements · refusal `FIRST_CONTACT_AUTHORITY_UNVERIFIED` | RT-184; PROF7 EX-23 |
| EX-24 | stricter reading of BC6-1 (HO-0019 §2b) | `gov trust fc-procedure` as a first-install instruction | compiled: no such command in the certified command register · refusal `PROFILE_MODE_EXCLUDED` | RT-184; PROF7 EX-24 |

### 4.1 What was removed from the certified surface (revision 6 → 7)

| Surface | Removed (history only) |
|---|---|
| Schemas | `first-contact-manifest.schema.json` and `freshness-witness.schema.json` moved to `schemas/withdrawn-non-production/` (validated by nothing certified) |
| Trust Policy fields | removed: `bootstrap.channel_quorum`, `bootstrap.admitter_digests` (replaced by the first-contact authority record), `bootstrap.op6_mode`, `bootstrap.op7_mode`, `bootstrap.pin_max_validity_days`, `bootstrap.c3_currency_window_hours`, `bootstrap.max_anchor_age_days`, `bootstrap.witness_max_validity_hours`, `bootstrap.freshness_witness_threshold`, `bootstrap.workstation_record_max_validity_days`, `bootstrap.revoked_self_scope`, `eligibility.eligible_until`, `registration.binary_digests_registered`, `registration.environment_diversity`; `gating.mode` values other than `always_gate` |
| Root grants | removed: purpose `freshness-witness`; whitelist pairs `root`+`release-registration`, `trust-policy`+`release-registration`, `release-final`+`release-candidate`, `revocation`+`certification-status`, `revocation`+`trust-state`, `retrieval-profile`+`release-final` (the only pairs are `root`+`trust-policy`, `root`+`first-contact-authority`, `trust-policy`+`first-contact-authority`) |
| Environment manifest v1 | `assembly {recipe_digest, tool}`, `components[].upstream_url`, `components[].upstream_checksum_reference`, `supplier_class` labels (replaced by the derived manifest v2 and the pinned supplier registry) |
| Commands | `gov trust fc-procedure`; the option questions of `gov trust draft-policy` (`OWNER_OPTION_UNANSWERED`), replaced by a CP-1 conformance check (`PROFILE_NONCONFORMANT`) |
| Executor paths | platform code signatures; compiled first-contact manifests; witness acceptance; OP-7 (b), (c), (d) decision rows; mode-B update path; OP-15 (b); records without expiry; script and helper-machine records; single-source admission — each now absent (refused when offered) |
| Calculator | configuration axes `reg`, `V`, `repro`, `fc`, `op4`, `tc`, `env`; victims WR, P2k1, P2k2 and FA per OP-13 answer; atoms `ch1`, `ch2`, `alt`, `media`, `wk1`, `wk2`, `submit`, `kc`, `owner_tc`, `owner_env`; the revision-6 rules survive only as the labelled non-production control (CP-R6-CONTROLS) |
| Evidence | revision-6 instruments stay under `evidence/r6/` as history; they model revision 6, not CP-1 |

## 5. Certified targets

**Rule.** A target is labelled `CERTIFIED` only when every criterion CC-1…CC-9 holds for both `gov` and `gov-admit` on that
target. Otherwise it is **not certified**: it is absent from the Trust Policy's `certified_targets` and from the first-contact
authority record's `certified_targets`, first contact refuses it (`TARGET_NOT_CERTIFIED`), and no mode of CP-1 admits it.
There is no fallback (owner text, OP-10 and OP-16).

| ID | Criterion | Checked by | Evidence required |
|---|---|---|---|
| **CC-1** | Bit-for-bit reproduction of `gov` and `gov-admit` by at least 2 of the 3 reproducer roles; no valid mismatching reproduction (OP-9 (b)) | registration ceremony (`30` R-REG-3 (e), (f)); verifier AP-6 | reproduction statements; registered `binary_digests` |
| **CC-2** | Matching builds from at least two supplier classes independent by provenance: distinct base OS/build image lineage, package source, build-system provenance and signing/control infrastructure; disjoint pinned checksum keys; disjoint component digests (OP-16 (b)) | `33` R-BENV-5″ at ceremony and verifier | environment reproductions per class; supplier registry in the Trust Policy |
| **CC-3** | Diverse double-compilation agreement: the registered compiler rebuilt through at least two toolchain lineages independent by provenance, at least one not rooted in an upstream binary compiler archive, yields bit-identical `gov` and `gov-admit` (OP-10 (b)) | `33` R-BENV-6″ | toolchain bootstrap registration; reproductions per lineage |
| **CC-4** | Static, self-contained linking: no program interpreter, no `DT_NEEDED` entry; CRT objects and linker from the registered toolchain | ceremony inspection of both binaries; reproducers | ELF inspection records in the registration evidence |
| **CC-5** | Environment manifests derived by `gov-envmanifest/1` from the registered environment lock; each reproduced identically by at least 2 of 3 environment reproductions | `33` R-BENV-3″, R-BENV-7″ | environment reproduction statements |
| **CC-6** | `gov-admit` for the target registered, reproduced (CC-1…CC-5), verified by two records, and listed in a first-contact authority record at root threshold | `32` R-FCA-1 | the authority record's `admitter_evidence` |
| **CC-7** | The protected admission store and protected installation locations of `31` §5 are implemented for the target's operating system (TCB-location predicate) | `31` GB-4′, R-STORE-1 | conformance vectors ADM7 on the target |
| **CC-8** | The shared conformance vectors (FA7, CUR7, ADM7 and PROF7 shapes) pass on the target's `gov` and `gov-admit` | differential conformance suite (`31` R-ADM-14) | vector results per target |
| **CC-9** | The Trust Policy lists the target in `certified_targets` at root threshold, citing the digest of the CC-1…CC-8 evidence | root ceremony | Trust Policy `certified_targets[].criteria_evidence_digest` |

**Initial certified target set** (narrow, reproducible, static targets):

| Target | Status | Reason |
|---|---|---|
| `x86_64-unknown-linux-musl` | **NOT CERTIFIED — pending criteria** | static musl target with the toolchain's self-contained CRT and linker; no CC-1…CC-9 evidence can exist before implementation, and CC-3 depends on OT-2 |
| `aarch64-unknown-linux-musl` | **NOT CERTIFIED — pending criteria** | as above |

Not in the initial set (each may be certified individually later when CC-1…CC-9 hold): `*-linux-gnu` (dynamic glibc),
`*-apple-darwin`, `*-pc-windows-msvc`. Until a target is certified no production admission exists for it; this is the owner's
stated preference ("do not weaken the trust model merely for immediate platform breadth").

## 6. Owner trade-offs surfaced (not decided)

HO-0019 §2 (5): a selected parameter that conflicts with another, or is infeasible, is stated here and not changed. CP-1
applies the stricter reading until the owner decides.

### OT-1 — OP-13 (b) offline media versus OP-7 (a) 24-hour production freshness

- **Conflict.** OP-13 (b) names the second source as a "separately controlled immutable/offline release mirror/media channel".
  OP-7 (a) requires production installation, which includes first admission, to use a state no older than 24 hours. Media
  prepared more than 24 hours before a machine is admitted cannot satisfy both.
- **CP-1 behaviour meanwhile.** The second source is the immutable release mirror, read at admission. Media may carry the
  mirror's byte-identical material, but the admitter refuses a state older than 24 hours (`FIRST_CONTACT_STATE_TOO_OLD`). An
  air-gapped machine is admitted only with media prepared within 24 hours of the state's issuance.
- **Options for the owner** (consequences computed with the CP-REVOKED goal; the sets do not change, only the bound of `win`):

| Option | Residual | Operational consequence |
|---|---|---|
| OT-1a keep CP-1 as is | CUR-R1 bounded by 24 hours | air-gapped admission needs a courier cycle under 24 hours and a Trust State re-issued at least daily |
| OT-1b a separate compiled ceiling for media admission (for example 7 days, the CI anchor limit) | CUR-R1 bounded by that ceiling on media-admitted machines; it changes the OP-7 (a) 24-hour parameter for that path | weekly media; a longer window in which a revoked binary is admitted |
| OT-1c media admit the lineage and evaluator only; the machine stays C0 until an online state ≤ 24 hours anchors it | none added | air-gapped machines never reach C1–C3 |

### OT-2 — OP-10 (b) feasibility for the current compiler version

- **Conflict.** OP-10 (b) requires agreement between independently bootstrapped compiler lineages. The pack's evidence (ENV7)
  models two toolchain identities with distinct provenance on `rustc 1.98.1`, but no toolchain lineage for that version that is
  not rooted in an upstream binary archive has been built or evidenced in this revision. A source bootstrap chain to a current
  compiler is a long, version-by-version chain whose feasibility and cost are not established.
- **CP-1 behaviour meanwhile.** CC-3 is unmet, so no target is certified (§5). There is no fallback to an upstream archive
  alone (EX-15).
- **Options for the owner:**

| Option | Consequence |
|---|---|
| OT-2a keep OP-10 (b) and wait for an evidenced bootstrap lineage of the chosen compiler version | no certified production release until it exists |
| OT-2b keep OP-10 (b) and constrain the certified compiler version to one an evidenced independent bootstrap chain reaches | older language features only; a compiler version constraint on the product |
| OT-2c revisit OP-10 | reopens an owner parameter; not proposed |

Computed consequence under OP-10 (b) (victim P1): the CP-TOOLCHAIN block in `33` §6.

## 7. Residuals of CP-1

| ID | Residual | Bound (computed) | Where |
|---|---|---|---|
| FC-R1′ | The first-contact root: with no key, the custody of both sources, or of their designation, or one of them with an operator who reads one source twice | exactly the eight sets of the CP-FC-ROOT block | `32` §9 |
| FC-R5 | Key theft at first contact: the registration threshold, the reproducer quorum and the trust-state threshold, with the publication process that hands the thief's Trust State to both custodians | CP-FC-KEY-THEFT block | `32` §9 |
| CUR-R1 | A revocation published within the 24 hours before admission | `{win}` (CP-REVOKED) | `32` §8 |
| RS-1 | A running machine anchored before a revocation that never receives later metadata | C1–C2 at its anchored chain within 90 days (CI 7 days); never C3; never shown `current` | `24` §10 |
| RS-2 | A machine without any store, stored codes and a clock set back | `{stored_old, clockback}` (CP-REVOKED) | `32` §8, `24` §10 |
| RS-2b | A store restored from backup, the clock set back into its range, every later statement withheld | as `24` §10 | `24` §10 |
| TB-4′ | Two verification processes and the pipeline | CP-SRC block | `30` §10 |
| TB-S2″ | Every supplier class used compromised together, or the common registered environment lock | CP-ENV block | `33` §8 |
| TA-12″ | Both toolchain lineages compromised, or the registered compiler source | CP-TOOLCHAIN block | `33` §8 |
| RR-2′ | At a project's first use on a machine without a per-project record, the operator confirms at the local trust gate an eligible release the repository requests | the repository requests only; the gate shows the newest eligible release known | `29` DR-25, `27` |
| A8 | Root threshold compromise | outside TA-4 | `01` |

## 8. Evidence

| Instrument | What it shows for CP-1 |
|---|---|
| `evidence/r7/PROF7-profile-conformance.{py,json}` | every exclusion holds under every declared mechanism; P1 profile file; P7 normative text |
| `evidence/r7/FA7-first-contact-authority.{py,json}` | first contact (review r6 B-A01 parts P, S, C; D-A01 parts P, C re-expressed for CP-1); executed minima equal CS7; shared vectors; rule mutants |
| `evidence/r7/CUR7-first-contact-currency.{py,json}` | B-A01 part R, D-A02, D-A08, D-A01 S2 re-expressed; the CUR-R1 and RS-2 residuals exactly |
| `evidence/r7/ADM7-admission-stores.{py,json}` | D-A07, RV6-M6, RV6-L9, OP-14 (b), OP-15 (a), the OP-7 (a) decision rule, R-CLK-1 |
| `evidence/r7/ENV7-environment-authority.{py,json}` | B-A02 A07a/b/c, A08, A09 with the real toolchain; toolchain lineages; computed controls |
| `evidence/r7/CS7-derivation-calculator.{py,json}` | minimal sets, invariants and statements for CP-1 only; revision-6 control |
| `evidence/r7/BA11r7-*`, `BA12r7-*`, `LAY7/crashmig7.py`, C `matrix6` re-run | machine classes, key subsets, crash recovery, legacy containment (R2-H4) |

Counts and the run log are in `22` §1 and `evidence/r7/EVIDENCE-RUN-LOG-r7.json`.
