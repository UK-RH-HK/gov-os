# D-synthesis 02 — Adjudication of reviewers B and C (review r5)

Revision reviewed: RoT-1 revision 5, `cdb4e14009bba60bea9b805563c1b60e84f30b4b`. Panel: reviewer B `248f12a` (AR-0012,
`BLOCKING_FINDINGS_PRESENT`), reviewer C `840d583` (AR-0013, `NO_BLOCKING_FINDINGS`). Synthesis run AR-0014.

Vocabulary: **CONFIRMED** (severity kept, or changed with the reason stated), **REFUTED** (with evidence), **DUPLICATE**.
"Reproduced" refers to `01-REPRODUCTION.md`. "D-Axx" is RV5-D-Axx (`03-HELDOUT-ATTACKS-RV5-D.md`).

## 1. Reviewer B

### 1.1 HIGH findings

| Item | Reproduced | Adjudication | Consolidated |
|---|---|---|---|
| **RV5-B-H1** first admission selected by the channel alone | **yes.** `RV5-B-A01` byte-identical: A01a (OP-13 (a)), A01b (OP-13 (b), both channels) and A01c (genuine OP-13 (b) owner, one compromised channel, one value typed) `ACCEPTED` with zero genuine keys; all four controls as designed. `RV5-B-A04` part L byte-identical: FA1 minimum {ch1} in 96/96 configurations, FA2 {ch1, ch2} in 96/96, FA2 with the quorum read from the selected state {ch1} in 96/96. **Code:** `gov_admit_reference.accept()` reads `bootstrap.channel_quorum` from the Trust Policy that the typed fingerprint selects, and never reads `admitter_digests`. | **CONFIRMED HIGH, extended by D-A02** | RV5-H1 |
| **RV5-B-H2** build image selects the bytes | **yes.** `RV5-B-A08`: every verdict identical (clean and malicious-image reproducers each bit-identical, injected code runs, toolchain unchanged, no path embedded); the digests differ only because they depend on the local compiler. `RV5-B-A04` part I byte-identical: {pipeline} or {image_up} under every OP-2, OP-8, OP-9 and OP-10 answer. **Design:** "image record" occurs only in `30` R-REG-3 (c); `29` §4 has no row for it; CS5 has no image atom. | **CONFIRMED HIGH** | RV5-H2 |
| **RV5-B-H3** policy-root content under OP-2 (b) lacks the verification restrictor | **yes.** `RV5-B-A04` part P, and `RV5-B-A09`, byte-identical: the variant regex is E7 exit 0 with no reduction, and on 4.1.5 the `ASIA…` file is indexed and served. | **CONFIRMED. The route as B states it is re-rated; the class is HIGH through D-A01** | RV5-H3 |

**RV5-B-H1: why the extension matters.**
- Under OP-13 (b), the admitter digest is compared with one channel. `31` R-ADM-2 compares it with "the admitter digest
  published in the independent channels", with no quorum. `21` OP-13 scopes the agreement rule to "typed state
  fingerprints". FA5's `operator_compare_admitter(measured, tps_admitter_list, channel_digest)` takes one channel digest.
- A single compromised channel can therefore substitute the evaluator, whatever fingerprint quorum is enforced. This holds
  even after B's correction 2 is applied to fingerprints only (D-A02).
- The unavoidable core is narrower than both the pack and B state it: the *set of channels the operator consults* selects
  the first-contact root. That set is the residual an owner trade-off must size (`11` CD5-1).

**RV5-B-H2: why HIGH and not CRITICAL.**
- `30` R-REG-3 (c) names "the owner's image record". A conforming process can keep its production outside the pipeline.
- The defect: no rule assigns that production, no check establishes the record's content, and no residual states the
  supplier that remains. Honest reproducers cannot detect it, because R-REP-2 makes all of them fetch the one registered
  image.
- An implementation that takes the image digest from release CI conforms to the text, and its minimum is {pipeline}. That
  is the TCB, below the declared minimum.
- `30` IR-REP-3 already requires cross-distribution reproducibility before a target is registered. Diversity of build
  environments is therefore achievable, but it is not required per release.

**RV5-B-H3: why B's route alone is MEDIUM, and why the class is HIGH.**
- **B's route alone.** It needs the registration authority at its threshold (two delegated custodians, or two delegated
  keys plus the trust-state key) plus `release-final`.
  - Under OP-2 (b), that authority is the selector the pack itself assigns to non-orderable content (`29` §4).
  - What the missing E7 restrictor changes is the composition of the minimal set: `release-final` replaces the OP-8
    verification compromise. It does not lower the set's authority rank.
  - Taken alone, that is a MEDIUM mechanism defect plus false consequence statements (`05` §1, `21` OP-2 (b), OP-4, OP-8).
- **D-A01** removes the registration authority from the minimal set.
  - The registration custodians sign a unit map and kernel tree digest that they never establish first-hand: the unit map
    is produced by CI (`23` §12.5), and R-REG-3 (d) binds verification records to source and inputs only.
  - E7 applies no verification restrictor.
  - So with honest custodians, verifiers and publisher, {pipeline, `release-candidate`, `release-final`} makes malicious
    non-orderable content eligible under OP-2 (a) and (b). Under OP-4 "no" the set is {pipeline, one everyday key}.
    Computed on the P4r5 functions; executed with the pack checker and on 4.1.5.
  - This is the recurring class at threshold 1, the shape of RV4-H3. The consolidated finding is HIGH.
- **B's correction is not sufficient.** Its correction 1 applies a verification restrictor "for its source". D-A01 part A
  computes E7 with that restrictor: still eligible. A restrictor bound to the registered candidate, together with
  final/candidate/registration consistency, refuses. So does a registration derived first-hand from the verified source.

### 1.2 MEDIUM, LOW and status claims

| Item | Panel severity | Reproduced | Adjudication | Consolidated |
|---|---|---|---|---|
| RV5-B-M1 revocation removes restrictors | MEDIUM | yes (A01 rows A03; A04 part R: 36/216 configurations lose `transport`) | CONFIRMED MEDIUM: the key sets still need q reproducer keys, the trust-state key and the victim's channel; bound rule | RV5-M1 |
| RV5-B-M2 registration reductions exact-match and ceremony-side only | MEDIUM | yes (A09, A10) | CONFIRMED MEDIUM: the actor is the registration authority; a verifier-side rule and restated claims close it. Interacts with CD5-3. | RV5-M2 |
| RV5-B-M3 re-admission discards monotonic state | MEDIUM | yes (A12 row M8; `write_admission_record` source; C's `admit_tx` A09, A10) | CONFIRMED MEDIUM; RV5-C-L3 merged | RV5-M3 |
| RV5-B-M4 source identity ambiguous; SRC5 tests another function | MEDIUM | yes. A05: every verdict identical. SRC5 re-run: 16 digest leaves differ from the committed output, every verdict leaf equal; `SRC5-source-identity.py` `content_digest()` hashes `git archive --format=tar <tree>` | CONFIRMED MEDIUM | RV5-M4 |
| RV5-B-M5 decision register incomplete | MEDIUM | design; D-A07 computed: `29` §4 has no row naming lineage selection, channel quorum or the image record, and the calculator has no image or content goal | CONFIRMED MEDIUM. As a finding it is carriable; completing the register is also a closure criterion of CD5-4. | RV5-M5 |
| RV5-B-L1 bundle order | LOW | yes (A01 ORD rows) | CONFIRMED LOW | RV5-L1 |
| RV5-B-L2 unsigned admission record | LOW | code (`gov_run`, `load_admission_records` honour any record under the directory by digest) | CONFIRMED LOW | RV5-L2 |
| RV5-B-L3 clock set back on restored machines | LOW | yes (A12 CLOCK-back rows) | CONFIRMED LOW | RV5-L3 |
| RV5-B-L4 contradictory text | LOW | design | CONFIRMED LOW; extended below | RV5-L4 |
| RV5-B-L5 calculator victim classes | LOW | yes (A04 part C) | CONFIRMED LOW | RV5-L5 |
| RV5-B-L6 no minimum root threshold | LOW | design; code (`COMPILED_MIN` 2 in the reference only) | CONFIRMED LOW | RV5-L6 |

**RV5-B-L4 extension.**
- `07` §3 still defines `release.source {release_commit, source_tree_digest, build_inputs_digest}`, "`source_tree_digest` is
  the SHA-256 of `git archive` of the commit". It also lists "Artefact v3" statements under `release-artifact`.
- `04` V8 names `source_tree_digest` and `build_inputs_digest`.
- `30` §4.1 replaced these with `content_digest` and `inputs_manifest_digest`, and `05` KS-13 withdraws `release-artifact`.

**Reviewer B's status claims.**

| Claim | Adjudication | Basis |
|---|---|---|
| RV4-H1, RV4-H2, RV4-H3 `CLOSED as stated` | CONFIRMED | CS5 self-checks `rep1 + pipeline` and `va1 + pipeline` refused; P4r5 VA5 rows; FA5 FB1a/b, FB2a/b/c, FB3, PH4, DA04; REG5 15/15 mixed identities exit 3. All reproduced byte-identical. |
| BC4-1 `OPEN → H2` | CONFIRMED; the class remainder is RV5-H2. The evaluator part belongs to RV5-H1. | as above |
| BC4-2 `NARROWED → H1` | CONFIRMED | A01, A04 part L |
| BC4-3 `NARROWED → H3, M2` | CONFIRMED and **widened**: D-A01 lowers the minimum to threshold-1 keys plus the pipeline | D-A01 |
| BC4-4 `OPEN` | CONFIRMED | `04-OWNER-REQUIREMENTS-AND-OPTIONS.md` §2 |
| RV4-M2 `NARROWED`, RV4-M3 `CLOSED by rule`, RV4-M4 `NARROWED`, RV4-M5 `CLOSED (selector)` | CONFIRMED (M3 and M5 are specification only: RT-149, RT-146) | design; P4r5 CLOCK row reproduced |
| RV4-M7 `CLOSED for the 20 mutants` | CONFIRMED (DA03r5 reproduced: 20/20 and 17/17). New oracle gaps outside those mutants: RV5-M9. | D-A04 |
| RV4-L1 `OPEN`; RV4-L2…L5 `CLOSED`; RV4-L6 `CLOSED as stated`; RV4-L7 `NARROWED`; RV4-L9 `CLOSED`; RV4-L10 `CLOSED (checker)` | CONFIRMED | selftest 71/71; P4r5 rows |
| RV4-L8 `CLOSED for release-final alone` | CONFIRMED. The remainder is RV5-H3: `release-candidate` + `release-final` + pipeline obtain the registration. | D-A01 |
| HO-0001 §3.2 `SATISFIED for transport and repository adversaries, with carried conditions` | **Not adopted as the class determination.** B's evidence is reproduced and holds for that adversary scope. As a class, §3.2 also requires the first-install machine and the workstation machine classes to be defined exactly (RV5-H1, RV5-M8, RV5-M3). | `04` §1.2 |

## 2. Reviewer C

| Item | Panel severity | Reproduced | Adjudication | Consolidated |
|---|---|---|---|---|
| RV5-C-M1 no `.gitattributes`; autocrlf and `text=auto` corrupt kernel bytes | MEDIUM | yes (`gitops` AUTOCRLF and TEXTAUTO_EOLCRLF states identical) | CONFIRMED MEDIUM: fails closed, but Git for Windows defaults to `core.autocrlf=true`, so the layout is unusable there; a bound transaction step and test close it | RV5-M6 |
| RV5-C-M2 out-of-project ignore sources re-drop the occupation | MEDIUM | yes (GLOBALEXCL, INFOEXCL) | CONFIRMED MEDIUM (same rating as RV4-M6, same fail-closed outcome) | RV5-M7 |
| RV5-C-L1 `26` §4 LP-1s overclaims | LOW | yes (`matrix5` property LP-1s: 16 counterexamples) | CONFIRMED LOW. Extended: D-0008 rule (12) repeats the claim ("every write under governance/ other than overlay content ... leaves a state RoT-1 binaries treat as PARTIAL or report"). | RV5-L7 |
| RV5-C-L2 transaction area outside `18` §9.1 and §9.2 | LOW | yes (96 rows, all `COMPLETE`, reported) | CONFIRMED LOW. Extended: D-0008 rule (10) says RoT-1 commands refuse a working directory inside the transaction area, which `18` §9.2 item 2 does not list. | RV5-L8 |
| RV5-C-L3 first admission undefined; re-run discards the store; record placement | LOW | yes (`admit_tx` A09, A10 identical) | **DUPLICATE of RV5-B-M3**, consolidated at MEDIUM. B's A12 row M8 shows the store loss removes E10 downgrade detection and strength vectors, so the effect is a loss of detection, not only spec clarity. | RV5-M3 |

**Reviewer C's status claims.**

| Claim | Adjudication | Basis |
|---|---|---|
| R2-H4 `CLOSED as a class` | CONFIRMED | `matrix5` re-run: 30,165 rows, property R2-H4 0 violations; LP-1r 1,335 rows, 0 project writes; 0 classifications lost; 0 Git-operation trees written into `COMPLETE`. Identical to C's summary except `elapsed_seconds`. |
| RV4-M1 `CLOSED` for `governance/trust/**` and the occupation; `NARROWED → L2` | CONFIRMED | as above |
| RV4-M6 `CLOSED` against the project `.gitignore`; `NARROWED → M2` | CONFIRMED | `gitops` UNTRACK_R5, UNTRACK_NOSURG |
| C-2 … C-6, RV4-M2 (transaction part), RV4-M5 (transaction part): carried, specification only | CONFIRMED | design |
| Role verdict `NO_BLOCKING_FINDINGS` | CONFIRMED within C's compatibility and transaction scope. The blocking findings of this review lie outside that scope. | — |

## 3. Refutations

None. Every panel finding is reproduced or is a design reading that this review checked against the text at `cdb4e14`.
