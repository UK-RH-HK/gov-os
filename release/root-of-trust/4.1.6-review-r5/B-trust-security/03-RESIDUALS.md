# 03 — Residual determinations (review r5 B)

Every residual that revision 5 declares within trust and security scope is judged here against explicit criteria.
Documentation alone is not a bound (HO-0012 §3.7).

## Criteria

These restate the criteria of review r4 synthesis D (`05-RESIDUALS.md`) and review r4 B (`03-RESIDUALS.md`), with
attribution.

**ACCEPTED** only if one of the following holds.
- **R-1 (excluded trigger).** The trigger needs a capability the trust model excludes, and the exclusion holds for the
  machine class as the architecture prescribes it.
- **R-2 (unavoidable and bounded).** All four hold:
  - (a) no reasonable design under the chosen assumptions removes or bounds it;
  - (b) the bound is stated exactly;
  - (c) no surface presents the residual state as stronger;
  - (d) an acceptance test fails when the bound is exceeded.

**ACCEPTED WITH CONDITION** names the carried requirement (`04`) that must hold. **NOT ACCEPTED** names the finding.

## Freshness, anchoring and currency (`24` §10)

| ID | Residual | Attacks | Determination |
|---|---|---|---|
| RS-1 | A machine anchored before a revocation that never receives later metadata | A12: 44 rows with C1–C2 on a thief descendant, all on anchored or OP-7 (d) machines; 0 rows with C3 on it; 0 `current` | **ACCEPTED** (R-2). Bound: C1–C2 at descendants of the anchor, never C3 without a proof naming the state. RT-80, RT-101, RT-147. |
| RS-1b | C3 staleness up to the window; P1 covers only the named state | A12 M6-B strip rows (C3 on t5, anchor 2 days old) | **ACCEPTED** (R-2): option 1 makes the label exact; bound `c3_currency_window_hours`. |
| RS-1c | A valid pin provisioned before a revocation admits C1–C2 | A12 M2 pin rows | **ACCEPTED** (R-2): `pin_max_validity_days`; RT-102. |
| RS-2 (restated) | Clock trust; a stateful machine fails closed below the high-water; stateless machines rely on TA-7 | A12 CLOCK-back rows; P4r5 `CLOCK-RV4-B-A13` (reproduced) | **ACCEPTED WITH CONDITION** CR5-B-08, CR5-B-09. The restated bound is exact. On restored-backup and long-offline machines the high-water is old, so a clock set back re-opens P1 on stale anchors, contrary to `24` §5.3 and §5.7 as written (RV5-B-L3). Contradictory witness-only text remains (RV5-B-L4). |
| RS-3 | A3 deletes or rewrites its own store; `gov`-run children confined | review r4 B part A re-run: legacy persistence unchanged | **ACCEPTED WITH CONDITION** CR4-B-01 (allow-list confinement and TCB-location predicate; specification only, RT-103, RT-138). |
| RS-4 | Pins provisioned by a party the repository writer controls | — | **ACCEPTED as scoping** (R-1, TA-9), with CR4-B-01 (d) (passwordless `sudo`) and CR5-B-12 (jobs running as root). |
| RS-5 | Compromise of witness keys | design `24` §3.3 | **ACCEPTED** (input and custody rules stated; RT-149 specification only). |
| OP-7 (d) residual | Unanchored C1–C2 at or above the compiled Trust State | A12 (d) rows | **ACCEPTED** as owner-selectable (never C3; labelled). |

## First admission (`31` §9)

| ID | Residual | Attacks | Determination |
|---|---|---|---|
| RS-B1 | A stale channel page selects the state it names | A12 M1s strip rows: C3 on t5 | **ACCEPTED** (R-2). Bound: the channels' own currency. `issued_at` and age are shown. Under OP-13 (b) both pages must be stale. FA5 CH1. |
| AD-1 | All channels the operator uses, together with the trust-state key and the reproducer quorum keys | A01, A04 part L | **NOT ACCEPTED** (RV5-B-H1). The bound is wrong: the channels alone suffice (zero keys). Under OP-13 (b) one channel suffices when the page asks for one value, because the quorum is read from the state that page selects. |
| AD-2 | Same-account code executed before the first admission | A13 | **ACCEPTED WITH CONDITION** CR5-B-03: "first admission" must be defined, and re-admission must not discard the store (RV5-B-M3). |
| TB-1′ | A malicious binary run directly, outside admission | A15 | **ACCEPTED WITH CONDITION** CR5-B-07. Malicious binaries are out of reach by construction (R-1). The statement that GB rules bind genuine revoked binaries holds only for installs that did not ship a record (RV5-B-L2). |
| VR-B1 | A same-account replacement of a user-writable binary | FA5 INS2 (reproduced) | **ACCEPTED** (R-1, A3; GB-4 restricts to C0–C2). |

## Binary, registration and reproduction (`30` §12, `25` §10)

| ID | Residual | Attacks | Determination |
|---|---|---|---|
| TB-S1 | Reproducer compromise at the quorum | CS5 re-run; A07 | **ACCEPTED WITH CONDITION** CR5-B-01. The process sets hold. The key-theft sets are overstated by `transport` where the trust-state key revokes restrictors (RV5-B-M1). |
| TB-S2 (TA-12) | A malicious upstream toolchain release passing the checksum check | A08 | **ACCEPTED for the toolchain archive** (OP-10). **NOT ACCEPTED** as covering the build image, which no checksum, option or residual reaches (RV5-B-H2). |
| TB-S3 (TA-10′) | Reproducers or custodians under common custody | — | **ACCEPTED** (process; not verifier-checkable). Channel custody should be stated the same way (CR5-B-02). |
| TB-4 | Route I: an insider change accepted by honest verification | A06 enumeration ({insider, repo} for policy content) | **ACCEPTED** (process, TA-11). |
| TB-4′ | OP-8 compromised verification processes plus pipeline input | CS5 re-run; A06 | **ACCEPTED for binaries.** For policy-root content, OP-8 does not bound the sets (RV5-B-H3). |
| AV-S1 | One reproducer key forces a conflict (availability) | FA5 K1 (reproduced) | **ACCEPTED** (R-2; remedy stated). |
| TB-L4 | Stateless runners lack an accepted-TBM high-water | P4r5 row | **ACCEPTED** (R-2; `min_binary_version` and revocations; RT-116). |

## Constitutional Surface (`23` §10)

| ID | Residual | Attacks | Determination |
|---|---|---|---|
| CS-1 | Classification correctness is a root-ceremony responsibility | A11, A16; review r4 B part U re-run | **ACCEPTED WITH CONDITION** CR4-B-05 (RV4-L1 open: U01, U02 still exit 0). |
| CS-2 (replaced) | One registration ceremony per release; retention no longer widens later releases | REG5 re-run; A09, A10; A06 | **ACCEPTED WITH CONDITION** CR5-B-04 as a cost. The accompanying claim that reversion, removal and narrowing are computed reductions holds only for exact reversion, in the ceremony tool (RV5-B-M2). Under OP-2 (b), content selection is below the declared authority (RV5-B-H3). |

## Verify-and-use (`18` §11), rollback (`20` §10), trust gates (`27` §7)

| ID | Determination |
|---|---|
| VR-1, VR-2, VR-4 | **ACCEPTED** (unchanged; not attacked). |
| VR-3 | **ACCEPTED WITH CONDITION** CR4-B-01. |
| RR-1 | **ACCEPTED** (fails closed). |
| RR-2 | **ACCEPTED WITH CONDITION** CR5-B-03 and CR5-B-05. Stated under OP-11 (a). Re-admission converts recorded machines into RR-2 machines (RV5-B-M3). The register labels Git delivery a carrier (RV5-B-M5). |
| RR-3 | **ACCEPTED** (R-1). |
| TG-1, TG-3 | **ACCEPTED**. |
| TG-2 | **ACCEPTED WITH CONDITION** CR4-B-01 (allow list specification only). |

## Legacy containment (`26` §8), trust aspects only

| ID | Determination |
|---|---|
| LR-1 … LR-3 | Not assessed by this reviewer (compatibility scope; ST5, P3r3 and LR2 not re-run). |
| LR-4 | **ACCEPTED WITH CONDITION** CR4-B-04 (pre-transaction requirements on machines without a record; specification only, RT-146). |

## Summary

| Determination | Residuals |
|---|---|
| NOT ACCEPTED | AD-1 (H1); TB-S2 as covering the build image (H2) |
| ACCEPTED WITH CONDITION | RS-2, RS-3, AD-2, TB-1′, TB-S1, TB-4′ (binaries only), CS-1, CS-2, VR-3, RR-2, TG-2, LR-4 |
| ACCEPTED | RS-1, RS-1b, RS-1c, RS-4 (scoping), RS-5, OP-7 (d), RS-B1, VR-B1, TB-S2 (toolchain archive), TB-S3, TB-4, AV-S1, TB-L4, VR-1, VR-2, VR-4, RR-1, RR-3, TG-1, TG-3 |
| Not assessed (compatibility scope) | LR-1 … LR-3 |
