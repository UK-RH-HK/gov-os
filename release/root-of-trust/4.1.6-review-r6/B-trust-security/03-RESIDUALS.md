# 03 — Residual determinations (review r6 B)

Every residual that revision 6 declares within trust and security scope is judged here against explicit criteria.
Documentation alone is not a bound (HO-0016 §3.7).

## Criteria

These restate the criteria of review r5 (reviewer B `03`, synthesis D `05`), with attribution.

**ACCEPTED** only if one of the following holds.
- **R-1 (excluded trigger).** The trigger needs a capability the trust model excludes, and the exclusion holds for the machine
  class as the architecture prescribes it.
- **R-2 (unavoidable and bounded).** All four hold:
  - (a) no reasonable design under the chosen assumptions removes or bounds it;
  - (b) the bound is stated exactly;
  - (c) no surface presents the residual state as stronger;
  - (d) an acceptance test fails when the bound is exceeded.

**ACCEPTED WITH CONDITION** names the carried requirement (`04`) that must hold. **NOT ACCEPTED** names the finding.

## First contact and admission (`32` §10, `31` §9)

| ID | Residual | Attacks | Determination |
|---|---|---|---|
| **AD-1′ / FC-R1** | The first-contact root of the OP-13 answer: "exactly the root sets of `32` §6" | A01 (P, C), A05, A06, A13 | **NOT ACCEPTED** (RV6-B-H1, RV6-B-H2). **Bound wrong (R-2 (b) fails):** the publisher that composes the code selects alone under (a), (b), (c) "either" and (d); the package submitter and a replayed package select under (c) "either". **Not unavoidable (R-2 (a) fails):** first-hand derivation of the manifest by each source, and a mandatory short `valid_until` with an established package, remove these sets. |
| FC-R2 | An operator who types one source's value for every required source (`op1src`) | FA6 rerun (A01c′ rows) | **ACCEPTED** (R-2): inside the stated root, executed; the procedure prints each source; RT-156 |
| **FC-R3** | Under (c): the signing service's compromise, alone ("either") or with the sources ("all") | A05, A06 | **NOT ACCEPTED** (RV6-B-H2). The stated atom `alt` is too narrow: an honest service signing a submitter's package, and a carrier replaying an old genuine package, both admit. |
| FC-R4 | Under (d): media custody | A01 part C | **ACCEPTED WITH CONDITION** CR6-B-01 (the media are prepared from a first-hand-derived manifest). With media prepared from the published code, the publisher selects (H1). |
| RS-B1 (restated) | A stale page selects the state its code names | FA6 rerun (FA5 `CH1`); A05 | **ACCEPTED** (R-2) for owner pages under (a), (b) and (c) "all": staleness is the owner's own source; `issued_at` and age are shown. **NOT ACCEPTED** for the (c) "either" platform path (RV6-B-H2): staleness is selectable by any carrier and `valid_until` is optional. |
| TB-1′ | A malicious binary run directly, outside admission | FA6 S6 (shipped record ignored); ADM6 A15 (rerun) | **ACCEPTED** (R-1): GB-1′ binds genuine binaries; records are honoured only inside the store |
| AD-2 | Same-account code executed before first admission | ADM6 A09b; A04 | **ACCEPTED WITH CONDITION** CR6-B-02 (RV6-B-M1). The fresh store at first admission bounds AD-2. Re-admission keeps the store, but bootstrap mode does not apply it. |
| VR-B1′ | Same-account replacement of a user-writable binary is A3 | UW6 rerun byte-identical; RV5-D-A03 rerun | **ACCEPTED** (R-1): §7.1 classes equal the computed classes |

## Binary, registration, reproduction, environment and content (`30` §12, `33` §8, `34` §6, `25` §10)

| ID | Residual | Attacks | Determination |
|---|---|---|---|
| TB-S1 | Reproducer compromise at the quorum | CS6 rerun; FA6 S5; A12 | **ACCEPTED** (R-2): process sets need q reproducer processes. Key-theft sets need q keys, `ts` and a currency input (A12: no accept with ≤ 1 key). Restrictor revocation needs the registration authority (AP-5r executed). For P1/P2/CIR currency inputs see H1. |
| TB-S1 (environment) | Environment reproducers at the quorum | ENV6 E8a/E8b rerun | **ACCEPTED WITH CONDITION** CR6-B-01 (RV6-B-H3). The bound holds for a manifest whose recipe and selection are established. For an authored manifest, honest reproducers reproduce the author's injection (A02). |
| TB-S2 (TA-12) | A malicious upstream toolchain release that passes its checksum | CS6 OP-10 rows | **ACCEPTED** (R-2) |
| **TB-S2′ (TA-12′)** | A malicious upstream environment component (a), every supplier class used (b), the owner's environment build (c) | A02 (A07a/b/c, A08, A09); computed | **NOT ACCEPTED** for (a) and (b) (RV6-B-H3). The minimum includes the manifest author ({pipeline}), and (b)'s "every supplier class" is a label. **ACCEPTED** for (c). |
| TB-S3 (TA-10′) | Reproducers, environment reproducers or custodians under common custody | — | **ACCEPTED** (process; not verifier-checkable; RT-180 flags) |
| TB-4 | Route I: an insider change accepted by honest verification | CS6 CONTENT/SRC blocks | **ACCEPTED** (process, TA-11) |
| TB-4′ | OP-8 compromised verification processes plus pipeline input | CON6 rerun (17/17 verdicts); P4r6 section G; CS6 INV-CONTENT | **ACCEPTED** (R-2) |
| RA-1 | The registration authority at threshold with OP-8 verification compromises | A10 (`verify-registration` exit 3 on every non-first-hand proposal); CON6 | **ACCEPTED** (R-2) for selection. The per-project listing omits some units (RV6-B-L1, carried CR6-B-04). |
| AV-S1 | One reproducer key forces a conflict | FA6 S5 rerun; P4r6 `R6-AP5r_registration_authority_revocation_clears_forged_conflict` | **ACCEPTED** (R-2): remedy by registration revocation |
| TB-L4 | Stateless runners lack an accepted-TBM high-water | A04 | **ACCEPTED WITH CONDITION** CR6-B-02. A re-admitted machine is not stateless, but bootstrap mode treats it as stateless (RV6-B-M1). |

## Freshness, anchoring and currency (`24` §10)

| ID | Residual | Attacks | Determination |
|---|---|---|---|
| RS-1 | A machine anchored before a revocation that never receives later metadata | A11: 47 rows with C1–C2 on the thief descendant, all anchored or OP-7 (d); 0 rows with C3 on it; 0 `current` | **ACCEPTED** (R-2) |
| RS-1b | C3 staleness up to the window; P1 covers only the named state | A11: C3 below t9 only on M1s and M6-B strip rows (a)–(d) | **ACCEPTED** (R-2) |
| RS-1c | A pin provisioned before a revocation admits C1–C2 | A11 M2 pin rows | **ACCEPTED** (R-2): `pin_max_validity_days` |
| RS-2 (restated) | Clock trust; stateful machines fail closed below the high-water; far-future statements disable clock proofs | A11 CLOCK-back rows (52 rows where revoked R7 is eligible for C1–C2, all under a clock set back 395 days; 0 C3 rows in either CLOCK-back variant); P4r6 `R6-CLOCK-*` rerun | **ACCEPTED** (R-1: A13 clock attacker, TA-7). Caveat as review r5: P4r4 `ingest` re-evaluates statements against the current clock, so rows for machines that had already persisted t9 overstate. |
| RS-2b | A restored store with the clock set back and every later statement withheld | P4r6 residual demonstration (rerun byte-identical) | **ACCEPTED** (R-2): bound stated; RT-178. A11's "later withheld" variant still delivered non-TSS statements issued after the backup, so C3 was refused there. |
| RS-3 | A3 deletes or rewrites its own store | — | **ACCEPTED WITH CONDITION** CR4-B-01 (allow-list confinement, specification only) |
| RS-4 | Pins provisioned by a party the repository writer controls; jobs as root | FA6 S6 `euid 0` rerun | **ACCEPTED as scoping** (R-1, TA-9; GB-6 executed predicate) |
| RS-5 | Compromise of witness keys | design | **ACCEPTED** |
| OP-7 (d) residual | Unanchored C1–C2 at or above the compiled Trust State | A11 (d) rows | **ACCEPTED** as owner-selectable (never C3; labelled) |

## Constitutional Surface and register shortfalls (`23` §10, `29` §2 (5))

| ID | Residual | Attacks | Determination |
|---|---|---|---|
| CS-1 | Classification correctness is a root-ceremony responsibility | A10 K5/K6 exit 2; RV5-B-A09 rerun (wildcard `informational` key admitted, byte-identical) | **ACCEPTED WITH CONDITION** CR4-B-05 (RV4-L1 still open) |
| CS-2 (replaced) | One first-hand registration per release | CON6 rerun; A10 | **ACCEPTED** |
| DR-15 shortfall | Verification records select nothing (TB-4′) | as TB-4′ | **ACCEPTED** |
| DR-25 shortfall (RR-2) | The repository writer selects among eligible registered releases on machines without a record | A11 M8 (E10 detects with the kept record) | **ACCEPTED** (R-2) |
| DR-33 shortfall (RS-2b) | as RS-2b | as RS-2b | **ACCEPTED** |

## Verify-and-use (`18` §11), rollback (`20` §10), trust gates (`27` §7)

| ID | Determination |
|---|---|
| VR-1, VR-2, VR-4 | **ACCEPTED** (unchanged; not attacked). |
| VR-3, TG-2 | **ACCEPTED WITH CONDITION** CR4-B-01. |
| RR-1, RR-3, TG-1, TG-3 | **ACCEPTED**. |
| RR-2 | **ACCEPTED** (DR-25 above). |

## Legacy containment (`26` §8)

| ID | Determination |
|---|---|
| LR-1 … LR-3 | Not assessed by this reviewer (compatibility scope; LAY6 not re-run). |
| LR-4 | **ACCEPTED WITH CONDITION** CR4-B-04 (specification only, RT-146). |

## Summary

| Determination | Residuals |
|---|---|
| NOT ACCEPTED | AD-1′/FC-R1 (H1, H2); FC-R3 (H2); RS-B1 on the (c) "either" platform path (H2); TB-S2′ for OP-16 (a) and (b) (H3) |
| ACCEPTED WITH CONDITION | FC-R4, AD-2, TB-S1 (environment), TB-L4, RS-3, CS-1, VR-3, TG-2, LR-4 |
| ACCEPTED | FC-R2, RS-B1 (owner pages), TB-1′, VR-B1′, TB-S1, TB-S2, TB-S2′ (c), TB-S3, TB-4, TB-4′, RA-1, AV-S1, RS-1, RS-1b, RS-1c, RS-2, RS-2b, RS-4 (scoping), RS-5, OP-7 (d), CS-2, DR-15, DR-25, DR-33, VR-1, VR-2, VR-4, RR-1, RR-2, RR-3, TG-1, TG-3 |
| Not assessed (compatibility scope) | LR-1 … LR-3 |
