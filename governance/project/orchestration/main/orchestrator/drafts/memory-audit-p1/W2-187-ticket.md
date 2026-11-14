---
id: DAEO-NEW1
wbs_id: W2-187
external-ref: W2-187
title: "The standing hidden set: each repository's memory judged end to end every week on the same questions at 95 %, counts only, with a monthly fresh set as the check against fitting, a weekly maintenance pass, and the audit's state per repository (MEMORY-AUDIT G1, G2, G3, G5 and G4's code)"
type: task
class: implementation
role: engineer
profile: FULL
status: open
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
- tests/acceptance/W2-172/test_w2_172_s7_digest.py
- docs/changes/W2-187-evidence.md
- docs/probes/DAEO-NEW1/**
reads:
- .gov-runtime/scratch/orchestrator/drafts/memory-scope-20261113/MEMORY-AUDIT.md
- .gov-runtime/scratch/orchestrator/drafts/memory-audit-p1/PACKAGE.md
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
  - 'S1 A standing set: `python3 -m gov.memaudit standing declare --set <name> --repo <dir>` records one standing set for the repository: its name, its digest (`LC_ALL=C sha256sum *.yaml | sha256sum` over the kept questions), n with the nonexistent-id questions apart, the sha256 of the writer''s and checker''s briefs, and the commit it was written at. A set whose questions were ever written to a `misses.jsonl` or read by an auditor is refused (`STANDING_SPENT`); an adopted repository''s Wave 0 verdict set is accepted once its `USED` marker and its counts-only result record exist (W2-88 S13, S16). One standing set is live per repository; a second is refused until the first is retired [DEC-1177 (1), DEC-1176 (1), DEC-1098 (1)] Verify: planted sets: a new set is recorded with each field; a set with a planted `misses.jsonl` line is refused with `STANDING_SPENT`; a planted Wave 0 verdict set with `USED` and its record is accepted; a second live set is refused'
  - 'S2 One judged run a week: a standing run writes `runs/<set>/<ISO year>-W<week>/DECLARATION.json` and then `USED`, before any search; a second judged run of the same set in the same ISO week exits 3 and writes nothing. A run stopped by the fault rule (FRESH-80-1 §3.5, `STOPPED <cause>`) before its reader run started may start once more that week; a run whose reader run started never runs again [DEC-1177 (1), DEC-1097 (1)(g)] Verify: planted runs: the file times and the ledger line show DECLARATION.json before USED before the first search; a second run the same week exits 3 with the tree byte-identical; a planted STOPPED before the reader run allows one restart and a second is refused'
  - 'S3 The same method as Gov OS''s memory: a standing run uses the fresh 80''s judged path unchanged: the store at the audit commit with the standard (the 0.6B through the one shared reranker, the pool on, the 6,000-token bundle widened to sections); each question''s first bundle from `gov.retrieval.measure`; `judge`''s reader run as built (the pinned `prompts.py`, the reader, the cap, the A2 cut judged, A1 and A3 as data); the named grader with the second grader''s agreement; the measure''s matcher with source families. Every search result''s store commit (W2-138) equal to the declared store''s commit, else that attempt is a fault [DEC-1177 (1), DEC-1097 (1)(a), DEC-1098 (1), DEC-1092 (1)] Verify: `tests/unit/memaudit/test_prompts.py` passes unchanged; a planted standing run calls the same reader, grader and matcher functions as a fresh run (one shared code path, asserted by a spy); a planted result from another store commit makes the attempt a fault'
  - 'S4 Counts only: a standing run writes no `misses.jsonl` and launches no auditor. Only counts leave its run folder: right end to end, wrong claims, not found, the misses by outcome (wrong, incomplete, not found) and by the first gold place''s rank in the first bundle (1-5, 6-20, absent), the questions dropped by the anchor check, and the figures beside (hit@5, gold in the first bundle, A1 against A2 with exact McNemar). No question id, question, gold, answer or citation of the standing set is printed, logged, written to `FIGURES.json`, `HISTORY.jsonl`, `AUDITS.log` or the digest block, or written outside its run folder (mode 0700) [DEC-1177 (2), DEC-1101 (2), DEC-1074 (1)] Verify: a planted standing run with five planted misses whose ids and texts are unique strings: no planted string appears in stdout, stderr, FIGURES.json, HISTORY.jsonl, AUDITS.log, the digest block or any file outside the run folder; no misses.jsonl exists; no auditor launch event is in the ledger'
  - 'S5 The bar at 95 %: `declare.bar(n)` gives `need_right = ceil(95 n / 100)` and `max_wrong = floor(5 n / 100)`; a verdict passes when right end to end at A2 reaches `need_right` (wrong claims stay reported and checked). It applies to standing and fresh runs alike, and the declaration''s rounding text says so. On 80 judged that is 76, on 79 it is 76, on 40 it is 38 [DEC-1177 (2), DEC-1097 (1)(d) as carried forward, DEC-957] Verify: unit cases n = 40, 79, 80 give 38, 76, 76; a planted run with right = need_right - 1 is a miss and with right = need_right a pass; the digest''s bar line prints the new figure; the revised W2-170, W2-171 and W2-172 cases pass, and W2-88''s S15 bar case (which reads W2-170''s helper `bar`) passes unedited'
  - 'S6 Staleness by count: before each standing run the pre-flight checks each question''s gold anchors at the audit commit; a question whose anchor no longer resolves, or whose nonexistent id now exists, is dropped from that week''s n and counted (`dropped k`); nothing in the set is edited. Fewer than 70 live questions prints `STANDING_THIN <live>` in the digest block and asks for a replacement [DEC-1177 (2), DEC-1097 (1)(f)] Verify: a planted set of 80 with 3 broken anchors: n is 77 and `dropped 3` is printed with no id; the set''s digest is unchanged after the run; a planted set with 69 live questions prints STANDING_THIN 69'
  - 'S7 The monthly check against fitting: at each fresh run the tool compares the fresh set''s right end to end per cent F with S, the mean of the standing set''s last four weekly figures; S - F of 5 points or more writes `STANDING_FITTED` in HISTORY.jsonl and the digest block, retires the standing set (no further standing run on it; it joins the pool as a diagnostic set, counts only) and asks for the writer''s replacement; F - S of 5 points or more writes `STANDING_STALE` and asks for the checker''s staleness pass; with fewer than four weekly figures the check prints `drift: not yet (k of 4)` [DEC-1177 (3), DEC-1074 (4)] Verify: planted histories: S 96, F 90 retires the set and a later standing run on it is refused; S 90, F 96 prints STANDING_STALE; S 95, F 92 prints no flag; two weekly figures print `drift: not yet (2 of 4)`'
  - 'S8 The two cadences and below 95 %: the standing set''s cadence is W2-172 S5''s computed rule, unchanged (weekly while active, monthly once stable, back to weekly at once on a miss, a retrieval change, churn of 10 % or more or a pool regression); the fresh set is due on the first Monday 28 days or more after the last fresh run. A standing miss is a HISTORY line `miss` with its counts; the fresh set is then due at the next Monday and every Monday until a standing run passes again (then every 28 days); the maintenance pass (S10) runs at once after the miss in the same cycle; the digest block carries a `P1 memory below 95 %` line with the counts by class. Two consecutive standing misses, or one miss 5 points or more below the last passing figure, write `MEMORY_REPAIR open` in HISTORY.jsonl, and `gov.memaudit status --repair` exits 1 while it is open and 0 once a later standing run passes or the owner''s decision id is given with `--residual DEC-<n>` [DEC-1177 (4), (5), DEC-1125 (2)] Verify: `tests/acceptance/W2-172/test_w2_172_s5_due.py` passes unchanged for the standing set; a planted fresh history 27 days old is not due and 28 days old is due on the Monday; planted histories: one miss makes the fresh set due next Monday and puts the P1 line in the digest; pass, miss, miss opens the repair; pass at 96 then miss at 90 opens it; `status --repair` exits 1, then 0 after a planted pass or `--residual DEC-1`'
  - 'S9 State per repository: the runs folder is `<runs>/indep/memaudit/<key>/` with `<key>` the repository''s directory name, a hyphen and the first 8 hex of the sha256 of its real path, so two repositories on one machine keep separate `AUDITS.log`, `HISTORY.jsonl` and `STARTS.log`. The retrieval change that sends an audit back to weekly is, for any repository, a change of the gov pin, of the repository''s `governance/project/retrieval.yaml` digest or of its path map''s digest, and for Gov OS also its six retrieval globs. `pool-import --sets <name>...` seeds the pool from that repository''s own sets root; with no `--sets` on Gov OS it imports Gov OS''s 79 and 138 as today [DEC-1177 (5), DEC-1101 (1), DEC-1125 (2)] Verify: two planted repositories on one runs folder write to two keys and neither reads the other''s history; a planted pin change on an adopted repository is a retrieval change and a change under `src/gov/retrieval/` of Gov OS is not, for it; `pool-import --sets a b` imports exactly those sets'
  - 'S10 One weekly maintenance pass before each standing run, `python3 -m gov.memaudit maintain --repo <dir>`: (1) the integration store at the main line''s head, else one refresh by W2-116''s `gov rebuild --integration`, a failed build leaving the last good store in service and named; (2) the store''s layout current, else one `gov rebuild`; (3) `gov links --since <the last pass''s commit>`: the count of new findings; (4) the count of tracked paths the path map indexes but the store holds no chunk of; (5) the standing and fresh runs'' reader `not found` answers and second searches, counted. It prints five counts in the digest block, never fails or delays the audit, and never changes one of the standard''s four settings [DEC-1177 (6), DEC-1072 (1), DEC-1101 (1), DEC-1096] Verify: a planted repository with a store 3 commits behind is refreshed once and the head printed; a planted failing rebuild keeps the old store and names the failure; planted link findings and two unindexed paths are counted; the audit runs whatever the pass finds; the retrieval.yaml digest is unchanged after the pass'
  - 'S11 The schedule''s code (G4): `memaudit_cron.sh` takes `--repo <dir>` and runs, when due, the maintenance pass, the standing run and, when the fresh set is due, the fresh cycle, in that order, within the gate''s wait (W2-172 S9); A9''s ACT package (`memory_sets.walls_act`) adds one step to its ACT.md with the repository''s cron line (the wrapper with `--repo <that repository>`, Mondays 21:00), written as text for the repository''s owner''s operator and never installed [DEC-1177 (5), DEC-1101 (2), W2-88 S22] Verify: a planted due standing run and a due fresh set run in that order from one wrapper call; nothing runs when neither is due; a planted A9 run''s ACT.md holds the cron line with the repository''s path and no crontab is changed'
  failure:
  - 'F1 A standing set''s question id, question, gold, answer or citation outside its run folder, or read by any session: the auditor, the CTO, a worker or a later fix. Verify: S4''s planted strings are absent from every file written outside the run folder and from every launched session''s brief; no code path hands a standing run''s rows to `classes`, the auditor''s launch or the pool''s fix judging'
  - 'F2 A standing set judged twice in one week, judged without DECLARATION.json and USED first, re-scored, or its labels changed after a figure exists. Verify: S2''s planted runs; `measure --kept` on a standing run exits 3 and writes nothing; the set''s digest is checked equal at every run and a planted edit is refused before any search'
  - 'F3 The standing set used to choose, adopt or reject a fix or a configuration. Verify: the tool offers no command that compares two configurations or two commits on a standing set; the standing run refuses `--decision` and any data condition'
  - 'F4 The method drifts: the reader or grader prompt, model, cap or A2 cut changed, or the standing path diverges from the fresh path. Verify: `test_prompts.py` passes unchanged; S3''s spy'
  - 'F5 A fresh set''s use-once behaviour changes. Verify: W2-170''s S3 and F2 cases on fresh sets pass with only their bar values revised; W2-171''s S5 case passes unchanged'
  - 'F6 The maintenance pass changes a setting of the standard, applies an ACT, installs a cron line or stops the audit. Verify: S10''s planted runs; the module imports no crontab writer and the retrieval.yaml and path map digests are unchanged after a pass'
non_goals:
- 'no new measuring method: the standing run reuses the fresh 80''s judged path as W2-170 to W2-173 built it'
- 'no change to the adopt skill or the practice record (W2-188), and no `.claude/` copy'
- 'no cron line installed and no walls or path-map change applied: those are ACT-MEMORY-AUDIT-CRON-1 for Gov OS (the CTO''s ACT) and each adopted repository''s own ACT package'
- 'no writing of the standing set: the independent writer and checker write it under the owner''s approved brief'
- 'no change to the release step or the re-pin ACT: they read `status --repair` (the CTO''s ACT text)'
- 'no DEC-1101 (1) count of "not found" answers from agents'' work returns: the pass counts the audit runs'' own; the work-returns count stays the CTO''s tool until a decision gives it a product home'
done_when: [DOD-1, DOD-2, DOD-3, DOD-4, DOD-5, DOD-6]
sources: [DEC-1177, DEC-1176, DEC-1101, DEC-1125, DEC-1126, DEC-1098, DEC-1097, DEC-1092, DEC-1074, DEC-1071, DEC-1072, DEC-1156, DEC-974, DEC-105, DAEO-61vm, DAEO-k1e2, DAEO-p8tv, DAEO-qz4p, DAEO-2bdu, DAEO-f58b, DAEO-rmhj]
acceptance_tests: {path: tests/acceptance/W2-187/}
---

# W2-187 The standing hidden set, judged every week at 95 %, counts only

**Problem.** The memory audit (W2-170 to W2-173) writes a fresh 40 each week and measures each set once; old questions
are re-run only for retrieval figures (the pool), never against the end-to-end bar, and 95 % is printed, not judged
(`src/gov/memaudit/declare.py:32-33`). Its state is one folder per machine with Gov OS's retrieval paths
(`schedule.py:18-22, 48-55`). There is no weekly maintenance job. The owner's MEMORY-AUDIT (a) (2026-11-14; DEC-1177,
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
DEC-1177 (2): about 16 lines of values and helpers. `tests/unit/memaudit/` is the engineer's.

**Rabbit holes.**
- Do not copy the reader path into a second module: one path, two modes.
- Do not print an id "for debugging".
- Do not make the maintenance pass a gate.
- Do not decide the replacement set's content: the writer's brief does.
- Size: about 300-450 lines for G1 and G2, 100-150 for G3, 150-250 for G5, about 20 for S11, plus tests. If the test
  designer's suite shows it larger than about 900 lines, the lead brings a split (S10 and S11 as their own ticket) to the
  CTO before building.
