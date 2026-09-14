# 05 — Residual determinations (review r4 synthesis D, AR-0008)

## Criteria

These restate review r3 synthesis D `05-RESIDUALS.md` and reviewer B `03-RESIDUALS.md`, with attribution. Documentation
alone is not a bound (HO-0008 §3).

**ACCEPTED** only if one holds:
- **R-1 (excluded trigger).** The trigger needs a capability the trust model excludes, and the exclusion holds for the
  machine class as the architecture prescribes it.
- **R-2 (unavoidable and bounded).** (a) No reasonable design under the chosen assumptions removes or bounds it; (b) the
  bound is stated exactly; (c) no surface presents the residual state as stronger; (d) an acceptance test fails when the
  bound is exceeded.

**ACCEPTED WITH CONDITION** names the carried requirement. **NOT ACCEPTED** names the finding.

## Freshness, anchoring and currency (`24` §10)

| ID | Residual | Attacks | Determination |
|---|---|---|---|
| RS-1 | a machine anchored before a revocation never receives later metadata | B MX 67 core rows (reproduced); P4r4 matrix 42 core rows | **ACCEPTED** (R-2): C1–C2 at descendants; never `current` (0 rows); never C3 without a proof; RT-80, RT-101 |
| RS-1b | C3 staleness up to the window | B PS sweep (reproduced) | **ACCEPTED WITH CONDITION** RV4-L3 (label) |
| RS-1c | a valid pin provisioned before a revocation admits C1–C2 | B PS sweep | **ACCEPTED** (R-2): bound = `pin_max_validity_days`; RT-102 |
| RS-2 | clock trust; "rollback below `clock_high_water` fails closed" | B A13, LB3 (reproduced) | **NOT ACCEPTED as stated** (RV4-M4): the detection bound does not exist under (a), (b), (d) or without a VTS. Acceptable with condition CR4-B-03 once restated. |
| RS-3 | A3 deletes or rewrites its VTS; `gov`-run children confined | B A05 (reproduced) | **ACCEPTED WITH CONDITION** RV4-M2 |
| RS-4 | pins provisioned by a party the repository writer controls | B MX 31 rows | **ACCEPTED as scoping** (R-1), with the CI `sudo` note of CR4-B-01 (d) |
| RS-5 | compromise of witness keys at the C3 threshold | B MX 9 rows; A14 | **ACCEPTED WITH CONDITION** RV4-M3 |
| OP-7 (d) | A2/A5 select genuine state ≥ compiled TSS on unanchored machines, C1–C2 | B MX 16 rows; P4r4 13 rows | **ACCEPTED** as an owner-selectable residual (never C3; labelled) |

## Binary and TCB (`25` §10)

| ID | Residual | Attacks | Determination |
|---|---|---|---|
| TB-1 | the binary is the TCB; running an unverified binary is outside the chain | B A03, A04; D-A04 | **NOT ACCEPTED** (RV4-H2): the documented procedures accept revoked, remediated and self-reporting binaries; a user following them is not "running an unverified binary". Accepted-TBM part: WITH CONDITION RV4-L4. |
| TB-2 | the build attestation trusts the rebuilder's environment | B A01 | **ACCEPTED only for what it bounds** (an honest rebuilder environment); it does not bound the key (RV4-H1) |
| TB-3 | compromise of a minimum capability set of `25` §7 | B A01, A02, A06; D-A07 | **NOT ACCEPTED** (RV4-H1): the true minimum is one key plus pipeline input |
| TB-4 | insider source accepted by an honest verifier | — | **ACCEPTED** (process residual, TA-11) |

## Constitutional Surface (`23` §10)

| ID | Residual | Attacks | Determination |
|---|---|---|---|
| CS-1 | classification correctness is a root-ceremony responsibility | B A09, A10 | **ACCEPTED WITH CONDITION** RV4-L1 |
| CS-2 | every final that changes registered content needs a root-threshold TPS (ceremony frequency) | B A08; D-A02, D-A10 | **NOT ACCEPTED as stated** (RV4-H3): presented as cost only; the retention it forces enables rollback by `release-final` |

## Verify-and-use (`18` §11)

| ID | Residual | Attacks | Determination |
|---|---|---|---|
| VR-1 | A3 modifies installed files between units of work | — | **ACCEPTED** (VU-11) |
| VR-2 | A3 ignores advisory locks | — | **ACCEPTED** (refusals only) |
| VR-3 | non-`gov` processes write PPS, overlay, records, VTS | B A05; C A01; D-A01 | **ACCEPTED WITH CONDITION** RV4-M1 (a legacy `gov` process writes the PPS with `COMPLETE`) and RV4-M2 (persistence) |
| VR-4 | profile runtimes consumed by path | — | **ACCEPTED** |

## Rollback and recovery (`20` §10)

| ID | Determination |
|---|---|
| RR-1 | **ACCEPTED** (fails closed) |
| RR-2 | **ACCEPTED** (inclusion anchors hold; staleness bound RS-1) |
| RR-3 | **ACCEPTED** (R-1; `UNANCHORED`) |

## Legacy containment (`26` §8)

| ID | Residual | Attacks | Determination |
|---|---|---|---|
| LR-1 | unconverted working copies and `git revert` | C A07 (reproduced) | **ACCEPTED** |
| LR-2 | occupation removal or Git restore: legacy regains a verified install | C A06 (reproduced) | **ACCEPTED WITH CONDITION** RV4-M1: on the intact layout, the subdirectory trigger reaches the overlay part of LR-2's outcome while the state is `COMPLETE`, so bound (1) does not cover that trigger; bounds (2) and (3) hold (D-A01 N1b) |
| LR-3 | explicit operator output paths | — | **ACCEPTED** |
| LR-4 | fresh clones accept the repository overlay | B A15 | **ACCEPTED WITH CONDITION** RV4-M5 |

## Trust gates (`27` §7)

| ID | Determination |
|---|---|
| TG-1 | **ACCEPTED** |
| TG-2 | **ACCEPTED WITH CONDITION** RV4-M2, RV4-L5 |
| TG-3 | **ACCEPTED** (TA-8; records are requests) |

## Summary

| Determination | Residuals |
|---|---|
| NOT ACCEPTED | TB-1, TB-3, CS-2 (as stated), RS-2 (as stated) |
| ACCEPTED WITH CONDITION | RS-1b, RS-3, RS-5, TB-1 accepted-TBM part, CS-1, VR-3, LR-2, LR-4, TG-2 |
| ACCEPTED | RS-1, RS-1c, RS-4 (scoping), OP-7 (d), TB-2 (scope only), TB-4, VR-1, VR-2, VR-4, RR-1, RR-2, RR-3, LR-1, LR-3, TG-1, TG-3 |
