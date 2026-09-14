# 02 — Falsification of the Selection-Authority Model (specialist A)

Every blocking probe of reviews r3 and r4, and 30 new attacks of this specialist's own, run against SAM (`01-ALTERNATIVE.md`).

## 1. Method

| Evidence class | Meaning |
|---|---|
| **executed** | real Git, the real legacy 4.1.5 binary (a consumer or command runner), the pack's unmodified checker, or real Ed25519 verification through OpenSSL |
| **computed** | a symbolic model in which honest actors act only on the checks their design states (E2), or the architect's unmodified functions (E0) |
| **design-encoded** | a classification of stated decisions (E1) |
| **design** | a reading of pack text or code |

| Script | Output | What it is |
|---|---|---|
| `evidence/E0-baseline-reproduction.sh` | `outputs/E0-*` | baseline: every retained instrument and every r3/r4 blocking probe, unmodified, against revision 4 |
| `evidence/E1-selector-audit.py` | `outputs/E1-*` | SEL-1 over 61 decision rows (43 for r1–r4, 18 for SAM) |
| `evidence/E2-tcb-capability-sets.py` | `outputs/E2-*` | minimal capability sets: revision 4 (control), the review's literal CD4-1 closure (RID) and SAM, over 64 SAM rows |
| `evidence/E3-first-binary-acceptance.py` with `evidence/gov_accept_reference.py` | `outputs/E3-*` | real-signature toy lineage; revision-4 paths (b) and (c) as controls; 16 vectors; 13 mutants. Deterministic: two runs compared equal with `cmp`. |
| `evidence/E4-release-scoped-registration.py` | `outputs/E4-*` | pack checker unmodified plus a registration projection; real 4.1.5 consumption; lookup-rule mutants |

- **Hygiene.** Every probe ran under `env -i` in `…/scratchpad/ar-0009/`, with `HOME` and `GOV_KERNEL_CACHE` in scratch,
  `PYTHONDONTWRITEBYTECODE=1`, and no other `GOV_*` in any child.
- **Legacy binaries.** Used read-only (SHA-256 in `outputs/E0-baseline-LOG.txt`).
- **Result vocabulary.**
  - `REFUTED`: the attack fails against SAM.
  - `CONFIRMED`: the attack succeeds; it is either a stated residual, or a defect in revision 4 used as a control.
  - `PASS`: an oracle or specificity check behaves as required.
  - `NOT_RUN`: the reason is given.

## 2. Baseline (E0): each attack exists at base; retained closures reproduce

All comparisons are against the committed outputs; `cmp` 0 means byte-identical.

| Probe | Result at base |
|---|---|
| CSI selftest; check framework and 4.1.5 | 56/56, exit 0; exit 0; exit 3 |
| P4r4, VA4, P1r4 (architect) | `cmp` 0 ×3 |
| RV4-B-M reference model, AF1–AF3, surface probes (U/T/P on 4.1.5), confinement and first-binary (B) | `cmp` 0 ×4 |
| RV4-D-A02 retention breadth (D) | `cmp` 0 |
| RV3-B-A01, RV3-D lattice, RV3-D surface removal (B's copies) | identical to review-r4 B's re-runs after path normalisation |

The attacks exist at base:
- **B part P:** mixed kernel exit 0; `ASIA…` file indexed and retrievable.
- **D-A02:** T1–T4 exit 0 under RETAIN.
- **AF1:** `ACCEPTED`.
- **FB1 and FB2:** tooling `PASS`.
- **Part B:** path (c) passes.

## 3. Review r4 blocking probes against SAM

| # | Probe | SAM result | Class, evidence | Revision-4 control |
|---|---|---|---|---|
| 1 | **RV4-B-A01** route B′: one `build-attestation` key plus pipeline, honest custodians | **REFUTED.** The purpose does not exist; bytes need a reproduction quorum. The minimal set is {2 reproducer keys, trust-state key, transport} (P1) or plus the channel (first install). | computed E2 | CONFIRMED {ba, pipeline} (E2 = B) |
| 2 | **RV4-B-A02** route S′: one `verification-attestation` key plus pipeline | **REFUTED.** Verification selects nothing; `va` appears in no SAM minimal set. | computed E2 | CONFIRMED {pipeline, va} (REJECTED not held) |
| 3 | **RV4-B-A06** every capability subset × options | **REFUTED.** 64 SAM rows; none accepts with fewer than 2 keys except `toolchain_upstream` (TA-12). | computed E2 | CONFIRMED (1 key under every OP-2) |
| 4 | **RV4-D-A07** OP-2 (iii) root co-signature | **REFUTED.** The route is removed: source and inputs are selected at registration, bytes by reproducers; the option no longer exists. | computed E2 plus design | CONFIRMED |
| 5 | **RV4-B-A03 FB1** revoked binary, revocation withheld | **REFUTED.** `STATE_NOT_HELD_OR_FINGERPRINT_MISMATCH`, and with every statement served, `BINARY_REVOKED`. | executed E3 FB1a, FB1b | CONFIRMED path (b) `PASS (A2-A6)` |
| 6 | **RV4-B-A03 FB2** remediated compromise, root v1 metadata | **REFUTED.** `STATE_NOT_HELD_OR_FINGERPRINT_MISMATCH`, and with everything served, `BINARY_REVOKED`. | executed E3 FB2a, FB2b | CONFIRMED path (b) `PASS (A2-A6)` |
| 7 | **RV4-B-A04** moved tag; planted binary prints genuine lineage and TBM | **REFUTED.** `RELEASE_UNREGISTERED_OR_NOT_REPRODUCED`; the candidate was not executed. | executed E3 FB3 | CONFIRMED path (c) `PASS` (executes the candidate) |
| 8 | **RV4-B-A04 / `11` Phase 4** self-verification | **REFUTED.** The executor is `gov-accept`. The legacy 4.1.5 `gov` has no `verify-artifact` (help lacks it; `trust` exits 2). | executed E3 FB4 plus design | CONFIRMED (design) |
| 9 | **RV4-D-A04** ceremonies on the unaccepted binary | **REFUTED.** 0 of the proposal executor's runs executed a candidate. The typed values are consumed by the executor; R-CER-1 forbids TA-5 ceremonies before acceptance. | executed E3 DA04 plus design | CONFIRMED (design) |
| 10 | **RV4-B-A08** pinned regex retention, higher-sequence mix, consumption | **REFUTED.** Closed rule exit 3 at 1800 and at 1700. On 4.1.5 the effective content excludes the `ASIA…` file (SAM); the revision-4 content indexes and returns it. | executed E4 P, C | CONFIRMED exit 0; secret indexed |
| 11 | **RV4-D-A02 T1–T4** (tool descriptor, invariant, schema, skill) | **REFUTED ×4.** Closed rule exit 3 at 1800 (open rule also 3). | executed E4 T | CONFIRMED exit 0 ×4 |
| 12 | **RV4-D-A06** Git-delivered forged final, no gate | **REFUTED.** E7 at **use** refuses an unregistered release; `release-final` confers nothing. | executed E4 (unregistered sequences exit 3) plus design | CONFIRMED (design) |
| 13 | **RV4-D-A10** forged final naming an older Trust Policy | **REFUTED.** Judged against effective registrations; a release unregistered there refuses. | executed E4 (stale-machine rows) plus design | holds in revision 4 |
| 14 | **RV4-C-A01 / RV4-D-A01** subdirectory legacy escape (consolidated MEDIUM RV4-M1) | **NOT_RUN.** SAM does not change the layout. RV4-M1 is carried: the closed entry set recorded by the install transaction selects `COMPLETE` (SEL-1). | design | CONFIRMED by review r4 (C matrix reproduced by D) |
| 15 | **RV4-D-A03** oracle regression sensitivity (RV4-M7) | **PASS for SAM's new rules.** E3: 12 of 13 mutants detected, 1 equivalent under KS-7. E4: open, union and latest each fail at least one vector; closed matches 6 of 6. The 20 revision-4 mutants are carried. | executed E3, E4 | CONFIRMED 9/20 (review r4) |

Carried non-blocking probes (not re-derived):
- **RV4-B-A05** (RV4-M2), **RV4-B-A13** (RS-2 restated), **RV4-B-A14** (RV4-M3, now the registered witness input): SAM does not
  change them.
- **RV4-B-A15** (RV4-M5): absorbed. Migrations are registered units (E4 M: the weaker M-017 at 1800 is refused under both
  rules), plus CR4-B-04.

## 4. Review r3 blocking probes against SAM

| # | Probe | SAM result | Evidence |
|---|---|---|---|
| 16 | **RV3-B-A01** precedence moved to `immutable` | **REFUTED** (retained mechanism): exit 3; project strengthening kept on 4.1.5 | executed E0 (identical) |
| 17 | **RV3-D-A01/A02** order lattice, TPS tightening | **REFUTED** (retained): 0 unsound pairs; tightenings are computed reductions | computed E0 (identical) |
| 18 | **RV3-D-A10** registered-file removals R01–R09 | **REFUTED** (retained): exit 2 | executed E0 (identical) |
| 19 | **RV3-B-A02** stale CI pin (100 d, 400 d) | **REFUTED** (retained pin validity); image acceptance is re-run at pin cadence (R-SUB-3) | computed E0 (P4r4 identical) |
| 20 | **RV3-B-A06** threshold-1 witness | **REFUTED** (retained witness purpose) | computed E0 |
| 21 | **RV3-B-A12 / RV3-D-A12** higher unchained TSS | **REFUTED** (retained inclusion). On first install, a trust-state thief's TSS is never selected by the owner's typed fingerprint (E3 N-FB5 `BINARY_NOT_PUBLISHED`). | computed E0; executed E3 |
| 22 | **RV3-D-A15** revoked binary on pinned CI | **REFUTED**: A3 selection plus A4 negatives, in running mode by currency proof and on first acceptance by fingerprint | computed E0; executed E3 FB1 |
| 23 | **RV3-B-A08** `release-final` names the source | **REFUTED**: `release-final` is not an authority (R-REG-6). A reproduction naming another source is not counted (E3 V09 `REPRODUCTION_QUORUM_NOT_MET`); `rf` appears in no SAM minimal set. | executed E3; computed E2 |
| 24 | **RV3-D-A03** OP-4 "no" | **REFUTED**: `rc` and `rf` appear in no SAM minimal set | computed E2 |

## 5. New attacks by this specialist

| ID | Attack | SAM result | Class, evidence | Notes |
|---|---|---|---|---|
| N01 | **poisoned input mirror** used by every honest builder | **REFUTED**: inputs by digest (R-REP-2) | computed E2 `evil_mirror` | revision 4 and RID: **CONFIRMED {input_mirror}, zero keys**, when inputs are fetched from the CI-named mirror |
| N02 | **malicious build inputs named by the release process** (toolchain in `build_inputs_digest`) | **REFUTED**: needs the registration quorum (R-REG-3) | computed E2 `evil_toolchain` | revision 4 S0/S1/S2 and RID S1/S2: **CONFIRMED {pipeline}, zero keys**, when the verifier does not evaluate input legitimacy (the text states no such check) |
| N03 | compromised upstream toolchain release | **CONFIRMED residual** TB-S2 (TA-12): {toolchain_upstream} in every row | computed E2 | `03` OC-3 |
| N04 | reproductions submitted through the pipeline | **CONFIRMED if R-REP-3 is dropped**: {pipeline, 2 reproducer keys} | computed E2 `via_pipeline` | R-REP-3 is architecture minimum |
| N05 | 2 reproducer keys + trust-state key + transport against a pinned (P1) machine | **CONFIRMED** stated minimum TB-S1 | computed E2 | 3 keys + transport |
| N06 | registration quorum + pipeline + trust-state key + transport | **CONFIRMED** stated minimum | computed E2 | OC-1 decides whether this is 2 root keys or 2 delegated keys |
| N07 | fingerprint typed from a stale channel page (t5; binary revoked in t9) | **CONFIRMED residual** RS-B1: `ACCEPTED`, `issued_at` shown | executed E3 N-FB1 | TA-5 |
| N08 | attacker lineage served in place of the owner's; fingerprint grinding | **REFUTED**: `STATE_NOT_HELD_OR_FINGERPRINT_MISMATCH` | executed E3 N-FB2 | second preimage on 128 bits ≈ 2^128; the 8-hex lineage label alone would be ≈ 2^32, so the label is never compared alone |
| N09 | right binary, wrong target | **REFUTED** | executed E3 N-FB3 | — |
| N10 | one stolen reproducer key signs a conflicting digest | **CONFIRMED residual** AV-S1 (availability): `REPRODUCTION_CONFLICT` | executed E3 N-FB4 | — |
| N11 | 2 reproducer keys + trust-state key publish B8x; transport withholds honest reproductions; operator types the owner's fingerprint | **REFUTED**: `BINARY_NOT_PUBLISHED` | executed E3 N-FB5 | — |
| N12 | same, with the channel compromised | **CONFIRMED** outside TA-5: `ACCEPTED` | executed E3 N-FB6 | needs channel + trust-state key + 2 reproducer keys + transport |
| N13 | substituted `gov-accept` (revocation check removed) | **REFUTED given R-FA-2**: digest differs from the channel's | executed E3 N-FB7 | an operator skipping the comparison is outside TA-5 |
| N14 | accepted binary replaced after install in a same-uid location | **CONFIRMED residual under OC-4 (b)**; the predicate reports `location_protected: false` | executed E3 N-FB8 | a same-uid read-only mode is no protection (chmod) |
| N15 | malformed-root and counting attacks: root below threshold, bad link, bad TSS signature, one key counted twice, one statement with two keys, reproduction naming another source, revoked-but-granted keys | **REFUTED ×7** | executed E3 V09–V16 | conformance vectors |
| N16 | superseded (4.1.6) content under a forged gap sequence 1650 | **REFUTED (closed)**: exit 3 | executed E4 | open rule: **CONFIRMED** exit 0 |
| N17 | sequence inflation (current content at 10^9; E10 high-water poisoning) | **REFUTED (closed)**: exit 3 | executed E4 | open rule: **CONFIRMED** exit 0 |
| N18 | stale Trust Policy machine + 4.1.6 content at 4.1.8-x's sequence | **REFUTED (closed)**: exit 3 | executed E4 | open rule: **CONFIRMED** exit 0 (RS-1-equivalent) |
| N19 | Trust Policy rewrites an existing registration entry | **REFUTED**: `REGISTRATION_REWRITE` detected | executed E4 R | — |
| N20 | owner reversion of a fixed regex without a gate | **REFUTED**: reported as `registration_reversion` (computed reduction) | executed E4 R | — |
| N21 | weaker migration file carried by a later release | **REFUTED** under both rules | computed E4 M | the pack checker does not pin migration digests; SAM does |
| N22 | owner contract set: Markdown v2 + compiled YAML v1 on a pinned machine | **REFUTED**: `OWNER_CONSTITUTIONAL_GROUP_UNCONFIRMED` | computed E4 G | revision 4 per-path slots: **CONFIRMED** accepted |
| N23 | additive secret pattern with an invalid regex (does an addition weaken?) | **REFUTED**: checker exit 0 (additive) and on 4.1.5 the `ASIA…` file stays excluded | executed E4 A, C | `secrets.rs` compiles per pattern |
| N24 | global registration of a new required member | **CONFIRMED on revision 4** (INFO): the "union" rule refuses legitimate installed 4.1.6 at 1600 with exit 2. SAM (closed): exit 0. | executed E4 `lookup_mutants` | part of why revision 4's retention was forced |
| N25 | reproducibility depends on VCS state | **CONFIRMED precondition**: `runtime/build.rs` falls back to `git rev-parse HEAD` for provenance | design (code) | R-REP-7 must remove it for production builds |
| N26 | genuine binary revoked after image build, revocation withheld from the runner | **CONFIRMED bounded residual** RS-1c (≤ `pin_max_validity_days`); self-restriction applies when the revocation arrives | design plus E0 P4r4 PIN_WINDOW | — |
| N27 | delegated registration quorum (OC-1 (b)) as a concentrated target | **CONFIRMED consequence**: 2 delegated keys can register weaker non-orderable content and source for new releases; floors and precedence still hold | design plus E2 | `03` OC-1 |
| N28 | specificity of SEL-1: does it flag mechanisms the reviews confirmed sound? | **PASS**: 0 of 12 sound rows flagged. All 18 HIGH rows (14 findings) and 10 MEDIUM/LOW rows flagged. | design-encoded E1 | classification by this specialist |
| N29 | all reproducers under one custodian | **CONFIRMED residual** TB-S3 (TA-10′): not verifier-checkable | design | same class as root custody |
| N30 | insider source accepted by a deceived verifier and ceremony (route I) | **CONFIRMED residual** TB-4 (retained) | design | — |

## 6. Tests of the review's stated invariants

| Stated invariant | Test | Result | Evidence |
|---|---|---|---|
| CD4-1 (independent parties at threshold) | literal closure RID | **insufficient**: {pipeline} (named inputs) and {input_mirror} (mirror) with zero keys, under stated readings | E2 RID rows |
| CD4-2 (same anchored decision over externally measured digests) | post-acceptance replacement; executor substitution; stale channel | **insufficient**: execution binding and executor authenticity missing; channel currency unlabelled | E3 N-FB8, N-FB7, N-FB1 |
| CD4-3 (per sequence; "release identity or a sequence range") | open ranges vs exact | **insufficient for ranges**: gap, inflation and stale-policy cases admitted; only exact registration matches 6/6 | E4 `lookup_mutants` |

## 7. Counts

| Group | Items | REFUTED | CONFIRMED (residual, consequence or control) | PASS | NOT_RUN |
|---|---:|---:|---:|---:|---:|
| Review r4 blocking probes | 15 | 13 | — | 1 | 1 |
| Review r3 blocking probes | 9 | 9 | — | — | — |
| New attacks | 30 | 15 | 14 | 1 | — |
| **Total** | **54** | **37** | **14** | **2** | **1** |

Revision-4 controls confirmed in the same runs:
- r4 probes 1–11 (11 controls, one per probe);
- N01, N02, N22, N24 (4 controls on revision 4) and N16, N17, N18 (3 controls on the open-range reading).

Oracle and vector counts:
- **E3:** 16/16 vectors as expected; 12/13 mutants detected, 1 equivalent under KS-7; 57 OpenSSL verifications.
- **E4:** lookup rules: closed 6/6; open, union and latest fail.

## 8. Limits and what was not run

- **No RoT-1 binary exists.** SAM's executor is a prototype. Its world is a toy lineage (deterministic keys, shell-script
  candidates) with real Ed25519.
- **E2 is symbolic.** Where revision 4's text does not fix a behaviour (input fetch; the verifier's evaluation of inputs), both
  readings are reported. The zero-key revision-4 routes hold only under the readings named.
- **E1 is design-encoded.**
- **Not re-run:** reviewer C's 10,618-invocation matrix and the architect's P3r3. SAM does not change the layout, and review r4
  D reproduced C's matrix.
- **Consumption stand-in.** The 4.1.5 binary shows what content does when effective; the choice of effective content is the
  checker plus the projection.
