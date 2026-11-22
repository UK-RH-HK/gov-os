---
id: W2-81-PROVING-RUN-0.1.4-ANALYSIS
type: research
status: DRAFT
state_class: EVIDENCE
title: "W2-81's proving run on release 0.1.4 (NOT_READY, seed 7429927): why, by class, and the plan"
role: research
decisions: [DEC-1221, DEC-1223, DEC-1224]
sources: [DEC-1211, DEC-1221, DEC-1223, DEC-1224, DEC-1210, DEC-192, DEC-210, DAEO-l78m, DAEO-xm6l, DAEO-0qs5, DAEO-xw3k, DAEO-cdoi, DAEO-siiz, DAEO-zflj, DAEO-2bdu, DAEO-s9qc, DAEO-zqvn, DAEO-mpq2, DAEO-j9z6, DAEO-0z8c, DAEO-6y0x, CAP-10, CAP-25, CAP-44.b, CAP-44.e, CAP-44.f, CAP-44.g, CAP-44.h, CAP-44.m, CAP-49, CAP-61.e, CAP-63, CAP-01.c, EMERGENCY-2]
---

# W2-81's proving run on release 0.1.4: the analysis

Not committed (the CTO's to commit). Written by a research session, read-only on everything else.

## Question, decision, stop rule

- **Question.** Why did W2-81's proving run on release 0.1.4 give `NOT_READY (seed 7429927)` with 63 reasons, which reasons are Gov OS defects, which are the test's, which are capabilities not built, which are the run's own gaps, which are the machine's, and what do the memory misses point at?
- **Decision it feeds.** EMERGENCY-2 8.2 item 2 (the proving run passes) and S-RERUN's "READY, or READY but for exceptions the owner names one by one" (DAEO-l78m; DEC-1221 (1); DEC-1224 (2): the release acceptance rests on the proving run and EXAMIN's fresh 80). Concretely: what to fix and build before the re-run, which reasons the owner names as exceptions, what a re-run should show.
- **Stop rule.** Evidence-bound: stop when every one of the 63 reasons and every wrong question of the five repositories under 95 % has a cause with a cited record, or is named a residual. Not time-bound.
- **Identity.** The launch's `{CMD:identity}` and `{ID}` slots were unfilled, so the identity command could not be run. `GOV_ROLE` in this shell reads `orchestrator` (inherited from the spawning session), not `research`. The brief of the launching agent named this one output file and nothing else; I wrote only it. Flagged for the CTO.

## Method and commands run

All of it reads records that exist. No suite, no `gov queue`, no `gov accept`, no retrieval, no model session was run.

- Memory first: `gov retrieve` twice (the NOT_READY and S-RERUN question; the trailers/F1 question) and a third on the verdict/findings tickets, bundles read whole; ids used: DAEO-l78m, P-W2-81-VERDICT-1 (the 0.1.0 run's triage), WAVE-2-WBS (W2-81 card), CAP-44.h/.m/.g records, DAEO-ha8z, DAEO-siiz, DAEO-2bdu, DEC-1197. A second search in my own words followed each.
- The run record and folder: `docs/plan/wave-2/w2-81-proving-run/{report.md,report.json,record.md,adopter-brief-0.1.4.md,tools/setup_0.1.4.py}` (branch `e2/w2-81-proving-run`), `~/gov-os-runs/W2-81/run-0.1.4/{report.json,run.log,read.out,outputs/*/FINDINGS.md,outputs/*/evidence/accept.out,outputs/*/dry-realhome/*,outputs/*/doctor.out,e2e/*/*.json,repos/*}`.
- Python one-offs over those files: reason grouping (63 reasons), per-question causes from `report.json` `figures.per_question`, the 121 verdict rows in `e2e/` (citations, attempts, grade), junit/`accept.out` of the dry runs, read-only `sqlite3` on each repository's `.gov-runtime/store.db` (`lexical_file`), the A2/A3/A6/A8 records' front matter, `gov.adopt.project.classify` over each final path map.
- Code and tickets read: `tests/acceptance/W2-81/{w2_81_judge,w2_81_score,w2_81_run}.py` and README; `src/gov/adopt/{command,stages,spec_audit,project}.py`; `src/gov/doctor/command.py`; `src/gov/telemetry/counter.py`; `src/gov/retrieval/{authority,retrieve,lexical}.py`; `src/gov/memaudit/prompts.py`; `docs/contract/contract.yaml`; `governance/project/tool-registry.yaml`; `.tickets/` by `wbs_id`.
- One tool call: `PATH=$HOME/.nvm/versions/node/v22.23.3/bin:$PATH ccusage --version` (answers 20.0.26); `claude --version` (2.1.329).
- Not opened, as instructed: `~/gov-os-eval/**`, `~/gov-os-runs/W2-81-manifests-0.1.4/`. Hidden questions are named by id and cause only; no hidden question or gold text is in this file.

## The 63 reasons, grouped

| # | Reason group | Count | Repositories |
|---|---|---|---|
| R1 | end-to-end figure under 95 | 5 | python-app 80.95, rust-workspace 75, typescript-monorepo 60, legacy-docs 60, secret-history 80 |
| R2 | `gov queue` exit 3 | 6 | all six |
| R3 | planted or hidden problem NOT_BUILT needing only `A2-content-class` | 13 | py 3, rust 2, ts 3, legacy 2, secret 3 |
| R4 | stale-spec NOT_BUILT (`A2-content-class` or `findings`, both absent) | 5 | one in each of the five with planted problems |
| R5 | planted or hidden NOT_BUILT needing only `findings` (secret, orphaned test) | 10 | two in each of the five |
| R6 | NOT_BUILT needing `A8-documents` | 3 | legacy 2, rust 1 |
| R7 | stage `VERDICT` NOT_BUILT | 6 | all six |
| R8 | stage `findings` NOT_BUILT | 6 | all six |
| R9 | control FLAGGED | 6 | rust, legacy, secret (2 each) |
| R10 | large-file MISSED | 2 | legacy |
| R11 | stage A10 ABSENT | 1 | rust |

13 + 5 + 10 + 3 + 6 + 6 + 6 + 2 + 5 + 6 + 1 = 63. (R3 to R5 sum to 28 and R6 to 3: the 31 "planted/hidden NOT_BUILT" lines of the report.)

## Class table (one row per reason group; each classed)

Classes: **1** product defect; **2** test-code defect; **3** not built; **4** the adoption run's own gap; **5** machine or tool; **6** memory miss.

| Row | Reasons | Class | Finding and evidence | Owner / pointer |
|---|---|---|---|---|
| R1 | 5 | **6** (with 2 and 4 inside it) | See the memory section. 25 of the 29 wrong questions in the five repositories are one thing: a stale or superseded source was in the bundle and the reader cited it beside the right one. 2 are stale gold or source choices. | below |
| R2a | 6 | **2** | The runner starts `gov queue` with `HOME=<run>/.home` (`w2_81_run.py:92-102`, `_env`; the call at `:392-399`). Pytest lives in the owner's user site, so the acceptance folder's run is `outcome: error, error_kind: crash`, 0 tests run. A customer runs `gov queue` with a normal `HOME`. Reproduced by the lead read-only (`--dry-run`) with both homes. | test designer, W2-81 (DAEO-l78m) |
| R2b | 6 | **4** (set-up) | With the real `HOME` the landing is still red in all six, on the ticket's own line F1: `outputs/*/dry-realhome/summary.txt` (python-app 16 passed 1 failed; legacy 15/1; secret 3/1; ts 2/1; clean 2/1; rust 2/4) and `accept.out` (`failure-1` failed, `success-1`, `success-2` passed). F1 is not a product KPI: the lead's own set-up wrote it (`tools/setup_0.1.4.py:125`: "every commit touching governance/adoption/ carries Role: orchestrator"). The product's stage commits are subject-only by design (`src/gov/adopt/project.py:128-146`, `commit()`; `governance/project/bootstrap.md` §"The adoption's commits": "carry no trailers"). Contract v5 does not require trailers on them (CAP-58.h: a commit with no `Role`/`Task` trailer is judged against the caller; CAP-63.a's trailer check did not fail them in the dry run). The same line sank release 0.1.1. | the run's set-up (lead); an owner option below |
| R3 | 13 | **3** | `A2-content-class`: A2 classes by path-map namespace only (`src/gov/adopt/stages.py:181-188`, `a2()`). See the not-built table. | CAP-44.b / CAP-01.c, both W1; no W2 line |
| R4 | 5 | **3** | stale-spec accepts either `A2-content-class` or `findings`; neither is built. AS (CAP-44.m, W2, built, ran in all six) is not a staleness check: it gives built/partly/not built from named code paths (`src/gov/adopt/spec_audit.py:1-60`) and the judge does not read it. | as R3 and R5 |
| R5 | 10 | **3** | `findings` (secret, orphaned test): CAP-44.g, **W3**. | CAP-44.g (W3) |
| R6 | 3 | **3** (and **2**: the demand exceeds the Contract's words) | `A8-documents`: A8 retires rule files, memory stores and chat databases only (`stages.py:30`, `KINDS`). CAP-44.e (W1) says "A8 legacy memory extraction/retirement": built exactly so. The "legacy document" kind is W2-81's own KPI line (DAEO-l78m, correct-handling line), not a Contract line. | owner decision |
| R7 | 6 | **3** | `VERDICT`: CAP-44.h, **W2**. The record type exists (`adoption-verdict`, W2-02, DAEO-zflj); no stage or command writes or checks it (`command.STAGES` = A0, A1, A2, AS, A3 to A10, MA). Adopters found it themselves (rust F-014). | no live ticket: see below |
| R8 | 6 | **3** | stage `findings`: CAP-44.g, **W3**. | CAP-44.g (W3) |
| R9 | 6 | **4** (and **2**: the judge reads the stale record) | Cause is one: A2 ran before the path map was written. Evidence below. | brief; judge optional |
| R10 | 2 | **4** (and **2**) | Same cause: `data/rostering-2009.bin` and `media/payroll-briefing-2009.wav` are `namespace: null` in A2's record; the final path map classes both `product-data`, not embedded, and neither is in the vectors (verified by `classify` over the final path map; `lexical_file.indexed = 0` for both). Handled in fact, unproven in the record the judge reads (`w2_81_judge.py:687-716`). | brief |
| R11 | 1 | **1** (and **4**) | See the product-defect table, P3. | W2-88, W2-52, W1-41 |

Reasons by primary class: **3 = 43** (R3 13, R4 5, R5 10, R6 3, R7 6, R8 6); **6 = 5** (R1); **2 = 6** (R2, sharing with class 4: R2b would keep all six red alone); **4 = 8** (R9 6, R10 2); **1 = 1** (R11). Total 63. Two verify lines of S-RERUN are not reasons the runner counts, and are class 1 and 5: `gov doctor` exit 3 in all six and the governance share unmeasured (rows D and T below).

### Class 4 evidence: A2 before the path map (R9, R10)

- The brief's order is A1, A2 (each committed), then MA, then "A3, the path map ... committed before A3 runs" (`adopter-brief-0.1.4.md` §5 steps 1-3). The kit's default path map holds only the kit's own trees, so A2 records `namespace: null` for every other tracked path.
- Per repository, the A2 record's null count: python-app 0 of 409, typescript-monorepo 0 of 410, python-app-clean 0 of 403; **rust-workspace 128 of 410, legacy-docs 128 of 410, secret-history 125 of 407**. The first three adopters re-ran A2 after writing the path map (git order: A2, path map, A2 again); the last three did not (A2, path map, A3).
- The six flagged controls are exactly the controls in those three repositories ("is mapped to no namespace the path map holds", `report.json` `controls[].evidence`), and the two MISSED large files are in one of them. With the path map in force the files classify correctly: legacy-docs' `historic/export_ledger.py` is `code`, `docs/specs/draft-rostering-record-format.md` is `specs`, both embedded.
- Also left behind in those repositories: 125 to 128 PROPOSED `DP-ADOPT-*` decision packages asking "what is this file" for files the later path map holds (rust F-008).
- What it changed: 8 of the 63 reasons. Nothing else.

## Class 1: product defects (Gov OS code does the wrong thing in ordinary adoption)

| # | Defect | Evidence | Owning ticket and KPI broken | Fix or new line? |
|---|---|---|---|---|
| P1 | `gov doctor` is unhealthy (exit 3, `DOCTOR_UNHEALTHY`) on a one-patch CLI/extension difference, in a repository with no registry entry for Claude Code (`pinned_version: null`) | `outputs/*/doctor.out`; record.md "gov doctor"; `src/gov/doctor/command.py:793-799` (any difference is `drift`) and `:926-929` (`healthy` = no part is `fail` or `drift`); machine: CLI 2.1.329, extension 2.1.328 (`~/.vscode-server/extensions/anthropic.claude-code-2.1.322..328-linux-x64`) | **W2-22** (DAEO-xm6l): "CLI and extension drift is reported by the owner's policy: a warning below a set gap, a failure above it [W2-M139, W2-M264]" (the list row W2-M264: "gov doctor with only version drift exits 0 and reports the drift"; W2-M139: "a newer extension above the minimum passes"). Also **W1-48** (DAEO-0qs5): "a difference between them ... is drift that gov doctor reports, not a failure, except the CLI at the recorded version with another sha256" (DEC-210, DEC-214). No gap policy exists in the code; `tests/acceptance/W2-22/` does not exist, so no test caught it. | **Fix** under W2-22, failing test first. Conflict to settle: Contract v5 CAP-25's acceptance says "exits non-zero on drift" and CAP-61.e says the CLI is "aligned with the extension's bundled version". The owner picks the policy (D6). |
| P2 | A verdict the A5 or A7 gate accepts is rejected as a record by `gov rebuild` ("required key missing or not a string: status"); the two files are then in neither list | rust F-013, python-app-clean F-013 (`outputs/*/FINDINGS.md`); the same files are rust's F-010 | **W2-52** (DAEO-siiz, A7/A10 gates), **W1-41** (DAEO-cdoi, A5): the gate's accepted verdict must be a record the store reads (core-schema is a hard-block check, W2-02, DAEO-zflj) | **Fix**, failing test first: a verdict front matter as the adopt skill and brief describe passes the gate and `gov rebuild` lists none invalid |
| P3 | rust-workspace's A9 stops `FABRIC_INCOMPLETE` ("vectors: 2 file(s) judged and in neither list") and names no file; so A10 never runs | rust F-008, F-010. Cause: the adopter's path map put `governance/project/audits/**` in two namespaces (project embedded, adoption not embedded), A3 and A5 accepted it, doctor's `path_map` passed; the two verdicts are also invalid records (P2). `src/gov/adopt/project.py:205-217`: `classify` takes the first match | **W2-88** (DAEO-2bdu) S1: "Every tracked file is either indexed or named with its reason": a refusal naming no file breaks it. The overlap check is a new line on a closed feature (W1-41 and W1-27 state no such check): **a new small ticket**, not a fix | Fix (message names the files) under W2-88; new ticket: A3 and `gov doctor` refuse or report a path in two namespaces |
| P4 | `gov telemetry` cannot find `ccusage` | record.md; `src/gov/telemetry/counter.py:180-182`, `shutil.which("ccusage")` | **W2-05** (DAEO-0z8c). Not a defect of the install: see row T | none for the ticket; a PATH condition (row T) |

Other defects the adopters met, not reasons the judge counts (counts from `outputs/*/FINDINGS.md`: python-app 16, rust 14, ts 14, legacy 10, secret 16, clean 12). Owners not traced here; residual: `gov brief` for the auditor and the test designer leaves `{W2}`, `{PROFILE}`, `{BRANCH}`, `{REGISTER}`, `{EXIT_FILE}`, `{SUBJECT}`, `{COMMIT_PATHS}` and an empty "Objective:", and refuses the test designer's on `UNSET_WHERE` (all six; EMERGENCY-2 5.4 says briefs are built by construction); MA and A9 treat the kit's own `governance/framework.lock` (a 70,728-character line) as over-limit with a secret (rule `generic-api-key`) and leave it unindexed, with proposals RP-03 and RP-04 naming a kit file (all six; `lexical_file.indexed = 0` for it in every repository, and for nothing else of the repository's own text but the two intended large files and one data table); AS reports 0 specs and 0 modules for five repositories because its rule finds only `type: spec` Markdown, a folder named `specs`, and `.py` under `src/` (by design in `spec_audit.py`, narrow for Rust, TypeScript, Go and RFC/ADR layouts); a second A3 run is allowed and leaves two commits; an empty A3 proposal is accepted and committed.

## Class 2: test-code defects (W2-81's runner, judge, scorer; the test designer's)

| # | File and line | Defect | Effect on 0.1.4's run |
|---|---|---|---|
| T1 | `tests/acceptance/W2-81/w2_81_run.py:92-102` (`_env`), `:392-399` | `gov queue` is started with the scrubbed `HOME` that suits retrieval isolation, so pytest is not found | R2: all six `outcome: crash`; not the cause of the red alone (R2b) |
| T2 | `w2_81_judge.py:72-73` (`STAGES`), README capability table | stage AS is not in the judge's stage list; AS (CAP-44.m, W2) ran in all six and is neither required nor credited; a missing AS record would not be named | none on 0.1.4; a gap for the next |
| T3 | `w2_81_judge.py:857-876` (`overall`) | no exceptions input: any non-FOUND planted problem, any stage not PRESENT, any figure under bar is a reason. S-RERUN allows "READY but for exceptions the owner names one by one"; the code cannot compute it, and it counts W3 capabilities (CAP-44.g, 16 reasons) the same as W2 | 43 of the 63 reasons can never clear as things are; the owner's naming has nowhere to go |
| T4 | `w2_81_judge.py:687-716` (`_large_file`), `:719-745` (`_control`) | classification is read only from A2's record (`artefacts[].namespace`), which is stale when the path map came after A2; for a moved file the judge already reads the path map's patterns (`namespace_by_patterns`, `:674-684`) | R9, R10 (8 reasons), with the brief (class 4); judged as the README states it, so the README and judge agree, and the brief is the first fix |
| T5 | `w2_81_judge.py:76-98` (`CAPABILITIES`, "as read in src/gov/adopt/ on 2026-10-31"), README line 306 | the capability table is dated; README row VERDICT still reads "the lite verdict (W2-52, not merged)" (W2-52 closed and built A7 and A10 only) | none; a stale statement |
| T6 | `w2_81_run.py:381-382` (`stacks`/`answers`), `w2_81_score.py:77-92` | the ranked bundle is not recorded: the row keeps only `first_gold_rank` and `forbidden_in_top_5`. "Forbidden ranked above the gold" cannot be told from the run | the memory causes below are by rank of the gold, not of the forbidden source |
| T7 | `w2_81_score.py:51-55` (`cited`), `:66-69` | the forbidden-citation rule is W2-81's own and stricter than the product's measure: `gov.memaudit.prompts.outcome` (`:60-72`) has no forbidden-citation concept; right is "grade correct and the cited place holds a gold line". 24 of the 30 wrong questions were graded `correct` by the grader | R1: not a defect against the README (M1 mutant) or DEC-1221's wording, but it decides the memory figure; D5 |
| T8 | hidden set (the held-out writer's, W2-93, DAEO-6y0x): `typescript-monorepo-h09` and `python-app-clean-h07` | both golds name a state of a tracked file that A0 itself edits (the grader's reasons: the answer added a line the gold lacks; `.gov-runtime/` is appended to the repository's `.gitignore` by `gov adopt --lite A0`, `git log -- .gitignore` in both repositories shows `gov adopt --lite A0: safety baseline`). A correct reader fails | 1 reason in ts (R1), clean's one miss (clean is at the bar, 95.0 exactly) |
| T9 | hidden set: `typescript-monorepo-h03` (est.) | the reader answered correctly, the row says "citation misses the gold sources"; its citations are adoption records only; the repository's one tracked data table is `product` class, not embedded, `indexed = 0` | R1; see memory section |

README line 384 states the A2-record reading of controls, so T4 is judged "as designed"; I class it a defect only in that it turns a stale intermediate record into a flag against the repository.

## Class 3: not built

The judge's `built` flags are hard-coded false for these (`w2_81_judge.py:76-98`), true to the code of 0.1.4 (`src/gov/adopt/`: no content class in `a2()`, no findings records, `KINDS` of three, no VERDICT stage).

| Capability | Contract v5 item and wave | Judge counts it against READY? | Reasons | Ticket that should deliver it |
|---|---|---|---|---|
| `VERDICT` (lite adoption verdict stage) | **CAP-44.h, W2**: "Adoption verdict, lite ... at the release, EXAMIN's copy gets its verdict"; its provider list is empty (W2-49 CIT-E: "no provider") | yes: every stage not PRESENT is a reason (`overall`, `:869`) | 6 | **None live.** CAP-44.h is in `closes:` of W2-28 (DAEO-csj8) and W2-30 (DAEO-60rw), both `status: moved` to EXAMIN's Wave 0 (DEC-1201). W2-02 built the record type only; W2-52's third KPI line ("the verdict reads both records as named conditions") was not delivered. Needs a new feature ticket (next free W2 id; closes CAP-44.h) |
| `findings` (finding states, human gates; the secret and the orphaned test) | **CAP-44.g, W3** ("EMERGENCY-2 8.4 (DEC-1211)") | yes (planted problems of kinds secret and orphaned-test; stage `findings`) | 10 + 6 = 16 | none: W3, friction only. Also: EMERGENCY-2 2.11 / DEC-1182 / CAP-03.a say no secret scan on a private repository until it goes public or is shared, so a history scan as a READY condition of an adoption conflicts with the strategy in force |
| `A2-content-class` (current, historical, superseded, live, dead; newer source) | No Contract v5 line names reading content at A2. The judge cites **CAP-44.b (W1)**, "A2 classification", built as namespace classification; the nearest authority clause is **CAP-01.c (W1)**, "historical material cannot replace current input" (W1-26). CAP-44.m (W2, AS) is not a staleness check | yes | 13 + 5 = 18 | **none, and no W2 line demands one**: a new feature ticket if the owner wants it, else a named exception |
| `A8-documents` (extract or retire a legacy document) | **CAP-44.e (W1)** "A8 legacy memory extraction/retirement": delivered by W1-41 for rule files, memory stores and chat databases. Documents are W2-81's own KPI line, not a Contract line | yes | 3 | none; named exception or drop the kind |
| `A7`, `A10` | CAP-44.f, W2, **built** (W2-52): present in all six; rust's A10 is ABSENT only because A9 stopped (P3) | n/a | 1 (rust) | n/a |

Of the 43 NOT_BUILT reasons: 6 are a W2 item the lean release must have (VERDICT), 16 are W3 (findings), 3 are not in the Contract (A8 documents), 18 are in no W2 line (content class).

## Class 4: the adoption run's own gaps

The adopter brief (`adopter-brief-0.1.4.md`) left out stage AS and used an A3 form 0.1.4 refuses; three adopters ended with `artefacts: []`.

| Gap | Source | What it changed in the planted problems |
|---|---|---|
| AS not in the order (§5 step 1-3: A1, A2, MA, A3) | carried from the 0.1.1 brief; A3 refuses `ADOPT_STAGE_MISSING "run AS first"` (rust F-003); the adopters ran AS as the refusal and the adopt skill say | **Nothing judged.** AS is not read by the judge (T2) and handles no planted kind. Cost: one finding and a minute per repository |
| A3 `artefacts` form (§5 step 3: a batch for every entry, `kind` for a RETIRE) | 0.1.4 takes KEEP with no batch or target, and RETIRE without target for the kinds rule-file, memory-store, chat-database only (rust F-005) | **Nothing judged, one thing for memory.** All six A3 records are all-KEEP (409, 410, 410, 410, 407, 403 entries; 0 A6 batches; 0 A8 retirements), the safe handling for every kind (never moved, never deleted), so no planted problem went MISHANDLED. A correct form could not have retired a superseded plain document anyway: RETIRE is limited to three kinds, and A3 refuses to delete a referenced or superseded file (W2-190). The product has **no route** for taking a superseded document out of default memory except the path map's `lexical_policy` |
| `artefacts: []` in three adopters' proposals | their probe of the form (rust F-005 (a)); the committed A3 records still list every path as KEEP | none |
| A2 before the path map (class 4 evidence above) | brief §5 order | 8 reasons (R9, R10) |
| The path map's memory rule: "product is only for ... binaries, media, generated data" | brief §5 step 3 | ts-h03's source (an 8 KB text table, "generated-looking filler") was classed `product`, not embedded, `indexed = 0`; see memory |
| `facts.yaml` slots (`where`, `tests_tree`, `accept`) not filled before the test designer's brief | brief §3 step 3 fills only what the auditor's brief needs | 3 to 4 findings per repository; no judged effect |
| F1 in the adoption ticket | `tools/setup_0.1.4.py:125` | R2b |
| Path map overlap (`audits/**` in two namespaces) | the rust adopter's own map | R11 (with P2, P3) |

## Class 5: machine or tool condition

| Item | Is it reasonable? | Evidence and recommendation |
|---|---|---|
| `gov doctor` exit 3 on `claude_code` drift: CLI 2.1.329 vs extension 2.1.328 | **No, for an adopted repository.** The code fails on any difference of the two version strings (`command.py:793-799`, `:926-929`), with no gap and no registry pin to compare (`pinned_version: null`). W1-48 and W2-22's KPIs say drift is reported, not a failure, or fails only above a set gap. The registry itself records that the extension "need not equal the pin (DEC-210)". The Contract (CAP-25 "exits non-zero on drift"; CAP-61.e "aligned") is the one source that reads the other way. The extension auto-updates, so a patch difference is the normal state of any VS Code machine | class 1 row P1; the fix is a policy the owner sets (D6); S-RERUN needs `gov doctor` at exit 0 in every repository |
| `ccusage` absent | **Not an install.** It is installed and registered: `governance/project/tool-registry.yaml` entry `ccusage`, version **20.0.26**, 5.1 MB with its platform package, sha256 `b8d59c19...eb1f2`, installed 2026-10-03 under Node v22.23.3 at `~/.nvm/versions/node/v22.23.3/bin/ccusage`, approved by DEC-192, install and uninstall commands recorded. It answers `ccusage 20.0.26` when that directory is first on `PATH` (the registry note: the script runs under whichever node is first). It was absent only from the `PATH` of the runs; `gov telemetry` uses `shutil.which` (`counter.py:180`) | no CTO approval is needed, no version change: put `~/.nvm/versions/node/v22.23.3/bin` first on `PATH` for the operator's `gov telemetry` and the read step (or have the product resolve the registry's prefix). Why it matters: S-RERUN needs "the governance share is measured" |

## Class 6: memory misses

Five repositories are under 95 %. Of 121 questions, 30 were judged wrong (29 in the five; python-app-clean's one is at the bar, 19 of 20). The ranked bundle is not recorded (T6), so causes come from the verdict row (reader verdict, grade, citations, attempts) and the rank diagnostics (`first_gold_rank`, `forbidden_in_top_5`, `forbidden_cited`). Bundles are 53 to 62 items; the reader read them whole.

### Counts per cause per repository

| Cause | python-app (4 wrong of 21) | rust-workspace (5 of 20) | typescript-monorepo (8 of 20) | legacy-docs (8 of 20) | secret-history (4 of 20) | python-app-clean (1 of 20, at bar) | Total |
|---|---|---|---|---|---|---|---|
| **A.** A stale or superseded source (the planted forbidden one) was in the bundle and the reader cited it beside the right source; the grader graded the answer `correct`; the scorer's forbidden rule made it wrong | 4 | 5 | 5 | 6 | 4 | 0 | **24** |
| **A'.** Same, and the answer itself was wrong | 0 | 0 | 1 (v03) | 0 | 0 | 0 | **1** |
| **B.** The gold source was not in the stack; the gold is stale against the adoption's own edit (test-code T8) | 0 | 0 | 1 (h09) | 0 | 0 | 1 (h07) | **2** |
| **C.** The gold source was not in the stack because adoption left it out of the index (the adopter's `product` class; est. T9) | 0 | 0 | 1 (h03) | 0 | 0 | 0 | **1** |
| **D.** The reader's answer was wrong though the gold was in the stack | 0 | 0 | 0 | 1 (v05) | 0 | 0 | **1** |
| **E.** The reader said "not found" though the gold was at rank 1 | 0 | 0 | 0 | 1 (v10) | 0 | 0 | **1** |
| **F.** The source not indexed because a stage was not run or `artefacts` was empty | 0 | 0 | 0 | 0 | 0 | 0 | **0** |
| Total wrong | 4 | 5 | 8 | 8 | 4 | 1 | 30 |

(The list of wrong questions: python-app v01 to v04; rust v01, v03, h03, h05, h06; typescript v01, v02, v03, h02, h03, h04, h06, h09; legacy v01, v02, v05, v10, h02, h03, h04, h05; secret v04, h03, h07, h09; clean h07.)

### What the numbers say

- **Cause A is the miss.** Wherever a forbidden source stood in the top five (26 questions), the reader cited it in 25 (96 %); wherever none did (95 questions), 90 were right (94.7 %). So away from the planted stale sources the figure is already at the bar; with them it is not.
- **22 of the 25 forbidden-citing answers themselves call the cited source superseded, older, stale, replaced or a draft** (keyword count over the answer text, est.): the reader used it as a labelled source to dismiss, and cited it. The gold was retrieved at rank 1 to 5 in all 25.
- **Why the stale sources are in the bundle at all.** The adopters did class them correctly: python-app's path map has a `superseded` namespace holding `docs/design/lending.md` and `plans/rollout-plan.md`, "found by the lexical route only", `embedding_policy: not embedded`. The product ignores the name. A namespace's `lexical_policy: not indexed` would keep a file out of the lexical route (`src/gov/retrieval/lexical.py:8`), and the path map's `retrieval_authority` block orders by authority (W2-87, DAEO-s9qc), but "with the block absent the bundle is today's, item for item" by W2-87's own KPI; none of the five adopted path maps has either key (checked, grep count 0 each), neither is in the adopt skill or the brief, and the record graph demotes only records with a `status: superseded` or a SUPERSEDES edge (`retrieve.py:117-130`), which a plain Markdown spec does not carry. This is the memory-side face of the unbuilt `A2-content-class`.
- **Adoption's own records enter the bundle.** 54 of 121 answers cite `governance/adoption/**`, `governance/project/audits/adoption-*` or `path-map.yaml` (legacy-docs 15 of 20, typescript-monorepo 14 of 20, python-app 9, secret-history 7, rust 6, clean 6). In ts-v03 the reader built its implementation answer from the A5 audit's quote of a file it never saw, and named the wrong package. These are not planted problems.
- **The product's own measure would have counted A as right.** `gov.memaudit.prompts.outcome` has no forbidden concept (T7). Under it, with the gold also cited, est. python-app 21/21, rust 20/20, secret 20/20, legacy 18/20, typescript 17/20, clean 19/20. That is the figure EXAMIN's 95 % is measured by, so the proving run and EXAMIN's gate are not the same measure; this is for the owner (D5).

### Do the misses point at memory or at the adoption run?

**At the adoption run, and at the lack of a product route for stale material, not at retrieval or ranking quality.** In 27 of the 29 misses in the five repositories the gold was in the stack (rank 1 to 5 in the 25 of cause A), so retrieval found it. 25 of 29 (86 %) are one thing: the stale or superseded document is retrievable in an adopted repository and nothing in the adoption (the path map, A2, the skill, the brief) takes it out; the product has the knobs (`lexical_policy`, `retrieval_authority`) and no step sets them. 1 (cause C) is the adopter's classification; 2 (cause B) are the test's golds; 2 (causes D and E, plus A' partly) are the reader failing on a large bundle, which is memory-side noise that adoption records add to. Zero are "a stage not run" or "artefacts empty": `lexical_file` holds every tracked text file indexed in all six repositories except `governance/framework.lock` (kit file), the two intended large files (legacy), and the ts data table. Ranking proper (a forbidden source above the gold) cannot be shown from this run; it is the question T6 would answer.

## Verdict

- The 63 reasons are not 63 problems. Roughly: **43 are capabilities not built** (6 W2, 16 W3, 3 not in the Contract, 18 in no W2 line); **8 are one brief-order gap**; **6 are one runner `HOME` and one set-up line**; **5 are the memory figure, 25 of whose 29 misses are one stale-source cause**; **1 is a product chain** (verdict form, overlapping path map, a nameless A9 refusal).
- On 0.1.4 the proving run cannot reach READY by any brief or test fix alone: VERDICT (W2) is missing, 16 reasons are W3, and the judge has no way to take an owner's named exceptions (T3).
- Two real product fixes (doctor drift policy, the verdict form chain) and one product gap that costs the memory figure (no route for stale and legacy documents in an adopted repository).

## The plan

### A. Product fixes (owner ticket each; failing test first)

| # | Fix | Owner ticket | Failing test first |
|---|---|---|---|
| A1 | `gov doctor`: a patch-level CLI/extension difference is `drift`, reported, exit 0; below the minimum, a different major or minor (or the owner's gap) or a CLI sha mismatch at the recorded version stays exit 3 | W2-22 (DAEO-xm6l), source W1-48 (DAEO-0qs5): a **fix**; CIT-P for CAP-25's "exits non-zero on drift" if the owner chooses D6 (a) or (b) | doctor in a scratch repository with a stand-in CLI 2.1.329 and extension 2.1.328, no registry entry: exit 0 and the drift named; CLI 2.1.280 or a sha mismatch: exit 3 |
| A2 | The verdict an A5 or A7 gate accepts is a record the store reads; `gov rebuild` lists none invalid | W2-52 (DAEO-siiz), W1-41 (DAEO-cdoi): a **fix** | a verdict written as the adopt skill says passes the gate and `gov rebuild` reports 0 invalid |
| A3 | A9's `FABRIC_INCOMPLETE` names each file in neither list | W2-88 (DAEO-2bdu) S1: a **fix** | a planted path in two namespaces: the refusal names it |
| A4 | A3 and `gov doctor` refuse or report a tracked path in two namespaces | **new small ticket** (new line on closed W1-41 and W1-27) | a path map with `governance/project/audits/**` in two namespaces: A3 refuses, doctor reports |
| A5 | The lite verdict stage (`gov adopt --lite --stage VERDICT` or a record check), closing CAP-44.h | **new feature ticket** (spec and KPIs; no live ticket carries it) | per the spec: refuses ADOPTED_HEALTHY with a condition not met; names itself lite |
| A6 | A route for superseded, historical and legacy documents out of default memory in an adopted repository: the adopt skill and the A3 form give such namespaces `lexical_policy: not indexed` (and not embedded) and say so; optionally the A2 record carries the class the adopter gave (namespace names) | **new feature ticket**, built on W2-13 S6 (`lexical_policy`), W2-87 and W2-88; the imports spec (DEC-1221 (2), `proposals/IMPORTS-ADOPTION-SPEC.md`) is the natural neighbour. Kernel text is the CTO's (EMERGENCY-2 3.5) | a planted stale spec in a namespace so marked is absent from `gov retrieve`'s bundle; a current one still present |
| A7 | `gov telemetry` finds `ccusage` by the registry's prefix, not `PATH` alone (optional; the operator's `PATH` suffices) | W2-05 (DAEO-0z8c) | low priority |

### B. Test-code fixes (the test designer, W2-81)

1. **T1** the `gov queue` call runs with the operator's `HOME` (or passes `PYTHONUSERBASE`/user site through): a runner case showing the landing's pytest resolves. Failing test first in `test_w2_81_runner.py`.
2. **T3** an owner-exceptions input to `overall`: a file of reason ids with the decision id; READY-with-exceptions only when every non-FOUND reason is named; one unnamed stays NOT_READY; W3-labelled capabilities named in `CAPABILITIES` so the exception list can be generated by wave.
3. **T2** add AS to the stage list (required, MISSED and named if absent); **T5** refresh `CAPABILITIES` and the README's VERDICT row.
4. **T6** record per question the ranked bundle's `(path, start, end)` list and the forbidden source's rank (ids and numbers only, no text) so cause A can be split into "above the gold" and "below".
5. **T8** the held-out writer corrects the two `.gitignore` golds (or accepts the line A0 adds); **T9** the writer confirms whether the ts data-table question's gold is a file the planted large-file rule keeps out of the index; if so, one of the two must give.
6. **T4** (optional) when A2's record is older than the path map, read the path map's patterns, as the judge already does for a moved file.
7. **T7** only if the owner picks D5 (b).

### C. Brief fixes for a re-run

1. Order: A1, **the path map committed (every tracked path in exactly one namespace; `governance/project/audits/adoption-*/**` and `governance/adoption/**` not both in `project` and `adoption`)**, then A2 (the A2 record then classes every path), then AS, then MA, then A3.
2. A3's form as 0.1.4 takes it: KEEP with no batch or target; RETIRE only for the three kinds; AS in the list.
3. Fill `facts.yaml` `where`, `tests_tree` and `accept` in step 3 (the product's test designer brief refuses without `where`).
4. The verdict front matter keys (including `status`) until fix A2 of this plan lands.
5. The memory rule: superseded and legacy namespaces `lexical_policy: not indexed`, not embedded (only after A6 gives the skill the sentence, or as the explicit treatment under test); a text file is `product` only if it is data that must stay out of memory, and say what "generated" means.
6. F1 in `setup_0.1.4.py:125` rewritten (see D7) and `ccusage`'s directory first on `PATH` for the operator's steps; the run's `gov queue` and `gov doctor` with the operator's `HOME`.
7. Everything else in the 0.1.4 brief held: no guard, the final `gov rebuild` (the adopters stopped clean, store commit = HEAD, all six), the LITE ticket cycle, `gov queue` after the adopters stop.

### D. Decisions only the owner can make

| # | Decision | Options | Recommendation |
|---|---|---|---|
| D1 | VERDICT (CAP-44.h, W2, 6 reasons) | (a) build before the release (A5); (b) name as an exception | **(a).** It is a W2 line the Contract gives the release, and CAP-44.h says EXAMIN's copy gets its verdict at the release |
| D2 | `findings` (CAP-44.g, W3; 16 reasons: 10 planted or hidden, 6 stage lines) | (a) name each as an exception (S-RERUN); (b) build | **(a).** W3, friction only; EMERGENCY-2 2.11 says no secret scan on a private repository |
| D3 | `A2-content-class` (18 reasons, in no W2 line) | (a) exception, and build only A6's route; (b) build a content-reading A2; (c) drop the planted kinds that need it | **(a).** The route (A6) is what fixes the memory figure; reading content to classify is the Wave 3 shape, driven by friction |
| D4 | `A8-documents` (3 reasons; not in the Contract) | (a) exception; (b) build; (c) drop the kind from the judge | **(a).** Contract v5 has no line for it; CAP-44.e's "legacy memory" is built |
| D5 | The forbidden-citation rule (24 of 30 misses) | (a) keep it strict (W2-81's own, DEC-1221 (1) "both answer and citation right"); (b) align with `gov memaudit`'s measure | **(a), medium confidence.** It is the only thing that tests that adoption keeps stale material out of memory, which is the planted point; but say plainly that EXAMIN's 95 % is measured without it |
| D6 | The `claude_code` drift policy (A1) | (a) a difference of patch version only (same major and minor): exit 0, reported; a larger difference: exit 3; (b) drift never fails; (c) keep as is | **(a).** It follows W2-22's "set gap" and W1-48; needs a CIT-P on CAP-25 and CAP-61.e |
| D7 | F1 on the adoption ticket | (a) the set-up's F1 rewritten to what the product guarantees (a stage record changes only by `gov adopt`'s own commit, subject `gov adopt --lite <stage>`); (b) the product writes `Task:` and `Role:` on stage commits (a new feature line on W1-41) | **(a).** No Contract line asks for (b); CAP-58.h accepts trailer-less commits; the hand-edit it guards is already refused by `gov adopt` (`stands_on`, record hashes) |
| D8 | Which release the re-run measures | on the one that carries A1, A2, A5 and A6 (0.1.5 or its successor; S-RERUN says "or its successor") | **After A1, A2, A5, A6 land and a patch release carries them**, so one re-run measures the fixed product, not 0.1.4 again |
| D9 | Exceptions (D1 to D4) | name them one by one in one owner decision, each by reason id | **Yes**, after D1 is answered, so the exception list is final before the re-run |

## Expected figures of a re-run once fixed (est.; method: the 0.1.4 verdict rows with the cause removed; single run, LLM variance about one question = 5 points on 20)

| Repository | 0.1.4 | Brief + test-code + set-up fixes only (C, B1, B3, D7) | Plus A6 (stale and legacy documents routed out) | Plus the two stale golds fixed (T8) |
|---|---|---|---|---|
| python-app | 80.95 | about 81 (unchanged) | about 100 (21/21) | about 100 |
| rust-workspace | 75 | about 75 | about 100 | about 100 |
| secret-history | 80 | about 80 | about 100 | about 100 |
| legacy-docs | 60 | about 60 | about 90 (18/20; v05 and v10 remain) | about 90 |
| typescript-monorepo | 60 | about 60 | about 85 (17/20; v03, h03, h09 remain) | about 90 (h09 fixed) |
| python-app-clean | 95 | 95 | 95 | about 100 (h07 fixed) |

- With the brief, test-code and set-up fixes only: queue exit 0 in all six (R2 gone, est.), controls 0 flagged, both large files FOUND (R9, R10: 8 reasons gone), rust's A10 present once its path map has no overlap (R11 gone). Remaining: R1 (5) plus the 43 NOT_BUILT unless named. With D1 built and D2 to D4 named as exceptions: only R1 remains.
- The honest reading: **even with A6, legacy-docs and typescript-monorepo are likely still under 95** on cause D, E and C residuals (about 2 to 3 questions each) and the adoption records in the bundle; the other four reach the bar. Reaching all six needs a second look at the bundle's noise (adoption records, T6 first) and the 8 to 10 questions of these two repositories; I would not promise READY on the first re-run.
- `gov doctor` exits 0 only after A1; the governance share is measured as soon as `ccusage` is on `PATH`.

## Draft KPI lines

Each for the ticket that takes it, with its verify.

1. **W2-22 (fix).** "`gov doctor` exits 0 and names the drift when the Claude Code CLI and the extension differ by a patch version and neither is below 2.1.285; it exits 3 when either is below the minimum, when the difference exceeds the owner's gap, or when the CLI at the recorded version has another sha256." Verify: a scratch repository with stand-in `claude` and `extensions.json`: 2.1.329 against 2.1.328 gives exit 0 with `drift` named; 2.1.280 gives exit 3; a planted sha mismatch gives exit 3.
2. **W2-52 / W1-41 (fix).** "A verdict that the A5 or A7 gate accepts is a record the store reads." Verify: a verdict front matter exactly as the adopt skill gives it passes `gov adopt --lite --stage A5` and `gov rebuild` reports no invalid record.
3. **W2-88 (fix).** "`FABRIC_INCOMPLETE` names each file that is in neither list." Verify: a planted tracked path matching two namespaces gives a refusal that names it.
4. **New (path map).** "A3 refuses a path map in which a tracked path matches two namespaces, naming the path and both." Verify: the rust adopter's map (`audits/**` in two namespaces) is refused at A3.
5. **New feature (verdict).** "`gov adopt --lite --stage VERDICT` gives ADOPTED_HEALTHY, ADOPTED_WITH_ACCEPTED_EXCEPTIONS or NOT_ADOPTED_HEALTHY from the lite conditions of CAP-44.h, names itself lite and the conditions it does not check, and gives ADOPTED_WITH_ACCEPTED_EXCEPTIONS only for an exception named in an owner decision." Verify: a stand-in adoption with A7 unmet gives NOT_ADOPTED_HEALTHY; the same with an owner decision naming A7 gives the accepted-exceptions verdict.
6. **New feature (stale route).** "In an adopted repository a document in a namespace marked superseded, historical or legacy is absent from the default bundle, and a current document on the same topic is present." Verify: the python-app stand-in's `docs/design/lending.md` is absent from `gov retrieve`'s bundle for the lending question and `lending-v2.md` is present.
7. **W2-81 (test code).** "`gov queue` is run with the operator's `HOME`; the report holds the ranked bundle's path ranges and the forbidden source's rank per question; `overall` reads an owner's exceptions file and is READY only when every non-FOUND reason is named in it." Verify: three runner and judge cases (a stand-in queue run resolves pytest; the report lists ranks and no text; one unnamed reason stays NOT_READY).

## Sources

- Records: `docs/plan/wave-2/w2-81-proving-run/{report.md,report.json,record.md,adopter-brief-0.1.4.md,tools/setup_0.1.4.py}` on `e2/w2-81-proving-run`; `~/gov-os-runs/W2-81/run-0.1.4/` (`report.json`, `run.log`, `outputs/*/FINDINGS.md`, `outputs/*/evidence/*`, `outputs/*/dry-realhome/*`, `e2e/*/*.json`, `repos/*`).
- Tickets: `.tickets/DAEO-l78m.md` (W2-81), `DAEO-xm6l.md` (W2-22), `DAEO-0qs5.md` (W1-48), `DAEO-xw3k.md` (W1-27), `DAEO-cdoi.md` (W1-41), `DAEO-siiz.md` (W2-52), `DAEO-zflj.md` (W2-02), `DAEO-2bdu.md` (W2-88), `DAEO-s9qc.md` (W2-87), `DAEO-zqvn.md` (W2-13), `DAEO-mpq2.md` (W2-192), `DAEO-j9z6.md` (W2-115b), `DAEO-0z8c.md` (W2-05), `DAEO-6y0x.md` (W2-93), `DAEO-csj8.md` and `DAEO-60rw.md` (W2-28, W2-30, moved).
- Register: DEC-1211, DEC-1221, DEC-1223, DEC-1224, DEC-1197 (via P-W2-81-VERDICT-1), DEC-192 (ccusage), DEC-210 and DEC-214 (Claude Code drift, via W1-48); `docs/contract/contract.yaml` v5 (CAP-01.c, CAP-03, CAP-10, CAP-25, CAP-44.b/.e/.f/.g/.h/.m, CAP-49, CAP-58.h, CAP-61.e, CAP-63); `docs/emergency-2/EMERGENCY-2.md` (2.11, 5.2, 5.3, 8.2, 8.4); `docs/emergency-2/proposals/IMPORTS-ADOPTION-SPEC.md`; `governance/project/tool-registry.yaml`; `governance/project/bootstrap.md` ("The adoption's commits").
- Code: as listed under Method.

## Residuals

- The ranked bundle is not recorded (T6): "forbidden ranked above gold" is open; causes are by the gold's rank and the forbidden source's presence in the top five.
- Cause C (ts-h03) is an estimate: I did not read the hidden gold; the reader's correct answer, its adoption-record-only citations, the data table's `product` class and `indexed = 0` point at it.
- The 22 of 25 count is a keyword proxy over answer text, not a grader's judgement.
- The "est. figures" of the product's own measure assume the gold line is also cited in each of the 24 cause-A rows; I could not check without the manifests, and sampled only the python-app v01 row.
- Rust's `gov queue` result (2 passed 4 failed) is the lead's, not re-derived; I read the same lines for python-app, legacy-docs and secret-history in `accept.out`.
- Kinds of the hidden variants are named only by capability in the report; I did not map them.
- The owners of the `gov brief` slot and framework.lock findings are not traced; AS's narrow spec and module rule is by design in `spec_audit.py` and is a W2-192 question only if the owner wants it widened.
- This session's `GOV_ROLE` was `orchestrator` (inherited) with no identity command to run (above).
