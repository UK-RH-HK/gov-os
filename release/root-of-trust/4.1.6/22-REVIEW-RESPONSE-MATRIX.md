# Output 22 — Response matrix to the independent review of revision 4

> **RoT-1 revision 5 — PROPOSED, pending fresh independent reviews; not approved, not implemented.**
> - **Review answered:** `release/root-of-trust/4.1.6-review-r4/` (synthesis `97a5545`; panel B `152e68e`, C `c6b8ba9`),
>   which reviewed revision 4 (`bca05a7`) and returned `ROOT_OF_TRUST_ARCHITECTURE_REJECTED`.
> - **Task:** HO-0011 (escalation synthesis of specialist alternatives `afda663` and `ed07926`).
> - **Scope:** RV4-H1 … RV4-I1; CR4-B-01 … CR4-B-11; reviewer C's requirements (RV4-C-M1, C-1a, C-2 … C-6); CD4-0 … CD4-4
>   and the §5 rule text; the §6 carried items including the D-A03 oracle mutants; the §7 re-review entry criteria; HO-0001
>   §3–§4.
>
> This matrix claims **no finding as accepted or closed**; acceptance is the next reviewers' decision. Status vocabulary:
> **ADDRESSED — executed** (real legacy binaries, real Git, real Ed25519 through OpenSSL, or the pack checker were run
> against the revision-5 rules); **ADDRESSED — reference** (a model or calculator encoding the revision-5 rules was run, with
> mutants where named); **ADDRESSED — specification only** (not executable before implementation; the RT is named);
> **CARRIED — named test**; **RESTATED** (text corrected from the revision-5 rules; nothing decided). No row is marked
> addressed on untested evidence. Where revision 5 uses a mechanism other than the correction delta's suggestion, the row
> says so.

## 1. Evidence produced for revision 5 (`evidence/r5/`)

All runs scratch-only under `env -i`, `GOV_*` stripped, `HOME` and `GOV_KERNEL_CACHE` in scratch, legacy binaries
read-only. Commands, digests and comparisons: `evidence/r5/EVIDENCE-RUN-LOG-r5.json`, `ST5-RUN-LOG.json`, `FA5-RUN-LOG.json`.

| ID | Evidence | Kind | Result |
|---|---|---|---|
| **CS5** | `CS5-tcb-capability-sets.{py,json}` | reference (derivation calculator) | 408 configurations (OP-2 × OP-8 × OP-9 (six answers) × four victim classes × four goals, plus OP-10 × OP-9 × two victims for the toolchain goal); exhaustive to size 10; **21/21 self-checks; 1,752 invariant checks, 0 failures; 138,042 monotonicity checks, 0 violations**; 8 controls |
| **P4r5** | `P4r5-conformance-oracle.{py,json}` (loads P4r4 unmodified) | reference (conformance oracle) | **65/65** revision-5 scenarios; **42/42** retained P4r4 scenarios; **0 expected-`ACCEPTED` attack rows** (7 honest controls); residual demonstration RS-2 reported separately |
| **DA03r5** | `DA03r5-oracle-regression-sensitivity.{py,json}` | reference (mutation) | D-A03's 20 normative rules: **20/20** have a detecting scenario (13/13 retained rules on P4r4; 7/7 `verify_artifact` rules re-expressed on the admission-predicate lines; 0/7 on the superseded P4r4 copy, as designed); **17/17** revision-5 rule mutants; 0 crashes |
| **FA5** | `gov_admit_reference.py`, `FA5-first-admission.{py,json}` | executed (real Ed25519 via OpenSSL CLI, 78 verifications; real legacy 4.1.5 register) | **45/45** scenarios, **17/17** conformance vectors, **26/27** single-rule mutants (the undetected `ignore_signer_revocation` is equivalent while KS-7 holds); two runs byte-identical; candidate never executed by the admitter; revision-4 controls: path (b) `PASS` on the revoked and the remediated binary, path (c) `PASS` with the candidate executed |
| **SRC5** | `SRC5-source-identity.{py,json}` | executed (real Git) | `git archive` of a commit binds the commit id; of a tree is time-stamped; the canonical content digest is equal across repositories and changes on a moved tag (10/10) |
| **REG5** | `REG5-release-scoped-registration.{py,json}` | executed (pack checker as amended; real 4.1.5 consumer) | all 10 verdicts true: legitimate 4.1.6 and 4.1.7 exit 0; part P and D-A02 T1–T4 mixed releases refused under every claimed identity (15/15 exit 3); revision-4 retention form exit 5; gap, inflation, stale-policy exit 3 (genuine release 0 once registered); rewrite exit 5; reversion exit 6 (0 with history); different migration exit 3; on 4.1.5 the revision-5 effective content keeps the `ASIA…` key file out of index and query, the revision-4 control indexes and serves it |
| **CSI5** | `CSI5-selftest.json`, `CSI5-CSI-check-*.json` | executed (checker) | self-test **71/71**; the 56 revision-4 cases identical in title, exit and pass; payload checks exit 0/3/2/2/2 with counts equal to revision 4 |
| **ST5** | `ST5-*` (reviewer C's trees and harness copies; real 4.1.2–4.1.5) | executed | pristine R4, R4RES, R4APP `COMPLETE`, L0 `LEGACY`; **6,292** subdirectory invocations (11 positions × 4 registers, no `--root`): 280 wrote, **112** under `governance/trust/**` or the occupation directory — all `COMPLETE` under revision 4, **none** under `18` §9.1 (P5-1: 0 counterexamples); 200 nested installs all reported (P5-2); discovery refuses exactly the 4 PPS positions (P5-3); D-A01 N1b, N2, N3 `COMPLETE` → `PARTIAL`, control `COMPLETE`; `.gitignore` surgery idempotent, idiom lists nothing, clone `COMPLETE` (control `PARTIAL`) |
| **P3r3** | `P3r3-rerun-r5-summary.json` | executed (harness unchanged) | 2,085 jobs; `summary`, `property_L3`, `chain_summary`, `job_count` equal to the committed output |
| **RERUN** | `EVIDENCE-RUN-LOG-r5.json` comparisons | executed | P1r4 on real 4.1.5 against the revision-5 checker: **byte-identical**; reviewer B's copies of the review-r3 probes (RV3-B-A01, A03/A14/A16, CSI injections I01–I09, r2 P2, D lattice, D forward-compat/removal): **6/6 identical** after scratch-path normalisation (4 byte-identical) |
| **CTL4** | same log | executed / computed on the base snapshot `c8cdfac` | P4r4, VA4, reviewer B's model, AF1–AF3, surface probes (part P on 4.1.5), confinement and first-binary, D-A02, D-A03 (9/20) and D-A03b: all **byte-identical** to their committed outputs, i.e. every attack exists at base |

## 2. Blocking classes

| Class | Findings | Revision-5 mechanism (removes the input) | Specified in | D-0008 rules | Evidence | Status |
|---|---|---|---|---|---|---|
| **BC4-1** independent decisions for the TCB | RV4-H1 | **Release registration** (root threshold or root-granted quorum ≥ 2, append-only) selects source identity, input manifest, final, targets and verification records, after first-hand records and upstream checksum checks; **≥ 2 first-person reproductions** confirmed first-hand select bytes; `release-artifact` and `build-attestation` withdrawn; verification and final become restrictors; Fact Threshold Check; minima computed (FD-3). **Different from CD4-1's examples:** instead of adding a second build attestation or verifier signature to the same predicate, revision 5 moves source and inputs to the registration authority and bytes to first-hand reproduction, and makes pipeline input, reproducer processes, mirrors and the upstream toolchain explicit atoms. | `29`, `30`, `25`, `05` | (9), (17), (22), (24) | CS5; P4r5 VA5 rows and AP rows; DA03r5; CTL4 (BC and AF1/AF2 at base) | ADDRESSED — reference; implementation RT-128…RT-134 |
| **BC4-2** anchored, non-circular first TCB | RV4-H2 | **One predicate, two executors**: `gov-admit` (registered, reproduced, digest compared) evaluates admission-predicate/1 with a **fingerprint typed now** as the only state selector, never executes the candidate, **installs from the measured buffer**, starts a fresh verifier trust store; **genuine-binary rule** (C0 only without an admission record); **no ceremony before admission**; Phase 4 and CI images use `gov-admit`; build-from-source is not a trust path. | `31`, `25` §5, `06`, `11` Phase 4 | (8), (16), (19), (23) | FA5 (FB1a/b, FB2a/b/c, FB3, PH4, DA04, CI1, CH1, CH2, ADM1, INS1, INS2, VTS1, K1, K2; vectors; mutants); CTL4 (FB at base) | ADDRESSED — executed (reference executor with real signatures); implementation RT-135…RT-139 |
| **BC4-3** release-scoped registration | RV4-H3 | **Exact per-release registration** of every non-join unit and the kernel tree digest in the release registration; single-valued and append-only; E7 and effective values use only the registration of the release judged; presence release-scoped; reversion, unit removal and member narrowing are computed reductions; binding groups for owner-domain sets. **Different from CD4-3 (1):** no sequence ranges (ranges admit gap, inflated and stale-policy releases). | `23` §12, `19`, `30` §5 | (6), (24) | REG5; CSI5 S56–S70 | ADDRESSED — executed (checker, real 4.1.5 consumer); binary RT-140…RT-143 |
| **BC4-4** owner options and blast radius | review r4 §7 | OP-1…OP-15 reconciled from OP-1…OP-7 and both specialists' lists; consequences taken from CS5, REG5, FA5; **no proposal and no default**; `release-final` blast radius: nothing becomes effective | `21`, `05` §1, `25` §7 | — | CS5 table; `21` §0 mapping | RESTATED; RT-127 |

## 3. Findings RV4-H1 … RV4-I1

| Finding | Revision-5 change | Specified in | Evidence | Status |
|---|---|---|---|---|
| **RV4-H1** | BC4-1 (§2). Each pack claim the finding contradicted is replaced: `25` §7 and `05` §3 minimum sets are calculator output; `05` §1 `build-attestation` withdrawn; `21` OP-2 replaced; VA4's route-B row is superseded by P4r5 VA5-11…13 (refused). | `30`, `25`, `05`, `21` | CS5: RV4-B-A01 shape {one reproducer key, pipeline} refused; RV4-B-A02 {one verification key, pipeline} refused; INV-ONE 0 failures; D-A07 re-expressed as the pass-through control | ADDRESSED — reference; RT-131, RT-134 |
| **RV4-H2** | BC4-2 (§2). `06` §2 step 6 paths (b) and (c) withdrawn; `11` Phase 4 uses `gov-admit`; `21` OP-6 states the dependence of TA-5 on admission; TA-1 and TB-1 restated (`01`, `25` §10). | `31`, `06`, `11`, `01` | FA5: revoked binary with revocation withheld `STATE_NOT_HELD_OR_FINGERPRINT_MISMATCH`, served `BINARY_REVOKED`; remediated compromise refused in three variants; moved tag `RELEASE_UNREGISTERED` with the candidate never executed; unadmitted binary's ceremonies `BINARY_NOT_ADMITTED`; legacy 4.1.5 has no `verify-artifact` | ADDRESSED — executed; RT-135…RT-137 |
| **RV4-H3** | BC4-3 (§2). The `release-final` blast radius (`05` §1, `21`) now states that no final becomes effective without its registration. | `23` §12, `05`, `21` | REG5 part P with consumption on real 4.1.5; D-A02 T1–T4; legitimate retention eligible | ADDRESSED — executed; RT-140 |
| RV4-M1 | `18` §9.1 closed entry sets; §9.2 root discovery and refusal inside the PPS; `26` §3 scope, LP-1r/LP-1s and LR-2 restated; D-0008 rules (10), (12) restated | `18`, `26`, `15`, D-0008 | ST5 matrix (6,292 invocations incl. `governance/` and `governance/trust/kernel/`), `subdir_escape`, D-A01 re-run | ADDRESSED — executed (legacy behaviour) and reference (predicate); binary RT-144 |
| RV4-M2 | CR4-B-01: allow-list confinement with explicit denies; TCB-location rule for C3, confirmations and decision pins; `27` §3.3 and `28` §5 restated; CI `sudo` note in `06` §3 | `27` §3.3, `31` GB-4, `06`, `09` R-CONF-4/5 | FA5 INS2 (the predicate refuses C3 from a user-owned location); confinement itself not executable before implementation | ADDRESSED — specification only (confinement); reference (predicate); RT-103, RT-138 |
| RV4-M3 | CR4-B-02: witness input from the ceremony or channel only; C3 threshold under two custodians or a flagged consequence | `24` §3.3, `05` §7 rule 10, `21` OP-7 | — | ADDRESSED — specification only; RT-149 |
| RV4-M4 | CR4-B-03: RS-2 restated; stateful clock high-water raised by every ingested non-future statement | `24` §8, §10; `21` OP-7 | P4r5 `CLOCK-RV4-B-A13` (stateful: refused); residual demonstration (stateless: accepted as RS-2); DA03r5 `R5-clock-high-water` detected | ADDRESSED — reference; RT-148 |
| RV4-M5 | The selector (`release-final` choosing migration content) is removed: migrations are registered units. CR4-B-04 requirements from pre-transaction inputs on machines without a record. | `23` §12, `19` §9 item 5 | REG5 migrations (registered 0, different 3); CR4-B-04 not executable before implementation | ADDRESSED — executed (selector) and specification only (CR4-B-04); RT-146 |
| RV4-M6 | RV4-C-M1: `.gitignore` surgery in the install transaction, idempotent | `26` §8, `08` | ST5 `gitignore-surgery` on real Git | ADDRESSED — executed (reference transaction step); RT-145 |
| RV4-M7 | Conformance oracle with a distinguishing scenario for all 20 D-A03 mutants, including the five with no RT and the two ambiguous ones; no expected-`ACCEPTED` attack row; mutants for every new rule | `12` §4c, §8.1; `29` R-SEL-4 | P4r5; DA03r5 20/20 and 17/17 | ADDRESSED — reference; RT-129 |
| RV4-L1 | CR4-B-05 carried: the lint refusal of a wildcard non-floor rule admitting unknown keys is specified; the draft inventory keeps `ROLES.authority_levels.*.*` until TPS v1 enumerates its leaves | `12` RT-150 | — (not changed in the reference checker) | CARRIED — specification only; RT-150 |
| RV4-L2 | CR4-B-06: WITNESSED at the C3 threshold is a currency proof (P3) in both the table and the definition | `24` §4.4 | P4r5 `AP-00b_stateless_witnessed_runner_op7c` | ADDRESSED — reference; RT-154 |
| RV4-L3 | CR4-B-07 **option 1**: a P1 proof covers only the TSS it names; C3 on a later descendant needs P2 or P3. Chosen under FD-1 (the trust-state key is not a C3 selector); CS5 control shows option 2 admits {reproducer keys, trust-state key, transport} on pinned machines. | `24` §4.4, §10 | P4r5 `AP-R5_p1_proof_does_not_cover_later_descendant`; DA03r5 `R5-descendant-proof`; CS5 `P1_relaxed_control` | ADDRESSED — reference; RT-147 |
| RV4-L4 | CR4-B-08: first-run recording only for resolving release builds; `accepted_tbm_reset`; stateless scope stated | `25` §5, `24` §8 | P4r5 `A7-CR4-B-08`; DA03r5 `R5-first-run-record` | ADDRESSED — reference; RT-151 |
| RV4-L5 | CR4-B-09: decision-pin maximum validity; increases are computed reductions | `27` §3.2, `19` §10.6, schema | P4r5 `GATE-CR4-B-09`; DA03r5 detected | ADDRESSED — reference; RT-152 |
| RV4-L6 | CR4-B-10: revoked attestations and reproductions never count | `25` AP-4, `30` R-REP-6 | P4r5 two rows; DA03r5 two mutants; FA5 vectors | ADDRESSED — reference; RT-153 |
| RV4-L7 | CR4-B-11: OP-4 restated as one statement; key counts removed (OP-4 affects evaluation candidates only) | `21` OP-4 | CS5 INV-RF | RESTATED; RT-127 |
| RV4-L8 | `release-final` blast radius: no final becomes effective without its registration; Git-delivered use judged by E7 against the registration | `05` §1, `20` §9, `21` | REG5 unregistered releases exit 3; P4r5 `E7-D-A06` | RESTATED and ADDRESSED — executed; RT-140 |
| RV4-L9 | `eligibility.production_sources[]` withdrawn; registering a release is not a reduction; reversion, removal and narrowing are | `19` §3, §10.6 | CSI5 S63, S64, S70 | RESTATED (rule re-scoped) and ADDRESSED — executed; RT-141 |
| RV4-L10 | Owner-domain binding groups; exact set match for several valid pins | `23` §7.2, `27` §3.2, schemas | CSI5 S66 (exit 3), S67 (exit 0) | ADDRESSED — executed (checker); RT-143 |
| RV4-I1 | unchanged: the acting role remains caller-declared; no trust gate depends on it | `27` §5 | — | INFO — stated |

## 4. Carried requirements CR4-B-01 … CR4-B-11 (review r4 B `04`)

| CR | From | Specified in | Test → evidence | Status |
|---|---|---|---|---|
| CR4-B-01 | M1 | `27` §3.3, `31` GB-4, `06` §3, `09` | (i) RT-103; (ii) RT-138 / FA5 INS2; (iii) platform variants RT-103 | spec only (confinement); reference (predicate) |
| CR4-B-02 | M2 | `24` §3.3 | RT-149 | spec only |
| CR4-B-03 | M3 | `24` §8, §10 | RT-148 / P4r5 CLOCK and residual demonstration | reference |
| CR4-B-04 | M4 | `19` §9 item 5 | RT-146 | spec only |
| CR4-B-05 | L1 | `12` RT-150 | RT-150 | carried, spec only |
| CR4-B-06 | L2 | `24` §4.4 | RT-154 / P4r5 AP-00b | reference |
| CR4-B-07 | L3 | `24` §4.4 (option 1) | RT-147 / P4r5; CS5 control | reference |
| CR4-B-08 | L4 | `25` §5 | RT-151 / P4r5 | reference |
| CR4-B-09 | L5 | `27` §3.2 | RT-152 / P4r5 | reference |
| CR4-B-10 | L6 | `25` AP-4 | RT-153 / P4r5, FA5 | reference |
| CR4-B-11 | L7 | `21` OP-4 | RT-127 | restated |

**B's acceptance cases for the blocking findings:** H1 (a)–(c) → CS5 (no set below the stated minimum; pipeline counted;
no oracle row expects an attack `ACCEPTED`); H2 (a)–(d) → FA5 (each refused by the documented procedure with the channel
fingerprint as selector, the negative set, and an externally computed digest; Phase 4 has no self-verification); H3 → REG5
(E7 refuses; the `ASIA…` file stays excluded on 4.1.5).

## 5. Reviewer C's requirements (review r4 C `04`)

| Item | Where | Test | Evidence | Status |
|---|---|---|---|---|
| RV4-C-M1 | `26` §8 | RT-145 | ST5 gitignore surgery | ADDRESSED — executed (reference) |
| C-1a | `12` RT-144, RT-50b | subdirectory positions of every register | ST5 matrix (hand-built layout; the genuine-install run needs the implementation) | ADDRESSED — executed (legacy behaviour and predicate); binary run specification only |
| C-2 | `18` §3, `20` §8 | RT-123 | — | CARRIED — specification only |
| C-3 | `18` §9 D033 | RT-124 | — | CARRIED — specification only |
| C-4 | `18` §3, `26` §2 | RT-125 | ST5 uses `lstat` types | CARRIED — specification only |
| C-5 | `12` RT-50 | full register on a genuine 4.1.6 install | P3r3 re-run equal (hand-built layout) | CARRIED — specification only |
| C-6 | `18` §9.1 item 5, D039 | RT-155 | — | CARRIED — specification only |

## 6. Correction delta CD4-0 … CD4-4 and the §5 rule text

| Item | Applied as | Different mechanism? |
|---|---|---|
| CD4-0 retain | Retained: every CD3-0 item; BC-1 closures (exact precedence registration, registration-only precedence, two-directional order, directed join, required presence — now release-scoped for non-join units — YAML profile, Overlay Surface, strength over effective policy); BC-2 closures (inclusion anchors, pin validity, currency proofs, witness purpose with threshold 2, no `current`, pin integrity); V8 (as a restrictor); root-anchored legacy containment; carried closures RV3-M1, M3, M4, L1, M8, L8. Evidence of non-regression: P1r4 byte-identical; CSI5 56 cases identical; P4r4 retained 42/42; review-r3 probe copies identical; P3r3 equal. | **Replaced:** the BC-3 closure's binary predicate (`release-artifact` ×2, one build attestation, attested source) by admission-predicate/1; the artefact playbook becomes "never drop published references" for `registrations[]` and `published_binaries[]`. |
| CD4-1 | `30`, `25`, `05`, `29` | **Yes**: registration selects source and inputs; first-hand reproduction quorum selects bytes; the review's "verification threshold ≥ 2" is offered as OP-8 because under registration it bounds process compromise, not key theft (CS5 INV-SRC-KEYS) |
| CD4-2 | `31`, `25`, `06`, `11` | as proposed, plus installation from the measured buffer, the genuine-binary rule and a fresh verifier trust store (gaps both specialists found in the stated invariant) |
| CD4-3 | `23` §12 | **Yes**: exact per-release lookup, not sequence ranges; presence scoped; removal and narrowing added as reductions |
| CD4-4 | `21` | as proposed; no proposals at all |
| §5 rules (6), (9), (16), (19), (17), (10), (12) | `15` §5, D-0008 | also (7), (8), (21) revised and (22)–(24) added |

## 7. Review r4 §7 re-review entry criteria

| Criterion | State |
|---|---|
| 1. CD4-1 … CD4-4 closed as classes in pack, schemas, D-0008, ARCH-0002; both PROPOSED | §2, §6; schemas `release-registration`, `binary-reproduction`, `input-manifest`, `admission-record` added and eight revised (`examples/rev5/validation.json`: every schema valid, four instances valid, four refused shapes); D-0008 and ARCH-0002 revision 5, PROVISIONAL, `in_effect: false`, no `chosen_option` |
| 2a. B's BC enumeration, AF1–AF3, FB constructions, D-A07 | BC → CS5 (enumeration under revision-5 rules; controls); AF1 → P4r5 VA5-B-prime/B-prime2 and CS5 self-check; AF2 → P4r5 VA5-07…10; AF3 and FB1/FB2 → FA5 FB1a/b, FB2a/b/c; D-A07 → CS5 pass-through control and OP-9 (d). At base all reproduce (CTL4). |
| 2b. B's part P on real 4.1.5 and D-A02 T1–T4 | REG5: refused under every identity; on 4.1.5 the effective content excludes the secret file |
| 2c. C's `subdir_escape`, matrix positions, D-A01 N1–N3 against the corrected predicate | ST5 (§1) |
| 2d. D-A03 and D-A03b against the next oracle | DA03r5 20/20 normative rules; RET-* scenarios are the D-A03b constructions |
| 2e. P1r4, P4r4, VA4 and the CSI self-test unchanged in what they refuse | P1r4 byte-identical; P4r4's 42 non-binary scenarios hold inside P4r5 and P4r4 re-runs byte-identical; **VA4:** its refused rows RV3-B-A08, REJECTED candidate, different attested source, RV3-D-A03 (two rows), root-registered source and threshold-2 variants, route B with one key and without attestation stay refused as P4r5 VA5-01, 03, 04, 05, 06, 08, 09, 12, 13; its three documented-`ACCEPTED` attack rows (route S, route S under OP-4 "no", route B) are refused as VA5-07, 10, 11; its three custodial pre-check rows have no revision-5 analogue (custodial stages are replaced by R-REG-3 and R-PUB-1, RT-130); its revision-3-rule reproduction row is a control of a superseded rule. CSI self-test: 56 revision-4 cases identical. |
| 3. Response matrix over RV4-H1 … RV4-I1, CR4-B-01 … 11, C's requirements, CD4-0 … CD4-4; no untested "resolved" | §3–§6 |
| 4. No expected-`ACCEPTED` attack row; every oracle mutant, including D-A03's, has a distinguishing scenario | P4r5 summary `expected_ACCEPTED_rows_that_are_attacks: []`; DA03r5 |

## 8. Review r3 and review r4 blocking probes re-run against revision 5

| Probe (origin) | How re-run | Result on revision 5 |
|---|---|---|
| RV4-B-A01, A02, A06 (B) | CS5 enumeration; P4r5 VA5 rows | refused below the computed minimum; 0 invariant failures |
| RV4-D-A07 (D) | CS5 pass-through control; OP-9 (d) rows | the purpose does not exist; the pass-through shape lowers the minimum, which R-REG-3 (f) forbids |
| RV4-B-A03 FB1/FB2 (B) | FA5 | refused (state not held; `BINARY_REVOKED`); revision-4 path (b) control `PASS` |
| RV4-B-A04 (B) and Phase 4 | FA5 FB3, PH4 | refused, candidate never executed; no self-verification; revision-4 path (c) control `PASS` |
| RV4-D-A04 (D) | FA5 DA04 | `BINARY_NOT_ADMITTED`; after admission in a user-owned scratch location GB-4 refuses (a root-owned location is not creatable in scratch; the predicate is shown on a system path, INS2) |
| RV4-B-A08 part P (B), RV4-D-A02 (D), RV4-D-A06 (D) | REG5; P4r5 E7 rows | refused; secret excluded on 4.1.5 |
| RV4-C-A01 (C), RV4-D-A01 (D) | ST5 | no trust-path write left `COMPLETE`; nested installs reported |
| RV4-D-A03, A03b (D) | DA03r5 | 20/20 |
| RV3-B-A01 precedence to `immutable` (B) | copy re-run | exit 3; identical |
| RV3-D-A01/A02 lattice (D) | copy re-run | 0 unsound; identical |
| RV3-D-A10 removals (D) | copy re-run | R01–R09 exit 2; identical |
| RV3-B I01–I09 (B) | copy re-run | identical |
| RV3-B-A02, A06, A12, A13; RV3-D-A11, A12 (B, D) | P4r4 retained scenarios inside P4r5 | 42/42 hold |
| RV3-D-A15 revoked binary on pinned CI (D) | P4r5 `RV3-D-A15r5` | never accepted; honest current pin `BINARY_REVOKED` |
| RV3-B-A08, RV3-D-A03 (B, D) | P4r5 VA5-01, 05, 06 | refused |
| RV3-B-A03/A14/A16 (B); r2 P2 | copy re-run | identical after normalisation |

## 9. HO-0001 owner requirements

| Requirement | Where | Evidence |
|---|---|---|
| §3.1 constitutional-floor closure (review r4: NOT SATISFIED on schema evolution and on sensitivity/tool floors under retention) | `23` §12, §7, §7.2; `19` | REG5 (secret pattern consumption on 4.1.5; tool descriptor T1; invariant, schema, skill); CSI5 71/71 |
| §3.2 new-machine trust bootstrap (NOT SATISFIED on first binary and RS-2) | `31`, `24`, `06` | FA5; P4r5 retained machine scenarios and CLOCK |
| §3.3 binary and root authenticity (NOT SATISFIED on one key and circular first binary) | `30`, `25`, `31`, `05` | CS5; P4r5; FA5 |
| §3.4 legacy-binary damage containment (SATISFIED; must not regress) | `26`, `18` §9 | P3r3 equal; ST5 |
| §4 forward compatibility | `23` §7.1, §7.2, §12.2 | CSI5 S66/S67; new non-join units register with the release that introduces them (S69) |

## 10. Unresolved or not yet executable

- **No implementation exists.** Every RT-128…RT-155 needs the implementation, including `gov-admit`, the decision register,
  confinement on real platforms, the TCB-location predicate on root-owned locations, cross-OS reproducibility (IR-REP-3),
  CR4-B-02, CR4-B-04, CR4-B-05, C-2…C-6 and RT-50 on a genuine install.
- **Models.** CS5's honest-party rules are this revision's specification (`30` §9); a real process that deviates changes the
  sets. P4r5 and FA5 are reference executors, not the product.
- **Owner decisions pending:** OP-1…OP-15 (`21`); none proposed.
- **Independence.** Revision 5 was written by a fresh synthesis architect session (AR-0011) that authored no earlier
  revision, review or specialist proposal.
