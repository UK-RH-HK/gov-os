---
id: DAEO-0cd2
wbs_id: W2-187
external-ref: W2-187
title: "The standing hidden set: each repository's memory judged end to end every week on the same questions at 95 %, counts only, with a monthly fresh set as the check against fitting, a weekly maintenance pass, and the audit's state per repository (MEMORY-AUDIT G1, G2, G3, G5 and G4's code)"
type: task
class: implementation
role: engineer
profile: FULL
status: in_progress
state_class: AUTHORITATIVE
priority: 1
created: 2026-11-14
deps: [DAEO-f58b, DAEO-rmhj]
allowed_paths:
- src/gov/memaudit/**
- src/gov/adopt/memory_sets.py
- governance/project/orchestration/tools/memaudit_cron.sh
- tests/unit/memaudit/**
- tests/unit/adopt/test_w2_187*
- tests/acceptance/W2-170/test_w2_170_s3_declare.py
- tests/acceptance/W2-170/w2_170_world.py
- tests/acceptance/W2-171/test_w2_171_s3_judge.py
- tests/acceptance/W2-171/w2_171_world.py
- tests/acceptance/W2-171/w2_171_scenario.py
- tests/acceptance/W2-171/test_w2_171_cli_layout_ledger.py
- tests/acceptance/W2-171/test_w2_171_s5_misses_f2.py
- tests/acceptance/W2-172/test_w2_172_s7_digest.py
- tests/acceptance/W2-172/w2_172_world.py
- tests/acceptance/W2-172/w2_172_git.py
- docs/changes/W2-187-evidence.md
- docs/probes/DAEO-0cd2/**
reads:
- .gov-runtime/scratch/orchestrator/drafts/memory-scope-20261113/MEMORY-AUDIT.md
- governance/project/orchestration/packages/MEMORY-AUDIT-P1.md
- governance/project/orchestration/packages/MEMORY-AUDIT-1.md
- governance/project/orchestration/packages/LIFT-1/FRESH-80-1.md
- governance/project/orchestration/packages/LIFT-1/E3-RESULT.md
- governance/project/orchestration/packages/LIFT-1/E3-SA-RESULT.md
- src/gov/retrieval/measure.py
- src/gov/rebuild/integration.py
- src/gov/links/command.py
- src/gov/adopt/**
- tests/acceptance/W2-170/**
- tests/acceptance/W2-171/**
- tests/acceptance/W2-172/**
- tests/acceptance/W2-173/**
- tests/acceptance/W2-88/**
needs:
- src/gov/rebuild/integration.py
- src/gov/retrieval/retrieve.py
waits_on:
- ref: DAEO-f58b
  reason: 'the maintenance pass brings the store to the main line''s head through W2-116''s double-buffered integration store (closed)'
- ref: DAEO-rmhj
  reason: 'the standing run checks each search result''s store commit (W2-138''s field) against the declared store; the maintenance pass reads it'
est_loc: 700
kpis:
  success:
  - 'S1 A standing set: `python3 -m gov.memaudit standing declare --set <name> --repo <dir>` records one standing set for the repository: its name, its digest (`LC_ALL=C sha256sum *.yaml | sha256sum` over the kept questions), n with the nonexistent-id questions apart, the sha256 of the writer''s and checker''s briefs, and the commit it was written at. A set whose questions were ever written to a `misses.jsonl` or read by an auditor is refused (`STANDING_SPENT`); an adopted repository''s Wave 0 verdict set is accepted once its `USED` marker and its counts-only result record exist (W2-88 S13, S16). One standing set is live per repository; a second is refused until the first is retired [DEC-1179 (1), DEC-1176 (1), DEC-1098 (1)] Verify: planted sets: a new set is recorded with each field; a set with a planted `misses.jsonl` line is refused with `STANDING_SPENT`; a planted Wave 0 verdict set with `USED` and its record is accepted; a second live set is refused'
  - 'S2 One judged run a week: a standing run writes `runs/<set>/<ISO year>-W<week>/DECLARATION.json` and then `USED`, before any search; a second judged run of the same set in the same ISO week exits 3 and writes nothing. A run stopped by the fault rule (FRESH-80-1 §3.5, `STOPPED <cause>`) before its reader run started may start once more that week; a run whose reader run started never runs again [DEC-1179 (1), DEC-1097 (1)(g)] Verify: planted runs: the file times and the ledger line show DECLARATION.json before USED before the first search; a second run the same week exits 3 with the tree byte-identical; a planted STOPPED before the reader run allows one restart and a second is refused'
  - 'S3 The same method as Gov OS''s memory: a standing run uses the fresh 80''s judged path unchanged: the store at the audit commit with the standard (the 0.6B through the one shared reranker, the pool on, the 6,000-token bundle widened to sections); each question''s first bundle from `gov.retrieval.measure`; `judge`''s reader run as built (the pinned `prompts.py`, the reader, the cap, the A2 cut judged, A1 and A3 as data); the named grader with the second grader''s agreement; the measure''s matcher with source families. Every search result''s store commit (W2-138) equal to the declared store''s commit, else that attempt is a fault [DEC-1179 (1), DEC-1097 (1)(a), DEC-1098 (1), DEC-1092 (1)] Verify: `tests/unit/memaudit/test_prompts.py` passes unchanged; a planted standing run calls the same reader, grader and matcher functions as a fresh run (one shared code path, asserted by a spy); a planted result from another store commit makes the attempt a fault'
  - 'S4 Counts only: a standing run writes no `misses.jsonl` and launches no auditor. Only counts leave its run folder: right end to end, wrong claims, not found, the misses by outcome (wrong, incomplete, not found) and by the first gold place''s rank in the first bundle (1-5, 6-20, absent), the questions dropped by the anchor check, and the figures beside (hit@5, gold in the first bundle, A1 against A2 with exact McNemar). No question id, question, gold, answer or citation of the standing set is printed, logged, written to `FIGURES.json`, `HISTORY.jsonl`, `AUDITS.log` or the digest block, or written outside its run folder (mode 0700) [DEC-1179 (2), DEC-1101 (2), DEC-1074 (1)] Verify: a planted standing run with five planted misses whose ids and texts are unique strings: no planted string appears in stdout, stderr, FIGURES.json, HISTORY.jsonl, AUDITS.log, the digest block or any file outside the run folder; no misses.jsonl exists; no auditor launch event is in the ledger'
  - 'S5 The bar at 95 %: `declare.bar(n)` gives `need_right = ceil(95 n / 100)` and `max_wrong = floor(5 n / 100)`; a verdict passes when right end to end at A2 reaches `need_right` (wrong claims stay reported and checked). It applies to standing and fresh runs alike, and the declaration''s rounding text says so. On 80 judged that is 76, on 79 it is 76, on 40 it is 38 [DEC-1179 (2), DEC-1097 (1)(d) as carried forward, DEC-957] Verify: unit cases n = 40, 79, 80 give 38, 76, 76; a planted run with right = need_right - 1 is a miss and with right = need_right a pass; the digest''s bar line prints the new figure; the revised W2-170, W2-171 and W2-172 cases pass, and W2-88''s S15 bar case (which reads W2-170''s helper `bar`) passes unedited'
  - 'S6 Staleness by count: before each standing run the pre-flight checks each question''s gold anchors at the audit commit; a question whose anchor no longer resolves, or whose nonexistent id now exists, is dropped from that week''s n and counted (`dropped k`); nothing in the set is edited. Fewer than 70 live questions prints `STANDING_THIN <live>` in the digest block and asks for a replacement [DEC-1179 (2), DEC-1097 (1)(f)] Verify: a planted set of 80 with 3 broken anchors: n is 77 and `dropped 3` is printed with no id; the set''s digest is unchanged after the run; a planted set with 69 live questions prints STANDING_THIN 69'
  - 'S7 The monthly check against fitting: at each fresh run the tool compares the fresh set''s right end to end per cent F with S, the mean of the standing set''s last four weekly figures; S - F of 5 points or more writes `STANDING_FITTED` in HISTORY.jsonl and the digest block, retires the standing set (no further standing run on it; it joins the pool as a diagnostic set, counts only) and asks for the writer''s replacement; F - S of 5 points or more writes `STANDING_STALE` and asks for the checker''s staleness pass; with fewer than four weekly figures the check prints `drift: not yet (k of 4)` [DEC-1179 (3), DEC-1074 (4)] Verify: planted histories: S 96, F 90 retires the set and a later standing run on it is refused; S 90, F 96 prints STANDING_STALE; S 95, F 92 prints no flag; two weekly figures print `drift: not yet (2 of 4)`'
  - 'S8 The two cadences and below 95 %: the standing set''s cadence is W2-172 S5''s computed rule, unchanged (weekly while active, monthly once stable, back to weekly at once on a miss, a retrieval change, churn of 10 % or more or a pool regression); the fresh set is due on the first Monday 28 days or more after the last fresh run. A standing miss is a HISTORY line `miss` with its counts; the fresh set is then due at the next Monday and every Monday until a standing run passes again (then every 28 days); the maintenance pass (S10) runs at once after the miss in the same cycle; the digest block carries a `P1 memory below 95 %` line with the counts by class. Two consecutive standing misses, or one miss 5 points or more below the last passing figure, write `MEMORY_REPAIR open` in HISTORY.jsonl, and `gov.memaudit status --repair` exits 1 while it is open and 0 once a later standing run passes or the owner''s decision id is given with `--residual DEC-<n>` [DEC-1179 (4), (5), DEC-1125 (2)] Verify: `tests/acceptance/W2-172/test_w2_172_s5_due.py` passes unchanged for the standing set; a planted fresh history 27 days old is not due and 28 days old is due on the Monday; planted histories: one miss makes the fresh set due next Monday and puts the P1 line in the digest; pass, miss, miss opens the repair; pass at 96 then miss at 90 opens it; `status --repair` exits 1, then 0 after a planted pass or `--residual DEC-1`'
  - 'S9 State per repository: the runs folder is `<runs>/indep/memaudit/<key>/` with `<key>` the repository''s directory name, a hyphen and the first 8 hex of the sha256 of its real path, so two repositories on one machine keep separate `AUDITS.log`, `HISTORY.jsonl` and `STARTS.log`. The retrieval change that sends an audit back to weekly is, for any repository, a change of the gov pin, of the repository''s `governance/project/retrieval.yaml` digest or of its path map''s digest, and for Gov OS also its six retrieval globs. `pool-import --sets <name>...` seeds the pool from that repository''s own sets root; with no `--sets` on Gov OS it imports Gov OS''s 79 and 138 as today [DEC-1179 (5), DEC-1101 (1), DEC-1125 (2)] Verify: two planted repositories on one runs folder write to two keys and neither reads the other''s history; a planted pin change on an adopted repository is a retrieval change and a change under `src/gov/retrieval/` of Gov OS is not, for it; `pool-import --sets a b` imports exactly those sets'
  - 'S10 One weekly maintenance pass before each standing run, `python3 -m gov.memaudit maintain --repo <dir>`: (1) the integration store at the main line''s head, else one refresh by W2-116''s `gov rebuild --integration`, a failed build leaving the last good store in service and named; (2) the store''s layout current, else one `gov rebuild`; (3) `gov links --since <the last pass''s commit>`: the count of new findings; (4) the count of tracked paths the path map indexes but the store holds no chunk of; (5) the standing and fresh runs'' reader `not found` answers and second searches, counted; (6) the list of gold questions whose cited lines changed at the audit commit (W2-61h S4''s list, with N2 (b), DEC-1180 (1): a heading-cited source whose section text (from its heading line to the next heading of the same or a higher level, or the end of the file) differs between the source''s own commit and the head is listed too, though its heading is still found; question id and entry number only, never a question, answer or path) handed to the walled writer''s request for re-anchoring or rewording, counted. It prints six counts in the digest block, never fails or delays the audit, and never changes one of the standard''s four settings [DEC-1179 (6), DEC-1178 (1), DEC-1072 (1), DEC-1101 (1), DEC-1096] Verify: a planted repository with a store 3 commits behind is refreshed once and the head printed; a planted failing rebuild keeps the old store and names the failure; planted link findings and two unindexed paths are counted; the audit runs whatever the pass finds; the retrieval.yaml digest is unchanged after the pass; a planted set with one changed cited block and one moved unchanged block lists only the changed one, by question id and entry number, in the writer''s request, with no question, answer or path text in it or in the digest'
  - 'S11 The schedule''s code (G4): `memaudit_cron.sh` takes `--repo <dir>` and runs, when due, the maintenance pass, the standing run and, when the fresh set is due, the fresh cycle, in that order, within the gate''s wait (W2-172 S9); A9''s ACT package (`memory_sets.walls_act`) adds one step to its ACT.md with the repository''s cron line (the wrapper with `--repo <that repository>`, Mondays 21:00), written as text for the repository''s owner''s operator and never installed [DEC-1179 (5), DEC-1101 (2), W2-88 S22] Verify: a planted due standing run and a due fresh set run in that order from one wrapper call; nothing runs when neither is due; a planted A9 run''s ACT.md holds the cron line with the repository''s path and no crontab is changed'
  failure:
  - 'F1 A standing set''s question id, question, gold, answer or citation outside its run folder, or read by any session: the auditor, the CTO, a worker or a later fix. Verify: S4''s planted strings are absent from every file written outside the run folder and from every launched session''s brief; no code path hands a standing run''s rows to `classes`, the auditor''s launch or the pool''s fix judging'
  - 'F2 A standing set judged twice in one week, judged without DECLARATION.json and USED first, re-scored, or its labels changed after a figure exists. Verify: S2''s planted runs; `measure --kept` on a standing run exits 3 and writes nothing; the set''s digest is checked equal at every run and a planted edit is refused before any search'
  - 'F3 The standing set used to choose, adopt or reject a fix or a configuration. Verify: the tool offers no command that compares two configurations or two commits on a standing set; the standing run refuses `--decision` and any data condition'
  - 'F4 The method drifts: the reader or grader prompt, model, cap or A2 cut changed, or the standing path diverges from the fresh path. Verify: `test_prompts.py` passes unchanged; S3''s spy'
  - 'F5 A fresh set''s use-once behaviour changes. Verify: W2-170''s S3 and F2 cases on fresh sets pass with only their bar values revised; W2-171''s S5 case passes with only its bar value revised (W2-187-P1 (a), DEC-1156 (7))'
  - 'F6 The maintenance pass changes a setting of the standard, applies an ACT, installs a cron line or stops the audit. Verify: S10''s planted runs; the module imports no crontab writer and the retrieval.yaml and path map digests are unchanged after a pass'
non_goals:
- 'no new measuring method: the standing run reuses the fresh 80''s judged path as W2-170 to W2-173 built it'
- 'no change to the adopt skill or the practice record (W2-188), and no `.claude/` copy'
- 'no cron line installed and no walls or path-map change applied: those are ACT-MEMORY-AUDIT-CRON-1 for Gov OS (the CTO''s ACT) and each adopted repository''s own ACT package'
- 'no writing of the standing set: the independent writer and checker write it under the owner''s approved brief'
- 'no change to the release step or the re-pin ACT: they read `status --repair` (the CTO''s ACT text)'
- 'no DEC-1101 (1) count of "not found" answers from agents'' work returns: the pass counts the audit runs'' own; the work-returns count stays the CTO''s tool until a decision gives it a product home'
done_when: [DOD-1, DOD-2, DOD-3, DOD-4, DOD-5, DOD-6]
sources: [DEC-1179, DEC-1176, DEC-1101, DEC-1125, DEC-1126, DEC-1098, DEC-1097, DEC-1092, DEC-1074, DEC-1071, DEC-1072, DEC-1156, DEC-974, DEC-105, DAEO-61vm, DAEO-k1e2, DAEO-p8tv, DAEO-qz4p, DAEO-2bdu, DAEO-f58b, DAEO-rmhj]
acceptance_tests: {path: tests/acceptance/W2-187/}
---

# W2-187 The standing hidden set, judged every week at 95 %, counts only

**Problem.** The memory audit (W2-170 to W2-173) writes a fresh 40 each week and measures each set once; old questions
are re-run only for retrieval figures (the pool), never against the end-to-end bar, and 95 % is printed, not judged
(`src/gov/memaudit/declare.py:32-33`). Its state is one folder per machine with Gov OS's retrieval paths
(`schedule.py:18-22, 48-55`). There is no weekly maintenance job. The owner's MEMORY-AUDIT (a) (2026-11-14; DEC-1179,
provisional) wants each repository's memory judged end to end every week on the same hidden questions, as Gov OS's was
measured, at 95 %, counts only, with a monthly fresh set as the check against fitting. The reconciliation, with file and
line for each part, is `drafts/memory-scope-20261113/MEMORY-AUDIT.md` §2 and §3 (G1, G2, G3, G5).

**Approach.** A `standing` mode beside the fresh mode in `gov.memaudit`, sharing its judged path. What differs:
- the per-week marker instead of the per-set lock (S2);
- no `misses.jsonl` and no auditor, counts only (S4);
- the pre-flight's anchor check drops by count (S6);
- the drift comparison at each fresh run (S7);
- the below-95 states (S8).

The bar function changes for both modes (S5). The runs folder is keyed by repository (S9). `maintain` calls the
existing checks (S10). The wrapper and A9's ACT text carry the schedule (S11).

**The method, exactly (S3; what "double search, agents as second rerankers" means here).** The fresh 80's judged
configuration (FRESH-80-1 §3.1, DEC-1097 (1)(a), accepted by DEC-1098 (1) at 78 of 79):
- the store with the standard;
- the first bundle from W2-61's measure (`gov.retrieval.measure`, 6,000 tokens, items widened to sections);
- the reader reads the whole ranked bundle and decides what answers, a second ranking after the 0.6B (E3: 114 of 138 in
  one call, against 84 for the top 5 and 101 for 40 unranked);
- it may search again once with its own words, the A2 cut (E2: 115 at one search, 128 at two; E3-SA: a second search
  never lost a right answer);
- graded by the named grader, with the second grader's agreement;
- the citation checked by the measure's matcher.

"A second reranker" in W2-88 S10 and its failure line means a second reranking model; it stays forbidden, and the
reader is not one.

**Test revisions (decided behaviour, DEC-1156 (7)).** S5 changes the bar the W2-170, W2-171 and W2-172 cases pin (85 %).
The ticket's independent test designer revises exactly the six files in `allowed_paths`, with a `Rewrite-Reason` naming
DEC-1179 (2): about 16 lines of values and helpers. `tests/unit/memaudit/` is the engineer's.

**Rabbit holes.**
- Do not copy the reader path into a second module: one path, two modes.
- Do not print an id "for debugging".
- Do not make the maintenance pass a gate.
- Do not decide the replacement set's content: the writer's brief does.
- Size: about 300-450 lines for G1 and G2, 100-150 for G3, 150-250 for G5, about 20 for S11, plus tests. If the test
  designer's suite shows it larger than about 900 lines, S10 and S11 split off as W2-187b, pre-approved by the owner
  (DEC-1179, O8 (a)): the lead tells the CTO, who files it, and nobody waits for a P1.

**Filed 2026-11-14 on the owner's decision (DEC-1179, MEMORY-AUDIT-P1; O3 (b): S8's cadence is W2-172 S5's computed rule, unchanged).** S10 gains a sixth item from DEC-1178 (1): the list of gold questions whose cited lines changed, for the walled writer, which the owner's operator handles in the Monday slot until this ticket lands.

## Interface (the CTO at claim, DEC-1179 (8), DEC-1157 (3) and (12); listed for the owner's reading)

- **I1, the command line (`src/gov/memaudit/__main__.py`; S1, S2, S8, S9, S10, F2, F3).** The exit map stays as it is
  (`gov.memaudit.EXIT`: 0 ok, 1 refused, 2 stopped, 3 used, 4 usage), `say` stays the only printer, and every subcommand
  keeps `--sets-root` (required, as today). The new and changed subcommands:
  - `standing declare --sets-root R --set <name> [--repo D] [--runs-dir DIR] [--replaces <old>]` (I3);
  - `standing run --sets-root R [--repo D] [--store-link P] [--gov EXE] [--claude EXE] [--gate-cmd CMD]` (I4). It has no
    `--decision`, no `--force` and no data flag, so any of them is argparse's exit 4 (F3);
  - `standing live --sets-root R [--repo D]`: prints `KEY <key>`, then `LIVE <set>` (exit 0) or `LIVE none` (exit 1). It
    writes nothing;
  - `maintain --sets-root R [--repo D] [--store-link P] [--gov EXE]` (I10);
  - `due --fresh` (I8); `status --repair [--residual DEC-<n>]`, with `--since` required only without `--repair` (I8);
  - `pool-import --sets <name>...` (I9);
  - `preflight`, `declare`, `measure`, `judge` and `figures` take `--week <YYYY>-W<ww>`. With it, the step works on the
    standing set's week folder (I2). `--audit` then names the standing set. Without `--week`, every byte of the fresh path
    is as today.
  - Name forms (`layout.py`): `SET_RE = memory-(audit|standing)-[0-9]{8}` (a Wave 0 verdict set keeps its
    `memory-audit-<date>` name; a new standing set is `memory-standing-<date>`) and `WEEK_RE = [0-9]{4}-W[0-9]{2}`, the
    ISO year and week of `schedule.now()` in UTC (the `GOV_MEMAUDIT_NOW` seam).

- **I2, where things live (`layout.py`, `schedule.py`; S2, S4, S9).**
  - `layout.paths(sets_root, name, week=None)` gives today's dict. With `week`, its `run` is
    `<sets root>/runs/<set>/<week>/` (mode 0700, `make_run`), and `preflight`, `declaration`, `used` and `ledger` lie in
    it. `set`, `hidden` and `map` are as today. "Its run folder" in S4 and F1 is `<sets root>/runs/<set>/` and everything
    under it.
  - `schedule.state_dir(runs, repo) -> Path` is `<runs>/indep/memaudit/<key>/`. `<key>` is
    `os.path.basename(real) + "-" + sha256(real.encode()).hexdigest()[:8]`, where `real = os.path.realpath(repo)`.
    `schedule.folder(runs)` is replaced by it everywhere (driver, due, status, baseline, maintain). The folder holds:
    - `HISTORY.jsonl`, `STARTS.log`, `LOCK` and `cron.log`;
    - `STANDING.jsonl` (I3) and `MAINTAIN.jsonl` (I10);
    - `<audit>/` (a fresh run's `COUNTS.json` and `DIGEST.txt`, as today) and `standing/<set>/<week>/` (the same two files
      for a standing run).
  - The driver passes `GOV_INDEP_RUNS_DIR=<key folder>` to every child it starts (it passes `<runs>` today). The launch
    script's `AUDITS.log`, `SEEDS.log` and `<kind>/<run>/counts.json` therefore land in `<key folder>/indep/`.
    `schedule.last_audit_commit`, `driver._refusal`'s `RN-NOBASE`, `baseline` and `preflight` (through its
    `$GOV_INDEP_RUNS_DIR` default) read them there. The launch script is unchanged.
  - Nothing of a standing set's questions is written under `<runs>`. `STANDING.jsonl` holds the set's name, digests,
    counts and commits only.

- **I3, `standing declare` (new module `src/gov/memaudit/standing.py`: the record, the spent check, the week rule, drift
  and repair; it calls the existing modules and copies none; S1, F1).**
  - **The call:** `standing.declare(sets_root, name, *, repo, runs_dir, replaces=None) -> (word, counts)`.
  - **The refusals, checked in this order, with nothing written:**
    - `STANDING_SPENT <k>` (exit 1): some `question` of the set's `hidden/*.yaml` equals the `question` of a line in
      any `<sets root>/runs/**/misses.jsonl`; or `<sets root>/runs/<set>/**/miss-classes.json` exists; or an
      `AUDITS.log` line (in `<key folder>/indep/` and in `<runs-dir>/indep/`) has `audit == <name>`. `<k>` is the count
      of matched questions, never an id.
    - The set's own `runs/<set>/USED` exists: the set is accepted only as the repository's Wave 0 verdict set.
      `runs/<set>/DECLARATION.json` and `runs/<set>/FIGURES.json` (its counts-only result record) must exist, and the
      declaration's `audit_commit` must equal the commit of the first line of the repository's `AUDITS.log` (the
      baseline W2-88 S21 writes at the verdict commit). Otherwise `STANDING_SPENT 0`. The spent check skips only that
      Wave 0 run's own `runs/<set>/misses.jsonl` and `miss-classes.json` (see the unresolved item U1).
    - `STANDING_LIVE <live set>`: `STANDING.jsonl` holds a live set. `--replaces <old>` lifts this only when `<old>` is
      the live set and its last weekly HISTORY line carries `STANDING_THIN` (O5 (a)). `<old>` is then retired with
      reason `thin` in the same write.
    - `STANDING_BRIEFS`: no delivered writer and checker `counts.json` (`status == "delivered"`, `set == <name>`) is
      found under `<runs-dir>/indep/{writer,checker}/*/` or `<key folder>/indep/{writer,checker}/*/`. `--runs-dir`
      defaults as `preflight` defaults: `$GOV_INDEP_RUNS_DIR`, else `~/gov-os-runs`.
    - `STANDING_FORM`: a file fails `preflight.form_ok`, or `hidden/` holds fewer than 36 files.
  - **The write:** one `STANDING.jsonl` line:
    `{"event": "declared", "set", "set_digest" (common.set_digest(hidden)), "n", "n_apart", "writer_brief_sha256",
    "checker_brief_sha256", "written_commit" (the writer counts' commit), "wave0": bool, "at"}`.
  - **The output:** `STANDING DECLARED <set>: n <n> apart <k> digest <12 hex> written at <12 hex>`, exit 0.

- **I4, `standing run` (`driver.standing(...)` beside `driver.run`, reusing `_Cycle`, `_refusal`'s RN-LOCK, RN-REBUILD,
  RN-SIDE and RN-STALE, `_history` and `_finish`; S2, S3, S4, S6, F2, F3, F4).**
  - **Its children,** in order, each `python3 -m gov.memaudit <step> --sets-root R --audit <set> --week <week> ...`:
    `preflight` (I6), `measure`, `judge`, `figures`. The gate is asked before `measure` and `judge`, as today (`GATED`).
  - **No `classes`, auditor launch, `pool` or writer launch:** `classes` and `pool` refuse a standing set name
    (`MS-STANDING`, exit 1), and so does `pool-import` (F1).
  - **The week rule** (`standing.week_state(paths)`; S2) is checked before anything is written:
    - The week folder is absent, or present without `USED`: the run goes on (the folder is re-used).
    - `USED` present with `reader/` or `FIGURES.json`, or `USED` present with no `STOPPED`: `USED`, exit 3, nothing
      written (no STARTS line, no digest).
    - `STOPPED` present with no `reader/`, and `<week>.stopped/` absent: the week folder is renamed to `<week>.stopped/`
      and the run starts once more.
    - `STOPPED` present and `<week>.stopped/` present: `USED`, exit 3.
  - **Before any search,** the refusals are `STANDING_NONE`, `STANDING_RETIRED` and `STANDING_DIGEST`. The last is
    `common.set_digest(hidden)` not equal to the record's `set_digest`; then nothing is written and the week is not spent
    (F2).
  - **The one judged path:**
    - `declare.declare(..., week=)` writes `DECLARATION.json`, its ledger line, then `USED`, as today. In standing mode
      `n` is the live count from the week's `PREFLIGHT.json`; `n_set` and `dropped` are recorded beside it.
      `DC-DROPS` is not asked.
    - A nonstandard `retrieval.yaml` is `DC-DECISION` with no way to allow it (F3).
    - `measure.run(..., week=)` measures the whole `hidden` part (wholeness against `n_set`) and scores the live ids.
    - `judge.run(..., week=)` asks only the live questions, by `_Judge.one`, `prompts` and `matcher` unchanged (S3's
      spy).
    - `figures.build` runs as today. In standing mode `figures.write_misses` is not called, and judge's `SEARCH FAILED`
      line prints its count with no ids (S4).
  - **The store commit (S3; W2-138's field `result.store.commit`):** `fault.not_whole(folder, n, families,
    store_commit=None)`. In standing mode it gives the cause `store_commit` when any kept result's `result.store.commit`
    is absent or not the declaration's `store_commit`; that attempt is then a fault under the existing rule (one restart,
    then `STOPPED fault`). A later search in `judge.search` from another commit is a counted search failure with an empty
    bundle (`why` `store`).
  - **After `figures`,** one HISTORY line:
    `{"kind": "standing", "set", "week", "audit": <set>, "commit", "at", "mode", "churn", "retrieval_28d", "passes",
    "pool_regression" (the last fresh line's), "measured": true, "used": true, "n", "right", "wrong", "not_found",
    "dropped", "pct" (100 right / n), "word": "pass"|"miss", "gov_pin", "retrieval_yaml_sha256", "path_map_sha256"}`.
    Then the states of I7 and I8, and the digest (I12).
  - **The last stdout line** is `STANDING <week> right <r> of <n>: passes|misses`.
  - **Exit:** 0 when the run ran (a miss is data, not a failure), 1 refused, 2 stopped, 3 week spent, 4 usage.

- **I5, the bar (`declare.bar`, `declare.ROUNDING`; S5).**
  - `bar(n) = {"need_right": -(-95 * n // 100), "max_wrong": 5 * n // 100, "target_right": -(-95 * n // 100)}`, which
    gives 38, 76 and 76 for n = 40, 79 and 80.
  - `figures.build`'s `passes` stays `right >= need_right and wrong <= max_wrong`; the second half is implied
    (n - ceil(0.95 n) = floor(0.05 n)).
  - `ROUNDING = "need_right = ceil(95 n / 100); max_wrong = floor(5 n / 100); target_right = need_right; integer
    arithmetic; standing and fresh runs alike (DEC-1179 (2))"`.
  - The digest's VERDICT line and `verdict_lines` print it unchanged. The revised W2-170 helper `bar` returns this dict,
    key for key, so W2-88's S15 case passes unedited.

- **I6, the standing pre-flight (`preflight.standing(sets_root, name, *, week, commit, repo) -> (word, counts)`; S6,
  F2).**
  - **Each question is loaded alone** through `matcher.questions(sets_root, set, "hidden", root, only=<stem>)`, a new
    one-file form. `root` is the store link's worktree at the audit commit. A load fault drops that one question, never
    the set.
  - **A question is dropped** when some entry of its `sources` has every alternative unresolved (`q["unresolved"]` names
    `entry n`, or `entry n.m` for every `m`), or when it is a nonexistent-id question and `preflight.id_exists` finds its
    id.
  - **The write:** `PREFLIGHT.json` in the week folder:
    `{"mode": "standing", "ok", "n_set", "n", "dropped", "dropped_ids", "n_apart", "set_digest", "files_sha256"}`. Ids
    stay in the run folder. `declare.preflighted` reads the same `files_sha256`.
  - **The output** is the single line `PRE-FLIGHT standing: n <n> of <n_set>; dropped <k>`, with no id. `ok` is false
    only for `STANDING_DIGEST`. Nothing in the set is edited or moved, so `void` is never called.
  - **Fewer than 70 live questions** puts `STANDING_THIN <live>` in the HISTORY line's `word` list and in the digest
    (O5 (a)).

- **I7, the check against fitting at each fresh run (`standing.drift(state, fresh_fig) -> dict`, called in `driver.run`
  after `figures`; S7).**
  - **The figures:** F is `100 * right / n` of the fresh run; S is the mean `pct` of the live set's last four standing
    measured lines.
  - **Fewer than four lines** gives `drift: not yet (k of 4)`.
  - **S - F >= 5:**
    - a HISTORY line `{"kind": "drift", "word": "STANDING_FITTED", "S", "F", "set"}`;
    - a `STANDING.jsonl` line `{"event": "retired", "reason": "fitted"}`;
    - a later `standing run` on that set is `STANDING_RETIRED`, exit 1.
  - **F - S >= 5:** the word is `STANDING_STALE`; nothing is retired.
  - **The retired set as a diagnostic set (counts only):** `pool.run` re-measures each retired set in place, retrieval
    only, into `<sets root>/runs/<set>/diagnostic-<audit>/`. It prints `POOL DIAGNOSTIC <set> hit5 <k> of <n>; full <k>`
    and never copies its files into `memory-pool/` (S4).
  - **With no live standing set,** `driver.run` writes its lines without `kind`, exactly as today.

- **I8, the two cadences, the miss and the repair (`schedule.py`, `standing.py`; S8).**
  - **The standing cadence:** `due` (its three lines and exit codes unchanged) is `schedule.decide(repo, state, head, at,
    lines)`, unchanged, over the live set's own standing lines. With no live set it reads the lines with no `kind`, which
    is W2-172's unedited S5 case. STARTS.log lines gain `"kind": "standing"|"fresh"` once a set is live.
  - **The fresh cadence:** `due --fresh` prints `MODE fresh`, `DUE yes|no next <yyyy-mm-dd>` and
    `REASON first|28d|miss|wait`.
    - `first`: no fresh start.
    - `miss`: the live set's last standing measured line has `passes: false` and no fresh start in the current ISO week.
    - `28d`: today is on or after the first Monday on or after (last fresh start's date + 28 days).
    - With no live set it answers as `due`.
  - **A miss** is the standing HISTORY line with `"word": "miss"`. The P1 digest line is in I12.
  - **The repair:** after each standing measured line, a HISTORY line
    `{"kind": "repair", "word": "MEMORY_REPAIR open", "set", "week"}` is written when none is open and either:
    - this line and the previous standing line are both misses; or
    - this line is a miss and the last passing `pct` minus this `pct` is 5 or more.

    A later pass writes `MEMORY_REPAIR closed`.
  - **`status --repair`:** prints `REPAIR open since <week>` (exit 1) or `REPAIR none` (exit 0). With
    `--residual DEC-<n>` it appends `{"kind": "repair", "word": "MEMORY_REPAIR residual", "decision": "DEC-<n>"}`,
    prints `REPAIR residual DEC-<n>` and exits 0. A malformed id is exit 4.

- **I9, a retrieval change per repository, and `pool-import --sets` (`schedule.retrieval_changed`, `pool.importing`;
  S9).**
  - `retrieval_changed(repo, since, until, gov=None)` keeps today's diff over the six globs for every repository. In an
    adopted repository the four code globs match nothing it tracks, so only `retrieval.yaml` and the path map count there.
  - It adds `gov-pin` when `declare.gov_pin(gov or ~/.local/bin/gov)` differs from the last HISTORY line's `gov_pin`. A
    line without the field (W2-172's planted lines) is no trigger.
  - `pool-import --sets a b` imports exactly those sets' `hidden` parts (and `visible` where present) from that sets
    root, leaving out nonexistent-id questions as today. It has no 79/138 count check. Each set is imported once
    (`runs/memory-pool/IMPORTED-<set>.json`; `MS-IMPORTED` names it again). A standing set name is `MS-STANDING`. With
    no `--sets`, the import is today's, byte for byte.

- **I10, `maintain` (new module `src/gov/memaudit/maintain.py`; S10, F6).**
  - **Its six items,** each bounded by a timeout (`GOV_MEMAUDIT_MAINTAIN_TIMEOUT_S`, default 1800 for a build, 300
    otherwise):
    1. **The store:** `schedule.head_of(store_link)` against `git rev-parse <mainline>`. When behind, one
       `<gov> rebuild --integration <mainline branch>`. A failure keeps the store in service and is named:
       `kept <12 hex> (refresh exit <c>)`.
    2. **The layout:** `gov.store.layout.found_of` on `<link>/.gov-runtime/store.db`, read-only. When not None, one
       rebuild by the same command, else named `stale kept`.
    3. **The links:** `<gov> links --since <the last MAINTAIN line's commit> --json` in the repository; the count of new
       findings. On a first pass it runs from the mark with no `--since`; a refusal is `none`.
    4. **Unindexed paths:** tracked paths of the link worktree that `gov.retrieval.lexical.kept_out` does not keep out,
       less the distinct `path` values of `lexical_chunk` in its store; the count.
    5. **Not found and second searches:** from the latest standing week folder's and the latest fresh run's
       `reader/*.json`, the rows with `final_verdict == "not_found"` and the rows with a non-empty `searches`; two
       counts.
    6. **The changed cited lines:** for every set the sets root's path map declares, except standing sets (live or
       retired), `matcher.questions(sets_root, set, part, link)`'s `unresolved` entries. This is W2-61h S4's list:
       re-anchoring runs in memory, so a block moved unchanged is not listed. With N2 (b) (DEC-1180 (1)), a heading-cited source whose section text (from its heading line to the next heading of the same or a higher level, or the end of the file) differs between the source's own commit and the head is listed too, though its heading is still found, though `matcher` resolves it; an entry is listed once. One request per set with at least one
       entry goes to `<sets root>/runs/<set>/REANCHOR-<week>.json` (mode 0600, written whole; the folder made 0700 by
       `layout.make_run`):

       `{"week", "audit_commit", "set", "changed": [{"id", "entry"}], "count"}`

       It holds no question, answer or path. This mirrors the auditor's walled input, which the launch script takes from
       `runs/<audit>/` (kinds.yaml `auditor.input: [set, misses]`). Count: the total.
  - **The write:** one `MAINTAIN.jsonl` line in the key folder: the week, the commit, the six items, and the sha256 of
    `retrieval.yaml` and of the path map before and after (equal, F6).
  - **The output:** one line,
    `MAINTAIN 1 store <word> 2 layout <word> 3 links <k> 4 unindexed <k> 5 not_found <a> second <b> 6 reanchor <k>`.
  - **Exit 0 always,** except 4 for usage. The module imports no crontab writer, applies no ACT and never writes
    `retrieval.yaml` or the path map.

- **I11, the schedule's code (`memaudit_cron.sh`, `memory_sets.walls_act`; S11).**
  - **The wrapper:**
    - It takes `--repo <dir>` (default: the cwd's top level), runs `cd` into it, and keeps its variables
      (`GOV_MEMAUDIT_PYTHON`, `GOV_MEMAUDIT_SETS_ROOT`, `GOV_INDEP_RUNS_DIR`, `GOV_MEMAUDIT_GATE`).
    - It first calls `standing live --repo`. Exit 0 gives the live path: `due` and `due --fresh`; then `maintain` when
      either is due; `standing run --gate-cmd` when `due`; `maintain` once more when that run's last line ends `misses`
      (S8 R4); and `run --gate-cmd` when `due --fresh`, in that order.
    - Any other exit gives today's path, byte for byte (`due`, then `run`). That keeps W2-172 S9's shim cases green:
      the shim passes `standing live` to the real interpreter, which answers `LIVE none`.
    - `cron.log` is `<key folder>/cron.log` (the `KEY` line), else `$RUNS/indep/memaudit/cron.log`. Its line's six keys
      are unchanged. The exit is the last started step's.
  - **The ACT text:** `walls_act(out, *, sets_root, audit, made, blind, repo=None)`. `repo` defaults to the git top level
    of `out`, which A9 writes inside the repository; `fabric.py` stays unchanged. ACT.md gains step 6:

    `6. Install the weekly memory audit's cron line for this repository (Mondays 21:00; never installed by adoption):
    \`0 21 * * 1 GOV_MEMAUDIT_SETS_ROOT=<sets_root> <GOV_OS>/governance/project/orchestration/tools/memaudit_cron.sh
    --repo <repo>\``

    It is text only; no crontab is read or written.

- **I12, the digest lines (`digest.py`; S4, S6, S7, S8, S10).**
  - **A standing run's block** (`standing/<set>/<week>/DIGEST.txt`, and on stdout):
    - `STANDING <set> week <week> commit <12>`;
    - `VERDICT right <r> of <n>; wrong <w>; not found <f>; bar <need> right: passes|misses`;
    - `MISSES outcome wrong <a> incomplete <b> not_found <c>; rank 1-5 <x> 6-20 <y> absent <z>`;
    - `QUESTIONS live <n> of <n_set>; dropped <k>` (and `STANDING_THIN <live>` below 70);
    - `BESIDE hit5 <k> of <n_gold>; first bundle <k>; A1 <a> A2 <b>: <g> gains <l> losses, exact McNemar p <p>`;
    - the I10 `MAINTAIN` line;
    - `P1 memory below 95 %: wrong <a> incomplete <b> not_found <c>` on a miss, else `P1 none`;
    - `REPAIR open|none`;
    - `NEXT standing <date> <mode>; fresh <date>`;
    - `STOP ...` and `OWNER ...` as W2-172's lines.
  - **A fresh run's twelve lines are unchanged.** After them come `DRIFT S <s> F <f>: none|STANDING_FITTED|STANDING_STALE`
    (or `DRIFT not yet (k of 4)`) and the latest `MAINTAIN` line, with a live set only. The revised W2-172 S7 case counts
    them.
  - **No line** holds a question id, question, gold, answer, citation or path of a standing set.

- **How the code-bound clauses read:**
  - **S1's command** is `standing declare` with `--sets-root` required, as every subcommand. "The sha256 of the writer's
    and checker's briefs" is the `brief_sha256` of their delivered `counts.json`. "The commit it was written at" is the
    writer counts' `commit`. "Ever written to a misses.jsonl" is matched by question text.
  - **S2's "writes nothing"** covers the sets root, the key folder and stdout's digest (only the `USED` line is printed).
  - **S4's "AUDITS.log"** is the repository's `<key folder>/indep/AUDITS.log`, which a standing run never touches.
  - **S5's "the revised W2-170, W2-171 and W2-172 cases"** are the six files in `allowed_paths`, plus the two helpers in
    Gap G1.
  - **S9's "keep separate AUDITS.log"** is met with the launch script's AUDITS.log at `<key folder>/indep/AUDITS.log`
    (I2), not `<key folder>/AUDITS.log`, because the launch script fixes `$GOV_INDEP_RUNS_DIR/indep/`. "For Gov OS also its
    six retrieval globs" is the six globs applied to every repository, as I9 says.
  - **S10's "six counts"** are one field per item; items 1 and 2 print a state word, item 5 two numbers. "Cited lines
    changed" is `gov.retrieval.measure`'s `unresolved` (a block not found once at the audit commit).
  - **S10 and S8's "runs at once after the miss"** is the wrapper's second `maintain` in the same cycle.
  - **S11's "within the gate's wait"** is `--gate-cmd` on both `standing run` and `run`.
  - **F2's `measure --kept` on a standing run:** a name with a `STANDING.jsonl` record or a week folder prints `USED`,
    exit 3, nothing written.

- **Gaps (a KPI that cannot be met inside `allowed_paths` as filed):**
  - **G1 (S9 against S5, S8 and W2-172's unedited cases).** Moving the state to `<runs>/indep/memaudit/<key>/` breaks
    W2-172's s1, s2-s4, s6, s8 and s9 cases and the f1-f4 cases. They read it through `self.mem` and `self.audits_log` in
    `tests/acceptance/W2-172/w2_172_world.py` (lines 281-282) and `w2_172_git.py` (lines 43-44). Neither helper is in
    `allowed_paths`, and S8 requires `test_w2_172_s5_due.py` unchanged. The fix keeps every W2-172 test file unchanged:
    add the two helpers to `allowed_paths` for the test designer, about four lines (the key, `mem`, `audits_log`), with a
    `Rewrite-Reason` naming DEC-1179 (5). That is a path case the CTO routes under DEC-1156 (7).
  - **G2 (S10 (6)'s hand-off).** The tool writes the request (I10). Staging it into a writer's wall needs a `reanchor`
    input in `governance/project/indep-walls/kinds.yaml` and the matching staging in
    `governance/project/orchestration/tools/indep_launch.py`, which are walls and control paths (an ACT). Until then the
    owner's operator hands it over in the Monday slot, as the ticket's last paragraph says.

- **The CTO's routings at claim (DEC-1156 (7), DEC-1157 (12); listed for the owner's reading):** G1: `tests/acceptance/W2-172/w2_172_world.py` and `w2_172_git.py` are added to `allowed_paths` for the test designer (about four lines: the key, `mem`, `audits_log`; `Rewrite-Reason: DEC-1179 (5)`); every W2-172 test file stays unchanged. G2: until an ACT adds a `reanchor` input to the walls (`kinds.yaml`, `indep_launch.py`), the owner's operator carries `REANCHOR-<week>.json` to the walled writer in the Monday slot (DEC-1179 (6), DEC-1178 (1)). U1: a Wave 0 verdict set's own run's `misses.jsonl` and `miss-classes.json` do not spend it (the package's §5.3: W2-187 S1 accepts a used Wave 0 verdict set). U2: `maintain` item (6) leaves standing sets out; their stale questions drop by count (S6). G6 (a same-head refresh of a stale-layout store) is the engineer's to show in evidence.

**Amended 2026-11-14 (the CTO within purpose, DEC-1157 (12); the owner's N2 (b), DEC-1180 (1)):** S10 (6) and I10 item 6 also list a heading-cited source whose section text (from its heading line to the next heading of the same or a higher level, or the end of the file) differs between the source's own commit and the head is listed too, though its heading is still found, matching W2-61h S4's list. The lead brings this in at its next merge of `w2/integrate`; the test designer's S10 cases take it with `Rewrite-Reason: DEC-1180 (1)`.

**Path case 2026-11-14 by the CTO (DEC-1156 (7); listed for the owner's reading): W2-187-P1 (a).** Two more W2-171 acceptance files pin the 85 % bar (`test_w2_171_cli_layout_ledger.py:120-121`, `test_w2_171_s5_misses_f2.py:82`; `docs/probes/DAEO-0cd2/PACKAGE-W2-187-P1.md`). Both are added to `allowed_paths` for the independent test designer (bar values only, `Rewrite-Reason: DEC-1179 (2)`), and F5's "W2-171's S5 case passes unchanged" now reads "with only its bar value revised", as it already did for W2-170. The behaviour guarded is unchanged; a narrow check covers it.
