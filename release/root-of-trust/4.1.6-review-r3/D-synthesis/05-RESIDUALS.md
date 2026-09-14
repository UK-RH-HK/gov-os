# 05 — Residual determinations (AR-0004)

Every residual declared by revision 3 gets a final determination.

## Criteria

HO-0004 §3 requires "an explicit bound that holds under your attacks; documentation alone is not a bound". A residual is
**ACCEPTED** only if one of the following holds:
- **R-1 (excluded trigger).** The trigger needs a capability the trust model excludes, and the exclusion holds for that machine class as the architecture itself prescribes it.
- **R-2 (unavoidable and bounded).** All four of these hold:
  - (a) no design reasonable under the chosen assumptions removes or bounds it;
  - (b) the bound is stated exactly;
  - (c) no verdict surface presents the residual state as a stronger one;
  - (d) an acceptance test fails when the bound is exceeded.

Determinations use three values:
- **ACCEPTED**;
- **ACCEPTED WITH CONDITION**, naming the carried requirement that must hold;
- **NOT ACCEPTED**, naming the finding.

These criteria match reviewer B's RC-1/RC-2 and review r2 `09`.

## Freshness and trust state (`24` §10, `20` §10)

| ID | Declared residual | Attacks | Determination |
|---|---|---|---|
| RS-1 | A machine that never receives newer metadata cannot know it exists; bounded by T0, raised by anchors; no governed mutation unanchored under (a)–(c) | RV3-B-A02, A06, A12, A13 matrix; D-A12, D-A15 | **NOT ACCEPTED as stated** (RV3-H2). Core accepted: a machine anchored before a revocation and never contacted again (M3, M4, M6B, M7), shown with anchor age. Not core, failing R-2(a)–(c): sequence-satisfied anchors; pins with no currency bound shown `ANCHORED` and permitted `current`, C3 and binary acceptance; a single threshold-1 witness. |
| RS-2 | OP-3 mode B and OP-7 (b)/(c) trust the local clock | RV3-B-A07 | **ACCEPTED WITH CONDITION** RV3-M3 (CR-06) |
| RS-3 | A3 deletes or rewrites its own VTS, anchors or confirmations | RV3-B-A03, A04 | Deletion **ACCEPTED** (R-1: the machine becomes `UNANCHORED`, fails closed). Forging **ACCEPTED WITH CONDITION** RV3-M2 (CR-03). On CI, `gov`-executed repository commands write pins, so R-1 needs CR-03. |
| RS-4 | Pins provisioned by a party the repository writer controls | RV3-B-A03 | **ACCEPTED** as scoping, with the TA-9 restatement of CR-03 (integrity after provisioning) |
| RR-1 | Automatic rollback may leave an ineligible installation | reading | **ACCEPTED** (fails closed; remedy stated) |
| RR-2 | Machine without a per-project record accepts an A2-delivered older eligible release; an anchored machine "judges it at its anchor epoch" | RV3-B-A12; D-A12 | **NOT ACCEPTED as stated** (RV3-H2): "at its anchor epoch" does not hold under sequence anchors, and the epoch has no currency bound |
| RR-3 | A3 deletes the per-project record or VTS | reading | **ACCEPTED** (R-1) |
| OP-7 (d) residual | Under (d) a repository writer selects older genuine state for unanchored governed use | D-A04 | **ACCEPTED WITH CONDITION** RV3-L6 as an owner-selectable residual: the consequence must name binaries whose compiled TSS predates the newest TSS; labelled `FRESHNESS_UNPROVEN`, never C3 (matrix) |

## Constitutional Surface (`23` §10)

| ID | Declared residual | Attacks | Determination |
|---|---|---|---|
| CS-1 | Classification correctness is a root-ceremony responsibility; weak classification limited by lint | RV3-B-A01, A16; D-A01, A02, A10 | **NOT ACCEPTED** (RV3-H1, RV3-M7): the lint's anchor (the `23` §4 order) is unsound for the project layer; absence passes |
| CS-2 | Every final that changes pinned content needs a root-threshold TPS | reading | **ACCEPTED** (operational cost, RK-17) |

## Binary and TCB (`25` §9)

| ID | Declared residual | Attacks | Determination |
|---|---|---|---|
| TB-1 | The binary remains the TCB; an unverified binary is outside the chain | D-A13 | **ACCEPTED WITH CONDITION** RV3-M8: the first-run self-check as written refuses every genuine binary after the next TSS |
| TB-2 | Build attestation trusts the rebuilder's environment | RV3-B-A08 | **ACCEPTED** only for what it bounds (bytes equal a build of `source_commit`); source choice is RV3-H3 |
| TB-3 | Accepted malicious binary needs release-artifact ×2 + build-attestation + trust-state | RV3-B-A08; D-A03 | **NOT ACCEPTED** (RV3-H3) |

## Verify-and-use (`18` §11)

| ID | Declared residual | Determination |
|---|---|---|
| VR-1 | A3 modifies installed files between units of work | **ACCEPTED** (VU-11; spec-only; RT-86 must exist) |
| VR-2 | A3 ignores advisory locks | **ACCEPTED** (refusals only) |
| VR-3 | Non-`gov` subprocesses write PPS, overlay, records, VTS | PPS detection **ACCEPTED**; records never authorising trust **ACCEPTED**; overlay detection by the strength vector **NOT ACCEPTED** as complete (RV3-H1, RV3-M5); VTS and pins **ACCEPTED WITH CONDITION** RV3-M2 |
| VR-4 | Plugin runtimes and model files consumed by path | **ACCEPTED** (unchanged; not attacked) |

## Legacy containment (`26` §8)

| ID | Declared residual | Attacks | Determination |
|---|---|---|---|
| LR-1 | Legacy binaries on a working copy that has not checked out the RoT-1 layout operate normally | C A09; D-A05(c) | **ACCEPTED** (no RoT-1 state in that tree) |
| LR-2 | A3 removes occupation entries → RoT-1 `PARTIAL`; "not a RoT-1 layout" | C A04–A06; D-A05, D-A06 | **ACCEPTED WITH CONDITION** RV3-M6. **Holds:** RoT-1 binaries fail closed (`PARTIAL`, `KERNEL_TAMPERED`); overlay weakening is detected on recorded machines. **Must be stated and tested:** the trigger includes a single Git restore of pre-migration paths; the legacy binary then has a `verified: true` install that serves material classified only after migration, and it can write `governance/trust/**` and the overlay. |
| LR-3 | Explicit operator output paths of producer commands | reading | **ACCEPTED** |
| LR-4 | Fresh clones accept the repository overlay | D-A06 | **ACCEPTED** (A2 authority over project configuration; per-machine detection after a record) |

## Trust gates (`27` §7)

| ID | Declared residual | Determination |
|---|---|---|
| TG-1 | A decision on one machine does not authorise another | **ACCEPTED** (by design) |
| TG-2 | A3 writes the VTS or drives a pseudo-terminal | **ACCEPTED WITH CONDITION** RV3-M2 (decision pins are the automation path) |
| TG-3 | Non-trust gates forgeable by A2 | **ACCEPTED** (R-1 for trust facts) |

## Summary

| Determination | Residuals |
|---|---|
| NOT ACCEPTED | RS-1, RR-2 (RV3-H2); CS-1 (RV3-H1, RV3-M7); TB-3 (RV3-H3); VR-3 overlay part (RV3-H1, RV3-M5) |
| ACCEPTED WITH CONDITION | RS-2 (M3); RS-3 forging (M2); TB-1 (M8); VR-3 VTS part (M2); LR-2 (M6); TG-2 (M2); OP-7 (d) (L6) |
| ACCEPTED | RS-3 deletion, RS-4, RR-1, RR-3, CS-2, TB-2 (scope only), VR-1, VR-2, VR-4, LR-1, LR-3, LR-4, TG-1, TG-3 |
