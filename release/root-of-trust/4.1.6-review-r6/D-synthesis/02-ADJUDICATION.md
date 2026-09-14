# 02 — Adjudication of the review r6 panel (synthesis D, AR-0018)

Every panel finding is judged here as `CONFIRMED` (with its severity kept or changed, and the reason), `REFUTED` (with the
evidence), or `DUPLICATE`. The probes behind each item were re-run (`01-REPRODUCTION.md`). Consolidated identifiers are those of
`10-BLOCKING-FINDINGS.md`.

## 1. Reviewer B (AR-0016, `5128086`)

| Item | B severity | Reproduction | Adjudication | Reason | Consolidated |
|---|---|---|---|---|---|
| **RV6-B-H1** publisher-composed first-contact code | HIGH | B-A01 parts P and C byte-identical | **CONFIRMED HIGH**, extended | No rule has a source establish the value it carries (`07` §7 step 15, `30` R-PUB-4, `06` §2, `32` §3–§4, §9; text search repeated). The executed rows admit a substituted evaluator under (a), (b), (c) either and (d) with no source compromised. D-A01 finds the same shape for the source list and procedure steps, and for WR victims. | RV6-H1 |
| **RV6-B-H2** OP-13 (c) "either": submitter and replay | HIGH | B-A01 parts R, S, I byte-identical | **CONFIRMED HIGH**, split by class | The submitter part is a first-contact **authority** defect (the party that submits a package selects the evaluator): RV6-H1. The replay part is a first-contact **currency** defect, which D-A02 and D-A08 show is not limited to (c) "either": RV6-H2. | RV6-H1 (submitter), RV6-H2 (replay) |
| **RV6-B-H3** environment manifest not established | HIGH | B-A02 (executed, real toolchain; computed) byte-identical | **CONFIRMED HIGH**, extended | R-BENV-1…5 establish that the tree follows from the manifest, not who chose the manifest. The executed recipe, placement, shared-recipe, label and key rows are all `ACCEPTED`. D-A05 E1 shows {pipeline} stays minimal under OP-9 (d), OP-8 = 2, OP-2 (b), FA and CIR. | RV6-H3 |
| **RV6-B-M1** re-admission keeps but does not apply the store | MEDIUM | B-A04 byte-identical | **CONFIRMED; re-rated LOW** for the accepted-TBM consequence; **the same root cause is HIGH** for held negatives and anchors | B's evidence "B8 runs C2 `ALLOWED`" comes from the reference executor's `gov_run`, which does not implement `09` R-ART-2 ("A binary MUST refuse trusted operations when its TBM is below the VTS accepted-TBM high-water"). Under the pack's rules the older binary is admitted, then refused at use: fail closed. D-A02 shows that the same omission, applied to held negatives and anchors, admits a malicious binary the store holds as revoked. | RV6-L5; RV6-H2 |
| **RV6-B-M2** CONTENT rendering (`repo` as a reproducer key) | MEDIUM | B-A03 byte-identical | **CONFIRMED MEDIUM** | False consequence statements for security-material options (OP-2, OP-4, OP-8). D-A06 bounds it: only `repo` is misrendered, only 8 CONTENT rows change, and the calculator's sets and invariants are unaffected. The fix is mechanical; it is a closure criterion of BC6-4. | RV6-M1 |
| **RV6-B-M3** register completeness over rule ids, not selectors | MEDIUM | REGISTER-CHECK byte-identical; B-A16 reasoning re-checked | **CONFIRMED MEDIUM**, extended; **not carriable** | D-A09 (schema fields) and D-A04 (plan detection) show the mechanism cannot see a selector no rule names. The correction changes the architecture's FD-1 mechanism (`29` §4–§5.5, R-SEL-1), so it is blocking class BC6-4, not an implementation requirement. | RV6-M2 |
| RV6-B-L1 R-CON-5 name-matched units | LOW | B-A10 byte-identical | **CONFIRMED LOW**, extended | Selection holds (`verify-registration` exit 3). D-A03: for new files outside the prefix list the listing depends on an optional inventory flag. | RV6-L1 |
| RV6-B-L2 stale text | LOW | design | **CONFIRMED LOW** | `05` §2 lists v1/v3 payload types; §1 `trust-state` row. | RV6-L2 |
| RV6-B-L3 verification before environment registration | LOW | design | **CONFIRMED LOW** | `06` §2 step 4 order; R-VER-1. Closed inside CD6-3. | RV6-L3 |
| RV6-B-L4 derivation-tool provenance | LOW | design | **CONFIRMED LOW** | R-CON-1 names commands, not binaries or scripts. | RV6-L4 |
| RV6-B-I1 acting role | INFO | — | **CONFIRMED** | unchanged | RV6-I1 |

### 1.1 B's status claims on review r5 findings

| B claim | Adjudication | Basis |
|---|---|---|
| BC5-1 NARROWED → H1, H2; RV5-H1 as stated CLOSED | **CONFIRMED**. The consolidated classes are BC6-1 (authority) and BC6-2 (currency). | FA6 ×2 byte-identical (one-page lineage and evaluator refused under (b) and (c) all; 14/14 mutants); B-A01 and D-A01 |
| BC5-2 NARROWED → H3; RV5-H2 as stated CLOSED | **CONFIRMED** | ENV6 byte-identical (E1 pipeline image refused); B-A02 |
| BC5-3 CLOSED as a class (within B's attacks); RV5-H3 CLOSED | **CONFIRMED at the registration.** Content on first-admission machines follows the first-contact root and inherits BC6-1 and BC6-2 (B-A01 part C content sets; D-A01 part C). | CON6 byte-identical (17/17); P4r6 G; CSI 78/78; B-A10; D-A03 exit 3 on non-first-hand new files; RV5-D-A01 re-run byte-identical |
| BC5-4 NARROWED → M2, M3 | **CONFIRMED**. The class is BC6-4 (blocking). | REGISTER-CHECK, STATEMENTS-CHECK byte-identical; B-A03, D-A04, D-A06, D-A09 |
| RV5-M1 CLOSED | **CONFIRMED** | P4r6 `R6-AP5r_*`, FA6 S5 byte-identical |
| RV5-M2 CLOSED as stated → L1 | **CONFIRMED** | CON6 (exits 8, 6, 7) byte-identical |
| RV5-M3 NARROWED → M1 | **CONFIRMED as narrowed**; the remainder is RV6-L5 plus the held-state part of RV6-H2 | ADM6 (verdicts), B-A04, D-A02 |
| RV5-M4 CLOSED | **CONFIRMED** | SRC6 byte-identical; RV5-B-A05 verdicts identical (time-dependent archive digests only) |
| RV5-M5 NARROWED → M3 | **CONFIRMED** | D-A09 |
| RV5-M8 CLOSED (restated) | **CONFIRMED** | UW6 byte-identical; RV5-D-A03 re-run byte-identical with B's revision-6 re-run |
| RV5-M9 CLOSED | **CONFIRMED** | FA6 S4 5/5 same codes |
| RV5-L1, L2, L5, L6, L9 CLOSED; L3 CLOSED by rule | **CONFIRMED** | FA6 ORD, S5, S6; CS6 victim classes; P4r6 KS14, mode-B and CLOCK rows; all byte-identical |
| RV5-L4 NARROWED → L2 | **CONFIRMED** | design |

### 1.2 B's HO-0001 and option determinations

| B determination | Adjudication |
|---|---|
| §3.1 SATISFIED (trust scope) | **CONFIRMED** as a class (`04` §1) |
| §3.2 NOT SATISFIED | **CONFIRMED**; extended by D-A02 (re-admitted workstations holding newer state) and D-A08 (CI images, media) |
| §3.3 NOT SATISFIED | **CONFIRMED** |
| §4 SATISFIED for classification and content selection | **CONFIRMED**; D-A03 adds data-only classification of new files and the listing default (RV6-L1) |
| OP-6, OP-9, OP-13, OP-16 false; OP-14 (b)/OP-15 (a) incomplete; §17 incomplete | **CONFIRMED**; OP-7 (c) and six §17 combinations added (`04` §2) |
| OP-11 "incomplete for binary rollback at re-admission" | **REFUTED as a false statement**: `09` R-ART-2 refuses the older binary at use, so OP-11 (a)'s E10 statement holds. The missing sentence is RV6-L5. |
| Residuals | adopted with the changes in `05-RESIDUALS.md` (FC-R2 bound, FC-R4, RS-B1, RS-5) |

## 2. Reviewer C (AR-0017, `02bb905`)

| Item | C severity | Reproduction | Adjudication | Reason | Consolidated |
|---|---|---|---|---|---|
| RV6-C-M1 out-of-project ignore sources | MEDIUM | `gitops6` output byte-identical | **CONFIRMED; re-rated LOW** | Fail closed (`PARTIAL(occupation)`). The condition is stated exactly and D033 names the source (RT-174). The remaining item, force-adding the occupation in `kernel reinstall`, is availability text. Review r5 held it MEDIUM while the condition was unstated. | RV6-L6 |
| **RV6-C-M2** first-install layout migration outside the journal model | MEDIUM | `crashmig6` output byte-identical | **CONFIRMED MEDIUM**, extended | RoT-1 never reaches `COMPLETE` from a half-migrated tree by a legacy command, and tracked files are restorable. D-A10: the pack does not state what `init` does with an existing overlay on `ABSENT`. The carried rule must forbid the unsafe behaviour. | RV6-M3 |
| **RV6-C-M3** record identity under duplication | MEDIUM | executed fact (C); design | **CONFIRMED MEDIUM** | Each reading converts a recorded machine into fresh-machine behaviour (LR-4, RR-2) or cross-contaminates two projects; a bound identity rule closes it. | RV6-M4 |
| **RV6-C-M4** contradictory re-record rules | MEDIUM | design | **CONFIRMED MEDIUM** | The safe reading is what RT-81 and RT-167 assert; a single rule removes the unsafe one. | RV6-M5 |
| **RV6-C-M5** two incompatible store specifications | MEDIUM | `admtx6` byte-identical; design | **CONFIRMED MEDIUM**, extended | D-A07 executes the reading in which the first-admission decision rests on an unsigned file in the account store: the move-aside is suppressed. A3 can write that store after admission too (RS-3), so no trust relationship changes. | RV6-M6 |
| RV6-C-L1 `.git/info/attributes` override | LOW | `gitops6` byte-identical | **CONFIRMED LOW** | fail closed; stated condition | RV6-L7 |
| RV6-C-L2 `done/` scan scope | LOW | design; `state_r6` | **CONFIRMED LOW** | fail safe | RV6-L8 |
| RV6-C-L3 `gov-admit` reference edges | LOW | `admtx6` byte-identical | **CONFIRMED LOW** | fail safe; within A3 | RV6-L9 |
| RV6-C-L4 overlay litter location | LOW | C matrix (`01-REPRODUCTION.md`) | **CONFIRMED LOW** | default-deny overlay file; weakening report is fail safe | RV6-L10 |
| RV6-C-L5 evidence and text accuracy | LOW | C's LAY6 reproduction (claim); design | **CONFIRMED LOW** | text and evidence corrections only | RV6-L11 |
| RV6-C-L6 rollback and accepted-TBM high-water | LOW | design | **DUPLICATE** of RV6-B-M1's re-rated consequence | same root cause and the same `09` R-ART-2 outcome | RV6-L5 |

### 2.1 C's status claims

| C claim | Adjudication | Basis |
|---|---|---|
| **R2-H4 CLOSED as a class** | **CONFIRMED** | `matrix6` re-run from C's unmodified probes on independently rebuilt trees (`01-REPRODUCTION.md` §3); `struct6`, `gitops6`, `attrprec6` byte-identical |
| RV5-M3 CLOSED at model level | **CONFIRMED for the store-keeping rule**; the store is not applied (RV6-L5, RV6-H2), which is trust scope | ADM6, `admtx6`, D-A02 |
| RV5-M6 CLOSED as a class | **CONFIRMED** | `gitops6` (`AUTOCRLF`, `TEXTAUTO_EOLCRLF`, `TEXTEOL_CRLF` `COMPLETE`), `attrprec6` byte-identical |
| RV5-M7 NARROWED → C-M1 | **CONFIRMED**, consolidated at LOW (RV6-L6) | as above |
| RV5-L7 NARROWED → C-L4; RV5-L8 CLOSED in specification | **CONFIRMED** | matrix; design |
| C-2, C-3, C-5 OPEN; C-4, C-6 NARROWED | **CONFIRMED** (carried) | design; `struct6`; `gitops6` sparse rows |
| HO-0001 §3.4 SATISFIED as a class | **CONFIRMED** (`04` §1) | matrix, `struct6`, `gitops6`, `crashmig6` |
| `NO_BLOCKING_FINDINGS` | **CONFIRMED within C's scope** | no C item is HIGH after adjudication |

## 3. Consolidation map

| Consolidated | From B | From C | From D |
|---|---|---|---|
| RV6-H1 | H1, H2 (submitter) | — | A01 (designation, WR) |
| RV6-H2 | H2 (replay) | — | A02, A08, A01 S2 |
| RV6-H3 | H3 | — | A05 E1 |
| RV6-M1 | M2 | — | A06 |
| RV6-M2 | M3 | — | A04, A09 |
| RV6-M3 | — | M2 | A10 |
| RV6-M4 | — | M3 | — |
| RV6-M5 | — | M4 | — |
| RV6-M6 | — | M5 | A07 |
| RV6-L1 | L1 | — | A03 |
| RV6-L2 … L4 | L2 … L4 | — | — |
| RV6-L5 | M1 (re-rated) | L6 (duplicate) | A02 (R-ART-2 row) |
| RV6-L6 | — | M1 (re-rated) | — |
| RV6-L7 … L11 | — | L1 … L5 | — |
| RV6-L12 | — | — | A05 E2 |
| RV6-I1, I2 | I1 | — | RV5-I2 carried |
