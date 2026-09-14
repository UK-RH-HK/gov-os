# 02 — Adjudication of reviewers B and C (review r4 synthesis D, AR-0008)

Vocabulary: `CONFIRMED` (severity kept or changed, with reason), `REFUTED` (with evidence), `DUPLICATE`. Every probe
cited was re-run (`01-REPRODUCTION.md`).

## Reviewer B (AR-0006, `152e68e`)

| Item | B severity | Adjudication | Reason | Consolidated |
|---|---|---|---|---|
| RV4-B-H1 | HIGH | **CONFIRMED HIGH** | R07 AF1: custodian and publisher stages `PASS`, `verify_artifact` `ACCEPTED`, world identical to VA4 route B; R06 `BC`: {ba, pipeline} under every OP-2 source authority and OP-4 answer. The custodial rules of `05` §7 rule 6 and `25` §9 contain no rebuild, and OP-2 (iii) root co-signers run the same stage (D-A07). The pack's route S counts pipeline input, so evaluating route B without it is inconsistent. Same outcome and adversary as RV3-H3. | RV4-H1 |
| RV4-B-H2 | HIGH | **CONFIRMED HIGH** | R07 AF3 and R06 `FB1`/`FB2`: A2–A6 tooling accepts revoked and remediated binaries; R09 part B: path (c) passes on self-report. `06` §2 step 6 and `25` §6 read as B states; `11` Phase 4 self-verifies. Not the unavoidable core: the channel already publishes the state fingerprint. D-A04 extends it to the first-install ceremonies. | RV4-H2 |
| RV4-B-H3 | HIGH | **CONFIRMED HIGH** | R08 part P executed on 4.1.5 (mixed release exits 0 and indexes the `ASIA…` file). D-A02 shows the same for tool descriptors, invariants, schemas and skills; D-A10 shows the variant naming an older TPS is refused, so the class is exactly retention. Retention is forced by `19` §5.2's `SURFACE_VALUE_UNAVAILABLE` for installed releases. | RV4-H3 |
| RV4-B-M1 | MEDIUM | **CONFIRMED MEDIUM** | R09 part A reproduced. Not raised: code the account later runs is A3 (RS-3, TG-2); system pins stay out of reach; the fix is a bound confinement rule plus a TCB-location predicate. | RV4-M2 |
| RV4-B-M2 | MEDIUM | **CONFIRMED MEDIUM** | `05` §7 rule 10 and `07` §7 step 16 name no input; OP-7 (c) is not the proposal. | RV4-M3 |
| RV4-B-M3 | MEDIUM | **CONFIRMED MEDIUM** | R06 LB3. Revision 4 removed statement-driven raising of `clock_high_water` (CR-06) while `24` §10 still claims detection. SV-11 already refuses future statements, so statement-driven raising is safe again on stateful machines; the stateless case rests on TA-7 and must be stated. | RV4-M4 |
| RV4-B-M4 | MEDIUM | **CONFIRMED MEDIUM** | `19` §9 evaluates only a recorded vector; P1r4 M5 reproduced. | RV4-M5 |
| RV4-B-L1 | LOW | CONFIRMED LOW | R08 U01, U02 exit 0 | RV4-L1 |
| RV4-B-L2 | LOW | CONFIRMED LOW | R06 LB2 | RV4-L2 |
| RV4-B-L3 | LOW | CONFIRMED LOW | R06 LB1 | RV4-L3 |
| RV4-B-L4 | LOW | CONFIRMED LOW | R06 AT1, AT2 | RV4-L4 |
| RV4-B-L5 | LOW | CONFIRMED LOW | schema read | RV4-L5 |
| RV4-B-L6 | LOW | CONFIRMED LOW | `25` A8 read | RV4-L6 |
| RV4-B-L7 | LOW | CONFIRMED LOW | `21` lines 132–134 read | RV4-L7 |
| RV4-B-I1 | INFO | CONFIRMED INFO | unchanged | RV4-I1 |
| B status: BC-1 `CLOSED` | — | CONFIRMED | R01, R02, R05, R10, R14, R15 | — |
| B status: RV3-H2 `CLOSED` as stated; BC-2 narrowed → H2 | — | CONFIRMED | R03, R06 | — |
| B status: RV3-H3 `CLOSED` as stated; BC-3 open → H1 | — | CONFIRMED | R04, R07 | — |
| B status: BC-4 `OPEN` | — | CONFIRMED, broadened (D-A04, A05, A06, A07) | — | CD4-4 |
| B residual determinations | — | CONFIRMED, with LR-2 and VR-3 conditions added from RV4-M1 | `05-RESIDUALS.md` | — |
| B §3.4 "not assessed" | — | noted; D determines §3.4 | `04` | — |

## Reviewer C (AR-0007, `c6b8ba9`)

| Item | C severity | Adjudication | Reason | Consolidated |
|---|---|---|---|---|
| RV4-C-H1 subdirectory escape | HIGH | **CONFIRMED (reproduced), re-rated MEDIUM** | R17 and R20 reproduce the writes and `COMPLETE`. D-A01 tests what they reach. (a) From `governance/trust/`, a nested-root legacy CIT rewrites `governance/trust/kernel/policies/SECURITY_POLICY.yaml`: the installed kernel tree changes, which `18` §6.1 step 5 makes `KERNEL_TAMPERED` (fail closed). (b) From `governance/`, a CIT deleting `trust/framework.lock` leaves the state `PARTIAL`. (c) From `governance/trust/kernel/`, `init` itself adds files to the installed kernel: `KERNEL_TAMPERED`. (d) Litter under `governance/trust/` changes no statement, kernel, lock or occupation entry. (e) An overlay-only rewrite from `governance/` leaves `COMPLETE`, is `PROJECT_STRENGTH_WEAKENED` on a recorded machine (architect's strength functions), and is accepted by fresh clones under LR-4: the bounds accepted for LR-2 in review r3 and by C here. C's own scope note says no trust-decision bypass was demonstrated. The correction tightens a state predicate, root discovery, rule text and tests, so it is carriable. | RV4-M1 |
| C status: "R2-H4 NOT CLOSED as a class" | — | **REFUTED as stated** | HO-0001 §3.4's class property — no silent mutation of kernel or trust state into a state treated as valid — holds on D-A01's evidence. The occupation class argument (`26` §3) and rules (10), (12) overstate their scope; that is RV4-M1. | §3.4 SATISFIED with RV4-M1 |
| RV4-C-M1 retained `.gitignore` line | MEDIUM | **CONFIRMED MEDIUM** | R18 R4 vs R4APP identical; fail closed | RV4-M6 |
| C: LR-2 / RV3-M6 bound holds | — | CONFIRMED | R19 | LR-2 |
| C: C-2 … C-5 carried; C-1a, C-6 new | — | CONFIRMED as carried constraints; C-1a merged into RV4-M1 | — | `11` §6 |
| C: residual determinations | — | CONFIRMED; VU-10 "not accepted as a pre-RoT invariant" merged into RV4-M1 | — | `05-RESIDUALS.md` |
| C: RV4-C-A03 … A10 "Pass" verdicts | — | CONFIRMED for A03–A07 (executed, reproduced within R19/R18/R20); A08–A10 design, specification only | — | — |

## Missed by both

| Item | Finding |
|---|---|
| The conformance oracle detects 9 of 20 plausible single-rule regressions; five have no RT, including the "held" clause of inclusion anchors | RV4-M7 (D-A03, D-A03b) |
| First-install ceremonies (OP-6 (a), `confirm-state`, P2 in-gate fingerprints) are evaluated by the unaccepted binary | extends RV4-H2 (D-A04) |
| OP-2 (iii) root co-signature does not stop malicious bytes for genuine attested source | extends RV4-H1 (D-A07) |
| The `release-final` blast radius lists an ingress gate that Git-delivered use never passes | RV4-L8 (D-A06) |
| OP-2 (S1) turns each binary release into a computed reduction | RV4-L9 (D-A05) |
| Owner-domain slots cannot bind the contract's hash-bound set; multi-pin resolution undefined | RV4-L10 (D-A08) |
| Retention breadth beyond one secret pattern | extends RV4-H3 (D-A02) |
| Nested legacy installs from `governance/` and `governance/trust/kernel/`; nested installs make every legacy command operational beneath them; RoT-1 root discovery unspecified | extends RV4-M1 (D-A01, D-A09) |
