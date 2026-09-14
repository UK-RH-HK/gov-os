# 02 — Falsification of the specialist-B alternative (AR-0010)

This file attacks `01-ALTERNATIVE.md` with:
- every blocking probe of review r3 and review r4;
- new attacks authored by this run.

Results that go against the proposal are reported as they came out.

## 1. Method, hygiene, evidence classes

| Class | Meaning |
|---|---|
| **E** | executed: the revision-4 checker (unmodified) on sequence projections, the real legacy 4.1.5 binary as consumer, real Git, real `cargo` builds |
| **C** | computed: this run's models (F1, F2), which load reviewer B's review-r4 reference model unmodified for anchors, inclusion, currency and the negative set |
| **D** | design reading |

**Hygiene.**
- Environment: every probe ran under `env -i`, with `HOME`, `XDG_*`, `AR10_SCRATCH` and `GOV_KERNEL_CACHE` in
  `…/scratchpad/ar-0010/` and `PYTHONDONTWRITEBYTECODE=1`. No other `GOV_*` variable reached any child.
- Legacy binaries: used read-only (SHA-256 in F0).
- Canonical checkout: never written.
- Deletions: no forced deletes.

**Baseline.** Before any modelling, reviewer and architect instruments were re-run unchanged (F0):
- reviewer B's reference model: identical;
- VA4: identical;
- the CSI self-test: 56 passed, 0 failed;
- D-A02: identical;
- reviewer B's surface probes on real 4.1.5: identical;
- the review-r3 probe copies RV3-B-A01, the CSI injections, the D lattice and the D forward-compatibility/removal probe:
  identical to review r4's re-run after path normalisation.

Three first attempts failed only because a scratch parent directory was missing; they were re-run.

**Construction errors found and corrected in this run (reported, not hidden).**
- F2's first run failed one of 32 scenarios: the RV3-D-A15 honest control put the revocation only in the TSS `revs`
  list. Both models take the negative set from revocation statements (`17` S5), so the scenario was wrong. The revocation
  statement was added; the scenario then refuses (`ARTIFACT_REVOKED`).
- Both predicates first checked anchors last, which produced correct refusals with misleading codes. The trust-state
  gate was moved first. F1's minimal sets did not change.
- F4's first tree-archive comparison was confounded by `git archive` stamping the current time on tree archives. This
  became a finding (N09).

## 2. Blocking probes of review r4

| Probe | What it attacks | Revision 4 | Alternative | Class, evidence | Result |
|---|---|---|---|---|---|
| **RV4-B-A01** route B, honest custodians | one `build-attestation` key + pipeline | `ACCEPTED` | `BUILD_QUORUM_NOT_MET` (F1 trace `rev4_route_B_prime`); minimal sets `{ba1, ba2, pipeline}`, `{ba1, ba2, ts}` | C: F1 | **FLIPPED** (minimum raised to 2 first-hand keys + 1) |
| **RV4-B-A02** route S, honest signers | one `verification-attestation` key + pipeline | `ACCEPTED` (S0, REJECTED not reaching) | L1: `NO_FINAL`; L2: needs two verifier keys | C: F1 | **FLIPPED** |
| **RV4-B-A06** capability enumeration | every subset × options | 1 key + pipeline | 32 configurations (L1/L2 × *q* 2/3 × OP-4 × REJECTED reaching); 0 minimal sets with fewer than 2 first-hand establishers | C: F1 `invariant_check` | **FLIPPED** |
| **RV4-D-A07** OP-2 (iii) pass-through by root co-signers | root threshold that does not establish the fact | co-signs malicious bytes | no purpose signs received bytes; root custodians sign admissions only on two first-hand verification records (`{rf, pipeline}` → `NOT_ADMITTED`) | C: F1 | **FLIPPED** |
| **RV4-B-A03** revoked binary to first-install tooling; remediated compromise with root v1 | first TCB | tooling `PASS` | `TRUST_STATE_BELOW_ANCHOR` / `ARTIFACT_REVOKED`; remediated: `BELOW_ANCHOR`, `INCOMPLETE(root_reference_unresolved)`, `BUILD_QUORUM_NOT_MET` | C: F2 | **FLIPPED** (5 variants) |
| **RV4-B-A04** moved tag; self-report; Phase 4 | first TCB | procedure (c) passes; Phase 4 self-validates | quorum or source mismatch; the candidate is never executed (E: F4 part B `candidate_executed_by_admitter: false`); `SELF_EVALUATION_REFUSED` | C: F2; E: F4 | **FLIPPED** |
| **RV4-D-A04** first-install ceremonies on the unaccepted binary | TA-5 | ceremonies run | genuine unadmitted binary: `BINARY_NOT_ADMITTED` for `confirm-root` and `confirm-state`; malicious binary: TB-1′ (stated) | C: F2; D | **FLIPPED** for genuine binaries; residual stated |
| **RV4-B-A08** retained superseded pinned digest (part P) | constitutional content | checker exit 0; `ASIA…` indexed on 4.1.5 | exit 3 at sequence 8 (open and closed forms); consumer excludes the file | E: F3 | **FLIPPED** |
| **RV4-D-A02** T1–T4 breadth | tool descriptor, invariant, schema, skill | exit 0 under RETAIN | exit 3 for all four, both forms; installed 4.1.6 and fixed 4.1.7 exit 0 | E: F3 | **FLIPPED** |
| **RV4-D-A06** Git-delivered higher-sequence forged final | blast radius | policy root at use, no gate | ineligible at use (E7 at its sequence; E1: not admitted) | E: F3; D | **FLIPPED** (E2-open residual RS-E2o: N04) |
| RV4-D-A10 forged final naming an older TPS | bound | holds | holds (effective values from the sequence registration of the effective TPS) | D | HOLDS |
| RV4-C-A01 / RV4-C-H1 subdirectory escape (re-rated MEDIUM, carried RV4-M1) | legacy containment | writes under `governance/trust/**` with `COMPLETE` | mechanism unchanged by this proposal; carried with review r4's acceptance test | D | **NOT_RUN** (no change to the attacked mechanism) |

## 3. Blocking probes of review r3

| Probe | Revision 3 finding | Alternative | Class, evidence | Result |
|---|---|---|---|---|
| RV3-B-A01 kernel precedence → `immutable` | RV3-H1 | mechanism kept from revision 4; probe copy re-run: identical to review r4 (refused, exit 3) | E: F0 | HOLDS |
| RV3-D-A01 / A02 lattice and TPS tightening | RV3-H1 | kept; lattice probe re-run identical (0 unsound pairs) | E: F0 | HOLDS |
| RV3-D-A10 removal of registered content | RV3-H1, RV3-M7 | kept; forward-compatibility/removal probe re-run identical | E: F0 | HOLDS |
| RV3-B-A02 stale CI pin | RV3-H2 | through AP: `TRUST_STATE_NOT_C3(UNANCHORED)` | C: F2 `RV3-D-A15_i` | HOLDS |
| RV3-B-A06 witness minted by the trust-state key | RV3-H2 | kept (revision-4 witness purpose); reviewer B's section R re-run identical | C: F0 | HOLDS |
| RV3-B-A12 / RV3-D-A12 higher unchained TSS | RV3-H2 | through AP: `TRUST_STATE_BELOW_ANCHOR` | C: F2 | HOLDS |
| RV3-B-A13 matrix | RV3-H2 | kept; reviewer B's 336-row matrix re-run identical | C: F0 | HOLDS |
| RV3-D-A15 revoked binary on pinned CI (stale pin; current pin + t100; honest control) | RV3-H2 | refused in all three | C: F2 | HOLDS |
| RV3-D-A11 oracle cannot distinguish anchor semantics | RV3-M9 | P4r4 distinguishes (review r4 reproduced); F2's mutation self-check detects 18 of 18 rule removals, including `no_anchor_inclusion` | C: F2 | HOLDS |
| RV3-B-A08 `release-final` names the source | RV3-H3 | V8 kept; F1 `{rf, pipeline}` → `NOT_ADMITTED` | C: F1 | HOLDS |
| RV3-D-A03 OP-4 "no" × source | RV3-H3 | F1 `OP-4_no_everyday_key_plus_pipeline` → `NOT_ADMITTED` | C: F1 | HOLDS |

## 4. New attacks against the alternative

Results use the vocabulary of `AGENT_RUNS/README.md`:
- **HOLDS** — the attack is refused;
- **CONFIRMED** — it succeeds, and a stated minimum, cost or residual applies;
- **FINDING** — a defect or missing rule was found.

| ID | Attack | Expected if the alternative is sound | Observed | Class, evidence | Result |
|---|---|---|---|---|---|
| N01 | Two stolen `build-attestation` keys + pipeline (the proposal's own minimum) | accepted, and stated as the minimum | `ACCEPTED`; *q* = 3 → `BUILD_QUORUM_NOT_MET` | C: F1 | CONFIRMED (stated minimum) |
| N02 | Two stolen build keys, no pipeline, no trust-state key | refused | `UNREFERENCED`: the honest publisher saw only the honest quorum digest | C: F1 | HOLDS |
| N03 | Two compromised verification processes + pipeline, under L1 | accepted, stated as a process residual | `ACCEPTED`; stealing the keys only, `{va1, va2, pipeline}`: `NO_FINAL` | C: F1 | CONFIRMED (TB-4′) |
| N04 | E2-open: a machine holding only TPS v1; a forged 4.1.8 carrying 4.1.6 content | refused, or stated | exit 0 (also with an additive member); E2-closed exit 3 | E: F3 | CONFIRMED (RS-E2o; owner choice OC-3) |
| N05 | E2-closed availability: a genuine 4.1.8 identical to 4.1.7 before registration | refused until registered | exit 3; after TPS v3 registers sequence 8: exit 0; the forged mixed release after v3: exit 3 | E: F3 | CONFIRMED (cost) |
| N06 | An honest or compromised root re-registers the superseded regex for sequence 8 | computed reduction | `content_reversion` + `registration_rewritten`, exit 6; with `lowering_history` exit 0. The unmodified revision-4 `reductions` tool on projections: exit 0 in open form. Closed form: exit 6, but only because the probe's v3 registers one key for sequence 8. | E: F3 | HOLDS for the new rule; **FINDING** on revision 4 (reversion invisible to `reductions`) |
| N07 | The root reversion declared in `lowering_history` | the per-project gate is the remaining protection | forged mixed release eligible at sequence 8: open form exit 0 (the reversion is the registered content); the per-project `policy_lowering` gate (revision 4 `19` §10.6) still applies to projects holding the stronger registration | E: F3; D | CONFIRMED (bound: root threshold + local gate) |
| N08 | Rewrite what registered sequence 6 means | computed reduction | `registration_rewritten`, exit 6 | E: F3 | HOLDS |
| N09 | Source identity by `git archive` (revision 4 `25` §4) | a content identity any holder of the tree can recompute | archive of a commit: deterministic, but binds the commit id (pax comment); same tree under another commit: digest differs; archive of a tree: differs between runs 1.2 s apart (time-stamped); canonical content digest: equal across repositories, changes on a moved tag | E: F4 | **FINDING** on revision 4; the alternative uses the canonical content digest |
| N10 | Measure, then swap the file before install | installed bytes = measured bytes | install by re-reading the path: `false`; install from the measured buffer: `true` | E: F4 | HOLDS with the buffer rule; **FINDING**: no revision-4 rule states it for binary install |
| N11 | A planted binary that prints the genuine TBM | refused without executing it | `ARTIFACT_BUILD_QUORUM_NOT_MET`; marker file absent | E: F4 | HOLDS |
| N12 | Reproducer independence vs reproducibility | independent reproducers get identical bytes | same Cargo home, different source paths: identical. Different Cargo home paths: differ (188 path strings). Path-remapped profile: 4 builds at different paths and homes identical, 0 path strings. One machine, one toolchain (cargo and rustc 1.98.1). | E: F5 | CONFIRMED (precondition holds only with a normative remapping profile; cross-OS not shown) |
| N13 | Admitter substitution; one channel stale; both channels compromised | refuse; refuse; TA-5 core | `ADMITTER_DIGEST_MISMATCH`; `CHANNEL_DISAGREEMENT`; `{ch1, ch2}` minimal accepted set | C: F2 | HOLDS; CONFIRMED (AD-1) |
| N14 | A genuine revoked binary started without the admitter; a malicious binary started directly | refuse; stated | `BINARY_NOT_ADMITTED`; runs (TB-1′) | C: F2 | HOLDS; CONFIRMED (TB-1′) |
| N15 | CI image: record within validity with the revocation not held; expired; revocation held | stated bound; refuse; refuse | runs (C1–C2 exposure bounded by record validity, the RS-1c analogue); `ADMISSION_RECORD_EXPIRED`; `BINARY_REVOKED_SELF` | C: F2 | CONFIRMED; HOLDS; HOLDS |
| N16 | A writable Admission Record | refuse | `BINARY_NOT_ADMITTED` | C: F2 | HOLDS |
| N17 | Two quorum-attested digests held for one final | refuse | `ARTIFACT_EQUIVOCATION` | C: F2 | HOLDS |
| N18 | Forged quorum attestations injected to the publisher without suppressing the honest ones | publication blocked | publisher refuses on two quorum digests: the genuine release is not published | D; C: F1 logic | CONFIRMED (denial of service needing *q* keys + pipeline) |
| N19 | Rotation re-signs retained build attestations of a stolen key (revision 4 `05` §8 applies to "build attestations") | forged attestations are not laundered | revision 4: re-signing without re-reproduction re-issues the forged attestation under the successor key. Alternative: re-attestation requires re-reproduction. | D | **FINDING** on revision 4; HOLDS with the rule |
| N20 | Compromised admitted toolchain (trusting-trust) | stated | every honest reproducer attests identical malicious bytes | D | CONFIRMED (TB-2′) |
| N21 | Same-user code runs before first admission and writes a stale VTS anchor | not read | the fresh VTS at first admission moves it aside; forged records written after admission are A3 (RS-3) | D | HOLDS; CONFIRMED (AD-2) |
| N22 | OP-4 "no" merges `release-candidate` into `release-final` | no smaller minimal set | F1 `op4_no_changes_any_minimal_set: true`, only in sets of seven capabilities under L2; the smallest sets are unchanged in all 32 rows | C: F1 | HOLDS |
| N23 | Mutation self-check: remove each AP / admitter / genuine-binary rule | every removal detected | 18 of 18 detected | C: F2 | HOLDS |
| N24 | Revision 4's multi-digest RETAIN inventory under the new lint | malformed | exit 5 (`REGISTRATION_NOT_SINGLE_VALUED`) | E: F3 | HOLDS |
| N25 | Selector audit of the proposal: any remaining choice by a lower party among higher-trust alternatives | none unstated | see §5 | D | CONFIRMED (5 stated, 0 unstated) |

## 5. Selector audit (N25)

| Remaining selection | Selector | Among | Why not the class, or where stated |
|---|---|---|---|
| which legitimate binary is current | `trust-state` key | root-admitted, quorum-attested, unrevoked binaries | legitimacy is not selectable; sticky negatives and the accepted-TBM high-water bound downgrade (RV4-L4 carried) |
| tunable, `release_bound` and informational leaves of a registered sequence (E2) | `release-final` | any value | revision 4's accepted tunable blast radius; E1 removes it |
| content of later sequences on a machine holding an older TPS (E2-open) | `release-final` + withholding | the content that TPS registered | RS-E2o (N04); E1 and E2-closed remove it |
| which TSS a stateless machine sees | A2/A5 | genuine TSSs | inclusion anchors and currency (revision 4, kept) |
| which state fingerprint the operator types | the channel | published fingerprints | TA-5 core (AD-1) |

## 6. Counts

| Item | Count |
|---|---|
| Review-r4 blocking probes attacked | 12: 9 FLIPPED, 1 HOLDS, 1 FLIPPED with a stated E2-open residual, 1 NOT_RUN |
| Review-r3 blocking probes attacked | 11: 11 HOLDS (5 re-executed unchanged in F0, 6 through AP or F1) |
| New attacks authored | 25 (N01–N25). Primary result: 13 HOLDS, 10 CONFIRMED (stated minimum, cost or residual), 2 FINDING. Attacks that also raise a finding on revision 4: 4 (N06, N09, N10, N19). |
| Executed / computed / design (new attacks) | 10 E (N04–N12, N24) / 10 C (N01–N03, N13–N17, N22, N23) / 5 D (N18–N21, N25) |
| F1 configurations; invariant violations | 32; 0 |
| F2 scenarios; mutants detected | 32 of 32 hold; 18 of 18 |
| F3 executed checker cases | 45 exit results recorded, plus 2 consumer runs on real 4.1.5 |

## 7. Limits

- **No RoT-1 implementation exists.** AP, the admitter and the genuine-binary rule are models (C). The consumer is the
  legacy 4.1.5 binary standing in for what the selected content does (E), as in review r4 part P and P1r4.
- **E1 (admission by final digest) is computed**, in F1 and F2 through the RAS final-digest check, not executed on the
  checker.
- **Reproducibility** was shown on one machine, one OS image and one toolchain (F5). Cross-OS or cross-distribution
  reproduction was not attempted.
- **F1's honest-party rules are this run's specification** (01 §3.4). Where a real process lets the pipeline reach a
  party this model protects, the minimal sets shrink. The derivation calculator is proposed precisely so that the owner's
  real process model is the one computed.
- **Capability semantics** follow reviewer B's (A5 delivery free; pipeline = control of honest parties' inputs), with
  one addition: verifier-process compromise `vpN`.
