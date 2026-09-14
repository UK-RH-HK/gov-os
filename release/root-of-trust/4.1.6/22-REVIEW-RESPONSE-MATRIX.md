# Output 22 — Response matrix to the independent review of revision 6

> **RoT-1 revision 7 — PROPOSED, pending fresh independent reviews; not approved, not active, not implemented.**
> - **Review answered:** `release/root-of-trust/4.1.6-review-r6/` (synthesis `ab6b1f8`, AR-0018; panel B `5128086`, C `02bb905`).
>   It reviewed revision 6 (`4106885`) and returned `ROOT_OF_TRUST_ARCHITECTURE_REJECTED`.
> - **Task:** HO-0019 (revision-7 architect, AR-0019): one certified production profile CP-1 (`35`) with the owner's selections of
>   OWNER-DESIGN-REQUIREMENTS-0001 applied exactly.
> - **Scope:** BC6-1 … BC6-4; RV6-H1 … RV6-I2 and the panel findings the synthesis confirmed; CR6-B-01 … CR6-B-07, CR6-C-1 …
>   CR6-C-12, the CR4-B items, C-2 … C-6 and the RV4 transaction parts; CD6-0 … CD6-4 and the §5 rule text; review r6's residual
>   determinations; the §7 re-review entry criteria; review r6's held-out attacks and review r5's decisive probes; HO-0001 §3–§4.
>
> This matrix claims **no finding as accepted or closed**; acceptance is the next reviewers' decision. Status vocabulary:
> - **ADDRESSED — executed:** real legacy binaries, real Git, the real Rust toolchain, real Ed25519 through OpenSSL, the pack
>   checker or the reference executor were run against the revision-7 rules.
> - **ADDRESSED — reference:** a model, oracle or calculator encoding the revision-7 rules was run, with mutants where named.
> - **ADDRESSED — specification only:** not executable before implementation; the RT is named.
> - **REMOVED BY EXCLUSION — tested:** the finding concerned a mode CP-1 excludes; the exclusion's mechanism is named in `35` §4 and
>   exercised by PROF7.
> - **CARRIED — named test.**
> - **RESTATED:** text corrected; nothing decided.
>
> No row is marked addressed on untested evidence. Where revision 7 uses a mechanism other than the correction delta's suggestion,
> the row says so.

## 1. Evidence produced for revision 7 (`evidence/r7/`)

Every run was scratch-only under `env -i`, with `GOV_*` stripped, `HOME`, `XDG_*` and `GOV_KERNEL_CACHE` in scratch, and legacy
binaries read-only. The final runs were from a copy of the work-product tree. Every revision-7 instrument was run in two full
passes (hash seed random, then `PYTHONHASHSEED=12345`); every output is byte-identical across the passes. Commands, digests,
durations, exit codes and comparisons are in `evidence/r7/EVIDENCE-RUN-LOG-r7.json`.

| ID | Evidence | Kind | Result |
|---|---|---|---|
| **PROF7** | `PROF7-profile-conformance.{py,json}` | executed (reference executor and admitter model) and computed (schemas, calculator, register) | **24/24 exclusions** hold under every declared mechanism; **113/113 checks** (21 schema, 18 compiled, 44 refusal, 5 calculator, 25 register); 43 refusal vectors; P1 profile file complete; P7: 11 normative files, **0 unmarked mentions** of an excluded mode; controls accepted |
| **CS7** | `CS7-derivation-calculator.{py,json}`, `CS7-results.json.gz` | reference (derivation calculator, CP-1 only) | 39 configurations over eight goals (G_BYTES, G_CONTENT, G_ENV, G_INPUTS, G_MIRROR, G_REVOKED, G_SRC, G_TOOLCHAIN) and ten victim classes (CIR, FA, ING_P1, ING_P2, P1, P1A, P2, RA_held, RA_unheld, USE); **26/26 self-checks**; incremental enumeration equal to the reference enumeration **21/21**; **177 invariant checks, 0 failures**; **4,680 monotonicity checks, 0 violations**; 38 rules (25 load-bearing in the model, 13 defence in depth); the revision-6 control (10 rules off) over the same 39 configurations; 10 generated statements (9 for CP-1, 1 labelled control); renderer injective |
| **FA7** | `gov_admit_reference_r7.py`, `FA7-first-contact-authority.{py,json}` | executed (real Ed25519 through OpenSSL, 105 verifications; `sha256sum`) | **13/13 verdicts**: S1 honest paths and procedure refusals; S2 P the publication process composes (custodians never publish a composed or below-threshold authority or state; the genuine admitter refuses composed codes; a descendant dropping a revocation is not published; control: the revision-6 shape admits); S2 D designation (one attacker page, weakened steps and an attacker lineage refused); S2 X only OP-13 (b) accepted, every other answer refused; S3 executed minima equal CS7; S4 shared vectors refused, control accepted; S5 restrictors; S7 every revision-7 rule mutant detected |
| **CUR7** | `CUR7-first-contact-currency.{py,json}` | executed (reference executor, real Ed25519) | **14/14 verdicts**: R replayed old values refused by age, the platform package route excluded, current codes refuse B7x, the age rule load-bearing; A02 the store applied at re-admission (control load-bearing; a current value re-admits); A04 re-admission below the accepted-TBM high-water refused and R-ART-2 at use; A08 stored values older than the ceiling refused (within-ceiling control accepted; a set-back clock is exactly RS-2); S2 designated old pages refused by age; W the CUR-R1 window exactly as stated |
| **ADM7** | `ADM7-admission-stores.{py,json}` | executed (reference executor) | **12/12 verdicts**: A07 first admission decided by the protected store only (mutant detected); A08 fail closed; A09 floors never lowered; A11 one first admission, every record kept; A15 records outside the protected store not honoured; CLK a clock below the high-water runs C0-R only; EX02/EX03 script and helper-machine records refused; L9; X14 every record expires; X15 a revoked genuine binary runs C0-R only; X7 the OP-7 (a) decision rule |
| **ENV7** | `ENV7-environment-authority.{py,json}` | executed (real `rustc 1.98.1 (48a229cea 2026-09-01)`) and computed | **14/14 verdicts**: E0 honest environments registered and accepted, bit-identical across supplier classes and toolchain lineages; A07a refused before registration; A07b pipeline selection refused, a selection needs source authority; A07c refused; A08 label diversity refused (control: counting labels accepts the injection); A09 pinned keys refuse; T1 conflict; T2 relabelled lineage refused; T3 residual as stated; computed: the pipeline never minimal and invariants hold, controls show the rules load-bearing, an independent class detects a compromised supplier |
| **BA11r7** | `BA11r7-machine-classes.{py,json}` | computed (CP-1 machine-class oracle, after RV6-B-A11) | **9/9 verdicts** over 89 rows: no row says `current`; no C3 on a state below t9 or on the thief descendant; unanchored machines and expired anchors C0 only; pins beyond 7 days are not anchors; a clock below the high-water C0 only; revoked R7 never eligible. Seven rows the revision-6 oracle allowed are removed: six by R-CLK-1, one by the CP-1 currency rule |
| **BA12r7** | `BA12r7-key-subsets-below-threshold.{py,json}` | computed (after RV6-B-A12) | **99,772 key subsets** over 39 configurations: **0 accepts with at most one key**; 0 accepts with release and trust-state keys plus infrastructure only |
| **PPR7** | `PPR7-project-records.{py,json}` | computed (per-project record model) | **7/7 verdicts**: worktree, move and bind-mount keep E10; clone and fork reported, fail closed, never overwrite; remedies keep the strength report and pending gate; only gates clear them; path-keyed, id-only and remedy re-record mutants detected |
| **DA05r7** | `DA05r7-combinations-under-CP1.{py,json}` | computed (after RV6-D-A05) | **6/6 verdicts**: E1 the pipeline never minimal under CP-1, invariants hold, control reproduces review r6; E2 the upstream toolchain archive alone (`toolchain_up`) not minimal under CP-1 (control: minimal); E3 the one combination stated |
| **DA06r7** | `DA06r7-rendering-and-classifier-vocabulary.{py,json}` | computed (after RV6-D-A06) | **7/7 verdicts**: renderer injective; no misrendered atom; the repository writer and a reproducer key render differently; no prefix classifier in invariants or statements; a prefix renderer changes rows and each changed set is detected at atom level; control reproduces the committed statements |
| **crashmig7** | `LAY7/crashmig7.{py,json}` | executed (real legacy 4.1.5 and 4.1.2; reviewer C's revision-6 trees and harness, attributed) | **5/5 verdicts** over 24 prefixes (both lock orders): never `ABSENT` or `PARTIAL` after recovery; rolled-back trees byte-equal to the legacy project; legacy behaviour on them equals the control (LR-1); an honoured journal is always `IN_TRANSACTION`; RoT-1 `init` never runs over an overlay; A-11 and B-11 roll forward to `COMPLETE` |
| **REG** | `decision-register/register_check.py` → `REGISTER-CHECK.json` | computed | **PASS C1–C11**: 45 decisions; 28 certified schemas, **578 schema fields**, each with a role and an establishing party; 23 procedure inputs; 24 excluded inputs |
| **STMT** | `decision-register/statements_check.py` → `STATEMENTS-CHECK.json` | computed | **PASS**: 12 block placements of 10 generated statements equal CS7; S1a **216 rendered sets** equal computed minimal sets at atom level; S2 10 hand-written sets (including this matrix); S3 renderer injective and a prefix-merging renderer detected |
| **DA09r7** | `DA09r7-schema-fields-versus-register.{py,json}` | computed (after RV6-D-A09) | **6/6 verdicts**: 578 fields of 28 schemas, **0 uncovered**, 0 selector, restrictor or binding without an establishing party; designation, procedure text, publication process, submitter and manifest author named; **7/7 held-out register mutations** fail with a named check (C3, C7, C9, C10, C11); control passes |
| **DA04r7** | `DA04r7-plan-regression-detection.{py,json}` | computed (after RV6-D-A04) | **15/15 review-r6 defects** each have a plan row, a register row and a passing detecting instrument; RT-184, RT-186, RT-192 and RT-193 are distinguishing with held-out or mutation inputs |
| **EX7** | `examples/rev7/make_rev7.py`, `validation.json` | computed | 28 schemas meta-valid; **17/17 instances** valid; 30 withdrawn or excluded shapes refused |
| **RERUN6** | retained revision-6 instruments (files unchanged) | executed | CS6, P4r6, DA03r6, FA6, CON6, SRC6, UW6, ATTR6, ENV6 and the CSI self-test **byte-identical** to their committed outputs; CSI checks ×5 exit 0/3/2/2/2, differing only in `kernel_dir`; ADM6 differs only in the unlocked mutant's race counts; DA07r6 reads the revision-7 plan and register (§8) |
| **RERUN5** | retained revision-5 instruments | executed | CS5, P4r5, DA03r5, FA5, REG5 and P1r4 **byte-identical** |
| **PROBES** | unmodified review r6 B and D probes; review r5 decisive probes (scratch copies, against the final export) | executed | §7 and §8 |
| **C** | reviewer C's `register6`, `gitops6`, `struct6`, `attrprec6`, `admtx6`, `crashmig6`, `matrix6` (unmodified scratch copies) | executed (real 4.1.2–4.1.5, real Git) | `registers6`, `struct6`, `attrprec6`, `admtx6` and `crashmig6` **byte-identical** to review r6's committed outputs; `gitops6` equal once the scratch prefix is mapped to `<ar17>`; `matrix6`: run on the earlier trees and on trees rebuilt by `build6` from the final export, 62,036 rows each (61,520 active, 516 skipped): **property R2-H4 0 violations**; LP-1r 2,492 root-anchored rows, 0 project writes; Git operations leaving a written tree `COMPLETE` 0; every property equal to review r6's committed summary (including 16 classification-lost rows on pre-migration checkouts, LR-2, and 96 transaction-area rows, reported and inert), which differs only in binary digests and elapsed time |

**Helper sessions:** none.

## 2. Blocking classes

HO-0019 §2b applies the owner's requirements to each class and asks for the stricter reading of BC6-1.

| Class | Findings | Revision-7 mechanism (removes the input) | Owner requirement applied | Specified in | D-0008 rules | Evidence | Status |
|---|---|---|---|---|---|---|---|
| **BC6-1** first-contact selector authority | RV6-H1 | **First-Contact Authority record at root threshold.** Lineage, the admitter digest per certified target, the two source identities and the procedure digest are fixed in one record signed 2-of-3 by the root keys, only after the admitter's registration, 2-of-3 reproduction and two verification records (R-FCA-1…R-FCA-4; purpose `first-contact-authority` on root keys only, KS-18). **State from threshold statements verified first-hand.** The trust code `gov-fct:…` is the digest of that record; the state code `gov-fcs:…` is the digest of a Trust State signed at the trust-state threshold. Each source custodian publishes a code only after verifying the statement first-hand with its own admitted `gov` (R-FCS-1…R-FCS-3); the publication process composes nothing (EX-23). **Designation** comes from the root ceremony record at onboarding, outside release carriers (R-FCD-1…R-FCD-3); `gov trust fc-procedure` is absent (EX-24). **No submitter:** platform package roots and OP-13 (c) are excluded (EX-04, EX-05). **Admitter:** compiled lineage, compiled quorum 2 over both codes and the procedure digest, state age ≤ 24 h (FC-4′…FC-10). **Stricter reading** (`32` §10): no value that selects lineage, state or evaluator is composed or selected solely by the trust-state publisher, an unadmitted binary or a package submitter. | "First-contact composer/signer"; OP-13 (b); OP-12 (a) | `32`, `35` §2, `05` §3, `06` §2–§3, `25` §6–§7, `31` §9, `24` §3.2 | (16), (19), (25) restated; (29) added | FA7 S1–S7; CS7 CP-FC-ROOT, CP-FC-KEY-THEFT; PROF7 EX-04, EX-05, EX-17, EX-18, EX-23, EX-24; DA09r7 | ADDRESSED — executed (reference executor) and reference; the excluded answers REMOVED BY EXCLUSION — tested; RT-184, RT-190 |
| **BC6-2** first-contact currency | RV6-H2 | **Compiled maximum age** of 24 hours for the admission state on every path: codes read from the sources, media carrying them, and CI images (FC-9, `FIRST_CONTACT_STATE_TOO_OLD`). **Re-admission applies the stores**: no state below held anchors, no binary or admitter revoked in held state, no release below the held security minimum, no binary below the accepted-TBM high-water (AP-R1…AP-R6); two stores with the protected admission store authoritative (R-STORE-1, R-STORE-2); R-ART-2 at use (GB-7). **Every admission record expires** (90 days workstation, 7 days CI). **Clock high-water** (R-CLK-1). Residuals stated with computed sets: CUR-R1 `{win}` (24 hours), RS-2 `{stored_old, clockback}` (CP-REVOKED). | OP-7 (a); OP-13 (b); OP-14 (b); OP-15 (a) | `32` §8, `31` §4.1, `24` §4.3, §4.5, `25` §5, `20` §9 | (7), (19), (23) restated | CUR7 14/14; ADM7 X14, CLK, A09; BA11r7 9/9; CS7 CP-REVOKED | ADDRESSED — executed (reference executor) and reference; RT-185, RT-189, RT-191. Owner trade-off OT-1 surfaced (`35` §6) |
| **BC6-3** first-hand environment manifest | RV6-H3 | **No author.** The environment lock is registered source content; the manifest is derived by `gov-envmanifest/1` (no free content) and assembled by `gov-envassemble/1`; supplier checksum keys are pinned in the root-signed Trust Policy; supplier classes and toolchain lineages are independent by provenance (base image lineage, package source, build system, signing infrastructure; disjoint keys and component digests); a manifest is authoritative only with ≥ 2 agreeing environment reproductions **and** the 2-of-3 registration over that exact `environment_id` (R-BENV-1″…R-BENV-7″). Verifiers build in derived environments before registration (R-BENV-8); derivation tools come from registered source or an admitted binary (R-BENV-9). Manifest v1's free fields are withdrawn. | "Build-environment manifest author/signer"; OP-16 (b); OP-10 (b); OP-9 (b)+(d) | `33`, `30` §2, §4.2, `35` CC-2, CC-3, CC-5 | (9), (26) restated | ENV7 14/14 (real toolchain); CS7 CP-ENV, CP-TOOLCHAIN; DA05r7 E1, E2; PROF7 EX-15, EX-21 | ADDRESSED — executed and reference; RT-186, RT-187. Owner trade-off OT-2 surfaced |
| **BC6-4** register over inputs; statements; plan detection | RV6-M2, RV6-M1; the false statements of H1–H3 | **Register complete over input values**: every certified schema field and every procedure input has a role (selector, restrictor, binding, carrier, informational, excluded) and an establishing party (`register_check` C9, C10); every exclusion is an `excluded` input row (C11). **Calculator** for CP-1 only, with a labelled revision-6 control. **Statements** generated and checked at atom level with an injective renderer (S1a, S3); hand-written sets checked (S2). **Independent detection**: held-out register mutations (DA09r7), the review-r6 defect list (DA04r7), RT-192, RT-193, RT-199. | "Register completeness over every input value … for the concrete profile only" (HO-0019 §2b) | `29`, `decision-register/`, `12` §4e | (22) restated | REG PASS; STMT PASS; DA09r7 6/6; DA06r7 7/7; DA04r7 15/15 | ADDRESSED — reference; RT-192, RT-193, RT-199 |

**Owner trade-offs of the correction delta.** The owner's selections answer F1-a…F1-c and C-a…C-c (`21` §3). BC6-1's state
portion is established first-hand within those selections (trust-state threshold plus both custodians' first-hand verification),
so no F1 residual is left undecided. BC6-2's per-path maxima are the owner's OP-7 (a) limits. Two conflicts between selections
are surfaced and not decided: OT-1 and OT-2 (§11).

## 3. Findings RV6-H1 … RV6-I2

| Finding | Revision-7 change | File | Evidence | Status |
|---|---|---|---|---|
| **RV6-H1** | BC6-1 (§2). Contradicted statements restated from CS7 for CP-1: FC-ROOT, FC-KEY-THEFT and FC-CONTENT replaced by CP-FC-ROOT, CP-FC-KEY-THEFT and CP-CONTENT; `25` §6–§7; `31` AD-1″ and TB-1′; `21` OP-6, OP-13 and combinations; D-0008 rules (16), (19), (25). Running-machine confirmations type the state codes each source publishes; an in-gate confirmation carries both (`24` §3.2). | `32`, `35`, `21`, `05`, `06`, `24`, `25`, `31`, `34` | FA7 S2 P, D, X and S3; CS7; PROF7 | ADDRESSED — executed and reference; excluded answers REMOVED BY EXCLUSION — tested; RT-184, RT-190 |
| **RV6-H2** | BC6-2 (§2). DR-04's "bounded by `valid_until`" replaced by the compiled 24-hour age; RS-B1 and FC-R4 replaced by CUR-R1 and RS-2 with computed sets. | `32`, `31`, `24`, `25`, `20` | CUR7; ADM7; BA11r7; CS7 CP-REVOKED | ADDRESSED — executed and reference; RT-185, RT-189, RT-191 |
| **RV6-H3** | BC6-3 (§2). `33` §2 (1)–(3), OP-16-ENV, INV-ENV-PIPELINE, TB-S2′, `25` §7 and D-0008 rules (9), (26) restated; TB-S2″ and TA-12″ stated from CP-ENV and CP-TOOLCHAIN. | `33`, `30`, `25`, `21`, `01` | ENV7; CS7; DA05r7 | ADDRESSED — executed and reference; RT-186, RT-187 |
| **RV6-M1** | CR6-B-03 (a): renderer injective over atom classes; S1 compares atoms (S1a); S3 shows the check detects a prefix-merging renderer. | `29` §5.5, `decision-register/statements_check.py`, CS7 | STMT S1a, S3; DA06r7 | ADDRESSED — reference; RT-193 |
| **RV6-M2** | BC6-4 (§2): C9–C11 over schema fields, procedure inputs and exclusions. | `29`, `decision-register/` | REG; DA09r7; DA04r7 | ADDRESSED — reference; RT-192, RT-199 |
| **RV6-M3** | CR6-C-7 (a)–(e) plus the `init` rule: every layout-migration step a journal phase with its undo record; `LAYOUT_MIGRATION_INCOMPLETE`; `IN_TRANSACTION` precedence; `ABSENT` requires no overlay and no views; an intent phase before the exchange; R-INIT-9 (`init` over an existing overlay refuses or evaluates `19` §9 item 5 with the `weakening` gate); `init` added to `19` §9's coverage. | `18` §5.3, §9; `19` §9; `20` §5; `09`; `26` §7–§8 | crashmig7 5/5; unmodified RV6-D-A10 re-run: all four of its checks now find the rule, the coverage, the `ABSENT` condition and the RT | ADDRESSED — executed; RT-195 |
| **RV6-M4** | CR6-C-8: record keyed by `project_trust_id`, repository paths and a locally recorded repository identity; inheritance and fail-closed duplication. | `20` §9; `18` §5.1 | PPR7 | ADDRESSED — reference; RT-196 |
| **RV6-M5** | CR6-C-9: re-records retain failing requirements; pending obligations are record fields cleared only by their gates. | `19` §9 item 4; `20` §8; `26` §6 | PPR7 | ADDRESSED — reference; RT-197 |
| **RV6-M6** | CR6-C-10: two stores specified (R-STORE-1); first admission decided only by the protected admission store's marker (R-STORE-2, R-ADM-8″); the account store for the lineage moved aside. | `31`, `24` §8, `06` §3 | ADM7 A07 (planted record, anchor, project record and confirmation do not survive; mutant detected) | ADDRESSED — executed (reference executor); RT-185, RT-202 |
| RV6-L1 | CR6-B-04 carried: `security_classified` per inventory row, refused when absent. The checker change is implementation work. | `34` §3 | unmodified RV6-B-A10 and RV6-D-A03 re-runs byte-identical: the unchanged checker still does not list K1–K3 or an unflagged unlisted path | CARRIED — named test RT-198 |
| RV6-L2 | CR6-B-05: `05` §1–§2 list the revision-7 payloads and name the first-contact codes. | `05` | text | RESTATED; RT-127 (revised in revision 7) |
| RV6-L3 | CR6-B-06: R-BENV-8 (verifiers build in derived environments before registration; attestations name `environment_ids`; others not counted). | `33`, `30` | ENV7 (derivation before registration) | ADDRESSED — specification only for the attestation count; RT-200 |
| RV6-L4 | CR6-B-07: R-BENV-9 and R-REG-3 (g). | `33`, `30`, `34` | design | ADDRESSED — specification only; RT-186 (`DERIVATION_TOOL_UNREGISTERED`) |
| RV6-L5 | CR6-B-02, CR6-C-12: AP-R6 applies the high-water at re-admission; GB-7 at use; the reference executor's `gov_run` implements R-ART-2. | `31` §4.1, GB-7; `20` §9; `25` §5 | CUR7 A04 | ADDRESSED — executed (reference executor); RT-170 extended, RT-191 |
| RV6-L6 | CR6-C-2: condition kept; every remedy that recreates the occupation force-adds `.governance-runtime/migration`. | `26` §8; `20` §8 | unmodified `gitops6` re-run | ADDRESSED — executed (condition), specification only (remedy); RT-174 extended |
| RV6-L7 | CR6-C-1 unchanged in rule; tests extended. | `18` §9.1, `26` §2, `08` §2 | `gitops6`, `attrprec6` re-runs | ADDRESSED — executed (reference layout); RT-50, RT-122, RT-173 extended |
| RV6-L8 | CR6-C-6: scan scope stated. | `18` §5.1 | design | ADDRESSED — specification only; RT-201 |
| RV6-L9 | Full 64-hex lineage store names; records bound to the lineage; a store without the marker is a first admission. | `31` R-STORE-1, R-ADM-8″, GB-1″ | ADM7 L9 | ADDRESSED — executed (reference executor); RT-202 |
| RV6-L10 | CR6-C-3: doctor names `governance/overlay/spec` litter and distinguishes it from an overlay change. | `26` §4, §8; `18` §9 | `matrix6` re-run (reported rows) | ADDRESSED — specification only (doctor); RT-176 extended |
| RV6-L11 | CR6-C-11: `08` §2 sentence corrected; `20` §5 `committed` phase withdrawn; this matrix states total rows. The revision-6 LAY6 rows (including `INFOATTR` and the `props6` input) are history and are not evidence for revision 7, which uses reviewer C's unmodified `gitops6`, `attrprec6` and `matrix6`. | `08`, `20`, `22` | text | RESTATED |
| RV6-L12 | CP-1 has one OP-10 × OP-16 combination, (b) with (b); every other pair is excluded. | `21` §4 | DA05r7 E2; PROF7 EX-15, EX-21 | ADDRESSED — reference; REMOVED BY EXCLUSION — tested; RT-187, RT-190 |
| RV6-I1 | unchanged: the acting role is caller-declared; no trust gate depends on it. | `27` §5 | — | INFO — stated |
| RV6-I2 | carried to the capability-contract phase. | `34` §5 | — | CARRIED — named test RT-182 |

## 4. Panel findings the synthesis confirmed (adjudication precedence)

| Panel item | Consolidated as | Revision-7 row |
|---|---|---|
| RV6-B-H1 publisher-composed code | RV6-H1 | §3 RV6-H1 |
| RV6-B-H2 (c) "either": submitter and replay | RV6-H1 (submitter), RV6-H2 (replay) | submitter: REMOVED BY EXCLUSION — tested (EX-04, EX-05; FA7 S2 X; PROF7); replay: §3 RV6-H2 |
| RV6-B-H3 environment manifest | RV6-H3 | §3 RV6-H3 |
| RV6-B-M1 re-admission does not apply the store | RV6-L5 (re-rated LOW); held-state part in RV6-H2 | §3 RV6-L5, RV6-H2 |
| RV6-B-M2 CONTENT rendering | RV6-M1 | §3 RV6-M1 |
| RV6-B-M3 register over rule ids | RV6-M2 | §3 RV6-M2 |
| RV6-B-L1 … L4; RV6-B-I1 | RV6-L1 … L4; RV6-I1 | §3 |
| B's "OP-11 incomplete" | REFUTED by the synthesis (R-ART-2 refuses at use) | R-ART-2 kept as GB-7; AP-R6 added at re-admission; OP-11 (b) computed minimum AP-SEC |
| RV6-C-M1 ignore sources | RV6-L6 (re-rated LOW) | §3 RV6-L6 |
| RV6-C-M2 first-install migration crash | RV6-M3 | §3 RV6-M3 |
| RV6-C-M3, M4 | RV6-M4, M5 | §3 |
| RV6-C-M5 two stores | RV6-M6 | §3 RV6-M6 |
| RV6-C-L1 … L5 | RV6-L7 … L11 | §3 |
| RV6-C-L6 rollback and high-water | duplicate of RV6-L5 | §3 RV6-L5 |

## 5. Carried requirements

Named tests for every item are indexed in `12` §4g (RT-200…RT-202 new; extended rows as stated there).

| Item | Specified in | Test → evidence | Status |
|---|---|---|---|
| CR6-B-01 | `32` R-FCS-1…R-FCS-3, FC-9; `33` | RT-184, RT-191, RT-186 → FA7 S2 P; CUR7 A08; ENV7 A07a | executed (reference executor, real toolchain) |
| CR6-B-02 (i)–(iii) | `31` AP-R6, GB-7 | RT-170 extended, RT-191 → CUR7 A04 | executed (reference executor) |
| CR6-B-03 (a), (b), (i)–(iii) | `29`, `decision-register/` | RT-192, RT-193 → STMT S1a, S3; DA09r7 M1–M7; DA06r7 | reference |
| CR6-B-04 | `34` R-CON-5 | RT-198 | CARRIED — named test |
| CR6-B-05 | `05` §1–§2 | text review; RT-127 | restated |
| CR6-B-06 | `33` R-BENV-8 | RT-200 | specification only |
| CR6-B-07 | `33` R-BENV-9; `30` R-REG-3 (g) | RT-186 | specification only |
| CR6-C-1 | `18` §9.1, `26` §2, `08` §2 | RT-50, RT-122, RT-173 extended → `gitops6`, `attrprec6` | executed (reference layout) |
| CR6-C-2 | `26` §8, `20` §8 | RT-174 extended → `gitops6` (condition) | executed (condition); specification only (remedy) |
| CR6-C-3 | `26` §4, §8; `18` §9 | RT-176 extended | specification only |
| CR6-C-4 | `18` §9.2 | RT-175 | specification only |
| CR6-C-5 | `31` R-ADM-8″, R-ADM-13, GB-1″ | RT-139, RT-170, RT-181 → ADM7 A09, A11 | executed (reference executor) |
| CR6-C-6 | `18` §5.1 | RT-201 | specification only |
| CR6-C-7 (a)–(f) | `18` §5.3, §9; `19` §9; `20` §5; `09`, `26` R-INIT-9 | RT-195 → crashmig7; RV6-D-A10 re-run | executed |
| CR6-C-8 | `20` §9; `18` §5.1 | RT-196, RT-99, RT-118 extended → PPR7 | reference |
| CR6-C-9 | `19` §9; `20` §8; `26` §6 | RT-197, RT-81, RT-167 extended → PPR7 | reference |
| CR6-C-10 | `31` R-STORE-1, R-STORE-2 | RT-185; RT-139, RT-170, RT-171 extended → ADM7 A07 | executed (reference executor) |
| CR6-C-11 | `08`, `20`, `22` | text review | restated |
| CR6-C-12 | `31` GB-7; `20` §9 | RT-170 extended → CUR7 A04 | executed (reference executor) |
| C-2 … C-6 | `18` §3, §9; `26` §2; `20` §8 | RT-123, RT-124 extended, RT-125 extended, RT-50, RT-155 | CARRIED — specification only |
| RV4-M2, RV4-M5 (transaction parts) | `18` §5.1; `19` §9 item 5 | RT-103, RT-146 | CARRIED — specification only |
| CR4-B-01, CR4-B-04, CR4-B-05 | as review r4 B | RT-103 and RT-138, RT-146, RT-150 | CARRIED — specification only |
| CR4-B-02 | witness custody | RT-149 removed by exclusion (EX-01); the custody check kept in RT-180 | REMOVED BY EXCLUSION — tested (PROF7 EX-01) |

**B's acceptance cases for the blocking findings** (review r6 B `04`, last table), on the reference executor and calculator:
- **H1 (a).** RV6-B-A01 part P on CP-1: the publication process is compromised and every source is honest. Custodians refuse to
  publish a composed or below-threshold authority or state, and the genuine admitter refuses composed codes. Control: the
  revision-6 shape admits (FA7 S2 P). The other OP-13 answers are refused (FA7 S2 X).
- **H1 (b).** CS7 computes the first-contact root for CP-1, and the executed minima equal it (FA7 S3). The revision-6 control
  keeps the rules that made the publisher an unstated selector (`28` §12, CP-R6-CONTROLS).
- **H2 (a).** The old platform-signed package route is excluded (EX-04, EX-05; CUR7 `R_platform_package_route_excluded`).
  Replayed old codes are refused by age (CUR7 R).
- **H2 (b).** The package submitter is excluded (EX-05; PROF7 refusal vectors at admission and at the procedure).
- **H2 (c).** FA6's platform-only branch is removed by exclusion.
- **H3 (a).** ENV7 A07a, A07b, A07c, A08 and A09 are refused before registration or conflict (real toolchain; reference
  tooling, not the implementation).
- **H3 (b).** CS7 with recipe, selection, label and upstream-key strategies: the pipeline is never minimal and the invariants
  hold (ENV7 computed; DA05r7 E1). The CP-ENV block equals its output (STMT).

## 6. Correction delta CD6-0 … CD6-4 and the §5 rule text

| Item | Applied as | Different mechanism? |
|---|---|---|
| **CD6-0 retain** | Retained: the BC5 closures as stated, carried closures, running-machine currency and legacy containment. **Non-regression:** CS6, P4r6, DA03r6, FA6, CON6, SRC6, UW6, ATTR6, ENV6, the CSI self-test (78/78) and the revision-5 instruments re-run byte-identical from the work-product tree. ADM6 is equal apart from the race counts, and the CSI checks apart from `kernel_dir`. Reviewer C's `crashmig6`, `struct6`, `attrprec6`, `admtx6` and `registers6` are byte-identical, and `gitops6` is equal apart from the scratch prefix. `matrix6`: R2-H4 0 violations over 62,036 rows on both tree sets. RV6-B-A11 and RV6-B-A12 (revision-6 models) are byte-identical, with CP-1 re-expressions BA11r7 and BA12r7. | none |
| **CD6-1** | `32`, `35`, `05`, `06`, `21`, `24`, `25`, `31` | Lineage, admitter, sources and procedure are fixed in a root-threshold record: CD6-1 (1), second form, as the owner's "composer/signer" requirement selects. **Also**, the state portion is not publisher-composed. The state code is the digest of a trust-state-threshold statement that each custodian verifies first-hand before publishing (the first form's first-hand derivation, applied to the state). Designation as CD6-1 (3). Submission: excluded rather than authorised (owner: OP-13 (c) and platform package roots excluded). |
| **CD6-2** | `32` §8, `31` §4.1, `24`, `25` §5 | C-a in the owner's form: a compiled 24-hour maximum age on every path instead of a per-path `valid_until` the owner sets. Re-admission applies the stores as proposed, with the protected admission store authoritative. A clock high-water is added (R-CLK-1). The calculator goal G_REVOKED covers victims FA, RA_held and RA_unheld. |
| **CD6-3** | `33`, `30`, `35` | CD6-3 (1), second form: a lock in source with a normative derivation and no free content. Keys pinned (2), supplier class by provenance (3), verification order (4), register, calculator and statements (5). **Also** the owner's authority condition: ≥ 2 agreeing environment reproductions and the 2-of-3 registration over that exact identity. Toolchain lineages are also by provenance (OP-10 (b)). |
| **CD6-4** | `29`, `decision-register/`, `12` §4e, §4g | As proposed. **Also** exclusions are register input rows (C11). S2 fails a hand-written set that names trust atoms beside unknown members (added after the unmodified RV6-B-A03 re-run, §12). |
| §5 rules | D-0008 revision 7, `15` §5 | (7), (9), (16), (19), (22), (23), (25), (26) restated as §5 lists; also (10), (14), (15), (18), (20), (27) restated for CP-1; (28) one certified profile, (29) the first-contact authority at root threshold, (30) certified targets, (31) owner trade-offs stated, never decided. |

## 7. Review r6 §7 re-review entry criteria

| Criterion | State |
|---|---|
| **1.** CD6-1 … CD6-4 closed as classes in pack, schemas, register, D-0008, ARCH-0002; both PROPOSED and not active | §2. **Schemas:** `first-contact-authority` and `environment-lock` added; `environment-manifest` v2 (derived; `assembly_function` constant); `first-contact-manifest` and `freshness-witness` withdrawn to `schemas/withdrawn-non-production/`. Revised for CP-1: `trust-root`, `trust-policy-statement`, `admission-record`, `release-registration`, `input-manifest`, `verification-attestation`, `binary-reproduction`, `environment-reproduction`, `trust-state-pin`, `trust-gate-confirmation`, `trust-decision-pin`, `trust-base-manifest`, `revocation-statement`, `trust-state-statement`, `framework-lock-3.0.0`. EX7: 28 meta-valid, 17/17 instances, 30 refused shapes. **Register:** REG PASS. **D-0008 and ARCH-0002:** revision 7, `status: PROVISIONAL`, `proposal_state: PROPOSED`, `human_approved: false` (D-0008), `in_effect: false`, no `chosen_option`; owner design requirements cite OWNER-DESIGN-REQUIREMENTS-0001 |
| **2a.** B-A01 parts P, S, C and D-A01 parts P, C under all seven OP-13 answers (WR included) | CP-1 has one answer, (b). The six others are refused (FA7 S2 X; PROF7 EX-04, EX-05, EX-17, EX-18). **P:** FA7 S2 P, four verdicts (above). **S:** the submitter is excluded and refused (PROF7 EX-05). **C:** CS7 CP-FC-ROOT, with executed minima equal (FA7 S3). **D-A01 P:** FA7 S2 D (attacker pages, weakened steps, attacker lineage refused). **WR:** removed by exclusion (EX-01). **Unmodified probes:** RV6-B-A01 cannot run (it opens the withdrawn `first-contact-manifest.schema.json`). RV6-D-A01 runs against the revision-6 executor (history) and reproduces its revision-6 rows; its design checks now find a plan row and the designation rule |
| **2b.** B-A01 part R, D-A02, D-A08, D-A01 S2 | CUR7 R, A02, A08, S2, W (14/14; above). **Unmodified probes:** RV6-D-A02 runs against the revision-6 executor (history); its plan-row check now finds RT-191. RV6-D-A08 cannot run (withdrawn schema) |
| **2c.** B-A02 (A07a/b/c, A08, A09; executed and computed) and D-A05 E1 | ENV7 14/14 with the real toolchain, including the computed verdicts; DA05r7 E1. **Unmodified probes:** RV6-B-A02 cannot run (it reads manifest v1's withdrawn `upstream_checksum_reference`). RV6-D-A05 cannot run (it reads `21` §17, which the option tree removal withdrew) |
| **2d.** D-A09 and D-A04 against the revision-7 register and plan | DA09r7 6/6: 0 unregistered selector inputs over 578 fields; 7/7 mutations fail with a named check. DA04r7 15/15. **Unmodified probes:** RV6-D-A09 cannot run (withdrawn schema). RV6-D-A04 runs and still reports 15 undetected, because it looks for the revision-6 instruments' outputs (FA6, ENV6, …), which revision 7 re-expresses |
| **2e.** B-A03 and D-A06 | DA06r7 7/7; STMT S1a and S3. **Unmodified probes:** RV6-D-A06 byte-identical (it analyses CS6, history). RV6-B-A03 analyses CS6 (history). Its part 3 against the revision-7 check: the misrendered set written outside a block fails S2. The "true atom" line also fails, because it names a configuration CP-1 excludes (OP-2 (a) with OP-8 = 1; EX-09, EX-13) |
| **2f.** Unchanged in what they refuse | CS6 self-checks and invariants, P4r6, DA03r6, FA6, CON6, ENV6, SRC6, UW6, ATTR6 byte-identical; ADM6 equal apart from the race counts; CSI self-test 78/78 byte-identical; register and statement checks as extended PASS; CS5, P4r5, DA03r5, FA5, REG5, P1r4 byte-identical; RV6-B-A11 and RV6-B-A12 byte-identical (plus BA11r7 and BA12r7 on CP-1); reviewer C's `matrix6` R2-H4 0 violations over 62,036 rows on both tree sets; `crashmig6` byte-identical and, with CR6-C-7, crashmig7 5/5 (no prefix `ABSENT` after recovery; no RoT-1 `init` over an overlay) |
| **3.** Response matrix over RV6-H1 … RV6-I2, CR6-B-01 … CR6-B-07, CR6-C-1 … CR6-C-12, CD6-0 … CD6-4, with no untested "resolved" | §3–§6; `12` §4g; specification-only rows are labelled |
| **4.** Owner options | The owner selected F1 and C through OWNER-DESIGN-REQUIREMENTS-0001 (`21` §1, §3); OP-6, OP-7, OP-9, OP-13, OP-14, OP-15 and OP-16 restated from the regenerated CP-1 blocks; `21` §17 replaced by `21` §4 (one combination). The architecture makes no choice; OT-1 and OT-2 are surfaced (§11) |

## 8. Held-out attacks and decisive probes re-run against revision 7

"Unmodified" means the review's probe file copied to scratch and run against the final export. Probes that import the
revision-6 or revision-5 executors, calculators or oracles evaluate those instruments, which are history, so they reproduce the
revision-6 or revision-5 rows. Probes that open withdrawn artefacts cannot run. The CP-1 result is the re-expression.

| Attack | Unmodified re-run | Re-expression on CP-1 | Result on revision 7 |
|---|---|---|---|
| RV6-B-A01 (parts P, S, C, R) | cannot run (withdrawn `first-contact-manifest` schema) | FA7 S2 P, S2 X, S3; CUR7 R | refused before any evaluator; only OP-13 (b); replay refused by age |
| RV6-B-A02 (A07a/b/c, A08, A09) | cannot run (withdrawn manifest v1 field) | ENV7; DA05r7 E1 | refused before registration or conflict; the pipeline never minimal |
| RV6-B-A03 | runs; part 3 S2 now rejects the misrendered set | DA06r7; STMT S1a, S3 | injective renderer; merged renderer detected |
| RV6-B-A04 | runs against the revision-6 executor; verdicts unchanged; two design leaves differ (`25` AP-8 and §7 row restated) | CUR7 A04 | `BINARY_T0_ROLLBACK` at re-admission and at use |
| RV6-B-A05, A06 | executed within B-A01 parts R, S | CUR7 R; PROF7 EX-04, EX-05 | route excluded (`PROFILE_MODE_EXCLUDED`); old codes `FIRST_CONTACT_STATE_TOO_OLD` |
| RV6-B-A07, A08, A09 | executed within B-A02 | ENV7 A07a/b/c, A08, A09 | refused |
| RV6-B-A10 | byte-identical | carried RV6-L1 | not listed by the unchanged checker; default deny holds; RT-198 |
| RV6-B-A11 | byte-identical (revision-6 model) | BA11r7 9/9 | never `current`; C0 below the clock high-water |
| RV6-B-A12 | byte-identical (revision-6 model) | BA12r7 | 0 accepts with ≤ 1 key over 99,772 subsets |
| RV6-B-A13 | design | `24` §3.2; FA7 S2 P; BA11r7 `no_C3_on_thief_descendant` | confirmations type the state codes each source publishes after first-hand verification; a Trust State below threshold or dropping a revocation is never published |
| RV6-B-A14 | design | `33` R-BENV-8 | RT-200 |
| RV6-B-A15 | design | `33` R-BENV-9; `30` R-REG-3 (g) | RT-186 |
| RV6-B-A16 | computed | REG C9–C11; DA09r7 | 0 unregistered selector inputs; mutations fail |
| RV6-C-A01 … A04 | `matrix6` R2-H4 0 violations over 62,036 rows on both tree sets | — | as `matrix6` |
| RV6-C-A05, A06, A07, A09 | `gitops6` equal apart from the scratch prefix | `12` §4g (RV6-L6, RV6-L7) | as review r6 |
| RV6-C-A08 | `attrprec6` byte-identical | RT-173 extended | as review r6 |
| RV6-C-A10 … A13 | `admtx6` byte-identical (revision-6 `gov-admit` model) | ADM7 A08, A09, A11, A15, L9 | fail closed; floors kept; one first admission; records only in the protected store |
| RV6-C-A14 | design | `18` §5.1 scan scope | RT-201 |
| RV6-C-A15 | `crashmig6` byte-identical | crashmig7 5/5 | never `ABSENT` or `PARTIAL` after recovery |
| RV6-C-A16, A17 | design and fact | PPR7 | E10 kept; fork reported and fail closed; report and pending gate survive remedies |
| RV6-C-A18 | design | ADM7 A07 | the protected admission store decides first admission |
| RV6-C-A19 | design | CUR7 A04 | trusted operations refused below the high-water; RT-170 extended |
| RV6-D-A01 | runs against the revision-6 executor (history); design checks now find the plan row and the designation rule | FA7 S2 D; CS7 CP-FC-ROOT | refused outside the stated root |
| RV6-D-A02 | runs against the revision-6 executor (history); plan-row check now finds RT-191 | CUR7 A02 | `READMISSION_STATE_BELOW_HELD`; `BINARY_REVOKED_IN_HELD_STATE` |
| RV6-D-A03 | byte-identical | carried RV6-L1 | default deny and first-hand refusal hold; the listing flag carried (RT-198) |
| RV6-D-A04 | runs; 15 undetected by its revision-6 instrument names | DA04r7 15/15 | detected |
| RV6-D-A05 | cannot run (`21` §17 withdrawn) | DA05r7 6/6 | as §1 |
| RV6-D-A06 | byte-identical (analyses CS6) | DA06r7 7/7 | injective renderer |
| RV6-D-A07 | runs against the revision-6 executor (history); four design rows it quotes are restated | ADM7 A07 | the planted record does not decide; mutant detected |
| RV6-D-A08 | cannot run (withdrawn schema) | CUR7 A08 | refused by age; RS-2 as stated |
| RV6-D-A09 | cannot run (withdrawn schema) | DA09r7 6/6 | 578 fields covered |
| RV6-D-A10 | runs; all four checks find the revision-7 text | crashmig7 | `init` never over an overlay |
| RV5-B-A01 | byte-identical (revision-5 executor) | FA7 | as above |
| RV5-B-A04 | byte-identical (CS5) | CS7 | as above |
| RV5-B-A05 | differs only in time-dependent archive digests | SRC6 byte-identical | source identity v2 unchanged |
| RV5-B-A08 | differs only in the image digest; verdicts equal | ENV7 | refused |
| RV5-B-A09, RV5-D-A01, RV5-D-A05 | byte-identical | CON6 byte-identical | unchanged |
| RV5-B-A12 | byte-identical (revision-5 model) | BA11r7 | as above |
| RV5-D-A03 | the pack-text check now finds RT-138 and GB-4′ restated | UW6 byte-identical | classes as stated |
| RV5-D-A04 | byte-identical | FA7 S4 | shared vectors refused |
| RV5-D-A07 | five defects now have plan rows | DA07r6 18/22 (below) | — |

**DA07r6 on the revision-7 plan (18/22).** Four review-r5 defects are "not detected" because DA07r6 matches revision-6 rows and
register ids that revision 7 restated. Their reference detection still holds, and each has a revision-7 row:
- RV5-M8: RT-138 restated in `12` §4f; register GB-4′.
- RV5-L2: RT-171 and RT-202; register GB-1″.
- RV5-L3: RT-178 and RT-189; register R-CLK-1.
- RV5-L4: the witness text removed by exclusion (EX-01); statements check S2.

## 9. Review r6 residual determinations under CP-1

| Residual (review r6 §6) | CP-1 |
|---|---|
| AD-1′/FC-R1, FC-R3, FC-R4, RS-B1 (not accepted) | replaced by FC-R1′ (exactly the CP-FC-ROOT sets; FC-R2′ and FC-R3′ inside it), CUR-R1 (`{win}`, 24 hours) and RS-2 (`{stored_old, clockback}`); FC-R4's media custody is no separate root (media carry the mirror's codes; OT-1) |
| FC-R2 (not accepted as stated) | FC-R2′ inside FC-R1′ (`op1src`); the bound no longer rests on a procedure printer (EX-24) |
| TB-S2′ under OP-16 (a), (b) (not accepted) | TB-S2″ from CP-ENV under OP-16 (b) with provenance classes; (a) and (c) excluded (EX-21) |
| AD-2 (condition RV6-M6) | AD-2′: the protected store is outside same-account reach (R-STORE-2; ADM7 A07) |
| TB-S1 environment (condition CD6-3) | R-BENV-7″ conflict refusal (ENV7 T1) |
| RA-1 (condition RV6-L1) | carried, RT-198 |
| TB-L4 (condition RV6-L5) | AP-R6 and GB-7 (CUR7 A04) |
| RS-5 (condition CD6-1 witness input) | removed by exclusion (EX-01) |
| RS-3, VR-3, TG-2 (condition CR4-B-01); CS-1 (CR4-B-05) | carried (RT-103, RT-138; RT-150) |
| RR-2, LR-2, LR-4 (conditions RV6-M3, M4, CR4-B-04) | RR-2′ (the local trust gate selects; OP-11 (b)); LR-2 triggers include a crash in the first install (CR6-C-7 (e)); PPR7; RT-146 |
| accepted residuals (TB-1′, VR-B1′, TB-S1, TB-S3, TB-4, TB-4′, AV-S1, RS-1, RS-1b, RS-1c, RS-2, RS-2b, RS-4, CS-2, DR-15, DR-33, VR-1, VR-2, VR-4, RR-1, RR-3, TG-1, TG-3, LR-1, LR-3, layout durability) | kept; RS-1 restated with the 90-day and 7-day anchors; OP-7 (d) excluded (EX-07) |

## 10. HO-0001 owner requirements

| Requirement | Where | Evidence |
|---|---|---|
| §3.1 constitutional-floor closure (review r6: SATISFIED; must not regress) | `34`, `23` §12, `19` E7 | CSI self-test 78/78 and checks 0/3/2/2/2 re-run; CON6 and P1r4 byte-identical; RV6-L1 carried (RT-198) |
| §3.2 new-machine trust bootstrap (NOT SATISFIED in revision 6) | `32`, `31`, `24`, `06`, `35` | FA7; CUR7; ADM7; BA11r7; residuals CUR-R1, RS-1, RS-2 stated with computed sets |
| §3.3 binary and root authenticity (NOT SATISFIED in revision 6) | `33`, `32`, `30`, `25`, `35` §5 | ENV7; FA7; BA12r7; CS7; TB-S2″ and TA-12″ stated; no certified target until CC-1…CC-9 hold (OT-2) |
| §3.4 legacy-binary damage containment (SATISFIED; must not regress) | `26`, `18` §9 | `matrix6` R2-H4 0 violations over 62,036 rows on both tree sets; `crashmig6`, `struct6`, `attrprec6` byte-identical, `gitops6` equal apart from the scratch prefix; crashmig7 5/5; P1r4 byte-identical |
| §4 forward compatibility | `34` §5, `23` §7.1 | RV6-D-A03 byte-identical: default deny and first-hand refusal; listing flag carried |

## 11. Owner-parameter conflicts (surfaced, not decided)

No owner parameter is reopened. `35` §6 states two conflicts, with options and consequences:
- **OT-1.** OP-13 (b)'s offline media channel versus OP-7 (a)'s 24-hour production freshness. CP-1 applies the 24-hour bound to
  media until the owner decides.
- **OT-2.** OP-10 (b)'s independently bootstrapped compiler agreement is not evidenced for the current compiler version. CC-3 is
  unmet, so no target is certified. There is no fallback to an upstream compiler archive (EX-15).

## 12. Unresolved, not yet executable, and disclosures

- **No implementation exists.** Every RT-184…RT-202 row and the extended rows need the implementation, as do the certified
  targets. `x86_64-unknown-linux-musl` and `aarch64-unknown-linux-musl` are NOT CERTIFIED pending CC-1…CC-9.
- **Models.** CS7's honest-party rules are this revision's specification. FA7, CUR7, ADM7 and PROF7 run the reference executor,
  not the product. ENV7 models supplier-class and toolchain-lineage provenance with synthetic components and one real
  `rustc 1.98.1`. No compiler was bootstrapped from source (OT-2). BA11r7, BA12r7, PPR7, DA05r7 and DA06r7 are computed.
- **Carried and unchanged:** RV6-L1 (the checker still lists by name list or optional flag), CR4-B-01, CR4-B-04, CR4-B-05,
  C-2…C-6, and the RV4 transaction parts.
- **Unmodified review probes.** Five cannot run because they open withdrawn artefacts: RV6-B-A01, B-A02, D-A05, D-A08, D-A09.
  Those that import revision-6 or revision-5 instruments reproduce history rows. Their CP-1 results are the re-expressions (§8).
- **Corrections made during the final evidence run.** Each was found by a run, fixed, and the affected instruments re-run in
  two passes.
  - The reference executor reported the first non-whitelisted key pair in set order. The refusal code was unchanged, but the
    output differed between runs; iteration is now sorted.
  - crashmig7 reused a fixed scratch directory; it now uses a fresh one per run.
  - DA09r7 counted a crashed register check as a detected mutation; it now requires a named failing check.
  - `statements_check.py` S2 skipped a brace set that mixed class phrases with unknown members; it now fails it. Found by the
    unmodified RV6-B-A03 re-run.
  - `19` §9's coverage sentence omitted `init`, and the overlay rule reused the id R-INIT-1 of `09`. It is now R-INIT-9 in `09`
    and `26`, and RT-195 names an existing overlay. Found by the unmodified RV6-D-A10 re-run.
  - `12` §4g was added so that every carried item has a named test.
- **Reviewer C's chain.** `build6` refused to overwrite an existing tree directory. `matrix6` and the other probes ran on the
  trees this run built earlier. `build6` was then re-run into a fresh directory from the final export, and `gitops6` and
  `matrix6` were re-run on those trees. The two tree sets differ only in build-time artefacts: Git object ids, a random
  `project_trust_id`, and file sizes that carry the scratch-path length. The pack inputs `build6` reads (`examples/rev2`,
  `rev3`, `rev6`) are unchanged since the base commit.
- **Independence.** Revision 7 was written by a fresh architect session (AR-0019) that authored no earlier revision, review or
  owner text. Orchestration files read: HO-0019, HO-0001, `AGENT_RUNS/README.md`, OWNER-DESIGN-REQUIREMENTS-0001 (`.md` and
  `.yaml`); the HANDOFFS directory listing (file names only) was seen. No other orchestration file was opened.
- **Scope disclosures.**
  - The harness persisted some of this session's own command outputs under a tool-results path in `~/.claude/projects/`. One
    background launch created a task output file. None was opened.
  - The host context included the user's auto-memory index; no memory file was opened.
  - Reviewer C's `register6.py` ran `git show` at the legacy release commits in this worktree (read-only).
  - No helper sessions. Nothing was written outside the allowed paths and the scratch root.
