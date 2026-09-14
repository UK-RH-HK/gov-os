# 02 — Held-out attack register RV6-B-A01 … A16 (review r6 B)

This review (AR-0016) authored these attacks. None of them is:
- an acceptance case of `12-ACCEPTANCE-TEST-PLAN.md` (§4d RT-156…RT-183, §7d);
- an architect self-attack (`28` §10 A-R6-01…15);
- an attack of reviews r2, r3, r4 or r5.

For each attack the nearest existing case is named, with the reason it does not cover the attack.

## Evidence classes

| Class | Meaning |
|---|---|
| **E** | Executed: the reference executor `evidence/r6/gov_admit_reference_r6.py` (unmodified, real Ed25519 through OpenSSL, `sha256sum`), the pack checker (unmodified), the real Rust toolchain and system C compiler |
| **C** | Computed: CS6 or P4r6 loaded unmodified (functions wrapped, originals called), or a brute-force search over CS6's acceptance function |
| **D** | Design or code reading at `4106885` |

## Register

| ID | Attack | Adversary | Expected secure outcome | Revision 6 as written | Class, evidence | Nearest case (why not covered) | Finding |
|---|---|---|---|---|---|---|---|
| **RV6-B-A01** | **Publisher-composed first-contact code.** The process that signs Trust States and emits their first-contact manifests (`07` §7 step 15) emits a manifest naming either a substituted `gov-admit` (genuine lineage and state), or an attacker lineage with the genuine admitter. Every designated source is honest and republishes the code it is given. All seven OP-13 answers. | trust-state publisher process (rank 3); no other key | Refused before an evaluator runs, or the composer is a stated first-contact root atom | Substituted evaluator admitted under (a), (b), (c) either k=1/2, (d); attacker lineage `ACCEPTED` under (a), (b); (c) "all" `PLATFORM_SIGNATURE_INVALID`. Controls: honest `ACCEPTED`; one compromised source under k=2 `FIRST_CONTACT_DISAGREEMENT` | E: `outputs/RV6-B-A01-first-contact-selectors.json` part P; C: part C (with `fcpub`, sets outside the declared root under every answer except (d) with first-hand media) | RT-156, FA6 S2 (a source compromised; the publisher always honest); RT-159 (compares the implementation's calculator with the same model); RT-180 (custody of sources, not who composes the value) | **H1** |
| **RV6-B-A02** | **Who authors the environment manifest?** A CS6 strategy for a pipeline-authored manifest (components genuine, recipe common to every class), plus a design search for the manifest author, recipe constraints, upstream-key pinning and supplier-class establishment. | pipeline (unassigned author) | G_ENV minimal sets without {pipeline}; INV-ENV-PIPELINE holds | {pipeline} minimal under OP-16 (a) and (b) for n2q2 and n3q2; INV-ENV, INV-ENV-PIPELINE and INV-ONE fail; (c) unaffected; control unmodified: 0 failures. Design: none of the four found | C, D: `outputs/RV6-B-A02-environment-manifest-author.json` `computed`, `design` | RT-162 (invariants on the implementation's model, which has the same two strategies); CS6 `E_pipe`, `E_sub` | **H3** |
| **RV6-B-A03** | **Generated statement rendering.** Compare the atoms behind the generated CONTENT block with its text; run `statements_check.py` with the same text written outside a block. | — (statement honesty) | The printed sets name the calculator's atoms | `repo` prints as "1 reproducer key" in 8 of 24 CONTENT rows (`21`, `34`). 120 G_CONTENT sets hold `repo`; 0 hold a reproducer atom. S1 passes the block; S2 rejects the same text outside a block and accepts `repo` | C + E: `outputs/RV6-B-A03-generated-statement-rendering.json` | RT-127, RT-183 (S1 compares rendering with rendering) | **M2** |
| **RV6-B-A04** | **Re-admission below the kept high-water.** After `ADMISSION_RECORD_EXPIRED`, re-admission with the current genuine code. A carrier supplies an older genuine, published, unrevoked binary B8 whose TBM is below the store's accepted-TBM high-water. | carrier + operator re-admission (OP-14 (b)) | `BINARY_T0_ROLLBACK` (as in running mode) | `ACCEPTED`; store kept with the high-water above B8; B8 runs C2 `ALLOWED`; running-mode row `RV3-D-A13r5` gives `BINARY_T0_ROLLBACK` | E: `outputs/RV6-B-A04-readmission-rollback.json` | RT-170 (E10 downgrade only); ADM6 A09 (checks files are kept, not applied); P4r5/P4r6 `RV3-D-A13r5` (running mode) | **M1** |
| **RV6-B-A05** | **Replay of an old genuine platform-signed package** under OP-13 (c) "either suffices". The package's manifest is T7's, with no `valid_until`. Candidate B7 (genuine) or B7x (malicious); both revoked at T9. | carrier (transport, mirror, archive) | Refused (`FIRST_CONTACT_MANIFEST_EXPIRED`) or bounded by a mandatory window | B7 `ACCEPTED`; B7x `ACCEPTED`. Controls: expired `valid_until` refused; current code refuses | E: part R | RT-156 "(c) the signing path compromised alone"; FA6 S2/S3 `c_either_*` (platform-only branch passes the current genuine manifest); FA5 CH1 (a stale owner page) | **H2** |
| **RV6-B-A06** | **Package submitter** under OP-13 (c). The honest signing service signs a substituted admitter with the genuine compiled lineage, submitted by the release pipeline. | pipeline / developer-account holder | Refused unless the package equals a root-signed admitter digest | (c) either k=1/2: procedure `OK`, substituted evaluator admits; (c) "all" control `ADMITTER_DIGEST_MISMATCH` | E: part S; D: no rule names the submitter | RT-156 (signing path compromised); FA6 `attempt()` (`signed = (adm == ADM_BYTES) or ("alt" in caps)`) | **H2** |
| **RV6-B-A07** | **Environment recipe and component selection.** (a) The recipe adds an inline wrapper and object; every component upstream-signed, keys pinned. (b) Placement only: the upstream's genuinely signed instrumented wrapper and runtime object are selected. (c) OP-16 (b) with both classes' manifests carrying the same author's recipe. | manifest author | Refused before registration, or conflict | (a) `REGISTERED`, bit-identical, injected, `ACCEPTED`; (b) `REGISTERED`, bytes differ from control, `ACCEPTED`; (c) both `REGISTERED`, injected in both classes, `ACCEPTED`. Control: honest recipes with class A compromised → `REPRODUCTION_CONFLICT` | E: `outputs/RV6-B-A02-environment-manifest-author.json` A07a/b/c (real `rustc 1.98.1`) | RT-160, RT-161; ENV6 E0–E9 (recipe is a digest of the component path list) | **H3** |
| **RV6-B-A08** | **Supplier class by label** under OP-16 (b): two environments built only from one (compromised) upstream, labelled A and B. | environment supplier A + manifest author | `ENVIRONMENT_DIVERSITY_NOT_MET` | Both `REGISTERED`; `ACCEPTED`, injected. Control: class B bound to a pinned distB key → `ENVIRONMENT_COMPONENT_UNVERIFIED` | E: A08; C: `supplier_class_by_label` (INV-ENV-B fails) | RT-161 (honest labels); ENV6 `op16b` counts labels | **H3** |
| **RV6-B-A09** | **Upstream checksum key named by the manifest.** The author's own key signs SHA256SUMS for injecting components; `upstream_checksum_reference` names it. | manifest author | `ENVIRONMENT_COMPONENT_UNVERIFIED` | Key from the reference: `REGISTERED`, `ACCEPTED`, injected. Pinned-key control: `ENVIRONMENT_COMPONENT_UNVERIFIED` | E: A09; D: no pinning rule | ENV6 E2 (the harness hands `cer()` the supplier's real key) | **H3** |
| **RV6-B-A10** | **Surface classes on the revision-6 checker.** Kernels changing only `COMMAND_CONTRACT.yaml`, `overlay-templates/TOOL_PERMISSIONS.yaml` (research-agent gains `SECRET_READ`) or taxonomy; SECURITY_POLICY control; `verify-registration` of each against the custodian's own genuine build; an unknown key; a new constitutional file. | registration authority; pipeline proposal | Non-first-hand proposals refused; security-relevant changes listed; default deny | `verify-registration` exit 3 for every changed proposal, 0 for genuine; `registration-changes` exit 0 for K1–K3, 8 for the control; unknown key and new file exit 2 | E: `outputs/RV6-B-A10-surface-classes.json` | CSI S71–S77 (regex and tool-registry cases only) | **L1**; selection and default deny hold |
| **RV6-B-A11** | **HO-0001 §3.2 machine classes × OP-7 × adversaries under revision-6 rules** (352 rows): CLOCK-back split into newer-delivered and later-withheld; re-admitted store kept. | A2, A5, A7 (`trust-state`), A13 | Never `current`; C3 only with a proof naming the state; stated residuals only | 0 `current`; 0 C3 on the thief descendant; C3 below t9 only on M1s and M6-B strip rows (RS-B1, RS-1b); CLOCK-back: 0 C3 rows; revoked R7 eligible for C1–C2 only in CLOCK-back rows (TA-7); M8 with the kept record detects downgrade | C: `outputs/RV6-B-A11-machine-classes-r6.json` (adapted from RV5-B-A12) | RT-80, RT-101…RT-105, RT-147, RT-148, RT-178 | none (holds); first install and re-admission: A01, A05, A04 |
| **RV6-B-A12** | **Key subsets below the declared thresholds.** Every subset of ≤ 3 key atoms, with any of pipeline, transport and repository input. OP-2 × OP-4 (including "no") × OP-8 × OP-9, victims P1, P2k1, WR, CIR, FA (a, b, c either 1); G_BYTES, G_SRC, G_INPUTS, G_ENV, G_CONTENT. | key thieves; pipeline; transport; A2 | No accept with ≤ 1 key; none with release keys, trust-state key and infrastructure only | 640 configurations; 246,608 subsets; 0 accepts with ≤ 1 key; 0 accepts with release, trust-state and infrastructure atoms only | C: `outputs/RV6-B-A12-key-subsets-below-threshold.json` | CS6 INV-ONE, INV-RF (derived from the minimal-set enumeration; this search is independent of it) | none (holds within CS6's model) |
| **RV6-B-A13** | **Anchors typed or provisioned from a publisher-composed fingerprint.** A P1 confirmation or pin, a CIR pin and an ingress P1 proof made after the publisher is compromised name its descendant. | trust-state publisher process + reproducer keys + transport | "never on P1" (`25` §7) | P1: {2 reproducer keys, transport, fcpub} and {2 registration keys, 2 reproducer keys, fcpub}; CIR likewise; ING_P1 adds {2 registration keys, 1 verification key, rc, rf, fcpub} | C: A01 part C | RT-101, RT-147 (a thief descendant after an anchor; the anchor names the genuine state) | **H1** |
| **RV6-B-A14** | **Verification before environment registration.** Where does the verifier's "registered environment" come from at step 3 of `06` §2 (environments are reproduced at step 5 and registered at step 6)? | — (ordering) | A stated source at the right authority | No source stated | D | RT-165 (binding to candidate and kernel) | **L3** |
| **RV6-B-A15** | **Derivation-tool provenance at the registration ceremony.** Which `gov release build --kernel-only` and which `csi_check.py` does each custodian run under R-CON-1? | pipeline-supplied tool | An admitted binary and the registered checker | Unstated | D | RT-163 (proposal mismatch against a genuine own build) | **L4** |
| **RV6-B-A16** | **Register completeness over selectors.** Do C2 and C5 see selectors that no rule id names (manifest composition, package submission, package manifest currency, environment manifest authoring, supplier class)? | — (FD-1 mechanism) | Every selector named with its establishing authority | REGISTER-CHECK PASS (re-run byte-identical) with none of them; adding them as strategies breaks CS6's invariants (A01 C, A02 computed) | C + D | RT-128, RT-183 | **M3** |

## Re-execution of review r5 decisive probes and the architect's instruments

Logs: `evidence/rerun/architect-instruments-log.tsv`, `evidence/rerun/review-r5-probes-log.tsv`; comparison
`evidence/rerun/COMPARISON.json`. Every run was from scratch exports of `4106885`.

| Probe (origin) | How re-executed | Revision 6 result | Status |
|---|---|---|---|
| CSI6 self-test and checks (architect) | `csi_check.py selftest`, `check` ×5 | self-test byte-identical (78/78); checks exits 0/3/2/2/2, identical except `kernel_dir` | claim reproduced |
| CS6 (architect) | re-run with `CS6_RESULTS_GZ` | JSON byte-identical; `CS6-results` uncompressed byte-identical | claim reproduced; model gaps: A01, A02, A03, A05, A06, A16 |
| P4r6, DA03r6, DA07r6 (architect) | re-run | byte-identical (28/28, 65/65; 20/20, 17/17, 18/18; 22/22) | claims reproduced; DA07r6 does not cover this review's defects |
| FA6 ×2 (architect) | re-run twice | byte-identical, both runs; S2 refusals, S3 equality, S4 R1–R5 same codes, S5, S6, S7 | claims reproduced; S3 `c_either_*` equality holds by construction (H2) |
| CON6, ENV6 ×2, SRC6 ×2, UW6, ATTR6 (architect) | re-run | byte-identical | claims reproduced; ENV6 recipe model narrower than `33` (H3) |
| ADM6 (architect) | re-run | identical except the unlocked mutant's race counts (reported, not asserted) | claim reproduced; A04 |
| register_check, statements_check (architect) | re-run; statements_check also against the re-run CS6 | byte-identical; PASS (paths differ in the second) | claims reproduced; A03, A16 |
| CS5, P4r5, DA03r5, FA5, REG5, P1r4 (retained revision 5) | re-run | byte-identical (FA5: equal leaves; formatting) | retained closures reproduced |
| RV5-B-A01 (B) | unmodified (loads the revision-5 executor) | byte-identical; the revision-6 executor's answer is FA6 S2 (re-run): A01a/b/c and A02 refused outside the root | instance closed; class remainder **H1, H2** |
| RV5-B-A03 (B) | FA6 S5, P4r6 `R6-AP5r_*` (re-run) | `REPRODUCTION_CONFLICT` kept; registration revocation is the remedy | closed |
| RV5-B-A04 parts L, I, P, R, C (B) | unmodified (CS5) byte-identical; CS6 strategies re-run | CS6 invariants hold inside its model; A01 C and A02 add the missing strategies | closed as stated; remainder **H1, H3** |
| RV5-B-A05 (B) | unmodified; SRC6 re-run | verdicts identical (archive digests time-dependent, as designed); SRC6 T1 refuses the two-tree construction | closed |
| RV5-B-A06 (B) | P4r6 `R6-E7-B-A06_registration_without_verification_record`; CON6 | ineligible | closed |
| RV5-B-A08 (B) | unmodified (verdicts identical; image digest compiler-dependent); ENV6 re-run; A07 | pipeline image refused (ENV6 E1); recipe and selection accepted (A07) | instance closed; class remainder **H3** |
| RV5-B-A09, A10, A11, A16 (B) | unmodified, byte-identical (checker plain registration mode unchanged); CON6 re-run; A10 | variant and tool command listed (exit 8); reversion 6; withheld 7; unknown key and new file exit 2; wildcard `informational` key still admitted | closed (M2 class); RV4-L1 open; **L1** |
| RV5-B-A12, A13 (B) | unmodified byte-identical; A11 under revision-6 rules; ADM6; A04 | as A11; store kept; high-water not applied | **M1**; otherwise holds |
| RV5-B-A14, A15, A18, A19 (B) | FA6 ORD, S6, S5; CS6 victim classes | order-independent; shipped record ignored; threshold 1 refused; 11 victim classes | closed |
| RV5-B-A17 (B) | register_check re-run; A16 | PASS; unruled selectors absent | narrowed → **M3** |
| RV5-D-A01 (D) | unmodified byte-identical; CON6 re-run | checker E7 mode unchanged; refusal now at the ceremony (`verify-registration` exit 3) and E7 restrictors (P4r6 G) | closed |
| RV5-D-A02 (D) | FA6 S2 re-run; A01 | one-page evaluator refused under (b); a composer selects every page (A01) | instance closed; remainder **H1** |
| RV5-D-A03 (D) | unmodified | computed classes unchanged; pack text now states them (`12_RT-138`, `31_GB-4` checks flip) | closed |
| RV5-D-A04 (D) | unmodified (revision-5 executor) byte-identical; FA6 S4 re-run | R1–R5 refused with the same codes in both revision-6 executors | closed |
| RV5-D-A05 (D) | unmodified byte-identical; CON6 N2–N4 re-run | N3, N4 refused at the ceremony and E7 | closed |
| RV5-D-A07 (D) | unmodified (20 leaves differ: plan rows now exist); DA07r6 re-run | 22/22 review-r5 defects detected; this review's defects are not | closed for review r5; **M3** |

## Counts

| Item | Count |
|---|---|
| Held-out attacks authored | **16** (A01–A16) |
| Executed | 8 (A01, A04, A05, A06, A07, A08, A09, A10) |
| Computed | 6 (A02, A03, A11, A12, A13, A16) |
| Design | 2 (A14, A15) |
| Contradicting a pack claim | 13 (all except A10's selection part, A11, A12) |
| Leading to HIGH | A01, A13 → H1; A05, A06 → H2; A02, A07, A08, A09 → H3 |
| Leading to MEDIUM | A04 → M1; A03 → M2; A16 → M3 |
| Leading to LOW | A10 → L1; A14 → L3; A15 → L4 (L2 from design reading) |
| Holding (no finding) | A11, A12; A10 for selection and default deny |
