# D-synthesis 05 — Residual determinations (review r5)

Every residual declared by revision 5 gets a final determination. Documentation alone is not a bound (HO-0014 §3).

## Criteria

These restate the criteria of review r4 synthesis D and of this round's panel.

| Determination | When |
|---|---|
| **ACCEPTED** | **R-1:** the trigger needs a capability the trust model excludes, for the machine class as prescribed. **Or R-2:** all of (a) no reasonable design under the chosen assumptions removes or bounds it; (b) the bound is stated exactly; (c) no surface presents the state as stronger; (d) an acceptance test fails when the bound is exceeded. |
| **ACCEPTED WITH CONDITION** | the bound holds under this review's attacks once the named carried requirement (`11-CORRECTION-DELTA.md` §6) holds |
| **NOT ACCEPTED** | the bound does not hold under attack, or is stated incorrectly; the finding is named |

## Freshness, anchoring and currency (`24` §10)

| ID | Determination | Basis |
|---|---|---|
| RS-1 | **ACCEPTED** (R-2) | RV5-B-A12 reproduced: 44 rows with C1–C2 on a thief descendant, all anchored or OP-7 (d); 0 rows with C3 on it; 0 `current` labels |
| RS-1b | **ACCEPTED** (R-2) | CR4-B-07 option 1; P4r5 `AP-R5_p1_proof_does_not_cover_later_descendant` reproduced |
| RS-1c | **ACCEPTED** (R-2) | `pin_max_validity_days`; RT-102 |
| RS-2 (restated) | **ACCEPTED WITH CONDITION** RV5-L3, RV5-L4 | Stateful high-water: P4r5 CLOCK row reproduced. Restored and long-offline machines re-open P1 on stale anchors when the clock is set back (A12 CLOCK-back rows). Contradictory witness-only text remains. |
| RS-3 | **ACCEPTED WITH CONDITION** CR4-B-01 | allow-list confinement and the TCB-location predicate are specification only (RT-103, RT-138) |
| RS-4 | **ACCEPTED as scoping** (R-1, TA-9), with CR5-B-12 | jobs running as root before `gov` are outside TA-9 |
| RS-5 | **ACCEPTED** | witness input and custody rules stated (`24` §3.3); RT-149 specification only |
| OP-7 (d) residual | **ACCEPTED as owner-selectable** | never C3; labelled |

## First admission (`31` §9)

| ID | Determination | Basis |
|---|---|---|
| RS-B1 | **ACCEPTED** (R-2) for a stale page only | FA5 CH1 reproduced; `issued_at` and age shown. A forged page is AD-1. |
| AD-1 | **NOT ACCEPTED** (RV5-H1) | The stated bound ("channels ... together with the trust-state key and reproducer quorum keys") is wrong: the channels alone suffice with zero keys (RV5-B-A01, A04 part L reproduced). Under OP-13 (b) one channel suffices when one value is typed, because the quorum is read from the selected state. One channel selects the evaluator under any OP-13 answer (D-A02). |
| AD-2 | **ACCEPTED WITH CONDITION** RV5-M3 | the fresh-store step that bounds AD-2 is the step that discards monotonic state on re-admission |
| TB-1′ | **ACCEPTED WITH CONDITION** RV5-L2 | malicious binaries run directly are out of reach by construction (R-1); "GB rules bind genuine revoked binaries" holds only for installs that did not ship a record |
| VR-B1 | **ACCEPTED WITH CONDITION** RV5-M8 | The security bound holds: a user-writable install never reaches C3 (D-A03, `gov_run`). The stated scope "C0–C2 only" is false under OP-7 (a), (b) and (c) without witnesses, where it is C0 only. |

## Binary, registration and reproduction (`30` §12, `25` §10)

| ID | Determination | Basis |
|---|---|---|
| TB-S1 | **ACCEPTED WITH CONDITION** RV5-M1 | process sets hold (CS5 reproduced); key-theft sets are overstated by `transport` where the trust-state key revokes restrictors |
| TB-S2 (TA-12) | **ACCEPTED for the toolchain archive** (OP-10). **NOT ACCEPTED** as covering the build environment (RV5-H2). | RV5-B-A08, A04 part I reproduced |
| TB-S3 (TA-10′) | **ACCEPTED** (process; not verifier-checkable) | — |
| TB-4 | **ACCEPTED** (process, TA-11) | — |
| TB-4′ | **ACCEPTED for binaries.** **NOT ACCEPTED** for constitutional content (RV5-H3). | For content, verification records are neither required at E7 nor bound to the registered candidate (D-A01). |
| AV-S1 | **ACCEPTED** (R-2) | FA5 K1 reproduced; remedy stated |
| TB-L4 | **ACCEPTED** (R-2) | `min_binary_version` and revocations. Condition from RV5-M9: no executor or oracle models `min_binary_version` at admission (D-A04 R4), so the bound is untested. Carried. |

## Constitutional Surface (`23` §10)

| ID | Determination | Basis |
|---|---|---|
| CS-1 | **ACCEPTED WITH CONDITION** CR4-B-05 | RV4-L1 open: U01, U02 still exit 0 (review r4 B part U re-run) |
| CS-2 (replaced) | **NOT ACCEPTED** (RV5-H3) | "One registration ceremony per release fixes source, inputs, content and final together" does not hold for content: the ceremony signs a unit map and kernel tree digest it does not establish, and `release-candidate` + `release-final` + pipeline select them (D-A01, D-A05 N3) |

## Verify-and-use (`18` §11), rollback (`20` §10), trust gates (`27` §7)

| ID | Determination | Basis |
|---|---|---|
| VR-1, VR-2, VR-4 | **ACCEPTED** | not attacked; unchanged |
| VR-3 | **ACCEPTED WITH CONDITION** CR4-B-01 | the VTS-registration gate makes transaction-area litter inert (RV5-L8) |
| RR-1 | **ACCEPTED** | fails closed |
| RR-2 | **ACCEPTED WITH CONDITION** RV5-M3, RV5-M5 | re-admission converts recorded machines into RR-2 machines; the register labels Git delivery a carrier |
| RR-3 | **ACCEPTED** (R-1) | `UNANCHORED`, fail closed |
| TG-1, TG-3 | **ACCEPTED** | — |
| TG-2 | **ACCEPTED WITH CONDITION** CR4-B-01 | allow list specification only |

## Legacy containment (`26` §8)

| ID | Determination | Basis |
|---|---|---|
| LR-1 | **ACCEPTED** (R-2) | `gitops` CHECKOUT_PRE, RESTORE_PRE_GOV are `LEGACY` (reproduced) |
| LR-2 (restated) | **ACCEPTED** (bound holds) | `matrix5` reproduced: no legacy write under `governance/trust/**` or the occupation is left `COMPLETE`; the intact-layout subdirectory trigger fails closed |
| LR-3 | **ACCEPTED WITH CONDITION** RV5-L8 | nested installs outside `governance/`, including in the transaction area, are reported and inert |
| LR-4 | **ACCEPTED WITH CONDITION** CR4-B-04 | pre-transaction requirements on machines without a record (specification only, RT-146) |
| Layout durability: sparse checkout | **ACCEPTED** (fail closed) | C-6 doctor note |
| Layout durability: line endings; out-of-project ignore sources | **ACCEPTED WITH CONDITION** RV5-M6, RV5-M7 | fail closed; bound transaction step and test |

## Summary

| Determination | Residuals |
|---|---|
| NOT ACCEPTED | AD-1 (RV5-H1); TB-S2 as covering the build environment (RV5-H2); TB-4′ for constitutional content and CS-2 (RV5-H3) |
| ACCEPTED WITH CONDITION | RS-2, RS-3, AD-2, TB-1′, VR-B1, TB-S1, CS-1, VR-3, RR-2, TG-2, LR-3, LR-4, layout durability (line endings, ignore sources) |
| ACCEPTED | RS-1, RS-1b, RS-1c, RS-4 (scoping), RS-5, OP-7 (d), RS-B1 (stale page), TB-S2 (toolchain archive), TB-S3, TB-4, TB-4′ (binaries), AV-S1, TB-L4, VR-1, VR-2, VR-4, RR-1, RR-3, TG-1, TG-3, LR-1, LR-2, sparse checkout |
