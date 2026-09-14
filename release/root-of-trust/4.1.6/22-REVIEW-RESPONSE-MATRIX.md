# Output 22 — Response matrix to the independent review of revision 5

> **RoT-1 revision 6 — PROPOSED, pending fresh independent reviews; not approved, not implemented.**
> - **Review answered:** `release/root-of-trust/4.1.6-review-r5/` (synthesis `d1228cb`, AR-0014; panel B `248f12a`, C
>   `840d583`). It reviewed revision 5 (`cdb4e14`) and returned `ROOT_OF_TRUST_ARCHITECTURE_REJECTED`.
> - **Task:** HO-0015 (revision-6 architect, AR-0015).
> - **Scope:** RV5-H1 … RV5-I2; CR5-B-01 … CR5-B-12 and the carried CR4-B items; reviewer C's items (RV5-C-M1, M2, L1, L2, L3,
>   C-2 … C-6, the RV4 transaction parts); CD5-0 … CD5-4 and the §5 rule text; the §6 items; the §7 re-review entry criteria;
>   review r5's held-out attacks; HO-0001 §3–§4.
>
> This matrix claims **no finding as accepted or closed**; acceptance is the next reviewers' decision. Status vocabulary:
> - **ADDRESSED — executed:** real legacy binaries, real Git, the real Rust toolchain, real Ed25519 through OpenSSL, the
>   pack checker or the reference executor were run against the revision-6 rules.
> - **ADDRESSED — reference:** a model, oracle or calculator encoding the revision-6 rules was run, with mutants where named.
> - **ADDRESSED — specification only:** not executable before implementation; the RT is named.
> - **CARRIED — named test.**
> - **RESTATED:** text corrected from the revision-6 rules; nothing decided.
>
> No row is marked addressed on untested evidence. Where revision 6 uses a mechanism other than the correction delta's
> suggestion, the row says so.

## 1. Evidence produced for revision 6 (`evidence/r6/`)

Every run was scratch-only under `env -i`, with `GOV_*` stripped, `HOME` and `GOV_KERNEL_CACHE` in scratch, and legacy
binaries read-only. The final run was from a copy of the work-product tree; commands, digests, durations, exit codes and
determinism comparisons are in `evidence/r6/EVIDENCE-RUN-LOG-r6.json`.

| ID | Evidence | Kind | Result |
|---|---|---|---|
| **CS6** | `CS6-derivation-calculator.{py,json}`, `CS6-results.json.gz` | reference (derivation calculator; FD-3) | 1,648 configurations over seven goals (source, inputs, bytes, mirror, toolchain, **environment**, **constitutional content**) and eleven victim classes (P1, P2k1, P2k2, **WR**, **CIR**, **FA under seven OP-13 answers**, USE, ING_P1, ING_P2k1, ING_P2k2, ING_WR); exact minimal sets (transversal method, no size bound); **38/38 self-checks; 4,840 invariant checks, 0 failures; 104,340 monotonicity checks, 0 violations**; mutation analysis of all 27 rules (18 load-bearing in the model; the 9 others are defence in depth, each covered by a named scenario in the register); 91 revision-5-profile controls reproduce review r5's minima; 8 generated statements |
| **P4r6** | `P4r6-conformance-oracle.{py,json}` (loads P4r5 and P4r4 unmodified) | reference (conformance oracle) | **28/28** revision-6 scenarios; the **65 P4r5 scenarios** re-run under revision-6 rules: 65 refusals or controls preserved, 65 hold with unchanged expectations; **0 expected-`ACCEPTED` attack rows** (6 honest controls); RS-2b residual demonstration reported separately |
| **DA03r6** | `DA03r6-oracle-regression-sensitivity.{py,json}` | reference (mutation) | review r4 D-A03's 20 normative rules **20/20** (13/13 retained on P4r4; 7/7 re-expressed on `accept_binary_r6`); revision-5 rule mutants **17/17**; revision-6 rule mutants **18/18**; 0 crashes |
| **FA6** | `gov_admit_reference_r6.py`, `FA6-first-admission.{py,json}` | executed (real Ed25519 via OpenSSL CLI, `sha256sum`) | S1 FA5 on revision 6 unchanged: **45/45, 17/17, 26/27**; S2 first contact under all seven OP-13 answers (`32` §11); S3 **executed first-contact minima equal CS6 for 7/7 answers**; S4 shared vectors R1–R5 refused with **the same codes as P4r6 (5/5)**; S5 restrictor revocation, root threshold; S6 records; S7 **14/14 revision-6 rule mutants detected**; 63 OpenSSL verifications; two runs byte-identical |
| **CON6** | `CON6-first-hand-constitutional-content.{py,json}` | executed (pack checker as amended; real 4.1.5 consumer) and computed (P4r6) | **17/17 verdicts**: D-A01 part A (P4r6) and part B; D-A05 N3, N4, N2; B-A09; B-A10; `ASIA…` file excluded under the content revision 6 makes effective, indexed and served under the refused content (control) |
| **ENV6** | `ENV6-build-environment.{py,json}` (helper session, attributed) | executed (real Rust toolchain `rustc 1.98.1`, system C compiler) | **21/21 verdicts** over E0–E9; two runs bit-identical |
| **SRC6** | `SRC6-source-identity-v2.{py,json}` | executed (real Git) | **11/11 verdicts**; two runs byte-identical |
| **ADM6** | `ADM6-admission-transactions.{py,json}` | executed (reference executor) | **7/7 verdicts** (A08, A09, A09b, A10, A11 lock, A15, revision-5 mutant); the unlocked mutant's race count is reported, not asserted |
| **UW6** | `UW6-user-writable-install.{py,json}` | executed and computed | **4/4 verdicts**; the `31` §7.1 table equals the computed classes |
| **ATTR6** | `ATTR6-gitattributes-condition.{py,json}` | executed (real Git) | **3/3 verdicts**: member protects under RV5-C-M1's configurations; controls show the harm; `.git/info/attributes` overrides (stated condition) |
| **LAY6** | `LAY6/` (reviewer C's `matrix5`, `gitops5`, `build5`, `c5lib` copies with the revision-6 predicate and layout; helper session, attributed; real 4.1.2–4.1.5) | executed | 30,735 writing rows (285 skipped by the harness); **property R2-H4 0 violations**; LP-1r 1,335 rows, 0 violations; classification lost 0; Git operations leaving a written tree `COMPLETE` 0; LP-1s as restated 0 counterexamples over 540 rows (as stated in revision 5: 16); `AUTOCRLF`, `TEXTAUTO_EOLCRLF` `COMPLETE`; `GLOBALEXCL`, `INFOEXCL` `PARTIAL(occupation)` with the ignore source named by `git check-ignore` |
| **CSI6** | `CSI6-selftest.json`, `CSI6-CSI-check-*.json` | executed (checker) | self-test **78/78**, the **71 revision-5 cases identical**; payload checks exit 0/3/2/2/2, identical to revision 5 apart from the scratch path |
| **REG** | `decision-register/register_check.py` → `REGISTER-CHECK.json` | computed | **PASS**: 35 decisions; 107 rule ids of the scoped files all belong to a decision; 34 selectors each with a calculator strategy or bound; 80 restrictors each with a failing scenario; 27/27 CS6 rules referenced; every RT exists; the `29` table equals the YAML |
| **STMT** | `decision-register/statements_check.py` → `STATEMENTS-CHECK.json` | computed | **PASS**: 17 generated blocks equal the calculator output; no hand-written minimal set outside a block |
| **DA07r6** | `DA07r6-plan-regression-detection.{py,json}` | computed | RV5-D-A07 re-run: **22/22** review-r5 defects each have a plan row, a register row and a failing reference row (§7 criterion 2 (d)) |
| **EX6** | `examples/rev6/make_rev6.py`, `validation.json` | computed | every schema meta-valid; every revision-6 instance valid; every withdrawn revision-5 shape refused; root threshold 1 refused |
| **RERUN6** | `EVIDENCE-RUN-LOG-r6.json` comparisons | executed | the unchanged revision-5 instruments re-run from the work-product tree: **CS5, P4r5, DA03r5, FA5 (two runs), REG5 and P1r4 byte-identical** to their committed outputs |

**Helper sessions.** LAY6 and ENV6 were produced by helper sessions under this architect's specification, in this run's
scratch root. This architect reviewed their outputs and re-ran ENV6 in the final run.

## 2. Blocking classes

| Class | Findings | Revision-6 mechanism (removes the input) | Specified in | D-0008 rules | Evidence | Status |
|---|---|---|---|---|---|---|
| **BC5-1** first-contact root | RV5-H1 | **First-contact code and manifest.** One code per Trust State commits to lineage, state epoch and admitter digests. The operator procedure FC-1…FC-3 (platform tools) selects the evaluator through the code agreed across the OP-13 sources. The admitter enforces the **compiled quorum** (the Trust Policy may only raise it), lineage from the typed value, compiled lineage under (c)/(d), and **evaluator binding** (FC-4…FC-8). The **first-contact root** is stated with computed minima equal to the executed results. The owner options T1-a…T1-d are integrated as OP-13 (a)–(d), with combinations the architecture does not support stated. **Beyond CD5-1's list:** one code covers every first-contact value, so a single agreement rule enforces "every first-contact value" by construction. | `32`, `31`, `25` AP-1…AP-3, `06`, `21` OP-13 | (16), (19), (23), (25) | FA6 S2, S3, S7; CS6 FC-ROOT, FC-KEY-THEFT, FC-CONTENT; DR-02…DR-06 | ADDRESSED — executed (reference executor) and reference (calculator); implementation RT-156…RT-159 |
| **BC5-2** build environment | RV5-H2 | **Environments as registered inputs.** Components pinned to upstream signed checksums, checked by ceremony and verifiers. The environment tree is established by ≥ 2 first-hand environment reproductions; no pipeline record is an input; reproducers re-assemble; OP-16 (b) diversity is enforced at acceptance. The common-mode residual is owner option OP-16 (E-a…E-c), separate from OP-10. | `33`, `30` §2, §4.2, R-REG-3 (c′), R-VER-1, R-REP-2 | (9), (17), (26) | ENV6 E0–E9; CS6 G_ENV (INV-ENV, INV-ENV-B, INV-ENV-PIPELINE); DR-13 | ADDRESSED — executed (real toolchain) and reference; implementation RT-160…RT-162 |
| **BC5-3** first-hand content | RV5-H3 | **First-hand derivation and binding.** Custodians derive the constitution block from their own kernel build (R-CON-1, `verify-registration`). Attestations v4 name the reproduced kernel and count only for the registered candidate and kernel (R-CON-2). **E7 applies AP-5's restrictors** (R-CON-3). Reductions are computed at the verifier (R-CON-4), security-classified changes listed per project (R-CON-5), and the publisher applies E7's restrictors (R-PUB-1′). **Both of D-A01's mechanisms are adopted** (part A's candidate-bound restrictor and part B's first-hand registration). | `34`, `30`, `25` AP-4/AP-5, `19` E7, `23` §12 | (6), (9), (17), (24) | CON6; P4r6 section G; CSI S71–S77; CS6 G_CONTENT; DR-15, DR-16, DR-23, DR-26 | ADDRESSED — executed (checker, real 4.1.5) and reference; implementation RT-163…RT-167 |
| **BC5-4** register and statements | RV5-M5, D-A07, option statements | **Complete register as data.** `DECISION_REGISTER.yaml`, 35 decisions, including every omitted one (lineage, state, quorum, evaluator, re-admission, environment, verification binding, content derivation, restrictor revocation, release selection as a stated shortfall). **Calculator.** CS6 has a strategy per selector substitution and a rule per restrictor over eleven victim classes. **Generated statements.** Every consequence statement is a generated block. **Checks.** `register_check.py` (completeness over rule ids, calculator coverage, failing scenario per restrictor, RT existence, rendering) and `statements_check.py`. OP-1…OP-16 are restated with no proposals; `24` §9's proposal is removed. | `29`, `21`, `decision-register/`, `12` RT-127, RT-128, RT-183 | (22) | REG PASS; STMT PASS; CS6; DA07r6 | ADDRESSED — reference; RT-127, RT-128, RT-183 |

## 3. Findings RV5-H1 … RV5-I2

| Finding | Revision-6 change | File | Evidence | Status |
|---|---|---|---|---|
| **RV5-H1** | BC5-1 (§2). Contradicted statements restated from CS6: `30` §10 FA rows (replaced by generated blocks); `25` §7 row; `05` §3 table (superseded, FC-ROOT block); `21` OP-9, OP-12, OP-13 and combinations; `31` §9 AD-1 → AD-1′; CS5 H-CH → CS6 `fc_lineage_sub`, `fc_eval_sub`; the executor's bundle-order lineage and one-channel admitter comparison. | `32`, `31`, `25`, `30`, `05`, `21`, `06`, `01` | FA6 S2 (A01a/b/c, A01c′, D-A02, ORD, evaluator rows) and S3 (7/7 equal); S7 mutants `quorum_from_selected_state`, `lineage_from_bundle_order`, `skip_evaluator_binding`, `skip_compiled_lineage`, `skip_fcm_*` detected | ADDRESSED — executed; RT-156…RT-159 |
| **RV5-H2** | BC5-2 (§2). CS5 G_INPUTS claim, `30` §10 and `05` §3 inputs row, `25` §8, `21` OP-10 and TB-S2/TA-12 restated; TA-12′ and TB-S2′ added. | `33`, `30`, `05`, `25`, `21`, `01` | ENV6 E1 (revision-5 shape refused), E2, E3, E5, E8a, E9 refused; E4, E6, E8b accepted as stated residuals; CS6 G_ENV | ADDRESSED — executed; RT-160…RT-162 |
| **RV5-H3** | BC5-3 (§2). `05` §1 `release-final` and `release-registration` rows, `21` OP-2, OP-4, OP-8, `23` CS-2, `00` summary and rule (17) restated. | `34`, `05`, `21`, `23`, `15` | CON6 part B (ceremony exit 3 on the CI-derived proposal; E7 exit 3 on the attacker kernel; genuine 0; `ASIA…` excluded); P4r6 G (attacker candidate and final, variant registration, OP-4 "no", B-A06, REJECTED, candidate not held); D-A05 N3/N4 | ADDRESSED — executed; RT-163…RT-167 |
| **RV5-M1** | CR5-B-01: AP-5r and R-REP-5′; R-REG-11 registration revocation is the only removal of a restrictor; `05` §1 `revocation` and `trust-state` rows; CS6 rule `V_REVOCATION_AUTHORITY`. | `25`, `30`, `05` | P4r6 `R6-AP5r_*` (3 rows); FA6 S5 (A03 with trust-state revocation still `REPRODUCTION_CONFLICT`; registration revocation remedy accepted); DA03r6 two mutants; CS6 mutation (18 configurations lose `transport` without the rule) | ADDRESSED — reference and executed; RT-168 |
| **RV5-M2** | CR5-B-04 (a)–(c): R-CON-4, R-CON-5; rule (6) restated. | `34`, `23` §12.4, `15`, `19` | CSI S73, S74, S75, S76 (tool registry now security-classified); CON6 B-A09 exit 8 ×2, B-A10 exit 6 and 7 | ADDRESSED — executed; RT-141, RT-166, RT-167 |
| **RV5-M3** | CR5-B-03, RV5-C-L3: R-ADM-8′ (first admission defined; re-admission keeps the store); R-ADM-7′ (one record per binary in the store); R-ADM-13 (lock); OP-14 (b), OP-15 (a) state the re-admission path. | `31`, `21`, `20` | ADM6 A08, A09, A09b, A10, A11; FA6 S6; revision-5 mutant detected | ADDRESSED — executed; RT-139 (revised), RT-170, RT-181 |
| **RV5-M4** | Source identity v2 (length-prefixed records, control characters refused, Git tree id also registered); SRC5 replaced by SRC6. | `30` §4.1, `07`, `05` §11, schemas | SRC6 T1 (B-A05 construction refused; encoding distinguishes); T2, T3; T4 identical across two clones; two runs byte-identical | ADDRESSED — executed; RT-172 |
| **RV5-M5** | CR5-B-05: complete register (BC5-4). | `29`, `decision-register/` | REG PASS; DA07r6 | ADDRESSED — reference; RT-128, RT-183 |
| **RV5-M6** | RV5-C-M1: `governance/trust/.gitattributes` (`* -text`) is a member of the trust top-level entry set. Stated condition: `.git/info/attributes` overrides; fail closed; doctor names it. | `18` §9.1, `26` §2, `08` | LAY6 `AUTOCRLF`, `TEXTAUTO_EOLCRLF` `COMPLETE`; ATTR6 C1, C2, C2b protected, O1–O4 override, K1/K2 controls | ADDRESSED — executed (reference layout); RT-50, RT-122, RT-173 |
| **RV5-M7** | RV5-C-M2: condition stated (no active ignore source may match `.governance-runtime/`); doctor D033 names the source via `git check-ignore --no-index -v`. | `26` §8, `09`, `13` | LAY6 `GLOBALEXCL`, `INFOEXCL` `PARTIAL(occupation)`; check-ignore rows name `excludesFile:1` and `.git/info/exclude:7` | ADDRESSED — executed (condition and detection source); RT-174 |
| **RV5-M8** | **Option (a) chosen by the architect** (a restatement; no rule change). A user-writable installation reaches C0 under OP-7 (a), (b) and (c) without witnesses, and C0–C2 under (c) with witnesses and under (d). The burden (administrator-protected installation or system pin) is stated in OP-7 and Phase 4; RT-138 corrected. | `31` GB-4′, §7.1; `24` §4.2; `21` OP-7; `11`; `12` RT-138 | UW6 (D-A03 re-run on revision 6): 6/6 stated rows equal computed; ceremonies and C3 refused; Phase 4 C3 refused | RESTATED and ADDRESSED — executed; RT-138 |
| **RV5-M9** | Shared vectors R1–R5 (R5: attestation for the registered candidate with another kernel) plus the floor control in both executors (R-ADM-14). AP-4 adds the registration's revocation and fails closed without a binary version when the floor is set. AP-5 binds to the registered candidate and kernel. | `25`, `31` | FA6 S4 (bootstrap executor): R1 `BINARY_REVOKED`, R2 `BINARY_REVOKED`, R3 `VERIFICATION_RECORDS_BELOW_MINIMUM`, R4 `BINARY_BELOW_TRUST_POLICY`, R5 `VERIFICATION_RECORDS_BELOW_MINIMUM`, each equal to P4r6 | ADDRESSED — executed and reference; RT-165, RT-169 |
| RV5-L1 | CR5-B-06: FC-6, lineage from the typed value. | `32`, `25` AP-2 | FA6 ORD-1…ORD-3 `ACCEPTED`; mutant `lineage_from_bundle_order` detected | ADDRESSED — executed; RT-158 |
| RV5-L2 | CR5-B-07: GB-1′, records honoured only inside the store. | `31` | FA6 S6 shipped record `BINARY_NOT_ADMITTED` (revision-5 mutant `ALLOWED`); ADM6 A15 | ADDRESSED — executed; RT-171 |
| RV5-L3 | CR5-B-08: statements refused as issued in the future disable clock-based proofs; `24` §5.3, §5.7 state TA-7; RS-2b added. | `24`, `17`, `01` | P4r6 `R6-CLOCK-*` (C3 refused); DA03r6 `R6-clock-future`; residual demonstration RS-2b | ADDRESSED — reference; RT-148, RT-178 |
| RV5-L4 | CR5-B-09: witness-only clock text removed from `24` §8, §10 RS-2, `17` header, S11 and §13, `01` TA-7 and G23, `02` I-68; `24` §3.5 (3) allow list; `24` §5 parameters are examples, not proposals; `24` §9 proposal removed. D extension: `07` §3 source identity v2 with `inputs_manifest_digest`; revision-4 artefact and build-attestation rows marked withdrawn; `04` V8. | `24`, `17`, `01`, `02`, `07`, `04` | text; STMT PASS | RESTATED; RT-127 |
| RV5-L5 | CR5-B-10: CS6 enumerates WR and CIR (and FA per OP-13); `25` §7 states its claim over the enumerated classes. | `29`, `25` §7, `30` §10 | CS6 victim classes (11); INV-ONE 0 failures; OP-9-BYTES block rows WR, CIR | ADDRESSED — reference; RT-131 |
| RV5-L6 | CR5-B-11: KS-14; OP-1 states the minimum. | `05` §3, `21` OP-1, schemas | P4r6 `R6-KS14_root_threshold_1` `ROOT_VERSION_INVALID`; FA6 S5 root v1 threshold 1 `ROOT_CHAIN_INVALID` (both codes stated in `25` AP-2); DA03r6 `R6-ks14`; EX6 root purpose threshold 1 refused | ADDRESSED — reference, executed; RT-132, RT-177 |
| RV5-L7 | RV5-C-L1: LP-1s restated to what holds; rule (12) restated; doctor names the stray trees. | `26` §4, `15`, D-0008 | LAY6 LP-1s restated 0 counterexamples over 540 rows (as stated in revision 5: 16) | RESTATED and ADDRESSED — executed; RT-176 |
| RV5-L8 | RV5-C-L2: RoT-1 cwd refusal extended to the transaction area; the containment of legacy litter there rests on the VTS registration gate (`18` §5.1) and doctor; rule (10) restated. | `18` §9.2, `15`, D-0008 | LAY6 96 transaction-area rows (reported, inert) | RESTATED; ADDRESSED — specification only (the refusal); RT-175 |
| RV5-L9 | OP-3 mode B states the per-update currency proof. | `21` OP-3, `27` | P4r6 `R6-OP3-B-*` (refused without a proof naming t12; proceeds with it); DA03r6 `R6-mode-B-currency` | RESTATED and ADDRESSED — reference; RT-179 |
| RV5-I1 | unchanged: the acting role remains caller-declared; no trust gate depends on it. | `27` §5 | — | INFO — stated |
| RV5-I2 | Carried to the capability-contract phase: derived members of a binding group recomputed by `gov` or confirmed with the derivation shown. | `34` §5, `12` RT-182 | — | CARRIED — named test RT-182 |

## 4. Carried requirements CR5-B-01 … CR5-B-12 (reviewer B `04`) and CR4-B items

| CR | From | Specified in | Test → evidence | Status |
|---|---|---|---|---|
| CR5-B-01 | M1 | `25` AP-5r, `30` R-REG-11, R-REP-5′ | (i) RV5-B-A03 on the bootstrap executor → FA6 S5 `REPRODUCTION_CONFLICT`; on running mode → P4r6 `R6-AP5r_trust_state_revocation_does_not_clear_conflict`. (ii) REJECTED → P4r6 `…_REJECTED` `ARTIFACT_SOURCE_REJECTED`. (iii) CS6 rule `V_REVOCATION_AUTHORITY` load-bearing: with it off, 18 configurations gain sets without `transport`. RT-168, RT-131. | reference and executed |
| CR5-B-02 | H1 | `32` §9, `05` §7, `06` §2 | RT-180 (`draft-policy` flag) | specification only |
| CR5-B-03 | M3 | `31` R-ADM-8′, R-ADM-7′, `21` OP-14, OP-15 | (i), (ii) RT-170 (FA6 S6 and ADM6 A09 show the store and per-project records kept); (iii) ADM6 A09b, RT-139 | executed (reference executor) |
| CR5-B-04 | M2 | `34` R-CON-4, R-CON-5; `23` §12.4 | (i) CON6 B-A10 exit 6, exit 7; (ii) CON6 B-A09 exit 8; (iii) RT-141 wording revised | executed |
| CR5-B-05 | M5 | `29`, `decision-register/` | REG PASS (C4: a failing scenario per restrictor); RT-128 | reference |
| CR5-B-06 | L1 | `32` FC-6 | FA6 ORD rows; RT-158 | executed |
| CR5-B-07 | L2 | `31` GB-1′ | FA6 S6; ADM6 A15; RT-171 | executed |
| CR5-B-08 | L3 | `24` §8, §5.3, §5.7, §10 | P4r6 `R6-CLOCK-*`; RT-178 | reference |
| CR5-B-09 | L4 | `24`, `17`, `01`, `02` | text; RT-127 | restated |
| CR5-B-10 | L5 | `29` §5.3, `25` §7 | CS6 WR, CIR; RT-131 | reference |
| CR5-B-11 | L6 | `05` §3 KS-14 | P4r6, FA6 S5, DA03r6; RT-177 | reference and executed |
| CR5-B-12 | RS-4 | `31` GB-6, `06` §3 | FA6 S6 `euid 0 → not protected`; RT-171 | executed (predicate) |
| CR4-B-01, CR4-B-02, CR4-B-04, CR4-B-05 | review r4 | as revision 5 | as review r4 B (RT-103, RT-149, RT-146, RT-150) | CARRIED — specification only |

**B's acceptance cases for the blocking findings** (B `04` last table):
- **H1 (a).** A01a/b/c are refused outside the stated root.
- **H1 (b).** A substituted evaluator is stopped by FC-1…FC-3 and a genuine unlisted or revoked admitter refuses itself.
- **H1 (c).** The calculator's FA minima equal the executed results (FA6 S2, S3).
- **H2 (a), (b).** An environment substitution is refused or conflicts, and the G_ENV sets contain the registration threshold
  with verification, a q-reproducer compromise, or the OP-16 residual atom (ENV6; CS6 INV-ENV).
- **H3 (a).** E7 refuses (CON6, P4r6).
- **H3 (b).** The variant regex is listed and gated on recorded machines (CON6 B-A09).

## 5. Reviewer C's items (review r5 C `04`)

| Item | Where | Test | Evidence | Status |
|---|---|---|---|---|
| RV5-C-M1 | `26` §2, `18` §9.1, `08` §2 | RT-50, RT-122, RT-173 | LAY6 gitops; ATTR6 | ADDRESSED — executed (reference layout) |
| RV5-C-M2 | `26` §8, `13` | RT-122, RT-145, RT-174 | LAY6 check-ignore rows | ADDRESSED — executed (condition, detection source) |
| RV5-C-L1 | `26` §4, rule (12) | RT-176 | LAY6 LP-1s restated | RESTATED; executed |
| RV5-C-L2 | `18` §9.2, rule (10) | RT-175 | LAY6 transaction-area rows | RESTATED; specification only |
| RV5-C-L3 | `31` R-ADM-8′, R-ADM-7′ | RT-139, RT-170 | ADM6 A09, A10 | ADDRESSED — executed |
| C-2 … C-6 | `18` §3, §9; `20` §8 | RT-123, RT-124, RT-125, RT-50, RT-155 | — | CARRIED — specification only |
| RV4-M2 (tx part), RV4-M5 (tx part) | `18` §5.1; `19` §9 | RT-103, RT-146 | — | CARRIED — specification only |
| RV5-C-A11 (concurrent admissions; listed by C as spec-only) | `31` R-ADM-13 | RT-181 | ADM6 A11 | ADDRESSED — executed (reference executor) |

## 6. Correction delta CD5-0 … CD5-4 and the §5 rule text

| Item | Applied as | Different mechanism? |
|---|---|---|
| **CD5-0 retain** | Retained: BC4-1, BC4-2 and BC4-3 closures as stated; carried closures; legacy containment. **Non-regression:** CS5, P4r5, DA03r5, FA5 (×2), REG5 and P1r4 re-run byte-identical from the work-product tree; the P4r5 scenarios hold under revision-6 rules (65/65); FA5 unchanged on the revision-6 executor (45/17/26); CSI 71 revision-5 cases identical; reviewer C's matrix R2-H4 0 violations. | none |
| CD5-1 | `32`, `31`, `25`, `06`, `21` | enforcement as proposed (compiled quorum, evaluator binding, lineage from the typed value, exact residual, register rows). **Also:** a single first-contact code over a manifest, so the quorum applies to every first-contact value at once. |
| CD5-2 | `33`, `30`, `21` OP-16 | as proposed (first-hand environment, named authority, calculator atoms and goal, substitution test); OP-16 is numbered next to OP-10 rather than merged, because the answers are independent (`21` §0) |
| CD5-3 | `34`, `30`, `25`, `19`, `23` | both mechanisms of D-A01 adopted: first-hand content and candidate-bound verification; E7 restrictors; verifier reductions; calculator policy-root goal |
| CD5-4 | `29`, `21`, `decision-register/`, `12` | as proposed; plus the register and statement checks as pack instruments |
| §5 rules | `15` §5, D-0008 | (6), (9), (16), (17), (19), (22), (23), (24), (10), (12) revised as §5 lists; also (7) (clock), and (25)–(27) added |

## 7. Review r5 §7 re-review entry criteria

| Criterion | State |
|---|---|
| **1.** CD5-1 … CD5-4 closed as classes in pack, schemas, D-0008, ARCH-0002; both PROPOSED | §2; **schemas:** `first-contact-manifest`, `environment-manifest`, `environment-reproduction` and `registration-revocation` added; `release-registration` v2, `input-manifest` v2, `verification-attestation` v4, `binary-reproduction` v2, `admission-record` v2, `trust-root` (KS-14), `trust-policy-statement` and `trust-base-manifest` revised; EX6 validation. D-0008 and ARCH-0002 are revision 6, PROVISIONAL, `in_effect: false`, no `chosen_option`, proposal state PROPOSED. |
| **2a.** RV5-B-A01 (A01a/b/c, A02, ORD), RV5-D-A02 on the corrected admitter; B-A04 part L with lineage and evaluator substitution | FA6 S2 across 7 OP-13 answers: every attack refused outside the stated root (under (b): one-page lineage `FIRST_CONTACT_DISAGREEMENT`, one value `CHANNEL_QUORUM_NOT_MET`, one-page evaluator `FIRST_CONTACT_DISAGREEMENT`; under (c) all: `FIRST_CONTACT_LINEAGE_NOT_COMPILED`, `PLATFORM_SIGNATURE_INVALID`); ORD 3/3 `ACCEPTED`; evaluator rows 3/3 refused; FA6 S3 part L: executed minima equal CS6 root sets for **7/7** answers |
| **2b.** RV5-B-A08 against the corrected ceremony and reproducer rules; B-A04 part I with environment atoms | ENV6 21/21 (substituted component `ENVIRONMENT_COMPONENT_UNVERIFIED`; pipeline image `ENVIRONMENT_NOT_REPRODUCED`; carrier `INPUT_DIGEST_MISMATCH`; class A compromised under (b) `REPRODUCTION_CONFLICT`); CS6 G_ENV: INV-ENV, INV-ENV-B, INV-ENV-PIPELINE 0 failures; revision-5 profile reproduces review r5's G_IMAGE sets |
| **2c.** RV5-D-A01 parts A and B, RV5-D-A05 N3, RV5-B-A06 and RV5-B-A09 against the corrected registration and E7 | CON6 17/17: part A 6/6 (P4r6 G), part B ceremony 3 and 0, E7 3 and 0, `ASIA…` excluded; N3 3, N4 3, N2 0; B-A06 `verification_records_below_minimum`, and every OP-2 (b) content set contains OP-8 verification compromises (CS6 INV-CONTENT); B-A09 variant and tool command exit 8 |
| **2d.** RV5-D-A04 against the next reference executor and oracle; RV5-D-A07 against the next plan | FA6 S4: R1–R5 refused in the bootstrap executor with codes equal to P4r6 (5/5); both vector sets contain the rows (R-ADM-14). DA07r6: 22/22 review-r5 defects each have a plan row, a register row and a failing reference row |
| **2e.** Unchanged in what they refuse | CS5 self-checks 21/21 (output byte-identical); P4r5 65/65 and 42/42 (byte-identical; and 65/65 under revision-6 rules); DA03r5 20/20, 17/17 (byte-identical); FA5 45/45 (byte-identical, two runs); REG5 (byte-identical); CSI self-test 71/71 cases identical (78/78 in total); P1r4 on real 4.1.5 (byte-identical); reviewer C's `matrix5` on the revision-6 layout: R2-H4 0 violations over 30,735 rows |
| **3.** Response matrix over RV5-H1 … RV5-I2, CR5-B-01 … CR5-B-12, C's items, CD5-0 … CD5-4, with no untested "resolved" | §3–§6; specification-only rows are labelled |
| **4.** Owner options T1-a … T1-d and E-a … E-c presented with computed consequences, no choice made | `21` OP-13 and OP-16 with generated blocks FC-ROOT, FC-KEY-THEFT, FC-CONTENT, OP-16-ENV; mapping table `21` §0; no proposal, recommendation or default; unsupported combinations stated (`21` §17) |

## 8. Review r5 held-out attacks re-run against revision 6

| Attack | How re-run | Result on revision 6 |
|---|---|---|
| RV5-B-A01 A01a/b/c; B-A02; D-A02 | FA6 S2 (attacker lineage world after B-A01's `lineage_world`) | refused outside the stated root under every OP-13 answer; admitted only inside the root (`32` §11) |
| RV5-B-A03, A07 | FA6 S5; P4r6 AP5r; CS6 mutation | conflict and REJECTED kept; `transport` needed without the registration authority |
| RV5-B-A04 parts L, I, P, R, C | CS6 (strategies for lineage, evaluator, environment, content, restrictor revocation; victim classes WR, CIR) | invariants hold; revision-5 profile reproduces review r5's sets |
| RV5-B-A05 | SRC6 T1 | `SOURCE_PATH_REFUSED`; encodings differ |
| RV5-B-A06 | P4r6 `R6-E7-B-A06_*`; CS6 INV-CONTENT | ineligible; every OP-2 (b) set contains OP-8 verification |
| RV5-B-A08 | ENV6 | refused or conflict; residuals only as stated |
| RV5-B-A09, A10 | CON6 | listed (exit 8); reversion 6; withheld 7 |
| RV5-B-A11 | CSI (S01–S03 unchanged) | exit 2 |
| RV5-B-A12 | P4r6 `R6-CLOCK-*` (M3 CLOCK-back); UW6 (M8) | C3 refused; classes as stated |
| RV5-B-A13 | ADM6 A09, FA6 S6 | store kept |
| RV5-B-A14 | FA6 ORD | order-independent |
| RV5-B-A15 | FA6 S6; ADM6 A15 | `BINARY_NOT_ADMITTED` |
| RV5-B-A16 | CSI S60 (tunable leaf under the kernel tree digest) | exit 3 |
| RV5-B-A17 | `register_check.py` | PASS (every omitted decision present) |
| RV5-B-A18 | P4r6 KS14; FA6 S5 | refused |
| RV5-B-A19 | CS6 victim classes | 11 classes enumerated |
| RV5-C-A01, A02, A13 | LAY6 matrix | R2-H4 0 violations; nested installs reported |
| RV5-C-A03 | LAY6 transaction-area rows | reported, inert; RoT-1 refusal specified (RT-175) |
| RV5-C-A04 | LAY6 LP-1s | 0 counterexamples as restated |
| RV5-C-A05, A06 | LAY6 gitops; ATTR6 | `COMPLETE` under RV5-C-M1 configurations; stated conditions fail closed with sources named |
| RV5-C-A07, A12 | LAY6 gitops (sparse, shallow, partial clone, checkout rows) | as revision 5 (`PARTIAL` or `LEGACY` where the occupation is absent) |
| RV5-C-A08…A11 | ADM6 | fail closed; store kept; record kept; lock |
| RV5-D-A01 | CON6 parts A and B | refused; genuine eligible; `ASIA…` excluded |
| RV5-D-A03 | UW6 | restated table equals computed |
| RV5-D-A04 | FA6 S4 | same codes in both executors |
| RV5-D-A05 | CON6 N2–N4 | N3 and N4 refused; N2 eligible |
| RV5-D-A06 | `21` §17 combinations; P4r6 mode B rows | combinations stated from the rules and calculator blocks |
| RV5-D-A07 | DA07r6 | every defect detected by plan, register and reference |
| RV5-D-A08 | `28` §9–§10; the class interactions above | each interaction bounded by a named row |

## 9. HO-0001 owner requirements

| Requirement | Where | Evidence |
|---|---|---|
| §3.1 constitutional-floor closure (review r5: NOT SATISFIED on sensitivity/indexing and tool floors via content selection) | `34`, `23` §12, `19` E7 | CON6 (`ASIA…` excluded on 4.1.5; tool command listed); CSI S71–S77 |
| §3.2 new-machine trust bootstrap (NOT SATISFIED on first install; RV5-M8) | `32`, `31`, `24`, `06` | FA6 S2, S3; UW6; P4r6 CLOCK |
| §3.3 binary and root authenticity (NOT SATISFIED on the build environment and first contact) | `33`, `32`, `30`, `25` | ENV6; FA6; CS6 |
| §3.4 legacy-binary damage containment (SATISFIED; must not regress) | `26`, `18` §9 | LAY6: R2-H4 0 violations; P1r4 byte-identical |
| §4 forward compatibility (content of new kernel-shipped files at the right authority) | `34` §5, `23` §7.1 | CON6 N2–N4 |

## 10. Unresolved, not yet executable, and scope disclosures

- **No implementation exists.** Every RT-128…RT-183 needs the implementation. That includes `gov-admit` with the first-contact
  rules, environment reproduction tooling, `draft-registration` with first-hand content, the compiled register, confinement
  on real platforms, root-owned install locations, cross-OS reproducibility, CR4-B-02, CR4-B-04, CR4-B-05, CR5-B-02 and
  C-2…C-6.
- **Models.** CS6's honest-party rules are this revision's specification (`30` §9); a real process that deviates changes the
  sets. P4r6, FA6, the reference executor, CON6's ceremony function and ENV6's assembly model are reference instruments, not
  the product.
- **ENV6** builds with a single-file Rust program and synthetic distribution components. Cross-distribution reproducibility
  of the real `gov` build under OP-16 (b) is not shown (RK-49, IR-REP-3).
- **Owner decisions pending:** OP-1…OP-16 (`21`); none proposed; no default.
- **Independence.** Revision 6 was written by a fresh architect session (AR-0015) that authored no earlier revision, review
  or specialist proposal.
- **Scope disclosures.**
  - Two helper sessions (LAY6, ENV6) worked in this run's scratch root under this architect's specification; their outputs
    are attributed.
  - One scratch file was first written one directory above this run's scratch root and moved into it; nothing else was
    written outside the allowed paths.
