# 05 — Residual determinations (review r6 synthesis D, AR-0018)

Every residual revision 6 declares gets a final determination. Documentation alone is not a bound (HO-0018 §3).

## Criteria

The criteria are those of reviews r5 D and r6 B/C, restated.

- **ACCEPTED** only if either:
  - **R-1:** the trigger needs a capability the trust model excludes, and the exclusion holds for the machine class as
    prescribed; or
  - **R-2:** all of the following hold:
    - (a) no reasonable design under the chosen assumptions removes or bounds it;
    - (b) the bound is stated exactly;
    - (c) no surface presents the state as stronger;
    - (d) an acceptance test fails when the bound is exceeded.
- **ACCEPTED WITH CONDITION** names the carried requirement that must hold.
- **NOT ACCEPTED** names the finding.

An owner-selectable residual (for example OP-7 (d)) is acceptable when its consequence is stated exactly.

## First contact and admission (`32` §10, `31` §9)

| ID | Residual | Attacks | Determination |
|---|---|---|---|
| **AD-1′ / FC-R1** | The first-contact root of the OP-13 answer | B-A01 P/S/C; D-A01 | **NOT ACCEPTED** (RV6-H1, RV6-H2). Bound wrong (R-2 (b)): the composer, designation and submitter select outside the stated sets; stored or designated values select stale state. Not unavoidable (R-2 (a)): `11` CD6-1, CD6-2. |
| FC-R2 | An operator typing one source's value for every required source | FA6 (reproduced); D-A01 | **NOT ACCEPTED as stated.** The residual itself (`op1src`) is core and inside the root, but its stated bound, "the procedure prints each source's name", rests on a printer an attacker can supply (RV6-H1). |
| **FC-R3** | Under (c): the signing service's compromise | B-A01 R, S | **NOT ACCEPTED** (RV6-H1 submitter; RV6-H2 replay) |
| **FC-R4** | Under (d): media custody | B-A01 C; D-A08 | **NOT ACCEPTED** (RV6-H2: media of any age admit binaries revoked since; RV6-H1: media prepared from the published code). Review r6 B's condition CR6-B-01 covers only the composition half. |
| **RS-B1** (restated) | A stale page selects the state its code names | D-A01 S2, D-A02, D-A08; FA5 CH1 | **NOT ACCEPTED** (RV6-H2). Its bound ("`issued_at`, `valid_until`, age shown … the admitted binary anchors next") fails: `valid_until` is optional; a malicious admitted binary never anchors; designated pages make staleness attacker-selected; a re-admitted machine holds newer state. The owner's own publication lag becomes core **once** a mandatory maximum age bounds it. |
| TB-1′ | A malicious binary run directly, outside admission | FA6 S6; ADM6 A15 (reproduced) | **ACCEPTED** (R-1). The procedure contradiction is counted in RV6-H1: `06` §3 step 0 prints steps with `gov`, while TB-1′ says the procedure never runs a candidate. |
| AD-2 | Same-account code executed before first admission | ADM6; D-A07 | **ACCEPTED WITH CONDITION** RV6-M6 (CR6-C-10 and an authenticated first-admission determination). D-A07 shows the bound rests on an unsigned file today. |
| VR-B1′ | Same-account replacement of a user-writable binary | UW6 (reproduced) | **ACCEPTED** (R-1) |

## Binary, registration, reproduction, environment, content (`30` §12, `33` §8, `34` §6, `25` §10)

| ID | Residual | Determination |
|---|---|---|
| TB-S1 | Reproducer compromise at the quorum | **ACCEPTED** (R-2): CS6, B-A12 reproduced. The currency inputs of P1, P2, CIR and WR victims are counted in RV6-H1. |
| TB-S1 (environment) | Environment reproducers at the quorum | **ACCEPTED WITH CONDITION** CD6-3 (the manifest they reproduce is established) |
| TB-S2 (TA-12) | Malicious upstream toolchain release | **ACCEPTED** (R-2), with RV6-L12 (the OP-10 × OP-16 statement) |
| **TB-S2′ (TA-12′)** | Malicious upstream environment component; every supplier class; owner-built environment | **NOT ACCEPTED** for OP-16 (a) and (b) (RV6-H3); **ACCEPTED** for (c) |
| TB-S3 (TA-10′) | Common custody | **ACCEPTED** (process; not verifier-checkable; RT-180) |
| TB-4, TB-4′ | Insider change; OP-8 verification processes plus pipeline | **ACCEPTED** (R-2): CON6, CS6 INV-CONTENT reproduced |
| RA-1 | Registration authority at threshold with OP-8 verification compromises | **ACCEPTED WITH CONDITION** RV6-L1 (per-project listing of every security-relevant change) |
| AV-S1 | One reproducer key forces a conflict | **ACCEPTED** (R-2): remedy by registration revocation (P4r6, FA6 S5 reproduced) |
| TB-L4 | Stateless runners lack the accepted-TBM high-water | **ACCEPTED WITH CONDITION** RV6-L5 |

## Freshness, anchoring and currency (`24` §10)

| ID | Residual | Determination |
|---|---|---|
| RS-1 | A machine anchored before a revocation that never receives later metadata | **ACCEPTED** (R-2): B-A11 reproduced |
| RS-1b | C3 staleness up to the window; P1 covers only the named state | **ACCEPTED** (R-2) for anchors made from an established value; anchors made from a publisher-composed value are RV6-H1 |
| RS-1c | A pin provisioned before a revocation | **ACCEPTED** (R-2) |
| RS-2, RS-2b | Clock trust; restored store with clock set back and later statements withheld | **ACCEPTED** (R-1 / R-2): P4r6 `R6-CLOCK-*` reproduced |
| RS-3 | A3 deletes or rewrites its own store | **ACCEPTED WITH CONDITION** CR4-B-01 |
| RS-4 | Pins or image codes provisioned by a party the repository writer controls | **ACCEPTED** as scoping (TA-9); the scoping does not cover an honest image operator storing an old code (RV6-H2) |
| RS-5 | Compromise of freshness-witness keys | **ACCEPTED WITH CONDITION** CD6-1 item 5: the witness input must be an established value. D-A01 part C shows WR victims accepting without witness keys when the publisher composes the input. |
| OP-7 (d) | Unanchored C1–C2 at or above the compiled Trust State | **ACCEPTED** as owner-selectable (never C3; labelled) |

## Surface, register shortfalls, verify-and-use, rollback, gates, legacy containment

| ID | Determination |
|---|---|
| CS-1 | **ACCEPTED WITH CONDITION** CR4-B-05 (RV4-L1 still open: B-A10 wildcard row reproduced) |
| CS-2 | **ACCEPTED** (CON6) |
| DR-15 (TB-4′), DR-33 (RS-2b) | **ACCEPTED** |
| DR-25 / RR-2 | **ACCEPTED WITH CONDITION** RV6-M4 (record identity) |
| VR-1, VR-2, VR-4, RR-1, RR-3, TG-1, TG-3 | **ACCEPTED** (design level; not attacked beyond the panel) |
| VR-3, TG-2 | **ACCEPTED WITH CONDITION** CR4-B-01 |
| LR-1, LR-3 | **ACCEPTED** (C `gitops6`, matrix reproduced) |
| LR-2 | **ACCEPTED WITH CONDITION** RV6-M3, RV6-M4 |
| LR-4 | **ACCEPTED WITH CONDITION** CR4-B-04, RV6-M4 |
| Layout durability (line endings, ignore sources, sparse checkout) | **ACCEPTED** (fail closed), with RV6-L6, RV6-L7 |
| Crash in any phase (`18` §10) | **ACCEPTED WITH CONDITION** RV6-M3 |
| Remedies never clear strength reports (`26` §6, `20` RB-3) | **ACCEPTED WITH CONDITION** RV6-M5 |
| Binary rollback keeps its record | **ACCEPTED WITH CONDITION** RV6-L5 |
| Litter "inert" (`26` §4) | **ACCEPTED WITH CONDITION** RV6-L10 |

## Summary

| Determination | Residuals |
|---|---|
| **NOT ACCEPTED** | AD-1′/FC-R1, FC-R2 (as stated), FC-R3, FC-R4, RS-B1 (RV6-H1, RV6-H2); TB-S2′ under OP-16 (a), (b) (RV6-H3) |
| ACCEPTED WITH CONDITION | AD-2, TB-S1 (environment), RA-1, TB-L4, RS-3, RS-5, CS-1, RR-2, VR-3, TG-2, LR-2, LR-4, crash in any phase, remedies, binary rollback, litter |
| ACCEPTED | TB-1′, VR-B1′, TB-S1, TB-S2, TB-S2′ (c), TB-S3, TB-4, TB-4′, AV-S1, RS-1, RS-1b (established anchors), RS-1c, RS-2, RS-2b, RS-4 (scoping), OP-7 (d), CS-2, DR-15, DR-33, VR-1, VR-2, VR-4, RR-1, RR-3, TG-1, TG-3, LR-1, LR-3, layout durability |
