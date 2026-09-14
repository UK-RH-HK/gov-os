# 02 — Adjudication of reviewer B and reviewer C (synthesis D, AR-0022)

Every B and C finding and every status claim is adjudicated here: **CONFIRMED** (severity kept or changed, with the reason),
**REFUTED** (with evidence) or **DUPLICATE**. Reproduction detail: `01-REPRODUCTION.md`. Consolidated statements:
`../10-BLOCKING-FINDINGS.md`.

Panel timing (routing fact, HO-0022 §1): reviewer B completed before OWNER-DESIGN-REQUIREMENTS-0002 existed; reviewer C received it
mid-run and disclosed it. This adjudication applies -0002 to both.

## 1. Reviewer B (AR-0020, `54be694`, `BLOCKING_FINDINGS_PRESENT`)

| B item | B severity | Reproduced | Adjudication | Reason | Consolidated |
|---|---|---|---|---|---|
| **RV7-B-H1** revocation effectiveness at first contact selected by listing | HIGH | yes: RV7-B-A01, A01m, CS7 byte-identical | **CONFIRMED HIGH, extended** | The executor, the custodian rule and the text behave as B states. RV7-D-A01 shows the same omission for an admitter revocation (FC-8′) and for a security-relevant registration (AP-SEC), so the class is every restrictive fact whose issuing authority is not the trust-state authority. Severity reasoning as B (RV6-H2 precedent; not CRITICAL because a held negative or a delivered statement refuses). | RV7-H1 |
| **RV7-B-H2** C3 currency names a state of unbounded age | HIGH | yes: RV7-B-A02 byte-identical | **CONFIRMED HIGH** | `gov_run` has no state-age input; R-CUR-1/2 bound the event; RS-1b, `24` §6 and A-R7-08 are false. The CI row is narrowed by RV7-D-A10: pin currency reaches gate-less C3 (`trust verify-artifact` acceptance) only; gated C3 on CI needs a terminal with in-gate codes, where the stored-code instance applies. Reviewer C's H1 is the same root cause. | RV7-H2 |
| **RV7-B-M1** one onboarding record designates both sources | MEDIUM, blocking | yes: CS7 A03 byte-identical; FA7 S2 D | **CONFIRMED MEDIUM; not carriable** | `{onboard}` is a minimal set the stated root omits; the designation is core when out of band (review r6), so not HIGH; the correction is architecture text. | RV7-M1 |
| RV7-B-L1 supplier and toolchain independence is inequality of free-text strings | LOW | yes: A04 byte-identical | **CONFIRMED; re-rated LOW → MEDIUM; merged** | OWNER-DESIGN-REQUIREMENTS-0002 (binding, after B) makes an explicit, executable, non-circular certification criterion a precondition of acceptance without a certified target and excludes "two different distributions" as independence. RV7-D-A03 shows the toolchain analogue accepted by the executor. B's LOW rested on the root threshold establishing the registry, which -0002 does not treat as sufficient. | RV7-M2 |
| RV7-B-L2 trust-root schema accepts root-held purposes at threshold 1 | LOW | yes: A05 byte-identical | **CONFIRMED LOW** | compiled `root_conforms` refuses; schema-only reliance is an implementation hazard | RV7-L1 |
| RV7-B-L3 custodian without history publishes a drop | LOW | yes: A01 publication row byte-identical | **CONFIRMED LOW** | two trust-state keys still needed; one rotated source fails closed | RV7-L2 |
| RV7-B-L4 no issuance cadence rule | LOW | design (confirmed: absence check; only OT-1a mentions "at least daily", for media) | **CONFIRMED LOW** | fail closed; becomes a load-bearing obligation under the RV7-H1 and RV7-H2 corrections (`11` §6) | RV7-L3 |
| RV7-B-L5 stale committed outputs; runner not self-contained | LOW | yes: DA07r6 (2 leaves) and RV6-B-A03 (2 leaves) differ exactly as B states; REGISTER-CHECK, DA09r7, DA04r7 byte-identical when run in the export | **CONFIRMED LOW** | no verdict leaf differs | RV7-L4 |
| RV7-B-L6 no genesis procedure for the custodians' verifier | LOW | design | **CONFIRMED LOW** | same shape as RV6-L4; carried CR7-B-07 | RV7-L5 |
| RV7-B-I1 OP-8 independence mechanics | INFO | code | **CONFIRMED INFO** | TB-4′ custody | RV7-I1 |
| RV7-B-I2 ARCH-0002 no `human_approved` field | INFO | yes: `RV7-D-A04.json` `decision_records` | **CONFIRMED INFO** | — | RV7-I2 |
| B: BC6-1 NARROWED; RV6-H1 CLOSED as stated | status | FA7 ×2, PROF7 byte-identical | **CONFIRMED** | composer, printer, submitter, platform root and attacker lineage refused; remainder RV7-M1, RV7-L5 | §3 |
| B: BC6-2 NARROWED; RV6-H2 CLOSED as stated | status | CUR7, cur7x M2 byte-identical | **CONFIRMED** | replayed, stored, media, CI and designated values refused at admission; remainders RV7-H1, RV7-H2 | §3 |
| B: BC6-3 CLOSED; RV6-H3 CLOSED | status | ENV7 byte-identical with the real `rustc 1.98.1` | **CONFIRMED as stated**, with two new remainders outside BC6-3's invariant (manifest authorship): label-based independence (RV7-M2) and cross-axis coverage (RV7-M3) | the manifest has no author; the pipeline selects nothing | §3 |
| B: BC6-4 NARROWED; RV6-M2 NARROWED | status | REGISTER-CHECK, DA09r7, DA04r7, DA06r7, STATEMENTS-CHECK byte-identical | **CONFIRMED** | remainders: listing completeness, designation atom, `sources_latest`, full-matrix build assumption (RV7-M3) | BC7-3 |
| B: RV6-M1, RV6-M6 (trust part), RV6-L2, L3, L4, L5, L12 CLOSED; RV6-L1 OPEN; RV6-I1, I2 unchanged | status | DA06r7, ADM7, CUR7 byte-identical; design | **CONFIRMED** | — | RV7-L12, I5, I6 |
| B: CP-1 conformance deviations OP-4 (revocation), OP-7 (a) (C3), OP-13 (b) (designation) | status | as H1, H2, M1 | **CONFIRMED**; added OP-10 (b) / OP-16 (b) label independence and the -0002 OT-2 criterion (RV7-M2), OP-11 (b) listing dependence (RV7-H1) | — | `04` §2 |
| B: OT-1 "real, bounded, genuine owner trade-off; understated" | assessment | CUR7 A08 byte-identical | **SUPERSEDED / REFUTED as an open trade-off**: OWNER-DESIGN-REQUIREMENTS-0002 resolved OT-1 after B completed. B's two understatement points stand: the daily cadence (RV7-L3) and the unbounded `win` (RV7-H1). | — | `04` §3 |
| B: OT-2 "real, bounded; not a new owner trade-off" | assessment | design | **CONFIRMED** (consistent with -0002) | the criterion itself is RV7-M2 | `04` §3 |
| B: residual determinations | status | as above | **CONFIRMED**, except TA-12″ (B: ACCEPTED as the owner's consequence) re-determined **NOT ACCEPTED as stated** (RV7-M2, RV7-M3), and TB-S2″ (B: WITH CONDITION) re-determined **NOT ACCEPTED as stated** (RV7-M3) | cross pairs and two-distribution lineages are outside the stated sets | `05` |

## 2. Reviewer C (AR-0021, `34633cc`, `BLOCKING_FINDINGS_PRESENT`)

| C item | C severity | Reproduced | Adjudication | Reason | Consolidated |
|---|---|---|---|---|---|
| **RV7-C-H1** C3 proof bounds the event, not the state; air-gapped machine C3 on an 882-hour-old media state | HIGH | yes: cur7x byte-identical | **CONFIRMED HIGH; DUPLICATE root cause of RV7-B-H2** (consolidated) | same rule (R-CUR-1/2), same executor gap; C's instance (offline media) is the OT-1 path and establishes the -0002 deviation | RV7-H2 |
| C's statement: "Whether C1–C2 on an anchored-but-stale chain is permitted is a genuinely new owner trade-off raised by OT-1" | claim | design (RV7-D-A09) | **REFUTED** | OP-7 (a) selects 90-day and 7-day anchors with C0 after expiry; -0002 clarifies OP-7 ("Do not extend or weaken") and its C1–C3 clause is scoped to production admission/install without fresh state. No new trade-off; the reading should be stated in the ratification package. | RV7-I3 |
| RV7-C-M1 first admission after protected-store loss discards a surviving high-water | MEDIUM | yes: adm7x X2 equal | **CONFIRMED MEDIUM; not escalated** | C proposed HIGH if protected-store loss with a surviving home is ordinary. It is ordinary (a reinstall keeping `/home`), but the exposure is bounded: the next admission still needs both sources' codes and a state ≤ 24 h, so what is lost is protection against material inside that window and the pending per-project obligations (which LR-4 already accepts on a fresh machine). Carriable as a restrictor-merge rule; strengthened in `11` §6. | RV7-M5 |
| RV7-C-M2 no realizable per-project record identity | MEDIUM | yes: ident7 (inode values differ; `every_candidate_contradicts_the_text` true; in this run I2 also matched a different repository re-cloned at the same path) | **CONFIRMED MEDIUM** | fail closed on one side; A2 request on the other | RV7-M6 |
| RV7-C-M3 journal honouring unreachable for a first install | MEDIUM | yes: txn7 `first_install_honouring` equal | **CONFIRMED MEDIUM** | `18` §5.1 versus `18` §4 (design7 quotes byte-identical) | RV7-M7 |
| RV7-C-M4 `git clean -fdx` defeats R-INIT-9 | MEDIUM | yes: txn7 summary equal | **CONFIRMED MEDIUM** | classifications recoverable from Git; `init` produces a valid-looking install without them | RV7-M8 |
| RV7-C-M5 roll-forward depends on the in-memory ARO; evidence stubbed | MEDIUM | yes: txn7 `rollforward_model` equal | **CONFIRMED MEDIUM** | fail closed (`IN_TRANSACTION`) | RV7-M9 |
| RV7-C-L1 recovery undo readings (with RV7-C-A23 uninstall result) | LOW | yes: txn7 rows (differences are commit ids and stash messages only) | **CONFIRMED LOW; merged** | fail closed | RV7-L6 |
| RV7-C-L2 clock high-water poisoned by the machine's own wrong-ahead clock | LOW | yes: adm7x X4 equal | **CONFIRMED LOW** | availability | RV7-L7 |
| RV7-C-L3 floors atomicity | LOW | yes: adm7x X5 (4,220 decode errors in this run; 0 below-floor reads) | **CONFIRMED LOW** | fail safe | RV7-L8 |
| RV7-C-L4 OT-2 label and criterion | LOW | design | **CONFIRMED; re-rated LOW → MEDIUM; merged** | the -0002 precondition (see RV7-B-L1 above); C deferred the evidence route to B, which predates -0002 | RV7-M2 |
| C: R2-H4 CLOSED as a class | status | yes: `matrix7` reproduced (all 196 position aggregates and every property equal after composing the P-TXN re-run; `01-REPRODUCTION.md`), `struct7` byte-identical, `gitops7` states equal for 45 operations, `txn7` summary equal, `registers7` byte-identical | **CONFIRMED** | 0 violations under every reading; LP-1r 0 project writes | CD7-0 |
| C: RV6-M3 NARROWED; RV6-M4 NARROWED; RV6-M5 CLOSED (model); RV6-M6 CLOSED (attack) / NARROWED (defence) | status | txn7, ident7, PPR7 (architect, byte-identical), ADM7, adm7x | **CONFIRMED** | remainders RV7-M5 … M9 | — |
| C: RV6-L5, L6, L7, L9, L11 CLOSED; L8 CLOSED in specification; L10 NARROWED; C-2, C-3, C-5 OPEN; C-4, C-6 NARROWED | status | CUR7, gitops7, struct7 | **CONFIRMED** | — | carried |
| C: residual CUR-R1 ACCEPTED | determination | CUR7 W; RV7-B-A01 | **REFUTED** | the bound is false under omission (RV7-H1); C's attacks did not include an omission | `05` |
| C: conformance (OP-3, OP-7 (a) deviation, OP-13 media, OP-14 (b) deviation, OP-15, OT-1 not met, OT-2 carried, exclusions conform) | status | as above | **CONFIRMED**, with OT-2 re-determined **NOT MET** (RV7-M2) and OP-14 (b) as a carried gap (RV7-M5) | — | `04` |
| C: D-0008 / ARCH-0002 / D-0007 state | status | design7 byte-identical; `RV7-D-A04.json` | **CONFIRMED** | — | RV7-I2 |

## 3. Prior blocking classes of review r6, consolidated status

| Class | Status | Basis |
|---|---|---|
| **BC6-1** First-contact selector authority | **CLOSED as stated** (composer, printer, submitter, platform root, attacker lineage); **class NARROWED → RV7-M1** (designation delivery) | FA7, PROF7, RV7-B-CS7 A03 reproduced |
| **BC6-2** First-contact currency | **CLOSED as stated** at admission; **class NARROWED → BC7-1** (RV7-H1, omission) and **BC7-2** (RV7-H2, running-machine C3) | CUR7, cur7x, RV7-B-A01, A02 reproduced; RV7-D-A01 |
| **BC6-3** First-hand environment manifest | **CLOSED** | ENV7 reproduced with the real toolchain |
| **BC6-4** Register over inputs; statements; plan detection | **NARROWED → BC7-3** (RV7-M1, M2, M3 statements) and RV7-M10 (plan detection, carried) | REGISTER-CHECK, DA09r7, DA04r7 reproduced; RV7-D-A02, A06 |
| R2-H4 | **CLOSED as a class** (confirmed again) | `matrix7` reproduced |
