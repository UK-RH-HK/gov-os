# 03 — Residual determinations (review r4 B)

Every residual that revision 4 declares, and that falls in trust or security scope, is judged here against explicit
criteria. Documentation alone is not a bound (HO-0006 §3.7).

## Criteria

These criteria restate review r3 synthesis D `05-RESIDUALS.md` and review r2 `09`, with attribution.

**ACCEPTED** only if one of the following holds:
- **R-1 (excluded trigger).** The trigger needs a capability the trust model excludes, and that exclusion holds for the
  machine class as the architecture itself prescribes it.
- **R-2 (unavoidable and bounded).** All four of these hold:
  - (a) no design reasonable under the chosen assumptions removes or bounds it;
  - (b) the bound is stated exactly;
  - (c) no verdict surface presents the residual state as a stronger one;
  - (d) an acceptance test fails when the bound is exceeded.

**ACCEPTED WITH CONDITION** names the carried requirement (`04`) that must hold. **NOT ACCEPTED** names the finding.

## Freshness, anchoring and currency (`24` §10)

| ID | Declared residual | Attacks | Determination |
|---|---|---|---|
| RS-1 | A machine anchored before a revocation that never receives later metadata | RV4-B-A07 (67 core rows); PS sweep | **ACCEPTED** (R-2). **(a)** Unavoidable for offline verification. **(b)** Bound exact: C1–C2 at descendants of the anchor. **(c)** Never labelled `current` (0 rows); never C3 without a proof. **(d)** RT-80, RT-101. Under (b) the bound `max_anchor_age_days` holds on the grid (4296 h at 180 d). |
| RS-1b | C3 staleness up to the window (P1, P3), zero for P2 | PS sweep (C3 ≤ 167 h at 168 h; ≤ 23 h at 24 h; ≤ 719 h at 720 h); A12 (i) | **ACCEPTED WITH CONDITION** CR4-B-07. The window bound holds. The label "published as of *t*" is inexact for descendants issued after *t* (RV4-B-L3). P2's zero staleness relies on TA-5: the operator types the fingerprint from the channel, not from a C0 surface. |
| RS-1c | A valid pin provisioned before a revocation admits C1–C2 | PS sweep (C2 ≤ 719 h at 30 d; ≤ 167 h at 7 d; ≤ 2136 h at 90 d) | **ACCEPTED** (R-2): bound equals `pin_max_validity_days` on the grid; tested by RT-102 |
| RS-2 | Pin validity, the C3 window and OP-7 (b)/(c) trust the local clock; rollback below `clock_high_water` fails closed | RV4-B-A13; 23 matrix rows | **NOT ACCEPTED as stated** (RV4-B-M3). The trust assumption TA-7 is explicit, but the stated detection bound does not exist: the high-water never rises under (a), (b) or (d), and a stateless runner has no VTS. This fails R-2 (b). It becomes ACCEPTED WITH CONDITION CR4-B-03 once restated. |
| RS-3 | A3 deletes or rewrites its own VTS; `gov`-run children are confined | RV4-B-A05; 27 matrix rows | **ACCEPTED WITH CONDITION** CR4-B-01. **Deletion:** accepted (R-1: fail closed). **Forgery by A3:** accepted as the same-user boundary. **Not bounded:** the claim that a `gov`-run repository command cannot reach A3. One planted executable or hook does it (RV4-B-M1). |
| RS-4 | Pins provisioned by a party the repository writer controls, or repository steps that can write the pin location | 31 matrix rows | **ACCEPTED as scoping** (R-1 with TA-9 as restated). **Condition** (CR4-B-01 note): the runner-image documentation (WP-21) must state that a job with passwordless `sudo` can write `/etc/gov` and violates TA-9. Hosted CI runners commonly grant it. |
| RS-5 | Compromise of witness keys at the C3 threshold | 9 matrix rows; RV4-B-A14 | **ACCEPTED WITH CONDITION** CR4-B-02 (RV4-B-M2). The key-compromise bound holds. The witness service's input and custody are unspecified, so the same exposure is reachable without key compromise, or through one service. |
| OP-7 (d) residual | A2/A5 select any genuine state at or above the compiled TSS, for C1–C2 on unanchored machines | RV3-D-A04 re-derived; 16 matrix rows | **ACCEPTED** as an owner-selectable residual: never C3; labelled `FRESHNESS_UNPROVEN`; scoped to binaries whose compiled TSS predates the newest TSS |

## Binary and TCB (`25` §10)

| ID | Declared residual | Attacks | Determination |
|---|---|---|---|
| TB-1 | The binary remains the TCB; a user who runs an unverified binary is outside the chain | RV4-B-A03, A04, A05, A11 | **NOT ACCEPTED** (RV4-B-H2). The documented first-binary procedures, and the Phase 4 migration path, accept revoked, remediated-malicious or self-reported binaries. A user following the architecture's own procedure is not "running an unverified binary". The accepted-TBM part is accepted with condition CR4-B-08 (RV4-B-L4). |
| TB-2 | The build attestation trusts the rebuilder's environment | RV4-B-A01 | **ACCEPTED only for what it bounds.** It bounds a genuine rebuilder environment. It does not bound the key: RV4-B-H1. |
| TB-3 | Compromise of a minimum capability set: route S 3 keys (2 under OP-4 "no") plus pipeline input; route B 4 keys over 3 purposes | RV4-B-A01, A02, A06 | **NOT ACCEPTED** (RV4-B-H1). The minimum is 1 key plus pipeline input for malicious bytes under every OP-2 source authority, and for malicious source under (S0) and (S3). |
| TB-4 | Insider source accepted by an honest verifier (route I) | RV4-B-A02 | **ACCEPTED** as a process residual (TA-11). The same outcome through key theft is RV4-B-H1, not TB-4. |

## Constitutional Surface (`23` §10)

| ID | Declared residual | Attacks | Determination |
|---|---|---|---|
| CS-1 | Classification correctness is a root-ceremony responsibility; too-weak classification is limited by lint, the consumer register, exact precedence, directed joins and reductions | RV4-B-A09, A10 | **ACCEPTED WITH CONDITION** CR4-B-05 (RV4-B-L1: a wildcard `informational` rule admits unknown keys). The tunable-only kernel yields no weaker outcome on 4.1.5 (A10). |
| CS-2 | Every final that changes pinned, registered or precedence content needs a root-threshold TPS (ceremony frequency) | RV4-B-A08 | **NOT ACCEPTED as stated** (RV4-B-H3). The residual is presented as operational cost only. The architecture does not say which registered digests may coexist, so the ceremony that keeps older releases working enables rollback of pinned content by `release-final`. |

## Verify-and-use (`18` §11)

| ID | Declared residual | Determination |
|---|---|---|
| VR-1 | A3 modifies installed files between units of work | **ACCEPTED** (VU-11; not attacked beyond review r3) |
| VR-2 | A3 ignores advisory locks | **ACCEPTED** (refusals only) |
| VR-3 | Non-`gov` subprocesses write PPS, overlay, records and VTS | **ACCEPTED WITH CONDITION** CR4-B-01. The persistence route turns a `gov`-run child into a non-`gov` process that writes the VTS. |
| VR-4 | Profile runtimes consumed by path | **ACCEPTED** (unchanged; not attacked) |

## Rollback and recovery (`20` §10)

| ID | Declared residual | Determination |
|---|---|---|
| RR-1 | Automatic rollback may leave an ineligible installation | **ACCEPTED** (fails closed) |
| RR-2 | A machine without a per-project record accepts an A2-delivered older eligible release; an anchored machine judges it at its effective state by inclusion | **ACCEPTED** (R-2). Inclusion anchors hold in the model (RV3-B-A12 variants). The staleness bound is RS-1. |
| RR-3 | A3 deletes the per-project record or VTS | **ACCEPTED** (R-1) |

## Legacy containment (`26` §8), trust aspects only

| ID | Declared residual | Determination |
|---|---|---|
| LR-1…LR-3 | Unconverted working copies; occupation removal or Git restore; explicit output paths | Not attacked by this reviewer (compatibility scope). No contrary evidence. |
| LR-4 | Fresh clones accept the repository overlay | **ACCEPTED WITH CONDITION** CR4-B-04 (RV4-B-M4). The bound "per-machine detection after the first record" does not cover a release-signed migration's weakening committed by an unrecorded machine. |

## Trust gates (`27` §7)

| ID | Declared residual | Determination |
|---|---|---|
| TG-1 | A decision on one machine does not authorise another | **ACCEPTED** |
| TG-2 | A same-user process with an unconfined shell writes its VTS or drives a pseudo-terminal; `gov`-executed children are confined | **ACCEPTED WITH CONDITION** CR4-B-01 (RV4-B-M1) and CR4-B-09 (RV4-B-L5: decision-pin expiry unbounded) |
| TG-3 | Non-trust gates forgeable by A2 | **ACCEPTED** (TA-8; r2 P2 re-run reproduces legacy behaviour; revision 4 records are requests) |

## Summary

| Determination | Residuals |
|---|---|
| NOT ACCEPTED | TB-1 (H2); TB-3 (H1); CS-2 as stated (H3); RS-2 as stated (M3) |
| ACCEPTED WITH CONDITION | RS-1b (L3); RS-3 (M1); RS-5 (M2); TB-1 accepted-TBM part (L4); CS-1 (L1); VR-3 (M1); LR-4 (M4); TG-2 (M1, L5) |
| ACCEPTED | RS-1, RS-1c, RS-4 (scoping), OP-7 (d), TB-2 (scope only), TB-4, VR-1, VR-2, VR-4, RR-1, RR-2, RR-3, TG-1, TG-3 |
| Not assessed (compatibility scope) | LR-1…LR-3 |
