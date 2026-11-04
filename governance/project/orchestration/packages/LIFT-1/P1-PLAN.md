# P1-PLAN — the refactoring plan, drafted (DEC-1050 THE PLAN; DEC-1039 steps 2, 3, 3b, 4)

## DECIDED BY DEC-1052 (owner, 2026-11-02 late evening) — this section overrides the draft below where they differ

**The basis:** `governance/project/orchestration/INTENT-DEC-1052.md` (one question, five tests; templates; READY and DONE by
code; path-map roles; what memory holds). Every affected ticket points to it.

**The rows' status (§B is to be updated to this):** approved: T-2, T-3 (first), T-6..T-11, T-13; Q-2..Q-14; G-4..G-9, G-13;
M-2, M-3, M-5, M-6; R-6, R-7, R-9, R-10, R-12, R-13; O-5, O-8, O-9, O-11, O-12, O-13; K-1..K-4; W-1..W-10; with DEC-1050's
T-1, T-4, T-5, Q-1, T-12/O-10 (wider), G-10/G-11 (the harvest stopped), O-7 (wider), R-8/R-11, G-1/G-2, E-1 (keep the
repository). Replaced by the templates (no cuts): R-1..R-5, O-1, O-2, O-4. Refused: O-3 (a fresh CTO session daily; long
contexts kept), G-12 (review effort as is). Re-decided: O-6 (ACTs only for machine changes, and only where they help;
the repository's own servers restarted from committed configs approved by class; no ACTs for records), G-3 (the hidden
half moves outside every worktree; no guard rule), G-14 (role separation from the path map, simple path checks),
M-1 (W2-04 accepted as built), M-4 (embed the WBS, specs and KPIs, tickets, code, decisions; not tests or close,
checkpoint and probe records; W2-61's measure before and after). E1 and R1-21 approved (E1 before the guard ACT).
Option A. The templates' four recommendations approved, READY and DONE computed by code from the filled templates.

**No run uses the old way from now on:** gitleaks off; no full suite but P1-12's; scoped selection; attribution once
each way. Nothing scheduled but the dispatcher (DEC-1051).

**Status of the steps (2026-11-03 14:20, session bb5cd8bd; the fresh session starts from `governance/project/orchestration/START-NEXT-SESSION.md`):**

| step | status | where |
|---|---|---|
| D-0 clean-up | **done** (DEC-1053 `d855e41a`) | `D0-CLEANUP-LIST.md` |
| D-1 memory branches merged as built; re-pin window 2 | **done**: seven branches and emg/w1-19-helper merged; `pin-9894b0cf` live (registry `b74d2c7f`) | `ACT-REPIN-W2.md` |
| D-2 the CTO's tools | **done**: E1 (Q-1, G-1), R1-21, E3 (ACT-GUARD-FIX-4), O-A1 and the LB held-slot fix; G-14 live by ACT-G14 (`4edd196c`, DEC-1059) | `ACT-GUARD-FIX-4.md`, `ACT-G14.md`, `reviews/` |
| D-3 configuration and text lifts | **done** (DEC-1057, `2e5c9cd9`); items 2-7 and 5 moved to D-4, item 9 to D-5 | `D3-WORKLIST.md` |
| D-4 the test suite cut | **done** (DEC-1061; merged `6008a41f`): 5,628 cases in the full run of 20,094 (opt-in `lifted` and `breadth` hold the rest); review READY at round 2; selection re-checked (34 tool tests pass). Open: ACT-G14b (a coordination ticket's link-based tests; `guard4_check` FAIL since the cut) | `D4-LIST.md`, `reviews/d4-cut.md` |
| **D-4b the memory stage** (DEC-1055, DEC-1066-DEC-1069) | **in progress (2026-11-04 ~18:00)**: measures m1 28/48 -> m2 29 (D-7 + G4) -> m2g1 35 (G1) -> m3 37 (x5: routing by question type + phrasings) -> m4 38 (contextual headers) -> **m5 38/48 on the product** (`dc8a2829`); merged: W2-13 S6, D-7 + G4, W2-32 (G1, S8 routing and phrasings, the padded reranker bound, headers), the five index-time methods M1-M5 (each off); **re-pin window 3 done** (`pin-8284fb408bd4` live, registry `b05f62b8`; integration store at `8284fb40` with headers); the 48 audited (rubric R1-R11, `docs/research/memory-measure-audit/`), labels fixed, the set grown to **80 (40 + 40)**; **m6, the new baseline: 65/80 (81.2 %), visible 36/40, hidden 29/40** (`24f06026`); **the reranker trial running** (ACT-RERANK-TRIAL-1: 0.6B, mxbai-rerank-large-v2, Qwen3-Reranker-4B 8-bit, in turn); next: the methods' measures by `DAY.md`'s rule, re-pin window 4 (W2-112's memory release, the adopted methods), D-5 | `D4B-MEMORY-STAGE.md`, `D4B-NIGHT.md`, `D4B-AUDIT.md`, `.gov-runtime/scratch/orchestrator/drafts/d4b/DAY.md` |
| D-5, D-6 | not started (after the trial, the methods' measures and re-pin window 4); D-5 row: the generated MR-1..MR-6 records take the Contract's status (the owner, 2026-11-04) | `D5-ROWS.md`, `DAY.md` rows |
| D-7, D-8 | **done inside D-4b**: D-8 (ACT-D8), D-7 + G4 (`27a80411`, extended to W2-15a's raw output and the measure's audit) (DEC-1055) | `D4B-MEMORY-STAGE.md` §5, §10 |
| D-9 the WBS refactor | not started (the fates and K9 to the owner first) | — |
| D-10 the full suite | not started (the owner's word) | — |
| D-11 the basis as a standing practice | after the lift | — |

**The order, as decided:**
1. **D-0 Clean-up** (O-8, O-13): stale worktrees, branches, scratch, dead copies, old run folders removed; **anything
   unmerged that may hold work is listed to the owner before it is deleted** (the CTO lists, the owner says).
2. **D-1 The memory branches merged directly into `w2/integrate`, accepted as built, no queue run:** W2-122
   (3fc448601e2d), W2-123 (3de9bcf44d91), W2-126 (2785b2e47432; an engineer resolves its conflict with W2-123 in
   `semantic.py`, then KPI 7), W2-112 (d5216599e6fd), W2-04 (its last head). With them the built emergency branches:
   `emg/noscan` (the DEC-1045 product switch), `emg/select` (T-4, 194e3289). **Re-pin window 2** carries them, with its
   checks (`pin/make_repin3_commands.sh`, `pin/repin3_checks.sh`, the ACT); the full suite on the refactored repository
   (P1-12) verifies them.
3. **D-2 The CTO's tools:** E1 (Q-1 attribution once each way; G-1 the landing check on who wrote any acceptance test),
   then R1-21 (the structural pass in `land.py`), then E3's guard ACT (rules 1 and 5 by path, `rm` free but the
   catastrophic), then G-14's path-map role checks in its place. O-A1 and the Load Balancer's held-slot fix (EMG-lb2).
4. **D-3 Configuration and text lifts** of every approved row (T-3 first, then T-2 ...), as the draft's P1-2.
5. **D-4 The test suite cut, before the full suite:** from about 19,000 cases to about 5,000 or fewer, every kept KPI
   line covered by at least one test; the guard's ~9,000 first (keep what the five rules need; lifted rules' cases and the
   roles x tools x input-forms breadth go or become representative cases); tests of features built but off leave the
   full suite (per group: delete, or an opt-in suite outside the full run, proposed). Test designers, one independent
   reviewer; **the deletions and merges listed to the owner first**; the count and the full suite's expected time,
   before and after. With P1-INVENTORY-1's approved rows (P1-5).
6. **D-5 The templates** (TPL-1..TPL-8, scripts first), READY and DONE by code; **D-6 the code tidy-up** (P1-6);
   **D-7 memory's embedding scope (M-4)** with W2-61's measure before and after; **D-8 G-3** (the hidden half outside
   every worktree).
7. **D-9 The WBS refactor (P1-8), with the homes:** every decision as KPI lines in its home ticket (templates and
   READY/DONE in W2-11, W2-33, W2-60a/b and TPL-1..8; path-map roles in the roles tickets and the guard's re-scoped
   ticket; what memory embeds in the memory tickets), or a new ticket where none fits; every affected ticket points
   to `INTENT-DEC-1052.md`; **the tests run per ticket, before and after the refactoring**, shown.
   **The ticket fates and K9 (EXAMIN's entry criteria) come to the owner first, as a list, before they are applied**
   (DEC-1039 (3b)): each ticket's fate (keep, re-scope, merge, close formally, retire, Wave 3) with its KPI lines' fate
   (met with evidence, or moved to the ticket that absorbs it), and the amended K9 with W2-27's re-derived dependencies.
8. **D-10 The full suite on the refactored repository (P1-12), on the owner's word**, every red fixed; then the lift,
   the restart and the formal closes (P1-13); then EXAMIN's adoption (P1-14).

9. **D-11 The basis as a standing practice, after the lift** (DEC-1052): at adoption, every new rule, gate, check,
   mechanism or KPI line states the basis question it passes, or is not adopted; on symptoms, repeated refusals,
   timeouts, retries, prompts to the owner and re-runs are flagged from the logs and assessed at once; weekly, a basis
   review of everything in force with measured costs (machine time, tokens, the owner's time); the lift-or-remove list
   to the owner first. Its home: a KPI line of the dispatcher/tools (the symptom flags) and the CTO template (the weekly
   review), placed in D-9.

The draft's estimate (§G: restart about 11-07, EXAMIN's copy about 11-14, range 11-12..11-19) is to be re-estimated after
D-4's count, since the suite cut and the direct merges change the time to green.

By the P1 planner, read-only, 2026-11-02 ~23:00. Sources: DEC-1039, DEC-1040, DEC-1047 to DEC-1050 (register, last
entries); `packages/INVESTIGATION-1-COMBINED.md` (the list, §3 rows, §5 fates, §6 order) and its part reports;
`packages/P1-LIFT-1.md` (with O-A1); `packages/P1-INVENTORY-1.md` and `INVENTORY-TESTS-CODE-1.md` (§5, §6a, §6b);
part E (E-2's four edges); `docs/plan/WAVE_2_WBS.md`; `.tickets/`; the lead logs `log/W2-*.json`. Helpers:
`/tmp/gov-os-inv-P1/{leads.py,deps.py,closure.py}`. **(est.)** marks an estimate, with how it was reached.

## Headline
1. 89 row ids (87 in the list's §3, plus O-A1 and E-1). **14 are approved by DEC-1050**: 13 of the 22 ids in the
   twelve items, plus E-1, "keep this repository". **9 are refused by DEC-1050**: R-1 to R-5, O-1, O-2, O-4 and G-12. **T-13
   was approved earlier (DEC-1045).** **65 are pending the owner** (DEC-1050 says 63; the gap is a count, see Evidence 1).
2. The plan is 14 steps. The critical path is: the owner's row decisions → config and text lifts → the CTO-tool code
   and the test refactor and the code tidy-up, in parallel → the full suite on the refactored repository until green → the lift.
   Product switches (W2-45, W2-115, G-4…) are **re-scoped tickets after the resume** (option A).
3. Resume (est.) **2026-11-07**, range 11-06 to 11-09. The owner's time (est.) is **4 to 6 hours** over 4 to 5 days.
4. **EXAMIN's copy (est.): centre 2026-11-14, range 2026-11-12 to 2026-11-19** (the old target was 11-18; the 11-01 estimate was 11-14).
   The freeze costs about 4 to 5 days. The fates and lifts cut the copy's remaining work from 44 tickets (~375
   lead-h) to 27 open tickets plus 4 formal closes (~175 to 225 lead-h after the lifts, est.).
5. Questions that change the plan: whether the 4 product-switch tickets go in before the full run (option B, +2 to 3
   days); K9 as amended; W2-04 decided by the owner once; G-3's measured tickets; whether the lead's templates must
   land before the resume (recommended: yes for the lead, engineer and test-designer templates); R1-21 (a structural
   pass in `land.py`, pending).
6. **Folded in from R1 and R2** (23:10):
   - **R1:** leads' `gov check` can go altogether (done, `cc8f64c9`). But **nothing in the queue or the close runs
     `gov check`**, and the CTO's record commits never pass through the queue. So two items enter the plan: R1-21 (pending
     the owner), a cheap structural pass in `land.py` after landings and after the CTO's record commits, as a notice only,
     after E1; and R1-22, a correction to E2 before it lands, so that T-4 keeps the quick `record_reading` cases.
     `core-mutation` is red on `w2/integrate` today (DAEO-tgk2, DAEO-a3u2): a ticket edit in P1-2.
   - **R2:** the "3 %" was the mandated decision reading list, not the brief; leads follow the brief's commands. Their time
     goes to wait loops (24.5 % of calls) and ceremony steps (11.6 %). So P1-7 becomes templates per run kind plus
     scripts (R2-4, R2-6, R2-9), with one template owner (R2-3).

---

## A. The steps (the form of INV-common; for a plan step, "recommendation" holds who does it and how it is verified, and "what lifting takes" holds the work)

| id | what | where (paths, tickets, decisions) | cost (machine / tokens / owner; source) | what it protects | DEC-1010 test | recommendation | what lifting takes | depends on |
|---|---|---|---|---|---|---|---|---|
| P1-0 | **In flight now** (DEC-1050's parallel work): T-5 and T-1 in the brief (done `cc8f64c9`); the harvest stopped (done: `guard_harvest_s` 10^9); schedules stopped (ACT-NIGHTLY-STOP-1, ACT-SCHEDULE-STOP-2 `7fe61d5a`); E1 (Q-1 + G-1's landing check, `EMG-queue`), E2 (T-4, `EMG-select`), E3 (G-2, rules 1 and 5, `rm`: `drafts/act-guard-fix-4/`); R1, R2, R3 and this P1; the memory landings (W2-122 + W2-123 merged onto `b60ff112` → `35a851b3` in the 22:25 run; **W2-126 EJECTED: conflict**; W2-112's lead started 22:17) | `LIFT-parts.md` E1–E3, R1–R3; `land-dispatch-20261102-222503.out` | E1 est. 4–6 h of engineer time plus a 1–2 h review; E2 est. 2–3 h plus a review; E3 est. 4–6 h plus a review, then the owner's ACT (~15 min). All est., from the size of the change (E1 ~60 lines out and ~10 in; E2 ~5 lines; E3 ~35 lines out plus the replay) | the decided rows; memory (DEC-1047 (1)) | in aim / yes / yes (decided) | **Engineers** for E1–E3, each with **one independent review** (READY by `verdict.py`); E1's candidates are promoted by the CTO only when no landing runs. **Verified:** E1: the queue's unit tests (`tests/unit/orchestration/test_merge_queue*`), plus planted ranges with and without `Role: independent-test-designer`. E2: unit tests of `select.py` and the scoped set, **plus R1-22** (fixed before E2 lands). The quick `record_reading` "here" cases still appear in every selection made through `select_tests.py`: W2-02 core-schema (4–11 s), W1-08 path map, W1-10 graph and register, W1-26 probe records. Alternatively, `select_tests.py` passes the record-only paths it strips through as the trigger. Only W2-54's costly cases leave. E3: the replay of every row in `log/guard-refusals.jsonl` (each false refusal now passes, each true one is still refused), the planted cases of ACT-GUARD-FIX-3, and the catastrophic-`rm` cases. T-5 and T-1: the next three lead returns show no nightly-routed entry and no full `gov check` | as briefed | — |
| P1-1 | **The owner decides** the 65 pending rows (§B), R1-21 and R2's two register amendments (DEC-851 item 1 and DEC-943 item 1, R2-3), the ticket fates (§C), K9's amendment, G-3's measured tickets, W2-04 once (M-1/W-7), G-14's "reads", and option A or B (§G) | `INVESTIGATION-1-COMBINED.md` §3, §5; this plan §B, §C | Owner est. 1.5–2.5 h for the rows (the §3 tables are ~45 KB, read at a package rate of ~2.5 h for 21–25 packages on 2 Nov, est.) and ~0.5 h for the fates and K9 | nothing is lifted before the owner decides (DEC-1047, DEC-1050) | — | **The owner**; the CTO records one DEC entry and edits this plan's status column. **Verified:** every §B row carries "approved", "refused" or "deferred" | one register entry; this file's status column | the list (done) |
| P1-2 | **Configuration and text lifts** of the approved rows: brief, prompt and DECISIONS-IN-FORCE lines, test-map couplings, path-map lines, DEC amendments. **Also now, whatever the rows:** the two engineer tickets whose `allowed_paths` cover `tests/acceptance/` (DAEO-tgk2 and DAEO-a3u2) are corrected, because `core-mutation` is red on `w2/integrate` (R1-6; aim 3). The brief's stated reason for T-1 is corrected too, since the queue runs no `gov check` (R1-1, R1-2) | `governance/project/briefs/LEAD-w2-common.md`, `governance/project/test-map.yaml`, `governance/project/path-map.yaml`, the prompt `governance/project/prompts/w2-orchestrator.md`, DECISIONS-IN-FORCE | est. 3–5 h of CTO time; no machine | — | — | **Orchestrator** (project files; kernel text goes to P1-11). **Verified:** each row's check line in §B (a diff and a named check), plus `tests/unit/close` select cases for the test-map edits | text and config only | P1-1 (rows); R-8 and R-11 are already approved |
| P1-3 | **The owner's ACTs:** (i) ACT-GUARD-FIX-4: rules 1 and 5 (G-1, G-2) and `rm` free but the catastrophic (O-7), hook files plus the settings change; (ii) if approved, R-7 and O-5: the Stop-hook entry; (iii) re-pin window 2: `emg/noscan` (T-13), the memory branches' code, G-8's import check | `.claude/hooks/`, `.claude/settings*.json`, `.rulesync/hooks.jsonc`, the pin | Owner est. 15 min per ACT, 30–60 min for the re-pin window; machine: one store rebuild at the re-pin (est. ~20 min warm) | role separation (rules 1 and 5 kept for resolvable targets); the owner's machine | in aim / yes / yes | **The owner's operator**, with the CTO's ACT text (exact commands, check, undo). **Verified:** each ACT's own check; after (i): `rm` prompts in the permission log drop, and a planted catastrophic `rm` is refused | 3 ACTs | (i) needs **E1's landing check live first** (DEC-1050 (12)) and E3 reviewed; (iii) needs W2-112, W2-126 and W2-122/123 landed |
| P1-4 | **The CTO's tools: code** (the tools lane). **First, if approved: R1-21.** After a queue run lands, and after the CTO's ticket-filing and decision-record commits, `land.py` runs `python3 -m gov.check.{schema,graph,claims,mutation,authority,pathmap}`, `audit_validator docs/audit/` and the skill validator on the new head. The result is **a notice to the CTO only**: it never refuses a lead. It costs under 1 min (est., R1). It is about 20 lines plus a test, sequenced after E1 because it is the same file. Portability runs only when the batch touches `template/governance/kernel/{roles,skills,hooks}/**` (R1-10). **Then the scripts the templates name** (R2-6, R2-9): `wait_for.sh <exit-file> [<max-s>]` (~20 lines and a test), `lead_verify.sh <W2> <ID>` and `launch_worker.sh <role> <effort> <brief>` (about 60 lines each, with tests). After those: Q-13 (hold and retry on infrastructure failure; refusals to the inbox), O-9 (fair `heavy_slot.sh`), O-A1 (the slots rule out of the admission), T-12 + O-10 (built now, live when the owner restarts schedules), R-10 (`--main` out of `sync_context.py`), R-13, G-9 (the hook's tests into `tests/unit/hooks/`), O-8 (backups and dead copies out, after E1's promotion) | `.gov-runtime/scratch/orchestrator/tools/{land.py,heavy_slot.sh,close_build.py}`, `governance/project/orchestration/tools/{merge_queue.py,dispatch/dispatcher.py,dispatch/balancer.py}`, `governance/project/orchestration/nightly/{nightly.sh,test_nightly.sh}` | est. 1.5–2 days for 1–2 engineers in parallel. R1-21 is 2–3 h. The three scripts are about 0.5 d (~140 lines with tests). Q-13 ~0.5 d, O-9 ~0.5 d (~40 lines + 4 cases), O-A1 2–3 h, T-12/O-10 3–4 h, the rest 1–2 h each (est., from the list's sizing) | landings and the machine (traffic) | in aim / yes / Q-13, O-9 and O-A1 lose time or work | **Engineer** (CTO tools lane), **one independent review** for each change where a bug blocks every run (Q-13, O-9, O-A1, T-12). **Verified:** `test_merge_queue*`, `test_heavy_slot.sh`, `test_dispatcher.py`/`test_balancer.py`, `test_nightly.sh`; a dry queue run on the current head | code + unit tests | P1-1 for the pending rows (Q-13, O-9, O-A1, R-10, R-13, G-9, O-8); T-12/O-10 are approved. **Reconcile the uncommitted edits to `nightly.sh` and `test_nightly.sh` first** (combined §6). O-9 comes before T-12's 2-slot nightly |
| P1-5 | **The test refactor** (P1-INVENTORY-1 (a), DEC-1040 (1)): D1–D3, M1 (+ M1b at the designer's judgement), M2, R1–R5; M9 now (W2-54's revision merged `88b33a38`); M3 optional. M4–M7 after the resume. **Plus the revisions that approved and pending lifts force** (W2-66's live test-map cases after T-4; W2-111's latency cases if T-6 is approved) | `tests/acceptance/{W1-01,W1-24,W1-45,W2-54,W2-66,W1-26,W1-35,W1-19,W1-21,W2-02,W2-03}`, `tests/unit/{install,retrieval}`; inventory §5 and §6a | est. 3–4 h of test-designer time plus 1–2 h of review (the package's own estimate); machine: one scoped run of the touched suites (W1-19/W1-21 are real-model: run against the shared service, in a heavy slot) | every KPI line keeps at least one test (DEC-1039 (2)) | in aim / yes / a lost line fails open | **Independent test designer** (acceptance cases; `Rewrite-Reason: DEC-1040` or `DEC-1050`); the unit cases D2, M9 and R5 may go to P1-6's engineer (DEC-136). **One independent reviewer** checks the coverage map: each deleted or merged case names the case that keeps its line (inventory §5). **Verified:** the scoped run green (or the same reds as before, named); the case count −32 (−33 with M3, about −35 with M9); M1's seconds saved measured in P1-12's JUnit | test edits only | the infrastructure stable (DEC-1040 (1)): the memory landings in P1-0; M1 and E2 (T-4) touch the same W2-54 cases: **do M1 with or after E2** |
| P1-6 | **The code tidy-up** (DEC-1039 (2), DEC-1040 (1): §6b to the senior engineer; part E's E-2 = row M-6): (1) the four coupling edges out of memory's import closure; (2) §6b: one frontmatter parser for 15, one `_ids` for 3, one SQLite `_open`, one sha256 helper, `close/evidence.py:junit_rel` deleted; the git wrappers only outside the guard's hot path; `retrieval/synthesis.py` kept (DEC-953) unless the owner says otherwise | E-2's edges: `store/loader.py:327,379 → close.fingerprint.of_commit → close.select → guard.decide._match_pattern` and `tasks.tickets`; `retrieve/command.py:26 → gov.decisions` (its `__init__` pulls `checker → guard.containment_merge`); `secrets/__init__.py:48 → guard.runs → guard.decide`; `retrieval/measure.py:51 → guard.reads`. The move: `of_commit`'s path classification, `_match_pattern`, `TICKETS_REL`, `runs.root` and `leave_out` into `gov.util`/`gov.store`; `gov.decisions/__init__` made lazy | est. 1–1.5 lead-days in all: E-2 0.5–1 (part E: an S-profile median is 9.2 lead-h), §6b about 0.5; review 1–2 h (est.) | nothing in itself; it unblocks EXAMIN's copy of memory, and memory changes stop selecting gate tests | accidental coupling | **Engineer** (senior), **one independent review**. **Verified:** the unit tests move with their helpers, and the existing unit and acceptance suites of the touched packages pass unchanged (public calls unchanged: no acceptance test changes); part E's `closure.py` re-run shows memory's closure without `close.*`, `guard.*` or `decisions.checker` (from 18,063 lines toward ~7,600 plus the in-flight ~1,290, est.); `select_tests.py` on a `src/gov/retrieval/` diff no longer selects close or guard suites | code + moved unit tests | **the four memory branches landed** (W2-112, W2-122, W2-123, W2-126); after E2 (both touch `close/select.py`); before W2-115 and W2-42a resume (or they rebase) |
| P1-7 | **The templates** (DEC-1050 TEMPLATES; R3's report as one work package, shaped by R2's evidence): one template for each role (research and discovery, product-spec, test designer, engineer, QA and reviewer, lead, CTO), for tickets and for briefs, plus the return form; delivered like the roles and skills; KPI lines that test that agents follow them. The fix in place of R-1 to R-5 (refused) and the root fix of G-1/G-2 (DEC-1050 (12)). **R2 sets the shape:**<br>• **The lead's template is one short template per kind of run** (R2-4): tests only; implement and verify; review round; resume; land. Order: identity, this run's steps, the exact commands (as P1-4's scripts), paths, return. `build_lead_brief.py` picks the template by run kind; the delivery mechanism stays (R2-14).<br>• The mandated decision list is replaced by "ask `gov retrieve` first; grep the register only by id" (R2-2, R2-16).<br>• The template gives the lead its first ~10 calls (R2-15).<br>• The harness's allowed commands are stated (R2-8, with O-7).<br>• The command forms stay, in positive form (R2-7: 68 % of sessions had a refusal before the forms, 17 % after).<br>• The stale and contradictory lines go (R2-12).<br>• **One worker template per role** comes out of the CTO's prompt Appendix A (R2-10).<br>• **One lead template**: the kernel's `brief-lead.md` is the base and the project fills it (R2-11, CIT-P).<br>• **One owner:** product-spec writes the templates and the CTO approves. A rule enters only where it changes what an agent does (R2-3: amend DEC-851 item 1, owner). Brief gaps are counted by kind, not added as paragraphs (R2-13: amend DEC-943 item 1, owner) | project part: `governance/project/briefs/` and `tools/build_lead_brief.py` (the lead brief rebuilt from the lead template). Kernel part: `template/governance/kernel/roles/`, `template/governance/kernel/skills/` (generated `.claude/agents/`, `.claude/skills/`). R2's and R3's reports | est. 1.5–2.5 days: product-spec 0.5–1 d, the test designer's KPI tests 0.5 d, review 2–3 h, the owner's approval ~30 min (est., by the size of W2-11/W2-33's work) | leads and workers briefed with the right paths, commands and return (aim 2–4) | in aim / yes / bad briefs lose work (the brief-gap minutes: 7,669 stated in 83 returns) | **Product-spec** writes them; an **independent test designer** writes tests from R3's KPI lines; **one independent review**; the kernel half is a **CIT-P under CAP-33** (evidence R2/R3, review, owner approval, a versioned promotion). **Verified:** R3's KPI tests (sizes, sections, every path and command in a built brief exists or parses); then the **pilot measure**: R2's "did the lead do it" counts re-run on the first 3 resumed leads, against R2's baseline (159 transcripts). The measures:<br>• the share of wait calls (24.5 % today);<br>• ceremony calls (median 14 a lead);<br>• hand-written verify wrappers (343 in 117 of 159 sessions);<br>• permission denials (218 in 110 logs);<br>• brief-gap lines by kind;<br>• guard refusals per lead.<br>The commands each template names must be run by at least 83 % of the leads it reaches, today's rate for named commands | text, a builder change, tests; one new ticket recommended (W2-128, STANDARD, product-spec), not folded into W2-11 (which lands as built) | R2 and R3 reports; P1-1 (the brief carries only what is kept); **the lead, engineer and test-designer templates before the resume** (recommended), the rest after |
| P1-8 | **The WBS refactor** (DEC-1039 (3b); part D; the list's §5, W-1 to W-10, K-2, K-3): the fates applied; every KPI line of a merged or retired ticket shown as met (with evidence) or moved; W2-27's deps re-derived and K9 encoded; one home per rule; the boilerplate lines, the lines that cannot pass and the contradictions edited; the new estimate | `docs/plan/WAVE_2_WBS.md` (§1 rows, §2 cards), `.tickets/*.md` (status, deps, KPI lines, tags), part D's per-line parse (`/tmp/gov-os-inv-D/kpis.txt`), `docs/plan/tools/validate_w2.py` | est. 0.5–1 day of CTO time; an auditor's spot-check of the line map 1–2 h; the owner ~45 min for the list and K9 (est.) | ordering (aim 4: the traffic); no KPI line lost | in aim / yes / a dropped line or a wrong dep fails open | **Orchestrator** (W2-00's paths), the list to **the owner first** (DEC-1039 (3b)); **one independent auditor** checks that each of the 716 lines is accounted for. **Verified:** `validate_w2.py` and `tests/unit/plan/test_validate_w2.py` green (K-3); the `tk` dependency graph acyclic (the cheap structural checks: claims, graph); W2-27's deps equal K9 | ticket and WBS edits | P1-1 (fates, K9); P1-9's rows that re-word lines (Q-1 → W2-115 S4) |
| P1-9 | **The product switches**, as re-scoped tickets **after the resume** (option A; option B puts them before P1-12): W2-45 (T-3, then T-2), W2-115 (Q-2 to Q-11, T-9, the product half of Q-1, absorbs W2-117), W2-42a re-scoped (G-7), W2-04 (M-1), W2-56 S1 (T-8), M-4, M-5, Q-12, Q-14 (W2-20) | the tickets named; `src/gov/{check,close,guard,context,store}/` | est., at the plan's medians: W2-45 F ~13.6 h; W2-115 26–34 h (scaled like W2-81, by its 19 lines plus W2-117's); W2-42a ~10 lines plus re-cut tests, 1–1.5 lead-days; M-5 0.5–1 day | the product for EXAMIN and adopters | per row | **Engineers with independent test designers** (FULL where memory, the guard's rules, close or the queue are touched, as DEC-1050 (11) keeps review effort); the kernel parts go to P1-11. **Verified:** each ticket's acceptance tests and its review | tickets | P1-8 (re-scoped KPI lines); T-3 before T-2, Q-4, Q-5, Q-8; Q-2 before T-9; G-1/G-2 live before G-4/G-7 |
| P1-10 | **The memory configuration lifts** (if approved): M-3 (incremental/seeded refresh in the template), M-4 (what memory embeds) | `governance/project/path-map.yaml` (`memory_class`); the template | machine: one seeded rebuild (est. ~20–80 min) plus W2-61's measure before and after | memory quality (aim 1) | in aim / yes / a silent recall loss loses work | **Research** runs W2-61's measure before and after; **engineer** for the close-record summary (~30 lines). **Verified:** hit@5 no lower on W2-61's set | config + a measure | W2-122, W2-123 and W2-126 landed; P1-1 |
| P1-11 | **One CIT-P/CIT-E and the Contract re-baseline**, last: T-3 (policies), G-4/G-5/G-6 (the template's guard profile and hooks), T-11 (lefthook), M-2 and G-13 (kernel hooks), K-4 (skill text), and the kernel half of P1-7 if it has not gone already; K-1 (DEC-105 option c): MR-3, CAP-58, CAP-37.b/.c, CAP-59, CAP-38.b, CAP-05, Charter §2, MR-6/§6, CAP-44.h; K-2 (W2-109) retired into it; K-3 re-run | `docs/contract/`, Charter, `template/governance/kernel/` | est. half a day of product-spec plus one review plus ~30 min of the owner (part B2's figure) | the yardstick matches practice | in aim / yes / no (drift only) | **Product-spec**, **one independent review**, **owner approval**, a versioned promotion (CAP-33). **Verified:** `validate_w2.py` (K-3); the Contract-reading tests (W1 schema and contract cases) green | text | the rows decided and the switches decided (built or not) |
| P1-12 | **The full suite on the refactored repository**, on the owner's word (DEC-1050 (5), DEC-1049, DEC-1039 (3)); every red fixed in emergency mode; repeated until green. No accepted red carries over (`accepted_reds` is `[]` today; DEC-1050 (5)) | `governance/project/orchestration/nightly/nightly.sh` run by hand on the head (with `--junitxml`, inventory §2's side finding); the 11-02 nightly's 32 reds as the starting map (`P1-NIGHTLY-2026-11-02.md`) | machine: **~5.4 h a run** (19,448 s measured on 11-02 under load; est. 4–5 h on a quiet machine, less ~0.25–0.5 h from M1); 2–3 runs (est.); the red fixes between runs est. 0.5–1 day each | tests and code green against the KPIs (the aim's centre) | in aim / yes / yes | **The CTO** starts it once the owner gives the word; **engineers** fix the reds; **test designers** revise acceptance tests that must change (DEC-1039 (1)); one review where needed. **Verified:** the run's JUnit with 0 failures and 0 errors | runs and fixes | P1-2, P1-4 (T-12 at least), P1-5, P1-6; P1-3 (iii) re-pin; option B adds P1-9 |
| P1-13 | **The lift and the restart**: the owner lifts the emergency and the freeze; re-pin if needed; formal closes of W2-05, W2-96, W2-112, W2-122, W2-123 (absorbs W2-20 S12) and W2-126, with their 48 lines shown met (W-9, DEC-1039 (4)); branches and worktrees pruned (O-13, if approved); the dispatcher's ready list refilled from the refactored WBS | `dispatch/ready*.txt`, close records | est. 0.5 day for the six formal closes (smart, scoped closes measured at 10–20 min each, PLAN-W2-DEC953 §2, plus their records); owner ~15 min | — | — | **Owner** (the lift); **orchestrator** (closes, ready list). **Verified:** six close records; the status block shows the freeze lifted | records | P1-12 green; P1-8 approved; P1-7's three templates (recommended) |
| P1-14 | **To EXAMIN's copy** (W2-27): 27 open tickets plus the 4 formal closes in its re-derived closure (§G) | §G | est. 175–225 lead-h after the lifts (230–281 at the old medians); 4–6 working days | the product's real goal | — | **Leads** under the dispatcher and the Load Balancer (2–3 leads, DEC-1039 (1b)) | tickets | P1-13 |

**Order (the critical path in bold):** P1-0 → **P1-1 → P1-2 → {P1-4, P1-5, P1-6} → P1-12 → P1-13 → P1-14**; P1-3 (i)
after E1 live; P1-3 (iii) after the memory landings and before P1-12; P1-7 and P1-8 beside P1-4 to P1-6 (both before
P1-13); P1-10 after the memory landings; P1-9 and P1-11 after the resume (option A).

---

## B. Every row, with its change and its status (edit the status cell when the owner decides)

Status: **APPROVED (DEC-1050)**, **REFUSED (DEC-1050)**, **PENDING the owner**. "Step" refers to §A. Where an
approved decision bears on a pending row, the row says so.

### B.1 Tests and runs
| id | status | the change | step | who | verified by |
|---|---|---|---|---|---|
| T-1 | **APPROVED (DEC-1050 (3))**, done in the brief (`cc8f64c9`). R1 confirms that **no family needs a lead's run**. The checks' code is tested by `tests/unit/check` and W1-26. But the queue and the close run **no** `gov check`, so the brief's reason is wrong (R1-1, R1-2) | leads run no `gov check`; the brief's reason is corrected | P1-0; P1-2 (the reason) | orchestrator | the next 3 lead returns |
| R1-21 | PENDING (new, from R1) | one structural pass (schema, graph, claims, mutation, authority, path map, audit validator, skill validator) on merged code in `land.py`, and after the CTO's record commits; a notice only; portability only for kernel role, skill or hook changes; later replaced by T-2's `--families` | P1-4 (after E1) | engineer + review | a planted broken ticket record gives a notice; the pass takes under 1 min |
| R1-22 | **APPROVED in substance** (a correction inside T-4, DEC-1050 (2)) | E2 keeps the quick `record_reading` "here" cases in every selection, or `select_tests.py` passes the stripped record paths as the trigger | P1-0 (E2) | E2's engineer | a unit case: a ticket-only change selects W2-02, W1-08, W1-10, W1-26's "here" cases |
| T-2 | PENDING | `gov check` scoped: each check's `inputs:` globs, `--changed <base>`, a timeout YELLOW not RED, the memory-heavy families nightly (retrieval regression also on `src/gov/{retrieval,context,store}/**`), index-freshness lifted | P1-9 (W2-45) | engineer + test designer (W1-26 runner cases) | W2-45's acceptance tests |
| T-3 | PENDING (**must come first** among the check changes) | policy coverage, skill-version and citations lifted; path-map becomes a warning | P1-9 (W2-45) + P1-11 (policy: CIT-P) | engineer + test designer; product-spec for the policy | W1-26 cases; `gov check` stays green after a family is removed |
| T-4 | **APPROVED (DEC-1050 (2))** | `record_reading` and `every_close` selected only when a record path changed; W2-54's two real `gov check` cases out of every scoped selection; its planted-fake cases stay | P1-0 (E2) | engineer; W2-66's live test-map cases by a test designer | `select.py` unit tests; a scoped selection without the record lists |
| T-5 | **APPROVED (DEC-1050 (1))**, done (`cc8f64c9`) | the lead's serial phase runs only what `gov.close.serial.phase()` selects | P1-0 | orchestrator | the next lead's serial log has no nightly-routed entry |
| T-6 | PENDING | hit@5 and the fused/reranked route kept, scoped to model paths; warm p95 to the nightly; the path-map and gitleaks-config couplings dropped; no private reranker in the fixture (DEC-1046); W2-111's latency cases into P1-5 | P1-2 (test map) + P1-5 | orchestrator; test designer | `select_tests.py` on a non-model diff omits W1-19/W1-21. **R1-15:** while no nightly runs, a retrieval change gets a regression run only from this scoped hit@5, so approving T-6 early closes that gap |
| T-7 | PENDING | a helper import reaches only the suites that call the changed helper (a test-map exception first) | P1-2 | orchestrator (config) | `select_tests.py` on a W2-96-like diff omits W1-47 |
| T-8 | PENDING | the real code-graph daemon only in W1-16/W1-20 and on `codeintel` or tool-pin changes; the tool off PATH elsewhere; a daemon folder per session, cleaned | P1-9 (W2-56 S1) | test designer (acceptance helpers) + engineer (conftest) | daemon folders per session = 1; W1-16/W1-20 green |
| T-9 | PENDING | `shared_core` runs its import closure; unit tests by package folder; `close/**`, `check/**` out of `shared_core` | P1-9 (W2-115) | engineer + test designer (W2-66 cases) | single-ticket selections drop from 5,091–6,615 cases |
| T-10 | PENDING | the suites of features lifted here run in the nightly only (a route plus `select_tests.py`'s exclusion); **the owner also says whether they count in P1-12's full run** | P1-2 | orchestrator | `select_tests.py` excludes them; `nightly_only.txt` |
| T-11 | PENDING | CI off here (or scoped); the template's pre-commit empty, the git-notes record dropped | P1-2 (here) + P1-11 (template) | orchestrator; product-spec; test designer (W1-40) | W1-40 revised cases |
| T-12 | **APPROVED (DEC-1050 (5), wider: nothing scheduled runs until the refactoring is finished)** | the clean-tree and head-age checks out (the head's SHA recorded at start); 2 slots; built now, live when the owner restarts schedules | P1-4 | engineer + review | `test_nightly.sh` |
| T-13 | **APPROVED (DEC-1045)**, not to decide | `emg/noscan` merged at re-pin window 2; `scan: off` overrides the nightly (done `22fdf687`); W2-50 out of tickets' selections | P1-3 (iii) | owner's operator | the re-pin's check |

### B.2 Closes, landings and the queue
| id | status | the change | step | who | verified by |
|---|---|---|---|---|---|
| Q-1 | **APPROVED (DEC-1050 (4))** | each red compared once each way against **the head without the batch**; no nightly-baseline clone; 3 rounds only for load-sensitive cases; the nightly record lookup stays first; the same in `close_build.py` (or its attribution retired); W2-115 S4 re-worded in P1-8 | P1-0 (E1) | engineer + review | `test_merge_queue*`; a queue run's attribution phase in minutes, not hours |
| Q-2 | PENDING | `close: strict\|smart`, smart by default; the product's nightly, batch, fingerprint and evidence merged into W2-115; W2-117 merges | P1-9 (W2-115) | engineer + test designer | W1-30/W2-07 fixtures |
| Q-3 | PENDING | the rebuild/STORE_STALE and the context packet out of the close's defaults; W2-125 retires | P1-9 | same | W1-30 STORE_STALE and context cases revised |
| Q-4 | PENDING | checkpoint freshness lifted as a gate; `fresh-agent-reconstruction` a warning (after T-3) | P1-9 | same | W1-30, W1-26 |
| Q-5 | PENDING | `gov check` out of the close's pre-close gate (and out of `close_build.py` here, if R1 finds it there) | P1-9 (+ P1-4) | engineer | close runs without the 5.7 min step |
| Q-6 | PENDING | kept out of the product close (already gone here) | P1-9 | — | — |
| Q-7 | PENDING | escalation counts and reports, never blocks; no repair ticket; W2-41 retires | P1-9 | engineer + test designer | the suite to the nightly |
| Q-8 | PENDING | trailers not refusals; the family a warning (after T-3); `traceability.py` an on-demand report; `accepted_history` and `trailers_base` deleted here; W2-44 retires | P1-2 (here) + P1-9 | orchestrator; engineer | close runs without TRAILER_MISSING |
| Q-9 | PENDING | containment off the close's defaults; the floor: the reviewed diff, `core-mutation`, G-1's landing check | P1-9 | engineer | W2-72's suite to the nightly |
| Q-10 | PENDING (DEC-1050 (5) already settles that no accepted red carries into the refactored full run) | the ratchet lists off the product's defaults; frozen here; a plain load-sensitive list kept as a CTO-tool list (Q-1 needs it); W2-12, W2-78 retire | P1-2 + P1-9 | orchestrator; engineer | no new entries; Q-1 reads the CTO list |
| Q-11 | PENDING | the probe gate keeps only "a READY verdict from `verdict.py` exists" | P1-9 (W2-115) | engineer + test designer | W2-53's suite to the nightly |
| Q-12 | PENDING | the disk floor's product default ~10 GiB (est.), 100 GiB in this repository's config | P1-9 | engineer | W2-07 cases |
| Q-13 | PENDING | the queue holds and retries on infrastructure failure (never a ticket's red); land and close refusals go to the inbox | P1-4 | engineer + review | `test_merge_queue*` with a planted embedder hang |
| Q-14 | PENDING | the memory-arithmetic gate off unless configured | P1-9 (W2-20) | engineer | W2-20's re-scoped lines |

### B.3 The guard and the roles
| id | status | the change | step | who | verified by |
|---|---|---|---|---|---|
| G-1 | **APPROVED (DEC-1050 (12))** | **first** the landing check (every commit in the range touching `tests/acceptance/` carries `Role: independent-test-designer` or `Role: owner`, or the landing refuses, naming the commits); then rule 1 keeps Write/Edit and the Bash targets that resolve into `tests/acceptance/`; the "unresolvable + names the tests" heuristic and the code reading go | P1-0 (E1, E3) → P1-3 (i) | engineer + review; owner's ACT | the landing check's tests; E3's replay and planted cases |
| G-2 | **APPROVED (DEC-1050 (12))** | rule 5 the same; plus one line for leads: after a review, `git status --porcelain` is clean in the reviewed tree (in the lead template, P1-7) | P1-0 (E3) → P1-3 (i); P1-7 | engineer; product-spec | E3's replay |
| G-3 | PENDING (**the owner names the measured tickets**; DEC-1050 (6)'s "the rules must not refuse honest work again and again" bears on it) | `measures: tickets: [...]`, `roles` dropped from rule 2's hidden half | P1-2 | orchestrator | the 9 false "names given at run time" rows replayed |
| G-4 | PENDING | the product's default guard is the five rules; `guard.profile: five-rules \| full`; no ticket extends a lifted rule; W2-10, W2-09 retire, W2-42 deferred | P1-9 + P1-11 | engineer + test designer; product-spec (CIT-P) | the template's `settings.json`; the suites under `full` in the nightly |
| G-5 | PENDING | post-command containment off in the template's defaults | P1-11 | product-spec | the template |
| G-6 | PENDING | a plain freeze flag; the lift-refusal parsing and the mirror machinery off the defaults | P1-9 + P1-11 | engineer | W1-50 freeze files under `full` |
| G-7 | PENDING (needs G-4; G-1 and G-2 approved) | W2-42a re-scoped: the product's rules 1 and 5 let an unresolvable write through (~10 lines in `decide.py`); the 61-row corpus and 167 planted writes kept as a regression fixture; absorbs W2-08 S7 | P1-9 | engineer + test designer + review | the fixture |
| G-8 | PENDING | the hook's product imports frozen until the next re-pin; the checked pin recorded in the ACT | P1-3 (iii) | orchestrator | the re-pin checklist line |
| G-9 | PENDING | the live hook's tests (`test_guard_fix_3.py`, `guard4_check.py`) moved into `tests/unit/hooks/` | P1-4 | engineer | they run in `tests/unit` |
| G-10 | **APPROVED (DEC-1050 (6), wider: the harvest stops)**, done (`guard_harvest_s` 10^9, backup `.pre-dec1050`) | also `refusal_watch.sh` lifted; W2-119 retires (§C) | P1-0; P1-2 | orchestrator | no harvest line in the dispatcher's log |
| G-11 | **APPROVED (DEC-1050 (6))**, with the harvest: no hand verdicts and no cost field (DEC-958 amended by DEC-1050) | one line `guard_refusals: <n>` stays in returns, in the return template (P1-7) | P1-7 | product-spec | the template |
| G-12 | **REFUSED (DEC-1050 (11))**: review effort stays as it is | — | — | — | — |
| G-13 | PENDING | the SubagentStop hook blocks only role agents and briefed workers | P1-11 (kernel hook) | product-spec/engineer; W1-29 cases | W1-29 |
| G-14 | PENDING (**the owner confirms** that `gov accept` and the two worktrees meet the aim's "reads") | none, or a sentence in the aim | P1-1 | owner | — |

### B.4 Memory and context
| id | status | the change | step | who | verified by |
|---|---|---|---|---|---|
| M-1 | PENDING (**W2-04: the owner once**, DEC-1010's cap) | the per-span count and hash kept; the ceiling a warning, never `CONTEXT_OVER_CEILING`; brief step 6a and DEC-1027 H's trimming lifted; W2-125 retires | P1-2 (brief) + P1-9 (W2-04) | orchestrator; W2-04's test designer (`Rewrite-Reason:`) | W2-04's cases |
| M-2 | PENDING | SessionStart injects the ticket's `sources` ids (no model); RESUME HERE kept | P1-11 (kernel hook) | product-spec/engineer | W1-29/W1-31 |
| M-3 | PENDING | incremental or seeded refresh; a full rebuild only when the store's code changed | P1-10 (after the memory landings) | orchestrator (brief/template) | lead rebuilds measured |
| M-4 | PENDING | tests lexical only (or what W2-61's measure picks); close, checkpoint and probe records not embedded; a close record holds a summary and a path | P1-10 / P1-9 | research (measure) + engineer | W2-61's measure before and after |
| M-5 | PENDING | the register split: frozen archive plus a short live file; ids still resolve | P1-9 | product-spec + test designer (W1-10, W2-03, W2-55 cases) | those cases |
| M-6 | PENDING as a row; its work is DEC-1039 (2)'s approved code refactor | the four edges untangled | P1-6 | engineer + review | `closure.py` re-run |

### B.5 Briefs, records and ceremony
| id | status | the change | step | who | verified by |
|---|---|---|---|---|---|
| R-1 | **REFUSED as written (DEC-1050 (7))**: no cut; better templates instead. R2 corrects the premise: the "3 %" was the decision list (R2-1), not the brief | the lead brief rebuilt as per-run-kind templates plus scripts (R2-4, R2-6, R2-9) | P1-7, P1-4 | product-spec; engineer (scripts) | P1-7's pilot measure |
| R-2 | **REFUSED as written (DEC-1050 (7))** | the template decides what a lead reads | P1-7 | — | — |
| R-3 | **REFUSED as written (DEC-1050 (7))**. R2-12 shows the stale and contradictory lines are still obeyed and cost time (16 gap lines, 169 min), and the templates replace them with correct lines. **For the owner to confirm** within P1-7 | — | P1-7 | — | — |
| R-4 | **REFUSED as written (DEC-1050 (7))**; the rule exists only for the scan DEC-1045 switched off: **ask the owner** whether the template drops it under DEC-1045 | — | P1-7 | — | — |
| R-5 | **REFUSED as written (DEC-1050 (7))** | — | P1-7 | — | — |
| R-6 | PENDING | the committed `gov checkpoint` record per round lifted; the prose checkpoint, PreCompact and SessionStart kept; DEC-511 marked lifted | P1-2 | orchestrator | brief diff |
| R-7 | PENDING | the Stop hook's automatic checkpoint unregistered here; product default off | P1-3 (ii) | owner's operator | the ACT's check |
| R-8 | **APPROVED (DEC-1050 (9))**, "not a priority" | the register for owner decisions and standing rules; a delegated choice is a line in the ticket's file or close record plus a daily list | P1-2; MR-6 in P1-11 | orchestrator | the next delegated choice is not a register entry |
| R-9 | PENDING (lifting the prompt's §0 is a prompt cut: DEC-1050 (10) asks for evidence first) | one DECISIONS-IN-FORCE list (≤ ~8 KB); the briefs point to it | P1-2 | orchestrator | one list |
| R-10 | PENDING | one decision-record commit per batch; the sync hourly and at session end; `--main` lifted | P1-4 (+ prompt) | engineer; orchestrator | `sync_context.py` test |
| R-11 | **APPROVED (DEC-1050 (9))**, "not a priority" | pings only when work waits on the owner; two digests a day; the short package form | P1-2 (+ `ping.sh` in P1-4) | orchestrator | `pings.log` per day |
| R-12 | PENDING | `Task:` and `Role:` kept; `Implements:` optional; the two-commit rule lifted | P1-2 | orchestrator | brief diff |
| R-13 | PENDING | the status block read from the head of `dispatch/status.txt` | P1-4 | engineer | `status_block.py` |

### B.6 The CTO's tools and practices
| id | status | the change | step | who | verified by |
|---|---|---|---|---|---|
| O-1 | **REFUSED (DEC-1050 (10))** | — | — | — | — |
| O-2 | **REFUSED (DEC-1050 (10))** | — | — | — | — |
| O-3 | PENDING (DEC-1050 (10)'s measure: productivity and drift, not tokens) | hand over at ~300k context | P1-2 | orchestrator | — |
| O-4 | **REFUSED (DEC-1050 (10))** | — | — | — | — |
| O-5 | PENDING | one stall net (the dispatcher's stale line and the sentinel) and the quiet-hours hook; the Stop-hook waiter check, `cto-standby.txt`, the heartbeat rituals and the scratch `deadman.py` lifted | P1-3 (ii) + P1-4 | owner's operator; engineer | the ACT's check |
| O-6 | PENDING | ACTs for installs, new services and crontab; standing approval by class for restarts from committed configs | P1-2 | owner (the class list) | DECISIONS-IN-FORCE |
| O-7 | **APPROVED (DEC-1050 (8), wider)** | `rm` free; refused only for the catastrophic (the repository's root, its `.git`, the main tree's tracked files, anything outside the project and its scratch) | P1-0 (E3) → P1-3 (i) | engineer; owner's operator | E3's catastrophic cases; prompts in the permission log |
| O-8 | PENDING | backups and dead copies deleted (the record branch keeps them); one `register_add.py` | P1-4 (after E1's promotion) | orchestrator/engineer | a list of what was deleted |
| O-9 | PENDING | `heavy_slot.sh`: FIFO in each class, aging after ~20 min, `log/heavy-slot.jsonl` | P1-4 | engineer + review | `test_heavy_slot.sh` (4 new cases) |
| O-10 | **APPROVED (DEC-1050 (5), wider)** | `gate_check.py` lifted everywhere; the nightly asks the Balancer/slots | P1-4 (with T-12) | engineer + review | `test_nightly.sh` gate cases |
| O-11 | PENDING | DEC-1012 scoped to rules that pass DEC-1010's test; DEC-1003 weekly, after a week in use | P1-2 | owner/orchestrator | one register entry |
| O-12 | PENDING | kept; a W2-121 line for deriving the root | P1-8 | orchestrator | W2-121's card |
| O-13 | PENDING | branches and worktrees pruned after the landings, from a list for the owner | P1-13 | orchestrator | the list |
| O-A1 | PENDING (P1-LIFT-1's addendum) | the dispatcher's slots rule lifted; the Load Balancer's forecast is the admission | P1-4 | engineer + review | `test_dispatcher.py`/`test_balancer.py` with the 22:17 case |

### B.7 The Contract, the Charter and the repository
| id | status | the change | step | who | verified by |
|---|---|---|---|---|---|
| K-1 | PENDING | one re-baseline, last (DEC-105 (c)) | P1-11 | product-spec + review + owner | K-3 |
| K-2 | PENDING | W2-109 retired into K-1 | P1-8 | orchestrator | its close reason |
| K-3 | PENDING | `validate_w2.py` advisory until re-run after K-1 and the ticket edits | P1-8, P1-11 | orchestrator | its run |
| K-4 | PENDING | two orchestration-skill lines edited after G-4; the duplicate `skills/superpowers/` dropped | P1-11 | product-spec | CIT-P |
| E-1 | **APPROVED (DEC-1050)**: keep this repository | — | — | — | — |

### B.8 The WBS and the tickets
| id | status | the change | step |
|---|---|---|---|
| W-1 | PENDING | 20 Wave-3 or parked tickets moved out of the count | P1-8 |
| W-2 | PENDING | one home per rule (12 pairs or triples; DEC-1010 restated in five tickets) | P1-8 |
| W-3 | PENDING | process boilerplate out of KPI lines | P1-8 |
| W-4 | PENDING | lines that cannot pass re-worded or retired | P1-8 |
| W-5 | PENDING (K9 is the owner's) | W2-27's deps re-derived; K9 encoded | P1-8 |
| W-6 | PENDING | status follows work (W2-56 to open, W2-109 retired, W2-20 rebuilt from the tools) | P1-8 |
| W-7 | PENDING (W2-04: the owner once) | land what is built; no new rounds for W2-05, W2-96, W2-55 | P1-1, P1-8 |
| W-8 | PENDING | W2-24 and W2-25 retired; exit criterion 5 re-worded (owner) | P1-8 |
| W-9 | PENDING (DEC-1039 (4) already orders it) | the six formal closes | P1-13 |
| W-10 | PENDING | the plan's contradictions follow the parking list | P1-8 |

**Tally (89 ids):**
- **Approved by DEC-1050: 14.** T-1, T-4, T-5, T-12, Q-1, G-1, G-2, G-10, G-11, R-8, R-11, O-7 and O-10 (13 of the
  twelve items' 22 ids), plus E-1.
- **Refused by DEC-1050: 9.** R-1 to R-5, O-1, O-2, O-4 and G-12.
- **Approved earlier (DEC-1045): 1.** T-13.
- **Pending: 65.** The 64 other table ids, plus O-A1.
- **New from R1:** R1-21 is pending; R1-22 is a correction inside the approved T-4. Both are in B.1, outside the count of 89.

---

## C. The ticket fates (the list's §5, all PENDING the owner; the notes say where an approved row already points)

| fate | n | lines | tickets | notes from decided rows |
|---|---:|---:|---|---|
| Keep | 21 | 160 | W2-00, W2-11, W2-13, W2-23, W2-28, W2-29, W2-30, W2-32, W2-52, W2-60a, W2-61h, W2-81, W2-90b, W2-91, W2-92, W2-93, W2-94, W2-105, W2-110, W2-116, W2-124 | W2-60a S10: "switchable off" depended on G-12, which was refused, so **S10 stays as is** |
| Re-scope | 23 | 245 | W2-04, W2-11b, W2-15b, W2-20, W2-27, W2-33, W2-37, W2-40, W2-42a, W2-45, W2-46, W2-47, W2-55, W2-56, W2-60b, W2-82, W2-88, W2-98, W2-104, W2-113, W2-115, W2-120, W2-121 | W2-115 S4 "against the head without the batch" follows **Q-1 (approved)**; W2-42a's re-scope needs G-4 (pending); G-1/G-2 are approved |
| Merge | 11 | 75 | W1-01b, W2-66b, W2-90c → P1-12's red fixes; W2-06 → W2-116, W2-122; W2-15a → W2-15b; W2-21 → W2-121, W2-33, W2-60a, W2-56; W2-99 → `discovery` skill; W2-111 → P1-5; W2-117 → W2-115; W2-118 → W2-121; W2-127 → W2-56 | **W2-32 depends on W2-15a** (`.tickets`): re-point it to W2-15b in P1-8 |
| Close formally | 6 | 48 | W2-05, W2-96, W2-112, W2-122, W2-123, W2-126 | DEC-1039 (4) |
| Retire | 22 | 131 | W2-08, W2-09, W2-10, W2-12, W2-14, W2-22, W2-24, W2-25, W2-31, W2-38, W2-39, W2-41, W2-43, W2-44, W2-78, W2-83a, W2-83b, W2-102, W2-103, W2-109, W2-119, W2-125 | W2-119 follows **G-10 (approved, harvest stopped)**; W2-78 follows **T-4 (approved, done as config)** |
| Wave 3 | 9 | 57 | W2-17, W2-18, W2-19, W2-34, W2-35, W2-36, W2-42, W2-100, W2-101 | — |
| total | 92 | 716 | | |

**New ticket proposed:** W2-128, the templates (P1-7), STANDARD, product-spec, with R3's KPI lines (option: fold them into W2-11 and W2-33 instead; not recommended, because W2-11 lands as built).

---

## D. The approved test refactor and the code tidy-up, in detail

**Test refactor (P1-5).** These are the rows DEC-1040 (1) approved, in the order the designer does them:
1. M1 (W2-54's two green-here cases → one; −900 to −1,800 s a full run, est.) together with E2's T-4 change, and M1b at the designer's judgement.
2. D1 (−28 W1-01 interim cases; Failure 3 retired as spent, like DEC-925), D2, D3, M2 (and M3 if the designer wants it).
3. R1 (W2-66 `test_inputs`), R2 (W1-26 exit-0 fixture made small), R3 (W1-35 ceiling clause), R4 (`HIT_AT_5_PASS_LINE` 80 → 85), R5 (lexical chunking).
4. M9 (`test_emg_query_device.py` into `test_semantic_cpu_embedder.py`).
5. Forced by the lifts: W2-66 `test_w2_66_live_test_map.py` (T-4); W2-111's load-failing latency cases (T-6, if approved).

**R4 risk:** raising the bar to 85 may turn W1-19/W1-21 red if memory sits between 80 and 85. That red is a real
finding (DEC-833), not a refactor error, and it goes to W2-32. Later (after the resume, as time allows): M4 (72 families
into parametrised tables, ~1,070 lines), M5, M6 (162 helper groups, ~1,500 lines), M7. Rule for every deletion and
merge: the KPI line it covered is named, with the case that keeps it (inventory §5). The reviewer checks exactly that
map. Totals: −32 to −35 cases, about −2,700 lines, 3 to 8 % of case time.

**Code tidy-up (P1-6).** Item 1 is E-2's four edges (listed in §A), so memory's import closure stops pulling in `close`,
`guard` and `decisions.checker`. Item 2 is §6b, in this order:
1. One frontmatter parser: five byte-identical copies in `src/gov/check/{mutation,authority,claims,runner,graph}.py`, plus `audit_validator`/`skill_validator`. Then `schema.py`, `store/loader.py`, `close/traceability.py`, `adopt/project.py`, `tasks/tickets.py`; **not** `guard/decide.py` (the hot path) unless it is measured.
2. `_ids` (×3), SQLite `_open` (×2), sha256 (×3).
3. `junit_rel` deleted.
4. The git wrappers merged only where the return types match (`store/loader._git` and `retrieval/lexical._git`), never the guard's copies.

`synthesis.py` stays (DEC-953). The CTO tools' archival (§6b item 8) is O-8 (P1-4). It does not conflict with P1-9, as long as P1-6 lands before W2-115 and W2-42a resume.

---

## E. The templates (P1-7) and the WBS refactor (P1-8), in brief
- **Templates:** R3 designs them and R2 supplies the evidence; this plan only places them. The project half (the lead
  brief rebuilt from the lead template by `build_lead_brief.py`, and the worker briefs) is the orchestrator's and
  product-spec's, with no CIT-P. The kernel half (role files, skills, the return form) goes through the CIT-P. The test that
  agents read and follow the templates is R2's counts, re-run on the first three resumed leads. If the brief-gap lines
  and guard refusals per lead do not fall, the template is revised before more leads start.
- **WBS refactor:** the list for the owner first (DEC-1039 (3b)):
  - per ticket: its fate, its KPI lines met (with the evidence path) or moved (to the absorbing ticket's line);
  - W2-27's deps re-derived: remove 13 and add 7 (the list's §5); cut W2-121 → W2-118; resolve W2-117's `after-examin` tag; re-point W2-32 → W2-15b;
  - K9 as W2-27's deps;
  - the duplicate lines (W-2), the boilerplate (W-3), the lines that cannot pass (W-4) and the contradictions (W-10) edited;
  - `validate_w2.py` re-run.

  Then the edits go in, in one commit per batch (R-10 if approved), and an auditor checks that all 716 lines are accounted for.

---

## F. Timeline (est.) and the owner's time

| date (est.) | steps | the owner |
|---|---|---|
| 11-02 night | P1-0: E1, E2, E3 and their reviews; R1–R3; the memory landings (W2-126 to re-merge after its conflict; W2-112's lead) | — |
| 11-03 | P1-1 decisions; P1-2 lifts (with the `core-mutation` ticket fix); E2 corrected (R1-22), then landed; E1 promoted; P1-3 (i) ACT-GUARD-FIX-4; P1-4 (R1-21, the three scripts) and P1-5 start; P1-7 drafting from R3 and R2 | 2–3 h (rows, fates, K9) + 15 min (ACT) |
| 11-04 | P1-4, P1-5 done and reviewed; P1-6 (if the memory branches have landed); P1-8's list; P1-3 (ii); P1-3 (iii) re-pin window 2 | ~45 min (WBS list) + 15 min (ACT) + 30–60 min (re-pin) |
| 11-05 | P1-6 reviewed; P1-7's three templates reviewed (CIT-P for the kernel half); P1-12 run 1 (~5.4 h) on the owner's word | ~30 min (templates) + the word |
| 11-06 | the reds fixed; P1-12 run 2 | — |
| 11-07 | green (est.; range 11-06 to 11-09) → P1-13: the lift, the six formal closes, the ready list | ~15 min |
| 11-07 → 11-14 | P1-14: the tickets to EXAMIN's copy; P1-9 and P1-11 inside them | packages as they come |

The owner's total over the refactoring is 4 to 6 h (est., the sum above). Machine: 2 to 3 full runs of ~5.4 h, plus the
scoped runs of P1-5 and P1-6 in heavy slots. Inside the Load Balancer, P1-12 does not overlap a re-pin's rebuild.

---

## G. The new estimate for EXAMIN's copy: **centre 2026-11-14, range 2026-11-12 to 2026-11-19 (est.)**

**What stands before the copy, once the fates and K9 are as proposed.** This is W2-27's re-derived closure, computed
from `.tickets` with `closure.py`, leaving out the tickets that are merged, retired or not gating. It comes to 31
tickets:
- **4 formal closes:** W2-112, W2-122, W2-123, W2-126.
- **13 in flight and built, or partly built:** W2-04, W2-11, W2-13, W2-52, W2-55, W2-60a, W2-61h, W2-81, W2-90b, W2-91, W2-92, W2-105, W2-110. At 1 to 1.5 runs each (median run 3.52 h), that is 46 to 69 lead-h.
- **2 restarted:** W2-56 (built nothing; absorbs W2-127 and W2-21 S5–S8), 17 to 20 h. W2-20 (rebuilt from the tools), 9 to 14 h.
- **12 open:**

  | ticket | estimate | basis |
  |---|---|---|
  | W2-115 | 26–34 h | scaled like W2-81 |
  | W2-121 | 17–20 h | |
  | W2-15b + W2-15a | 17–20 h | |
  | W2-88 | 20–26 h | the plan's figure |
  | W2-23 | 13.6 h | |
  | W2-32, W2-33, W2-60b, W2-93, W2-94, W2-98, W2-124 | 9.2 h each | |

**Volume.** In all, 230 to 281 lead-h at the plan's medians. Those medians include the old gate waits. The approved
lifts take out a share of each run:
- the full `gov check`: 15.5 to 24 min a run;
- the nightly-routed serial cases: about 5 h over 3 days;
- W2-54's 870 s per scoped run;
- attribution hours in the queue.

That share is about 20 to 25 % (est.: about 1 h of a 3.5 h median run). That leaves **175 to 225 lead-h**. Capacity
under the Load Balancer is 2 to 3 leads (DEC-1039 (1b)) at ~16 to 20 h a day, so **40 to 55 lead-h a day** (est.;
measured 80 to 110 a day on 10-30 to 11-01 with more leads). That is **3.2 to 5.6 days**.

**Chains (the longest decide):**
- W2-55 → W2-115 → W2-27: about 2.5 to 3 days, with W2-115 the largest ticket.
- W2-04 (the owner once) → W2-15b → W2-32 (85 % or escalate) → W2-27: about 3 days.
- W2-81 → W2-88: 1.5 to 2 days.
- W2-20 → W2-121: about 1.5 days.

On top of the chains comes the owner's answer time on packages: 61 % of returns ended in PACKAGES (PLAN-GROWTH-1).
That adds about 0.5 to 1 day (est.).

**So:** resume about 11-07, plus 4 to 6 working days, puts the copy's start on **11-12 to 11-14**. The range runs to
**11-19** if any of these happen:
- P1-12 needs a third run, or more red-fix days. The 11-02 nightly had 32 reds. Now none may be carried as accepted, and the 11 install and hook reds go to W2-90c's merge.
- Memory misses 85 % at W2-32.
- The owner's row decisions slip past 11-03.

**Against the earlier figures:**
- The 11-01 estimate (11-14, range 11-12 to 11-17) assumed 44 tickets, ~375 lead-h and more parallel leads.
- The freeze costs about 4 to 5 days.
- The fates and lifts give back about 150 to 200 lead-h (est.): about 3 to 4 days at today's capacity.
- The net is about the same centre, with a wider range. **The old target, 11-18, holds at the centre and is at risk at the top of the range.**
- **Option B** (W2-45 and W2-115's switches before the full run) adds about 2 to 3 days to the resume, but takes W2-115 off the chain afterwards. The net is about +1 day: centre about 11-15.

---

## H. How to update this plan after the owner decides
1. Change the status cell of each row in §B. Use APPROVED (DEC-10xx), REFUSED (DEC-10xx), or DEFERRED with a reason.
2. An approved row joins the step its row names. A refused row leaves that step's list in §A. If a step's list empties, mark the step "not needed".
3. The ticket fates (§C): a decided fate goes into P1-8's list. If a fate differs, re-run `/tmp/gov-os-inv-P1/closure.py` with the new remove list, and update §G's ticket counts and estimate.
4. Option A or B moves P1-9 before or after P1-12. Change the order line under §A and §F's dates.
5. Re-estimate EXAMIN's date in §G with old and new figures side by side (the standing rule at the register's line 11535: "re-estimated weekly, with old and new figures side by side").

---

## Evidence
1. **The row count.** `grep -cE "^\| (T|Q|G|M|R|O|K|W)-[0-9]+ " INVESTIGATION-1-COMBINED.md` gives 87 ids: T 13, Q 14, G 14, M 6, R 13, O 13, K 4, W 10.
   - Add O-A1 (the addendum) and E-1 (the repository question): 89.
   - The twelve items decided 22 ids. T-13 was decided earlier (DEC-1045). With E-1 decided too, **65 remain** (64 table ids plus O-A1).
   - DEC-1050 and P1-LIFT-1 say "75 rows" and "63 remaining". Those figures appear to count the twelve items as 12 rows and to leave out W-rows, or something like it. This plan lists every id, so nothing is lost either way.
2. **Lead throughput.** `python3 -I /tmp/gov-os-inv-P1/leads.py .gov-runtime/scratch/orchestrator/log` gives lead-hours a day by the files' modification date:
   - 10-30: 110.2 h (16 runs, $137);
   - 10-31: 93.1 h (25 runs, $203);
   - 11-01: 79.8 h (31 runs, $207);
   - 11-02: 33.3 h (14 runs, the emergency).
3. **W2-27's closure.** `python3 -I /tmp/gov-os-inv-P1/deps.py .tickets W2-27` lists 46 deps: 12 closed, 17 in progress, 17 open. `closure.py`, run with the list's removals (W2-05, W2-96, W2-06, W2-21, W2-99, W2-100, W2-101, W2-102, W2-103, W2-109, W2-83a, W2-104, W2-82, W2-118, W2-117) and additions (W2-115, W2-121, W2-124, W2-112, W2-122, W2-123, W2-126), gives 31 non-closed tickets in the transitive closure. That count includes W2-13, W2-15a and W2-55, which come in through W2-15a's and W2-115's deps.
4. **The plan's medians.** From `PLAN-W2-DEC953.md` §2.0:
   - L 4.3 h, S 9.2 h, F 13.6 h;
   - a run 3.52 h (median), 2.7 runs per ticket;
   - large tickets scaled by LOC (W2-81, 1,200 LOC: 26 to 30 h).
5. **The last landing.** `log/land-dispatch-20261102-222503.out`: "merged W2-123, W2-122 onto b60ff1120424: 35a851b36c6d"; "EJECTED W2-126: conflict".
6. **The ratchet lists.** In `governance/project/path-map.yaml`: `accepted_reds: []`, `load_sensitive` 24 entries, `acceptance_exemptions` 2, `accepted_history` 47.
7. **The full run's cost.** `P1-NIGHTLY-2026-11-02.md`: the run took 19,448 s against an estimate of 11,176 s, with 32 reds in 8 groups.
8. **The earlier EXAMIN estimates.** `P1-MORNING-2026-11-01.md:47` (14 Nov, range 12 to 17); `PLAN-GROWTH-1.md` §5 (11-11 to 11-16, centre 11-13); the register's target of 2026-11-18 (line 11535).
9. **R1 and R2** (folded in at 23:10, from `drafts/LIFT-1/R1-GOVCHECK.md` and `drafts/LIFT-1/R2-BRIEFS.md`):
   - **R1:** `merge_queue.py`, `land.py`, `close_build.py` and `nightly.sh` run pytest only; `gov check` runs only in the product's strict `gov close` (`src/gov/close/command.py:1145`), and nothing here has used that since 28 Oct.
   - **R1:** since 25 Oct the CTO committed directly to `w2/integrate`: 270 commits to `.tickets/`, 124 to the register, 7 to the path map and 8 to `.claude/`.
   - **R1:** `core-mutation` is red from `e08717ec` (DAEO-tgk2) and `1b3ba635` (DAEO-a3u2). W1-26's probe-record case caught the CTO's own record fault twice (fixed by `b60ff112`).
   - **R2:** across 159 lead transcripts, 4,528 wait calls (24.5 % of all calls), 2,135 ceremony calls (11.6 %), 343 hand-written verify wrappers in 117 sessions, and 218 harness permission denials in 110 logs.
   - **R2:** named commands were run by 83–100 % of the leads whose brief named them. The share of sessions with a guard refusal fell from 68 % to 17 % after the command forms were added (29 Oct).
