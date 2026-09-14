# Independent architecture synthesis review (D) — RoT-1 revision 6 (Governance OS 4.1.6)

| | |
|---|---|
| **Architecture verdict** | **`ROOT_OF_TRUST_ARCHITECTURE_REJECTED`** |
| Run | AR-0018, role `rot-review-synthesis`, handoff `HO-0018` |
| Revision reviewed | `release/root-of-trust/4.1.6/`, `spec/decisions/D-0008.yaml`, `spec/architecture/ARCH-0002.yaml`, `docs/DECISIONS.md` at `4106885dadebac55596067a2586cf4d3097fc025`; identical at this review's base (`git diff --quiet 4106885 b9bed32` for those paths) |
| Panel verified | reviewer B `512808695e8f3eb11187a8c70dc07e6783ad8395` (`BLOCKING_FINDINGS_PRESENT`); reviewer C `02bb90550342e8bb6d42ba636430ae3394d3a0f7` (`NO_BLOCKING_FINDINGS`); both directories identical at the base (checked) |
| Branch and base | `phase1/rot1-r6-review-d` from `b9bed32` |
| Implementation | `runtime/`, `cli/`, `framework/`, `migrations/`, `capabilities/`, `Cargo.*`, `release/releases/` unchanged since `da9c851` (checked) |
| Date | 2026-09-14 |
| D-0008 / ARCH-0002 | Remain PROPOSED: record status `PROVISIONAL`, `in_effect: false`, no `chosen_option`. This review approves nothing. Acceptance of an architecture would not be owner approval. |

## Scope

The whole of revision 6, as the architecture that governs 4.1.6, judged against HO-0018 §3's acceptance rule and HO-0001 §3–§4's
owner requirements. The review covers:
- reproduction of every panel probe behind a HIGH claim or a claim that a prior HIGH is closed, and of the architect's
  instruments;
- adjudication of every B and C finding;
- held-out attacks RV6-D-A01…A10;
- owner requirements, residuals and owner options;
- for each blocking class, its novelty and the kind of fix it needs (HO-0018 §2a).

## Independence

- **Authored before by this session:** nothing. No RoT-1 revision, specialist proposal, reviewer B or C work, or prior review.
- **Orchestration files read:** `HO-0018`, `HO-0001` and `AGENT_RUNS/README.md` only.
  - Disclosure: to check that the pack was unchanged since `4106885`, `git diff --stat 4106885 b9bed32` was run. It lists the names
    and line counts of orchestration files added since (run records, report files, checkpoints, handoffs HO-0016/HO-0017,
    orchestrator state, ledger). None was opened.
- **Disclosure: memory index.** The host context included the user's auto-memory index (one-line summaries of earlier Governance
  OS reviews). No memory file was opened; nothing here rests on it.
- **Disclosure: harness file.** The harness saved one of this session's own command outputs (the schema and D-0008 text) under a
  tool-results path in `~/.claude/projects/`. The file was not opened; the content was re-read from the worktree.
- **Disclosure: Git reads.** Reviewer C's `register6.py` ran `git show` at the four legacy release commits in this review's
  worktree (read-only). Reviewed-content digests were computed from Git objects at the named commits.
- **Not inspected:** other branches, other worktrees, other scratch directories, session or agent transcripts, task-output files.
- **Helper sessions:** none.
- **Treated as claims:** the response matrix (`22`), the class-remainder analysis (`28`), the decision register and its checks,
  the calculator, the generated statements, every architect evidence file, and every statement of reviewers B and C.
- **Hygiene:** `D-synthesis/evidence/README.md`.

## 1. Verdict against the acceptance rule (HO-0018 §3)

| Condition | Result |
|---|---|
| No open CRITICAL or HIGH after adjudication | **Not met.** 3 HIGH: RV6-H1, RV6-H2, RV6-H3 (`10-BLOCKING-FINDINGS.md`) |
| Every HO-0001 §3 requirement `SATISFIED` as a class | **Not met.** §3.2 and §3.3 `NOT SATISFIED`; §3.1 and §3.4 `SATISFIED` (§5) |
| Every open MEDIUM carried as a bound, testable requirement; none needs an architecture change | **Not met for RV6-M2**, whose correction is the architecture's FD-1 mechanism (blocking class BC6-4). RV6-M1, M3, M4, M5 and M6 are carriable (`11` §6). |
| Every residual explicitly bounded under attack | **Not met.** AD-1′/FC-R1, FC-R2 (as stated), FC-R3, FC-R4, RS-B1 and TB-S2′ under OP-16 (a)/(b) are not accepted (§6). |
| Owner options complete and honest, none pre-decided | **Not met** for honesty and completeness (§7). Met for "none pre-decided". |

**Verdict: `ROOT_OF_TRUST_ARCHITECTURE_REJECTED`.** The correction is architectural and stated as classes in
`11-CORRECTION-DELTA.md`.

### What revision 6 does close (confirmed by reproduction)

- **RV5-H1 as stated.**
  - One page no longer selects lineage, quorum or evaluator: the quorum is compiled, lineage comes from the typed value, and the
    evaluator is bound.
  - Evidence: FA6 byte-identical over two runs (S2, S4 5/5, S7 14/14).
- **RV5-H2 as stated.**
  - No pipeline image record: components are checked against upstream checksums, the environment is established by a
    reproduction quorum, and reproducers re-assemble.
  - Evidence: ENV6 byte-identical (21/21).
- **RV5-H3 at the registration.**
  - Content is derived first-hand; attestations are bound to the registered candidate and kernel; E7 carries AP-5's restrictors;
    reductions are computed at the verifier.
  - Evidence: CON6 byte-identical (17/17); P4r6 G; CSI 78/78; B-A10 and D-A03 (`verify-registration` exit 3 on every
    non-first-hand proposal, including new constitutional files).
- **R2-H4 as a class.**
  - Evidence: reviewer C's `matrix6` re-run (62,036 rows; R2-H4 0 violations; LP-1r 2,492 rows, 0 project writes); `gitops6`,
    `struct6`, `attrprec6` and `crashmig6` byte-identical.
- **Carried closures.**
  - RV5-M1, M4, M8, M9 and RV5-L1, L2, L3 (by rule), L5, L6, L9.
  - Running-machine currency for transport and repository adversaries: B-A11 (352 rows, 0 `current`).
  - Key subsets below threshold: B-A12 (246,608 subsets, 0 accepts with ≤ 1 key).

## 2. Reproduction table

Detail: `D-synthesis/01-REPRODUCTION.md`; logs and comparisons in `D-synthesis/evidence/reproduction/`.

| Probe (owner) | Behind claim | Reproduced |
|---|---|---|
| RV6-B-A01 (B) | **RV6-B-H1, H2** | **yes**, byte-identical |
| RV6-B-A02 (B; real toolchain) | **RV6-B-H3** | **yes**, byte-identical |
| RV6-B-A03, A04, A10 (B) | M2, M1, L1 | **yes**, byte-identical |
| RV6-B-A11, A12 (B) | §3.2 running machines; §3.3 key subsets | **yes**, byte-identical |
| CS6, P4r6, DA03r6, FA6 ×2, CON6, ENV6, SRC6, UW6, ATTR6, DA07r6, REGISTER-CHECK, STATEMENTS-CHECK, CSI6 self-test (architect) | RV5-H1/H2/H3 as stated closed; BC5-4; carried closures | **yes**, byte-identical |
| ADM6; CSI6 checks ×5 (architect) | RV5-M3; §3.1 | **yes**, except the unlocked mutant's race and the `kernel_dir` path |
| CS5, P4r5, DA03r5, REG5, P1r4, FA5 (retained) | CD5-0 | **yes** (FA5 equal in every leaf) |
| reviewer C `matrix6` (14 workers) | **R2-H4 CLOSED as a class** | **yes**: every count, property and aggregate equal |
| reviewer C `crashmig6`, `gitops6`, `struct6`, `attrprec6`, `admtx6`; `register6` | RV6-C-M2; RV5-M6; C-L1, L3; registers | **yes**: byte-identical; `register6` equal in every count and leaf path |
| review r5 decisive probes (B-A01, A04, A05, A08, A09, A12; D-A01, A03, A04, A05, A07) | prior HIGH closures | **yes**: byte-identical, or differing only in time- or compiler-dependent digests or rows revision 6 restated |

## 3. Adjudication of the panel

Detail: `D-synthesis/02-ADJUDICATION.md`.

| Panel item | Panel severity | Adjudication | Consolidated |
|---|---|---|---|
| RV6-B-H1 publisher-composed first-contact code | HIGH | **CONFIRMED HIGH**, extended (D-A01 designation; WR victims) | RV6-H1 |
| RV6-B-H2 (c) "either": submitter and replay | HIGH | **CONFIRMED HIGH**, split: submitter → authority class, replay → currency class | RV6-H1, RV6-H2 |
| RV6-B-H3 environment manifest | HIGH | **CONFIRMED HIGH**, extended (D-A05 E1) | RV6-H3 |
| RV6-B-M1 re-admission does not apply the store | MEDIUM | **CONFIRMED**. The accepted-TBM consequence is re-rated LOW: `09` R-ART-2 refuses at use, and the reference `gov_run` lacks it. The same root cause for held negatives and anchors is HIGH (D-A02). | RV6-L5; RV6-H2 |
| RV6-B-M2 CONTENT rendering | MEDIUM | **CONFIRMED MEDIUM** (D-A06 bounds it) | RV6-M1 |
| RV6-B-M3 register over rule ids | MEDIUM | **CONFIRMED MEDIUM**, not carriable (D-A04, D-A09) | RV6-M2 |
| RV6-B-L1 … L4 | LOW | **CONFIRMED LOW** (L1 extended by D-A03) | RV6-L1 … L4 |
| RV6-B-I1 | INFO | CONFIRMED | RV6-I1 |
| RV6-C-M1 ignore sources | MEDIUM | **CONFIRMED, re-rated LOW** (condition stated exactly, detection specified, fail closed) | RV6-L6 |
| RV6-C-M2 first-install migration crash | MEDIUM | **CONFIRMED MEDIUM**, extended (D-A10) | RV6-M3 |
| RV6-C-M3, M4 | MEDIUM | **CONFIRMED MEDIUM** | RV6-M4, M5 |
| RV6-C-M5 two stores | MEDIUM | **CONFIRMED MEDIUM**, extended (D-A07) | RV6-M6 |
| RV6-C-L1 … L5 | LOW | **CONFIRMED LOW** | RV6-L7 … L11 |
| RV6-C-L6 rollback and high-water | LOW | **DUPLICATE** of RV6-B-M1's re-rated consequence | RV6-L5 |
| B: BC5-1, BC5-2 narrowed; RV5-H1/H2 as stated closed; BC5-3 closed | status | CONFIRMED; BC5-3 closed at the registration (first-admission content inherits BC6-1, BC6-2) | §8 |
| B: OP-11 incomplete | status | **REFUTED** as a false statement (R-ART-2 refuses at use) | RV6-L5 |
| C: R2-H4 CLOSED as a class | status | CONFIRMED (reproduced) | §8 |
| C: `NO_BLOCKING_FINDINGS` | verdict | CONFIRMED within C's scope | — |

## 4. Consolidated findings

Full statements: `10-BLOCKING-FINDINGS.md`.

| ID | Severity | Title | Origin | Adjudication |
|---|---|---|---|---|
| **RV6-H1** | **HIGH** | First-contact values (manifest and code, source list and procedure steps, platform package) are composed, designated and submitted by parties outside the stated first-contact root | B + D | CONFIRMED HIGH, extended |
| **RV6-H2** | **HIGH** | First-contact currency is unbounded: stored, replayed or designated values select stale state, also on re-admission over a store holding newer state | B + D | CONFIRMED HIGH, extended |
| **RV6-H3** | **HIGH** | No party establishes the environment manifest; its author selects every production binary's bytes under OP-16 (a)/(b) | B + D | CONFIRMED HIGH, extended |
| RV6-M1 | MEDIUM | CONTENT block renders `repo` as a reproducer key (8/24 rows); S1 compares text | B + D | CONFIRMED |
| RV6-M2 | MEDIUM | Register completeness is over rule ids, not input values; tests cannot detect a missing selector | B + D | CONFIRMED, extended; not carriable (BC6-4) |
| RV6-M3 | MEDIUM | First-install layout migration outside the journal model; `init` on `ABSENT` with an existing overlay unstated | C + D | CONFIRMED, extended |
| RV6-M4 | MEDIUM | Per-project record identity unsound under duplication | C | CONFIRMED |
| RV6-M5 | MEDIUM | Contradictory re-record rules can clear strength reports or pending gates | C | CONFIRMED |
| RV6-M6 | MEDIUM | Two incompatible store specifications; a planted unsigned record suppresses the first-admission move-aside | C + D | CONFIRMED, extended |
| RV6-L1 | LOW | R-CON-5 listing by name list or optional flag; new files at unlisted paths not listed | B + D | CONFIRMED, extended |
| RV6-L2 | LOW | Stale revision-5 text in `05` | B | CONFIRMED |
| RV6-L3 | LOW | Verification precedes environment registration | B | CONFIRMED |
| RV6-L4 | LOW | Derivation-tool provenance unstated | B | CONFIRMED |
| RV6-L5 | LOW | Accepted-TBM high-water not applied at admission or rollback (fail closed by R-ART-2); reference lacks R-ART-2 | B + C + D | B-M1 re-rated; C-L6 duplicate |
| RV6-L6 | LOW | Out-of-project ignore sources (fail closed; condition stated) | C | re-rated from MEDIUM |
| RV6-L7 | LOW | `.git/info/attributes` override (fail closed) | C | CONFIRMED |
| RV6-L8 | LOW | `done/` archive in the foreign-artefact scan | C | CONFIRMED |
| RV6-L9 | LOW | `gov-admit` reference edges | C | CONFIRMED |
| RV6-L10 | LOW | Overlay subtree litter unnamed | C | CONFIRMED |
| RV6-L11 | LOW | Evidence and text accuracy | C | CONFIRMED |
| RV6-L12 | LOW | `21` §17 omits OP-16 (b) + OP-10 (a) | D | NEW |
| RV6-I1 | INFO | Acting role caller-declared | B | unchanged |
| RV6-I2 | INFO | Binding-group derivation carried to the capability-contract phase (RT-182) | RV5-I2 | carried |

## 5. HO-0001 §3 owner requirements

Detail: `D-synthesis/04-OWNER-REQUIREMENTS-AND-OPTIONS.md` §1.

| Requirement | Determination | Decisive evidence |
|---|---|---|
| §3.1 Constitutional-floor closure | **SATISFIED** | CSI 78/78, checks 0/3/2/2/2, P1r4, CON6 (reproduced); B-A10 and D-A03 default deny and first-hand refusal. Carried: RV6-L1. |
| §3.2 New-machine trust bootstrap | **NOT SATISFIED** | **Fails:** first install (RV6-H1, H2); clean CI runner (D-A08, RV6-H1); signed-state replay at first admission and re-admission (B-A01 R, D-A02). **Holds:** restored, old epoch, no epoch, two machines, long offline, for transport and repository adversaries (B-A11 reproduced); repository gate records. |
| §3.3 Binary and root authenticity | **NOT SATISFIED** | **Fails:** the bytes, and every compiled trust input, inherit the unestablished environment manifest (RV6-H3); at first contact the first link is a value no counted party establishes (RV6-H1). **Holds:** no accept with ≤ 1 key (B-A12); root threshold ≥ 2; running-mode chain. |
| §3.4 Legacy-binary damage containment | **SATISFIED** | `matrix6` re-run (R2-H4 0 violations, LP-1r 0 writes); `gitops6`, `struct6`, `crashmig6` byte-identical. Carried: RV6-M3, M4, M5, L6, L7, L10. |
| §4 Forward-compatibility constraint | **SATISFIED** for classification and content selection | D-A03: new Gate W and G0–G6 files default deny, classified by data only, non-first-hand proposal refused; listing default carried (RV6-L1) |

## 6. Residual determinations

Detail: `D-synthesis/05-RESIDUALS.md`.

| Residual | Determination |
|---|---|
| **AD-1′/FC-R1, FC-R3, FC-R4, RS-B1** | **NOT ACCEPTED** (RV6-H1, RV6-H2) |
| **FC-R2** | **NOT ACCEPTED as stated**: the residual is core, but its stated bound rests on the procedure printer (RV6-H1) |
| **TB-S2′** | **NOT ACCEPTED** under OP-16 (a), (b) (RV6-H3); ACCEPTED for (c) |
| AD-2 | ACCEPTED WITH CONDITION RV6-M6 |
| TB-S1 (environment) | ACCEPTED WITH CONDITION CD6-3 |
| RA-1 | ACCEPTED WITH CONDITION RV6-L1 |
| TB-L4 | ACCEPTED WITH CONDITION RV6-L5 |
| RS-5 | ACCEPTED WITH CONDITION CD6-1 (witness input established) |
| RS-3, VR-3, TG-2 | ACCEPTED WITH CONDITION CR4-B-01 |
| CS-1 | ACCEPTED WITH CONDITION CR4-B-05 |
| RR-2, LR-2, LR-4 | ACCEPTED WITH CONDITION RV6-M3, M4 (and CR4-B-04 for LR-4) |
| TB-1′, VR-B1′, TB-S1, TB-S2, TB-S3, TB-4, TB-4′, AV-S1, RS-1, RS-1b (established anchors), RS-1c, RS-2, RS-2b, RS-4 (scoping), OP-7 (d), CS-2, DR-15, DR-33, VR-1, VR-2, VR-4, RR-1, RR-3, TG-1, TG-3, LR-1, LR-3, layout durability | ACCEPTED |

## 7. Owner options

| Question | Determination |
|---|---|
| Pre-decided? | **No.** D-0008 has no `chosen_option`; every OP-1…OP-16 parameter is pending "no proposal"; `21` states no default. |
| Honest about security consequences? | **No.** OP-6, OP-9 (P1, P2, CIR, WR), OP-13 and OP-16 are false. OP-7 (c), OP-14 (b), OP-15 (a) and §17 are incomplete. OP-2 and OP-4 misprint CONTENT (`04` §2). |
| Complete? | **No.** There is no option for who establishes first-contact values (CD6-1 F1-a…F1-c), and none for the maximum age of stored first-contact values (CD6-2 C-a…C-c). |

## 8. Prior findings, consolidated status

| Finding | Status | Basis |
|---|---|---|
| RV5-H1 / BC5-1 | as stated **CLOSED**; class **NARROWED → RV6-H1** (authority) and **RV6-H2** (currency) | FA6 reproduced; B-A01, D-A01, A02, A08 |
| RV5-H2 / BC5-2 | as stated **CLOSED**; class **NARROWED → RV6-H3** | ENV6 reproduced; B-A02, D-A05 |
| RV5-H3 / BC5-3 | **CLOSED at the registration**; content on first-admission machines inherits BC6-1 and BC6-2 | CON6, P4r6 G, CSI, B-A10, D-A03 reproduced |
| BC5-4 | **NARROWED → BC6-4** (RV6-M1, RV6-M2, the false statements) | REGISTER-CHECK, STATEMENTS-CHECK; D-A04, A06, A09 |
| R2-H4 | **CLOSED as a class** (confirmed again) | `matrix6` re-run; `gitops6`, `struct6`, `crashmig6` |
| RV5-M1, M4, M8, M9 | CLOSED | P4r6, FA6, SRC6, UW6 reproduced |
| RV5-M2 | CLOSED as stated; listing scope → RV6-L1 | CON6; D-A03 |
| RV5-M3 | NARROWED → RV6-L5 and the held-state part of RV6-H2 | ADM6, D-A02 |
| RV5-M5 | NARROWED → RV6-M2 | D-A09 |
| RV5-M6 | CLOSED as a class; → RV6-L7 | `gitops6`, `attrprec6` |
| RV5-M7 | NARROWED → RV6-L6 | `gitops6` |
| RV5-L1, L2, L5, L6, L9; L3 (by rule) | CLOSED | FA6, CS6, P4r6 reproduced |
| RV5-L4 | NARROWED → RV6-L2 | design |
| RV5-L7 | NARROWED → RV6-L10 | matrix |
| RV5-L8 | CLOSED in specification | design; matrix transaction-area rows |
| RV5-I1; RV5-I2 | unchanged → RV6-I1; carried → RV6-I2 | — |

## 9. Blocking classes: novelty and kind of fix (HO-0018 §2a)

| Class | Findings | Remainder of, or new | Root invariant not established | Kind of fix and route |
|---|---|---|---|---|
| **BC6-1** First-contact selector authority | RV6-H1 | **Narrowed remainder of BC5-1** (R2-H2/BC-2 ∩ R2-H3/BC-3). The instances (publisher composition, designation and procedure printer, package submitter) are new; the class is not materially new. | Every value that selects the lineage, the state or the evaluator at first contact is established first-hand by a party the stated root counts, or that party is itself a stated root atom with computed sets. The candidate, a carrier or an unregistered party supplies none. Running-machine anchors and witness inputs taken from the channel meet the same condition. | **ENGINEERING_CORRECTION** (first-hand manifest or root-threshold record; lineage compiled into every admitter; designation delivered outside the release carriers; submission at the registration authority; register, calculator, statements) **plus OWNER_TRADE_OFF**: who establishes first-contact values. **F1-a**: every source custodian derives first-hand (cost: an anchored `gov` per custodian and a derivation per Trust State; availability tied to every custodian). **F1-b**: root-threshold record for lineage and admitter, publisher-composed state epoch (residual: the publisher selects the state epoch within CD6-2's age; cost: root ceremony per admitter change). **F1-c**: composer as a stated root atom (residual: one rank-3 process selects every first TCB). Route: **architect, then owner**. |
| **BC6-2** First-contact currency | RV6-H2 | **Narrowed remainder of BC5-1 at its intersection with R2-H2/BC-2** (currency). The instances (replayed package, media, CI codes, designated pages, re-admission over newer state) are new; the class is not materially new. | A first-contact selector of state is current now, or within a mandatory maximum age enforced against a compiled ceiling. No admission selects a state below the store's anchor, or admits a binary the store holds as revoked or below its accepted-TBM high-water. | **ENGINEERING_CORRECTION** (mandatory `valid_until` and ceiling; re-admission applies the store; residuals restated; calculator goal; tests) **plus OWNER_TRADE_OFF**: the maximum age of stored values. **C-a**: per-path maximum (residual: binaries revoked within the window on first-install machines; cost: re-publish, re-sign, re-prepare within the window). **C-b**: stored values select lineage and evaluator only, state read now (cost: online sources at first contact; offline provisioning lost). **C-c**: a mix. Route: **architect, then owner**. |
| **BC6-3** First-hand environment manifest | RV6-H3 | **Narrowed remainder of BC5-2** (BC4-1/R2-H3). The instance (manifest content) is new; the class is not. | Every byte-determining selection, placement, recipe, assembly tool, upstream key and supplier-class fact is established at the registration's authority. The pipeline selects none, and diversity counts established identity. | **ENGINEERING_CORRECTION** only: manifest as reviewed source or normative derivation; upstream keys pinned in the root-signed Trust Policy; supplier class from key identity and disjoint digests; register, calculator, statements. The common-mode residual is already OP-16. Route: **architect**. |
| **BC6-4** Register over inputs; statements; plan detection | RV6-M2, RV6-M1; the false statements of H1–H3 | **Remainder of BC5-4** | Register completeness is defined and checked over every input value with its establishing party. Statements are generated by an injective renderer. Each selector has a test with an input independent of the register. | **ENGINEERING_CORRECTION**. Route: **architect**. |

Each blocking class is the recurring rejection class: **a lower-trust input yielding a current, higher-trust fact**.

| Class | Lower-trust input | Higher-trust fact obtained |
|---|---|---|
| BC6-1 | the trust-state publisher process (rank 3); the carrier-delivered candidate or documentation naming the sources and steps (rank 5); the package submitter (rank 5) | the lineage, the evaluator and the first TCB; anchors of P1, P2, CIR and WR machines |
| BC6-2 | a replayed package, stored media or CI codes, a stale or designated page (rank 5) | a revoked, including malicious, binary as the current TCB, including on machines that hold its revocation |
| BC6-3 | the environment manifest's author (rank 5) | the bytes of every production binary |
| BC6-4 | the scope of the architect's rule tables | the owner's view of consequences; what the plan can detect |

**Unavoidable core versus these classes.** A machine cannot know metadata it never received. At first contact it must accept what
its designated sources show, and the operator must already know where the owner publishes. Both are core and may remain stated
residuals. They are not these findings. The findings are:
- values that no counted party establishes;
- source lists that a carrier or the unadmitted candidate supplies;
- stored or replayed values of unbounded age;
- and admissions that ignore newer state the machine itself holds.

## 10. Held-out attacks

This review authored **10** held-out attacks, RV6-D-A01 … A10 (`D-synthesis/03-HELDOUT-ATTACKS-RV6-D.md`).

| Evidence class | Attacks |
|---|---|
| Executed (reference executor or checker), with computed or design parts | A01, A02, A03, A07, A08 |
| Computed | A04, A05, A06, A09 |
| Design | A10 |

| Required area (HO-0018 §2.3) | Attacks |
|---|---|
| Class-level interactions between the four R2 closures | A01, A02, A07, A10 |
| Owner-option combinations | A05 (with the OP-13, OP-14/15 and OP-7 (c) rows of A01, A02, A08) |
| Forward-compatibility constraint | A03 (and A09) |
| Implementation plan's ability to detect regressions | A04, A06, A09 |

## Output files

| File | Content |
|---|---|
| `00-REVIEW-REPORT.md` | this report |
| `10-BLOCKING-FINDINGS.md` | every consolidated finding, CRITICAL to INFO |
| `11-CORRECTION-DELTA.md` | blocking classes, invariants, engineering corrections, owner trade-offs with options, carried items, re-review entry criteria |
| `D-synthesis/01-REPRODUCTION.md` | reproduction method, results and disclosed deviations |
| `D-synthesis/02-ADJUDICATION.md` | per-item adjudication of B and C; consolidation map |
| `D-synthesis/03-HELDOUT-ATTACKS-RV6-D.md` | held-out register RV6-D-A01 … A10 |
| `D-synthesis/04-OWNER-REQUIREMENTS-AND-OPTIONS.md` | HO-0001 §3/§4 sub-items; owner options |
| `D-synthesis/05-RESIDUALS.md` | residual criteria and determinations |
| `D-synthesis/evidence/` | probes, outputs, reproduction logs and comparisons, reviewed-content digests, README |
