# 04 — HO-0001 owner requirements and owner options (review r6 synthesis D, AR-0018)

## 1. HO-0001 §3 and §4, judged as classes

### §3.1 Constitutional-floor closure — **SATISFIED**

| Sub-item | Determination | Evidence |
|---|---|---|
| complete constitutional key inventory | holds | CSI self-test 78/78 and checks 0/3/2/2/2 reproduced (framework, 4.1.5, 4.1.2–4.1.4) |
| default deny of unknown constitutional keys and files | holds | B-A10 K5/K6 exit 2 (reproduced); D-A03: three new files exit 2 |
| explicit floor mode per mutable field; coverage check fails the release | holds | self-test; `csi_check.py check` exit codes |
| schema evolution cannot silently add an unfloored setting | holds | D-A03: new files classified by inventory data only (exit 0); unclassified exit 2 |
| role→authority map; irreversible Human Gate authority; install/update authority; exception authority; project override | holds | P1r4 on real 4.1.5 byte-identical; self-test cases retained from revision 5 |
| sensitivity and indexing exclusions; plugin and tool permission floor | holds at the registration | CON6 byte-identical: the `ASIA…` file excluded on 4.1.5 under the content revision 6 makes effective; `verify-registration` refuses non-first-hand content (exit 3). Carried: RV6-L1 (listing of some units). On first-admission machines, effective content follows the first-contact root (RV6-H1, RV6-H2, counted under §3.2/§3.3) |
| outbound and export controls | holds (floor units classified) | self-test; checks |
| a future unknown constitutional field | holds | B-A10 K5; D-A03 |

### §3.2 New-machine trust bootstrap — **NOT SATISFIED**

| Sub-item | Determination | Evidence |
|---|---|---|
| first install | **fails** | RV6-H1 (composer, designation, submitter select the evaluator); RV6-H2 (stored, replayed or designated values select stale state) |
| clean CI runner | **fails** | codes provisioned into an image have no age bound (D-A08: B7x `ACCEPTED`); image codes are composed values (RV6-H1) |
| restored from backup; old epoch; no epoch; two machines at different epochs; long offline | holds for trust-state selection by transport and repository adversaries | B-A11 reproduced byte-identical: 352 rows, 0 `current`, 0 C3 on the thief descendant, CLOCK-back 0 C3; RS-2b stated |
| signed-state replay | **fails at first admission and re-admission**; holds for running machines | B-A01 R, D-A02, D-A08; P4r6 and B-A11 for running machines |
| safe without freshness; gated; freshness witness; persisted monotonic state | stated; **monotonic state not applied at re-admission** | `24` §4.3, §8; D-A02 |
| OP-7's effect | stated for running machines; **(c) witness input taken from a publisher-composed value** | B-A11; D-A01 part C (WR) |
| gate records from repository state | holds | `27`; DR-34; retained P4r4 row (P4r5/P4r6 re-run byte-identical) |

### §3.3 Binary and root authenticity — **NOT SATISFIED**

| Sub-item | Determination | Evidence |
|---|---|---|
| no single lower-threshold key mints a binary | holds | B-A12 reproduced (246,608 subsets, 0 accepts with ≤ 1 key); CS6 INV-ONE; KS-14 |
| threshold root signature; multi-signature | holds | KS-14 (P4r6, FA6 S5 reproduced); OP-2 registration at rank 1 or 2 |
| reproducible-build evidence | mandatory in the rules; **the build environment's manifest is not established** | RV6-H3 (B-A02 executed; D-A05 E1) |
| the binary, compiled roots, minimum floors, trust-policy identity, historical-release set, trust-state and bootstrap rules | **inherit RV6-H3**: they are files of the registered source compiled in a registered environment whose manifest has no establishing party | `25` §8; RV6-H3 |
| non-circular chain | holds in running mode; **at first contact the first link is a value no counted party establishes** | P4r6; RV6-H1 |

### §3.4 Legacy-binary damage containment — **SATISFIED**

| Sub-item | Determination | Evidence |
|---|---|---|
| kernel, legacy lock, trust, rollback, reinstall, init-force and migration paths | holds | reviewer C's `matrix6` re-run (`01-REPRODUCTION.md` §3): R2-H4 0 violations, LP-1r 0 project writes; `struct6`, `gitops6`, `attrprec6` byte-identical |
| no dependence on old binaries understanding RoT-1 | holds | registers derived from each binary's own `--help` and source (`registers6` counts reproduced) |
| no silent mutation into a state RoT-1 then treats as valid | holds | as above; `crashmig6` byte-identical (no legacy command reaches `COMPLETE`) |
| carried | RV6-M3 (crash in the first-install migration; `init` on `ABSENT`), RV6-M4, RV6-M5, RV6-L6, RV6-L7, RV6-L10 | `11` §6 |

### §4 Forward-compatibility constraint — **SATISFIED for classification and content selection**

D-A03: new Gate W and G0–G6 files fail default deny without an inventory row, are classified by a data-only row, and a
non-first-hand weakened proposal is refused. The per-project listing of their changes depends on an optional flag at unlisted paths
(RV6-L1, carried with the flag made mandatory). The Capability Acceptance Contract's owner-domain binding group is exercised by the
checker's self-test (78/78 reproduced); derivation between its members is carried (RV6-I2, RT-182).

## 2. Owner options OP-1 … OP-16

| Question | Determination |
|---|---|
| Pre-decided? | **No.** D-0008 has no `chosen_option`; `owner_parameters_pending` states "no proposal" for each; `21` states no default. (D-0008's `recommended_option: C` concerns the architecture alternative, labelled "RECOMMENDATION ONLY — NOT A DECISION", not an owner parameter.) |
| Honest about security consequences? | **No** (table below) |
| Complete? | **No.** There is no option for who establishes first-contact values (`11` CD6-1 F1-a…F1-c), and none for the maximum age of stored first-contact values (CD6-2 C-a…C-c). |

| Option | Consequence statement at `4106885` | Basis |
|---|---|---|
| OP-1 | accurate | KS-14 rows reproduced |
| OP-2 | selection statements hold at the registration; the CONTENT block misprints `repo` (8 rows); first-admission content follows the first-contact root, which is misstated | RV6-M1; RV6-H1 |
| OP-3 | accurate | P4r6 mode-B rows reproduced |
| OP-4 | holds; CONTENT misprint | RV6-M1 |
| OP-5 | informational | — |
| OP-6 | **false**: "the lineage confirmed is the one the first-contact root selects"; the lineage is the one the composer or the designation selects | RV6-H1 |
| OP-7 | (a), (b), (d) and the user-writable table accurate; **(c) incomplete**: the witness input can be a publisher-composed value, so WR victims need no witness keys | B-A11, UW6 reproduced; D-A01 part C |
| OP-8 | accurate | CON6, CS6 reproduced |
| OP-9 | **false** for P1 ("never on P1"), P2k1, P2k2, CIR and WR | RV6-H1 (B-A01 C, D-A01 C) |
| OP-10 | accurate; the combination with OP-16 (b) is unstated | RV6-L12 |
| OP-11 | accurate (E10 kept; an older binary fails closed at use by R-ART-2) | `09` R-ART-2; RV6-L5 |
| OP-12 | accurate as stated; under (b) the script's source list is subject to RV6-H1 (designation) | D-A01 |
| OP-13 | **false**: composer, designation and submitter (RV6-H1); replayed, stored or designated values of unbounded age (RV6-H2); FA6 S3's equality holds within a model that omits them | B-A01; D-A01, A08 |
| OP-14 (b), OP-15 (a) | **incomplete**: re-admission keeps the store but does not apply it; a binary revoked in held state is admitted from an older value | D-A02 |
| OP-16 | **false** for (a) and (b): the manifest author selects the bytes; (b) counts labels | RV6-H3 |
| §17 combinations | **incomplete**: six security-changing combinations unstated (D-A05) | D-A05 |

**Consequence statements the next revision must regenerate** (inputs to the owner decision package once an architecture is
accepted): FC-ROOT, FC-KEY-THEFT, FC-CONTENT, OP-9-BYTES (P1, P2k1, P2k2, CIR, WR), OP-16-ENV, CONTENT (rendering), `25` §6–§7,
`21` OP-6, OP-7 (c), OP-13, OP-14 (b), OP-15 (a), OP-16 and §17, plus the new F1 and C option tables. None of them is corrected here:
they depend on the mechanisms the next architect chooses.
