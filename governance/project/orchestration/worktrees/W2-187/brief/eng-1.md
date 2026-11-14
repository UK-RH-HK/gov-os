Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-187/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# Brief eng-1: engineer for DAEO-0cd2 (W2-187), profile FULL, class C2

You are the engineer for ticket DAEO-0cd2 (W2-187: the memory audit's standing hidden set, judged every week at 95 %,
counts only; the monthly fresh set as the check against fitting; the weekly maintenance pass; the audit's state per
repository; the schedule's code). You build it in `gov.memaudit` to the ticket's `## Interface` section (I1-I12, the
gaps and the CTO's routings G1, G2, U1, U2 at its end), which is binding: you conform to it and never change it. A KPI
you cannot meet within it or within your allowed paths comes back as a package (status PACKAGES: question, options with
cost, recommendation, confidence, what it blocks), never as wider scope or your own invention.

## Where you work
| what | path |
|---|---|
| your tree (write here only) | /home/usain/gov-os-worktrees/W2-187 |
| branch | w2/W2-187 |
| your allowed paths | src/gov/memaudit/**, src/gov/adopt/memory_sets.py, governance/project/orchestration/tools/memaudit_cron.sh, tests/unit/memaudit/**, tests/unit/adopt/test_w2_187*, docs/changes/W2-187-evidence.md |
| the ticket (read it first, whole: KPI lines, Approach, the method, rabbit holes, the Interface at its end) | /home/usain/gov-os-worktrees/W2-187/.tickets/DAEO-0cd2.md |
| the tool you extend (W2-170 to W2-173): keep every existing subcommand's behaviour byte for byte without `--week` and with no live set | src/gov/memaudit/ (`__main__.py`, layout.py, schedule.py, driver.py, declare.py, preflight.py, measure.py, judge.py, figures.py, digest.py, pool.py, fault.py, matcher.py, common.py, say.py, prompts.py); their Interfaces .tickets/DAEO-61vm.md, DAEO-k1e2.md, DAEO-p8tv.md, DAEO-qz4p.md |
| A9's ACT package | src/gov/adopt/memory_sets.py (`walls_act`); `fabric.py` stays unchanged |
| W2-138's store commit field, W2-116's integration rebuild, the links command, the store layout, lexical keep-out | src/gov/retrieval/measure.py, src/gov/retrieval/retrieve.py, src/gov/rebuild/integration.py, src/gov/links/command.py, src/gov/store/layout.py, src/gov/retrieval/lexical.py |
| the launch script (never changed; the AUDITS.log form, `$GOV_INDEP_RUNS_DIR/indep/`) | governance/project/orchestration/tools/indep_launch.py |
| the package and the reconciliation | governance/project/orchestration/packages/MEMORY-AUDIT-P1.md (§2, §5), MEMORY-AUDIT-1.md, LIFT-1/FRESH-80-1.md (§3.1, §3.5) |
| the existing suites that must stay green (read them, never edit them) | tests/acceptance/W2-170/, W2-171/, W2-172/, W2-173/, W2-88/, tests/unit/memaudit/ |
| the sources (read each by id in docs/DECISION_REGISTER.md; grep the register only by id) | DEC-1179, DEC-1176, DEC-1101, DEC-1125, DEC-1098, DEC-1097, DEC-1092, DEC-1074, DEC-1072, DEC-1178, DEC-1156 |

Search with the Read, Grep and Glob tools; if the first search does not answer, search once more in different words,
then answer from both or say "not found" (DEC-1065). No `gov retrieve`, no `gov context` in the sandbox.

## Held-out rules (DEC-820)
Never open the real sets root (`~/gov-os-eval`), the real runs folder (`~/gov-os-runs`, and never any `indep/` folder
under it), any hidden half or memory-verdict folder, the real crontab. Never run a real model call, a real search or the
real launch script against real sets. Never print a question id, question, answer, path or span of any hidden set; do
not print an id "for debugging".

The ticket's context packet (`gov context DAEO-0cd2 --role engineer`, built by your lead from the integration store)
follows; its `ticket_text` is the same ticket file as above.

----

{
  "ticket": "DAEO-0cd2",
  "ticket_text": "---\nid: DAEO-0cd2\nwbs_id: W2-187\nexternal-ref: W2-187\ntitle: \"The standing hidden set: each repository's memory judged end to end every week on the same questions at 95 %, counts only, with a monthly fresh set as the check against fitting, a weekly maintenance pass, and the audit's state per repository (MEMORY-AUDIT G1, G2, G3, G5 and G4's code)\"\ntype: task\nclass: implementation\nrole: engineer\nprofile: FULL\nstatus: open\nstate_class: AUTHORITATIVE\npriority: 1\ncreated: 2026-11-14\ndeps: [DAEO-f58b, DAEO-rmhj]\nallowed_paths:\n- src/gov/memaudit/**\n- src/gov/adopt/memory_sets.py\n- governance/project/orchestration/tools/memaudit_cron.sh\n- tests/unit/memaudit/**\n- tests/unit/adopt/test_w2_187*\n- tests/acceptance/W2-170/test_w2_170_s3_declare.py\n- tests/acceptance/W2-170/w2_170_world.py\n- tests/acceptance/W2-171/test_w2_171_s3_judge.py\n- tests/acceptance/W2-171/w2_171_world.py\n- tests/acceptance/W2-171/w2_171_scenario.py\n- tests/acceptance/W2-172/test_w2_172_s7_digest.py\n- docs/changes/W2-187-evidence.md\n- docs/probes/DAEO-0cd2/**\nreads:\n- .gov-runtime/scratch/orchestrator/drafts/memory-scope-20261113/MEMORY-AUDIT.md\n- .gov-runtime/scratch/orchestrator/governance/project/orchestration/packages/MEMORY-AUDIT-P1.md\n- governance/project/orchestration/packages/MEMORY-AUDIT-1.md\n- governance/project/orchestration/packages/LIFT-1/FRESH-80-1.md\n- governance/project/orchestration/packages/LIFT-1/E3-RESULT.md\n- governance/project/orchestration/packages/LIFT-1/E3-SA-RESULT.md\n- src/gov/retrieval/measure.py\n- src/gov/rebuild/integration.py\n- src/gov/links/command.py\n- src/gov/adopt/**\n- tests/acceptance/W2-170/**\n- tests/acceptance/W2-171/**\n- tests/acceptance/W2-172/**\n- tests/acceptance/W2-173/**\n- tests/acceptance/W2-88/**\nneeds:\n- src/gov/rebuild/integration.py\n- src/gov/retrieval/retrieve.py\nwaits_on:\n- ref: DAEO-f58b\n  reason: 'the maintenance pass brings the store to the main line''s head through W2-116''s double-buffered integration store (closed)'\n- ref: DAEO-rmhj\n  reason: 'the standing run checks each search result''s store commit (W2-138''s field) against the declared store; the maintenance pass reads it'\nest_loc: 700\nkpis:\n  success:\n  - 'S1 A standing set: `python3 -m gov.memaudit standing declare --set <name> --repo <dir>` records one standing set for the repository: its name, its digest (`LC_ALL=C sha256sum *.yaml | sha256sum` over the kept questions), n with the nonexistent-id questions apart, the sha256 of the writer''s and checker''s briefs, and the commit it was written at. A set whose questions were ever written to a `misses.jsonl` or read by an auditor is refused (`STANDING_SPENT`); an adopted repository''s Wave 0 verdict set is accepted once its `USED` marker and its counts-only result record exist (W2-88 S13, S16). One standing set is live per repository; a second is refused until the first is retired [DEC-1179 (1), DEC-1176 (1), DEC-1098 (1)] Verify: planted sets: a new set is recorded with each field; a set with a planted `misses.jsonl` line is refused with `STANDING_SPENT`; a planted Wave 0 verdict set with `USED` and its record is accepted; a second live set is refused'\n  - 'S2 One judged run a week: a standing run writes `runs/<set>/<ISO year>-W<week>/DECLARATION.json` and then `USED`, before any search; a second judged run of the same set in the same ISO week exits 3 and writes nothing. A run stopped by the fault rule (FRESH-80-1 \u00a73.5, `STOPPED <cause>`) before its reader run started may start once more that week; a run whose reader run started never runs again [DEC-1179 (1), DEC-1097 (1)(g)] Verify: planted runs: the file times and the ledger line show DECLARATION.json before USED before the first search; a second run the same week exits 3 with the tree byte-identical; a planted STOPPED before the reader run allows one restart and a second is refused'\n  - 'S3 The same method as Gov OS''s memory: a standing run uses the fresh 80''s judged path unchanged: the store at the audit commit with the standard (the 0.6B through the one shared reranker, the pool on, the 6,000-token bundle widened to sections); each question''s first bundle from `gov.retrieval.measure`; `judge`''s reader run as built (the pinned `prompts.py`, the reader, the cap, the A2 cut judged, A1 and A3 as data); the named grader with the second grader''s agreement; the measure''s matcher with source families. Every search result''s store commit (W2-138) equal to the declared store''s commit, else that attempt is a fault [DEC-1179 (1), DEC-1097 (1)(a), DEC-1098 (1), DEC-1092 (1)] Verify: `tests/unit/memaudit/test_prompts.py` passes unchanged; a planted standing run calls the same reader, grader and matcher functions as a fresh run (one shared code path, asserted by a spy); a planted result from another store commit makes the attempt a fault'\n  - 'S4 Counts only: a standing run writes no `misses.jsonl` and launches no auditor. Only counts leave its run folder: right end to end, wrong claims, not found, the misses by outcome (wrong, incomplete, not found) and by the first gold place''s rank in the first bundle (1-5, 6-20, absent), the questions dropped by the anchor check, and the figures beside (hit@5, gold in the first bundle, A1 against A2 with exact McNemar). No question id, question, gold, answer or citation of the standing set is printed, logged, written to `FIGURES.json`, `HISTORY.jsonl`, `AUDITS.log` or the digest block, or written outside its run folder (mode 0700) [DEC-1179 (2), DEC-1101 (2), DEC-1074 (1)] Verify: a planted standing run with five planted misses whose ids and texts are unique strings: no planted string appears in stdout, stderr, FIGURES.json, HISTORY.jsonl, AUDITS.log, the digest block or any file outside the run folder; no misses.jsonl exists; no auditor launch event is in the ledger'\n  - 'S5 The bar at 95 %: `declare.bar(n)` gives `need_right = ceil(95 n / 100)` and `max_wrong = floor(5 n / 100)`; a verdict passes when right end to end at A2 reaches `need_right` (wrong claims stay reported and checked). It applies to standing and fresh runs alike, and the declaration''s rounding text says so. On 80 judged that is 76, on 79 it is 76, on 40 it is 38 [DEC-1179 (2), DEC-1097 (1)(d) as carried forward, DEC-957] Verify: unit cases n = 40, 79, 80 give 38, 76, 76; a planted run with right = need_right - 1 is a miss and with right = need_right a pass; the digest''s bar line prints the new figure; the revised W2-170, W2-171 and W2-172 cases pass, and W2-88''s S15 bar case (which reads W2-170''s helper `bar`) passes unedited'\n  - 'S6 Staleness by count: before each standing run the pre-flight checks each question''s gold anchors at the audit commit; a question whose anchor no longer resolves, or whose nonexistent id now exists, is dropped from that week''s n and counted (`dropped k`); nothing in the set is edited. Fewer than 70 live questions prints `STANDING_THIN <live>` in the digest block and asks for a replacement [DEC-1179 (2), DEC-1097 (1)(f)] Verify: a planted set of 80 with 3 broken anchors: n is 77 and `dropped 3` is printed with no id; the set''s digest is unchanged after the run; a planted set with 69 live questions prints STANDING_THIN 69'\n  - 'S7 The monthly check against fitting: at each fresh run the tool compares the fresh set''s right end to end per cent F with S, the mean of the standing set''s last four weekly figures; S - F of 5 points or more writes `STANDING_FITTED` in HISTORY.jsonl and the digest block, retires the standing set (no further standing run on it; it joins the pool as a diagnostic set, counts only) and asks for the writer''s replacement; F - S of 5 points or more writes `STANDING_STALE` and asks for the checker''s staleness pass; with fewer than four weekly figures the check prints `drift: not yet (k of 4)` [DEC-1179 (3), DEC-1074 (4)] Verify: planted histories: S 96, F 90 retires the set and a later standing run on it is refused; S 90, F 96 prints STANDING_STALE; S 95, F 92 prints no flag; two weekly figures print `drift: not yet (2 of 4)`'\n  - 'S8 The two cadences and below 95 %: the standing set''s cadence is W2-172 S5''s computed rule, unchanged (weekly while active, monthly once stable, back to weekly at once on a miss, a retrieval change, churn of 10 % or more or a pool regression); the fresh set is due on the first Monday 28 days or more after the last fresh run. A standing miss is a HISTORY line `miss` with its counts; the fresh set is then due at the next Monday and every Monday until a standing run passes again (then every 28 days); the maintenance pass (S10) runs at once after the miss in the same cycle; the digest block carries a `P1 memory below 95 %` line with the counts by class. Two consecutive standing misses, or one miss 5 points or more below the last passing figure, write `MEMORY_REPAIR open` in HISTORY.jsonl, and `gov.memaudit status --repair` exits 1 while it is open and 0 once a later standing run passes or the owner''s decision id is given with `--residual DEC-<n>` [DEC-1179 (4), (5), DEC-1125 (2)] Verify: `tests/acceptance/W2-172/test_w2_172_s5_due.py` passes unchanged for the standing set; a planted fresh history 27 days old is not due and 28 days old is due on the Monday; planted histories: one miss makes the fresh set due next Monday and puts the P1 line in the digest; pass, miss, miss opens the repair; pass at 96 then miss at 90 opens it; `status --repair` exits 1, then 0 after a planted pass or `--residual DEC-1`'\n  - 'S9 State per repository: the runs folder is `<runs>/indep/memaudit/<key>/` with `<key>` the repository''s directory name, a hyphen and the first 8 hex of the sha256 of its real path, so two repositories on one machine keep separate `AUDITS.log`, `HISTORY.jsonl` and `STARTS.log`. The retrieval change that sends an audit back to weekly is, for any repository, a change of the gov pin, of the repository''s `governance/project/retrieval.yaml` digest or of its path map''s digest, and for Gov OS also its six retrieval globs. `pool-import --sets <name>...` seeds the pool from that repository''s own sets root; with no `--sets` on Gov OS it imports Gov OS''s 79 and 138 as today [DEC-1179 (5), DEC-1101 (1), DEC-1125 (2)] Verify: two planted repositories on one runs folder write to two keys and neither reads the other''s history; a planted pin change on an adopted repository is a retrieval change and a change under `src/gov/retrieval/` of Gov OS is not, for it; `pool-import --sets a b` imports exactly those sets'\n  - 'S10 One weekly maintenance pass before each standing run, `python3 -m gov.memaudit maintain --repo <dir>`: (1) the integration store at the main line''s head, else one refresh by W2-116''s `gov rebuild --integration`, a failed build leaving the last good store in service and named; (2) the store''s layout current, else one `gov rebuild`; (3) `gov links --since <the last pass''s commit>`: the count of new findings; (4) the count of tracked paths the path map indexes but the store holds no chunk of; (5) the standing and fresh runs'' reader `not found` answers and second searches, counted; (6) the list of gold questions whose cited lines changed at the audit commit (W2-61h S4''s list: question id and entry number only, never a question, answer or path) handed to the walled writer''s request for re-anchoring or rewording, counted. It prints six counts in the digest block, never fails or delays the audit, and never changes one of the standard''s four settings [DEC-1179 (6), DEC-1178 (1), DEC-1072 (1), DEC-1101 (1), DEC-1096] Verify: a planted repository with a store 3 commits behind is refreshed once and the head printed; a planted failing rebuild keeps the old store and names the failure; planted link findings and two unindexed paths are counted; the audit runs whatever the pass finds; the retrieval.yaml digest is unchanged after the pass; a planted set with one changed cited block and one moved unchanged block lists only the changed one, by question id and entry number, in the writer''s request, with no question, answer or path text in it or in the digest'\n  - 'S11 The schedule''s code (G4): `memaudit_cron.sh` takes `--repo <dir>` and runs, when due, the maintenance pass, the standing run and, when the fresh set is due, the fresh cycle, in that order, within the gate''s wait (W2-172 S9); A9''s ACT package (`memory_sets.walls_act`) adds one step to its ACT.md with the repository''s cron line (the wrapper with `--repo <that repository>`, Mondays 21:00), written as text for the repository''s owner''s operator and never installed [DEC-1179 (5), DEC-1101 (2), W2-88 S22] Verify: a planted due standing run and a due fresh set run in that order from one wrapper call; nothing runs when neither is due; a planted A9 run''s ACT.md holds the cron line with the repository''s path and no crontab is changed'\n  failure:\n  - 'F1 A standing set''s question id, question, gold, answer or citation outside its run folder, or read by any session: the auditor, the CTO, a worker or a later fix. Verify: S4''s planted strings are absent from every file written outside the run folder and from every launched session''s brief; no code path hands a standing run''s rows to `classes`, the auditor''s launch or the pool''s fix judging'\n  - 'F2 A standing set judged twice in one week, judged without DECLARATION.json and USED first, re-scored, or its labels changed after a figure exists. Verify: S2''s planted runs; `measure --kept` on a standing run exits 3 and writes nothing; the set''s digest is checked equal at every run and a planted edit is refused before any search'\n  - 'F3 The standing set used to choose, adopt or reject a fix or a configuration. Verify: the tool offers no command that compares two configurations or two commits on a standing set; the standing run refuses `--decision` and any data condition'\n  - 'F4 The method drifts: the reader or grader prompt, model, cap or A2 cut changed, or the standing path diverges from the fresh path. Verify: `test_prompts.py` passes unchanged; S3''s spy'\n  - 'F5 A fresh set''s use-once behaviour changes. Verify: W2-170''s S3 and F2 cases on fresh sets pass with only their bar values revised; W2-171''s S5 case passes unchanged'\n  - 'F6 The maintenance pass changes a setting of the standard, applies an ACT, installs a cron line or stops the audit. Verify: S10''s planted runs; the module imports no crontab writer and the retrieval.yaml and path map digests are unchanged after a pass'\nnon_goals:\n- 'no new measuring method: the standing run reuses the fresh 80''s judged path as W2-170 to W2-173 built it'\n- 'no change to the adopt skill or the practice record (W2-188), and no `.claude/` copy'\n- 'no cron line installed and no walls or path-map change applied: those are ACT-MEMORY-AUDIT-CRON-1 for Gov OS (the CTO''s ACT) and each adopted repository''s own ACT package'\n- 'no writing of the standing set: the independent writer and checker write it under the owner''s approved brief'\n- 'no change to the release step or the re-pin ACT: they read `status --repair` (the CTO''s ACT text)'\n- 'no DEC-1101 (1) count of \"not found\" answers from agents'' work returns: the pass counts the audit runs'' own; the work-returns count stays the CTO''s tool until a decision gives it a product home'\ndone_when: [DOD-1, DOD-2, DOD-3, DOD-4, DOD-5, DOD-6]\nsources: [DEC-1179, DEC-1176, DEC-1101, DEC-1125, DEC-1126, DEC-1098, DEC-1097, DEC-1092, DEC-1074, DEC-1071, DEC-1072, DEC-1156, DEC-974, DEC-105, DAEO-61vm, DAEO-k1e2, DAEO-p8tv, DAEO-qz4p, DAEO-2bdu, DAEO-f58b, DAEO-rmhj]\nacceptance_tests: {path: tests/acceptance/W2-187/}\n---\n\n# W2-187 The standing hidden set, judged every week at 95 %, counts only\n\n**Problem.** The memory audit (W2-170 to W2-173) writes a fresh 40 each week and measures each set once; old questions\nare re-run only for retrieval figures (the pool), never against the end-to-end bar, and 95 % is printed, not judged\n(`src/gov/memaudit/declare.py:32-33`). Its state is one folder per machine with Gov OS's retrieval paths\n(`schedule.py:18-22, 48-55`). There is no weekly maintenance job. The owner's MEMORY-AUDIT (a) (2026-11-14; DEC-1179,\nprovisional) wants each repository's memory judged end to end every week on the same hidden questions, as Gov OS's was\nmeasured, at 95 %, counts only, with a monthly fresh set as the check against fitting. The reconciliation, with file and\nline for each part, is `drafts/memory-scope-20261113/MEMORY-AUDIT.md` \u00a72 and \u00a73 (G1, G2, G3, G5).\n\n**Approach.** A `standing` mode beside the fresh mode in `gov.memaudit`, sharing its judged path. What differs:\n- the per-week marker instead of the per-set lock (S2);\n- no `misses.jsonl` and no auditor, counts only (S4);\n- the pre-flight's anchor check drops by count (S6);\n- the drift comparison at each fresh run (S7);\n- the below-95 states (S8).\n\nThe bar function changes for both modes (S5). The runs folder is keyed by repository (S9). `maintain` calls the\nexisting checks (S10). The wrapper and A9's ACT text carry the schedule (S11).\n\n**The method, exactly (S3; what \"double search, agents as second rerankers\" means here).** The fresh 80's judged\nconfiguration (FRESH-80-1 \u00a73.1, DEC-1097 (1)(a), accepted by DEC-1098 (1) at 78 of 79):\n- the store with the standard;\n- the first bundle from W2-61's measure (`gov.retrieval.measure`, 6,000 tokens, items widened to sections);\n- the reader reads the whole ranked bundle and decides what answers, a second ranking after the 0.6B (E3: 114 of 138 in\n  one call, against 84 for the top 5 and 101 for 40 unranked);\n- it may search again once with its own words, the A2 cut (E2: 115 at one search, 128 at two; E3-SA: a second search\n  never lost a right answer);\n- graded by the named grader, with the second grader's agreement;\n- the citation checked by the measure's matcher.\n\n\"A second reranker\" in W2-88 S10 and its failure line means a second reranking model; it stays forbidden, and the\nreader is not one.\n\n**Test revisions (decided behaviour, DEC-1156 (7)).** S5 changes the bar the W2-170, W2-171 and W2-172 cases pin (85 %).\nThe ticket's independent test designer revises exactly the six files in `allowed_paths`, with a `Rewrite-Reason` naming\nDEC-1179 (2): about 16 lines of values and helpers. `tests/unit/memaudit/` is the engineer's.\n\n**Rabbit holes.**\n- Do not copy the reader path into a second module: one path, two modes.\n- Do not print an id \"for debugging\".\n- Do not make the maintenance pass a gate.\n- Do not decide the replacement set's content: the writer's brief does.\n- Size: about 300-450 lines for G1 and G2, 100-150 for G3, 150-250 for G5, about 20 for S11, plus tests. If the test\n  designer's suite shows it larger than about 900 lines, S10 and S11 split off as W2-187b, pre-approved by the owner\n  (DEC-1179, O8 (a)): the lead tells the CTO, who files it, and nobody waits for a P1.\n\n**Filed 2026-11-14 on the owner's decision (DEC-1179, MEMORY-AUDIT-P1; O3 (b): S8's cadence is W2-172 S5's computed rule, unchanged).** S10 gains a sixth item from DEC-1178 (1): the list of gold questions whose cited lines changed, for the walled writer, which the owner's operator handles in the Monday slot until this ticket lands.\n",
  "authority": [
    {
      "id": "DEC-1179",
      "sha256": "1e8a43d29a1e95f8035f6687d2da5a27c2991b8c9f3a61d6e5b61354061f0c54",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "1e8a43d29a1e95f8035f6687d2da5a27c2991b8c9f3a61d6e5b61354061f0c54",
      "reason": "declared in sources",
      "tokens": 6606
    },
    {
      "id": "DEC-1176",
      "sha256": "cd714551d522eee60ef1585e138e5108dba585ac574c5a5eb3893cbc5a1d1751",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "cd714551d522eee60ef1585e138e5108dba585ac574c5a5eb3893cbc5a1d1751",
      "reason": "declared in sources",
      "tokens": 1994
    },
    {
      "id": "DEC-1101",
      "sha256": "b6565d2ce8443f5ba7bc21aa29882da61c5303dc9119b83c43247ccbfc8b3f95",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "b6565d2ce8443f5ba7bc21aa29882da61c5303dc9119b83c43247ccbfc8b3f95",
      "reason": "declared in sources",
      "tokens": 884
    },
    {
      "id": "DEC-1125",
      "sha256": "5a826a6d8b70da46067c51dbcc12ecee8b8113a8264f98bd2f21a7319bd8a874",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "5a826a6d8b70da46067c51dbcc12ecee8b8113a8264f98bd2f21a7319bd8a874",
      "reason": "declared in sources",
      "tokens": 954
    },
    {
      "id": "DEC-1126",
      "sha256": "d52aee2baf9e3733badf9e1bc0795da3ec4b2f00ef6118390387794c69b1f68d",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "d52aee2baf9e3733badf9e1bc0795da3ec4b2f00ef6118390387794c69b1f68d",
      "reason": "declared in sources",
      "tokens": 667
    },
    {
      "id": "DEC-1098",
      "sha256": "e5432f2700d05ae8bbc03609187a8a5e08f08b70105bc4f11e8e97730c4c94ee",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "e5432f2700d05ae8bbc03609187a8a5e08f08b70105bc4f11e8e97730c4c94ee",
      "reason": "declared in sources",
      "tokens": 886
    },
    {
      "id": "DEC-1097",
      "sha256": "9a368306f2d766cf446887d4dcf8ca97bef125b49517058fd278b7c7b32f1135",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "9a368306f2d766cf446887d4dcf8ca97bef125b49517058fd278b7c7b32f1135",
      "reason": "declared in sources",
      "tokens": 1535
    },
    {
      "id": "DEC-1092",
      "sha256": "c1327f6bb3056c181e8788c4fe081d7532ebd280666f4a923a28eb2e8a337139",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "c1327f6bb3056c181e8788c4fe081d7532ebd280666f4a923a28eb2e8a337139",
      "reason": "declared in sources",
      "tokens": 564
    },
    {
      "id": "DEC-1074",
      "sha256": "fc0e27770674570700adaecd19746a45f3530a9d00bd501a08071fced78b810b",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "fc0e27770674570700adaecd19746a45f3530a9d00bd501a08071fced78b810b",
      "reason": "declared in sources",
      "tokens": 903
    },
    {
      "id": "DEC-1071",
      "sha256": "468aa847b29812505c2966b6bd132211008e7137015b6a1dfab93c91ecde2065",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "468aa847b29812505c2966b6bd132211008e7137015b6a1dfab93c91ecde2065",
      "reason": "declared in sources",
      "tokens": 771
    },
    {
      "id": "DEC-1072",
      "sha256": "76ab4c349512b436a54241cb5817eddbcc072af662f52a31ac725b005c2d45e5",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "76ab4c349512b436a54241cb5817eddbcc072af662f52a31ac725b005c2d45e5",
      "reason": "declared in sources",
      "tokens": 710
    },
    {
      "id": "DEC-1156",
      "sha256": "ae45fec87ddb5ad969cad9abbb5ec5ef4652208564394a7722aaf36c8b62db32",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "ae45fec87ddb5ad969cad9abbb5ec5ef4652208564394a7722aaf36c8b62db32",
      "reason": "declared in sources",
      "tokens": 1068
    },
    {
      "id": "DEC-974",
      "sha256": "18b68361216a317b57e2fa5b15932f2732fa8894e9e68185549626d74c208e30",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "18b68361216a317b57e2fa5b15932f2732fa8894e9e68185549626d74c208e30",
      "reason": "declared in sources",
      "tokens": 642
    },
    {
      "id": "DEC-105",
      "sha256": "69bdb3db50cfc9270b6d3cd1f648b8616d0bc8bb370a6c868ba76614d4a46126",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "69bdb3db50cfc9270b6d3cd1f648b8616d0bc8bb370a6c868ba76614d4a46126",
      "reason": "declared in sources",
      "tokens": 211
    },
    {
      "id": "DAEO-61vm",
      "sha256": "838076d20592cc01b7d21caf6ce5cbef0e9ee2a2c44dd05df03042e8acbe7b6c",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "838076d20592cc01b7d21caf6ce5cbef0e9ee2a2c44dd05df03042e8acbe7b6c",
      "reason": "declared in sources",
      "tokens": 8838
    },
    {
      "id": "DAEO-k1e2",
      "sha256": "85b0e20e6d1e5410459798110c058500bf447d7bb068e6fefe2b0d376f0e6877",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "85b0e20e6d1e5410459798110c058500bf447d7bb068e6fefe2b0d376f0e6877",
      "reason": "declared in sources",
      "tokens": 8114
    },
    {
      "id": "DAEO-p8tv",
      "sha256": "880033516602ec801a638d825f28244c9394fa27818d23814032f8dce41f16ed",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "880033516602ec801a638d825f28244c9394fa27818d23814032f8dce41f16ed",
      "reason": "declared in sources",
      "tokens": 6860
    },
    {
      "id": "DAEO-qz4p",
      "sha256": "20b6817806e4939fe383b416c423c74c0613fd78c6536136d2a127157cac9101",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "20b6817806e4939fe383b416c423c74c0613fd78c6536136d2a127157cac9101",
      "reason": "declared in sources",
      "tokens": 2119
    },
    {
      "id": "DAEO-2bdu",
      "sha256": "6ad76eb296cdc5f9e1774d9f20dbdfae3c982fd1f1623a34f7ecffb37efb8987",
      "authority": "task",
      "lifecycle": "in_progress",
      "constraint": "6ad76eb296cdc5f9e1774d9f20dbdfae3c982fd1f1623a34f7ecffb37efb8987",
      "reason": "declared in sources",
      "tokens": 13611
    },
    {
      "id": "DAEO-f58b",
      "sha256": "6a9d30f9924da8831da6f2f858dd745bdba9ca8645aa68d30afab17ab2261c2d",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "6a9d30f9924da8831da6f2f858dd745bdba9ca8645aa68d30afab17ab2261c2d",
      "reason": "declared in sources",
      "tokens": 1049
    },
    {
      "id": "DAEO-rmhj",
      "sha256": "e114ef4c956e07648b2107cfed1ff07f7049d98a09563f6c5214eed163e72649",
      "authority": "task",
      "lifecycle": "in_progress",
      "constraint": "e114ef4c956e07648b2107cfed1ff07f7049d98a09563f6c5214eed163e72649",
      "reason": "declared in sources",
      "tokens": 506
    }
  ],
  "mandatory": [
    {
      "id": "DEC-1179",
      "sha256": "1e8a43d29a1e95f8035f6687d2da5a27c2991b8c9f3a61d6e5b61354061f0c54",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "1e8a43d29a1e95f8035f6687d2da5a27c2991b8c9f3a61d6e5b61354061f0c54",
      "reason": "declared in sources",
      "tokens": 6606
    },
    {
      "id": "DEC-1176",
      "sha256": "cd714551d522eee60ef1585e138e5108dba585ac574c5a5eb3893cbc5a1d1751",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "cd714551d522eee60ef1585e138e5108dba585ac574c5a5eb3893cbc5a1d1751",
      "reason": "declared in sources",
      "tokens": 1994
    },
    {
      "id": "DEC-1101",
      "sha256": "b6565d2ce8443f5ba7bc21aa29882da61c5303dc9119b83c43247ccbfc8b3f95",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "b6565d2ce8443f5ba7bc21aa29882da61c5303dc9119b83c43247ccbfc8b3f95",
      "reason": "declared in sources",
      "tokens": 884
    },
    {
      "id": "DEC-1125",
      "sha256": "5a826a6d8b70da46067c51dbcc12ecee8b8113a8264f98bd2f21a7319bd8a874",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "5a826a6d8b70da46067c51dbcc12ecee8b8113a8264f98bd2f21a7319bd8a874",
      "reason": "declared in sources",
      "tokens": 954
    },
    {
      "id": "DEC-1126",
      "sha256": "d52aee2baf9e3733badf9e1bc0795da3ec4b2f00ef6118390387794c69b1f68d",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "d52aee2baf9e3733badf9e1bc0795da3ec4b2f00ef6118390387794c69b1f68d",
      "reason": "declared in sources",
      "tokens": 667
    },
    {
      "id": "DEC-1098",
      "sha256": "e5432f2700d05ae8bbc03609187a8a5e08f08b70105bc4f11e8e97730c4c94ee",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "e5432f2700d05ae8bbc03609187a8a5e08f08b70105bc4f11e8e97730c4c94ee",
      "reason": "declared in sources",
      "tokens": 886
    },
    {
      "id": "DEC-1097",
      "sha256": "9a368306f2d766cf446887d4dcf8ca97bef125b49517058fd278b7c7b32f1135",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "9a368306f2d766cf446887d4dcf8ca97bef125b49517058fd278b7c7b32f1135",
      "reason": "declared in sources",
      "tokens": 1535
    },
    {
      "id": "DEC-1092",
      "sha256": "c1327f6bb3056c181e8788c4fe081d7532ebd280666f4a923a28eb2e8a337139",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "c1327f6bb3056c181e8788c4fe081d7532ebd280666f4a923a28eb2e8a337139",
      "reason": "declared in sources",
      "tokens": 564
    },
    {
      "id": "DEC-1074",
      "sha256": "fc0e27770674570700adaecd19746a45f3530a9d00bd501a08071fced78b810b",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "fc0e27770674570700adaecd19746a45f3530a9d00bd501a08071fced78b810b",
      "reason": "declared in sources",
      "tokens": 903
    },
    {
      "id": "DEC-1071",
      "sha256": "468aa847b29812505c2966b6bd132211008e7137015b6a1dfab93c91ecde2065",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "468aa847b29812505c2966b6bd132211008e7137015b6a1dfab93c91ecde2065",
      "reason": "declared in sources",
      "tokens": 771
    },
    {
      "id": "DEC-1072",
      "sha256": "76ab4c349512b436a54241cb5817eddbcc072af662f52a31ac725b005c2d45e5",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "76ab4c349512b436a54241cb5817eddbcc072af662f52a31ac725b005c2d45e5",
      "reason": "declared in sources",
      "tokens": 710
    },
    {
      "id": "DEC-1156",
      "sha256": "ae45fec87ddb5ad969cad9abbb5ec5ef4652208564394a7722aaf36c8b62db32",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "ae45fec87ddb5ad969cad9abbb5ec5ef4652208564394a7722aaf36c8b62db32",
      "reason": "declared in sources",
      "tokens": 1068
    },
    {
      "id": "DEC-974",
      "sha256": "18b68361216a317b57e2fa5b15932f2732fa8894e9e68185549626d74c208e30",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "18b68361216a317b57e2fa5b15932f2732fa8894e9e68185549626d74c208e30",
      "reason": "declared in sources",
      "tokens": 642
    },
    {
      "id": "DEC-105",
      "sha256": "69bdb3db50cfc9270b6d3cd1f648b8616d0bc8bb370a6c868ba76614d4a46126",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "69bdb3db50cfc9270b6d3cd1f648b8616d0bc8bb370a6c868ba76614d4a46126",
      "reason": "declared in sources",
      "tokens": 211
    },
    {
      "id": "DAEO-61vm",
      "sha256": "838076d20592cc01b7d21caf6ce5cbef0e9ee2a2c44dd05df03042e8acbe7b6c",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "838076d20592cc01b7d21caf6ce5cbef0e9ee2a2c44dd05df03042e8acbe7b6c",
      "reason": "declared in sources",
      "tokens": 8838
    },
    {
      "id": "DAEO-k1e2",
      "sha256": "85b0e20e6d1e5410459798110c058500bf447d7bb068e6fefe2b0d376f0e6877",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "85b0e20e6d1e5410459798110c058500bf447d7bb068e6fefe2b0d376f0e6877",
      "reason": "declared in sources",
      "tokens": 8114
    },
    {
      "id": "DAEO-p8tv",
      "sha256": "880033516602ec801a638d825f28244c9394fa27818d23814032f8dce41f16ed",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "880033516602ec801a638d825f28244c9394fa27818d23814032f8dce41f16ed",
      "reason": "declared in sources",
      "tokens": 6860
    },
    {
      "id": "DAEO-qz4p",
      "sha256": "20b6817806e4939fe383b416c423c74c0613fd78c6536136d2a127157cac9101",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "20b6817806e4939fe383b416c423c74c0613fd78c6536136d2a127157cac9101",
      "reason": "declared in sources",
      "tokens": 2119
    },
    {
      "id": "DAEO-2bdu",
      "sha256": "6ad76eb296cdc5f9e1774d9f20dbdfae3c982fd1f1623a34f7ecffb37efb8987",
      "authority": "task",
      "lifecycle": "in_progress",
      "constraint": "6ad76eb296cdc5f9e1774d9f20dbdfae3c982fd1f1623a34f7ecffb37efb8987",
      "reason": "declared in sources",
      "tokens": 13611
    },
    {
      "id": "DAEO-f58b",
      "sha256": "6a9d30f9924da8831da6f2f858dd745bdba9ca8645aa68d30afab17ab2261c2d",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "6a9d30f9924da8831da6f2f858dd745bdba9ca8645aa68d30afab17ab2261c2d",
      "reason": "declared in sources",
      "tokens": 1049
    },
    {
      "id": "DAEO-rmhj",
      "sha256": "e114ef4c956e07648b2107cfed1ff07f7049d98a09563f6c5214eed163e72649",
      "authority": "task",
      "lifecycle": "in_progress",
      "constraint": "e114ef4c956e07648b2107cfed1ff07f7049d98a09563f6c5214eed163e72649",
      "reason": "declared in sources",
      "tokens": 506
    }
  ],
  "supplementary": [
    {
      "id": "b43d3fbced602d7011fddd95",
      "path": "docs/changes/W2-172-evidence.md",
      "text": "## Per KPI line\n\nThe acceptance files are named for the KPI line they serve; the engineer reads their names and results only.\n\n| KPI | acceptance file | result |\n|---|---|---|\n| S1 | `test_w2_172_s1_cycle.py` | passes |\n| S2, S4 | `test_w2_172_s2_s4_refusals.py` | passes, except `test_s4_a_second_start_on_the_same_date_is_refused_rn_name_and_writes_nothing_there`: awaiting the test designer's revision (it plants the folder and no `STARTS.log` line; TD-2 (b) judges RN-NAME by `STARTS.log`) |\n| S3 | `test_w2_172_s3_stops.py` | passes |\n| S5 | `test_w2_172_s5_due.py` | passes |\n| S6 | `test_w2_172_s6_baseline.py` | passes |\n| S7 | `test_w2_172_s7_digest.py` | passes |\n| S8 | `test_w2_172_s8_status.py` | passes |\n| S9 | `test_w2_172_s9_cron_gate.py` | passes |\n| F1, F4 | `test_w2_172_f1_f4_access.py` | passes |\n| F5 | `test_w2_172_f5_paths.py` | passes |\n\n",
      "tokens": 216
    },
    {
      "id": "a7840d80200c6984ef13ae57",
      "path": "tests/acceptance/W2-172/README.md",
      "text": "| S1 | `test_w2_172_s1_cycle.py::test_s1_a_set_with_revisions_runs_the_twelve_steps_in_this_order`, `test_w2_172_s1_cycle.py::test_s1_a_clean_set_goes_straight_from_the_first_checker_to_the_measure`, `test_w2_172_s1_cycle.py::test_s1_every_launch_line_names_only_the_sets_root_the_brief_and_its_hash_at_the_audit_commit`, `test_w2_172_s1_cycle.py::test_s1_the_printed_command_lines_hold_no_folder_of_the_sets_root`, `test_w2_172_s1_cycle.py::test_s1_the_auditor_runs_also_when_there_is_no_miss_with_an_empty_misses_file`, `test_w2_172_s1_cycle.py::test_s1_the_auditor_gets_the_judges_misses`, `test_w2_172_s1_cycle.py::test_s1_the_children_are_kept_in_the_audits_folder_and_nothing_a_child_says_is_printed`, `test_w2_172_s1_cycle.py::test_s1_the_second_round_runs_exactly_when_the_first_checkers_counts_say_revise_or_reject`, `test_w2_172_f1_f4_access.py::test_s1_figures_prints_one_json_line_of_numbers_and_writes_nothing`, `test_w2_172_f1_f4_access.py::test_s1_figures_of_an_audit_with_no_files_is_a_json_line_and_exit_0`, `test_w2_172_f1_f4_access.py::test_s1_the_runs_folder_is_never_a_flag_and_the_sets_root_is_required`, `test_w2_172_f1_f4_access.py::test_s1_run_prints_through_say_only_never_a_path_under_the_sets_root`, `test_w2_172_s5_due.py::test_s5_each_new_subcommand_has_a_help_that_exits_0` | `gov.memaudit` has no `run`, `due`, `baseline`, `status` or `figures`: argparse refuses the subcommand (exit 4, `ERROR: UsageError`); no `STEP` line, no ledger, no digest; the staged whole audits give exit 4 where 0 is required |\n",
      "tokens": 385
    },
    {
      "id": "f68422db58a467fbb6d663ae",
      "path": "tests/acceptance/W2-172/README.md",
      "text": "| S5 | `test_w2_172_s5_due.py::test_s5_with_no_audit_yet_it_is_weekly_and_due_for_the_start`, `test_w2_172_s5_due.py::test_s5_fewer_than_three_measured_lines_is_weekly`, `test_w2_172_s5_due.py::test_s5_three_audits_each_stable_with_the_rest_met_is_monthly`, `test_w2_172_s5_due.py::test_s5_only_measured_lines_count_and_only_the_last_three`, `test_w2_172_s5_due.py::test_s5_a_store_link_named_by_rebuild_yaml_on_the_main_line_is_the_default`, `test_w2_172_s5_due.py::test_s5_a_churn_of_40_percent_is_weekly_at_once`, `test_w2_172_s5_due.py::test_s5_churn_of_10_percent_or_more_is_the_trigger_9_is_not`, `test_w2_172_s5_due.py::test_s5_the_paths_the_exclusion_file_names_never_count_in_the_churn`, `test_w2_172_s5_due.py::test_s5_a_change_to_a_retrieval_path_since_the_last_audit_is_weekly_at_once`, `test_w2_172_s5_due.py::test_s5_a_retrieval_change_before_the_last_audit_is_not_a_trigger`, `test_w2_172_s5_due.py::test_s5_a_last_verdict_below_the_bar_is_weekly_at_once`, `test_w2_172_s5_due.py::test_s5_a_last_pool_regression_is_weekly_at_once`, `test_w2_172_s5_due.py::test_s5_one_of_the_last_three_audits_failing_a_condition_keeps_it_weekly`, `test_w2_172_s5_due.py::test_s5_churn_just_under_5_percent_in_each_of_the_three_is_stable`, `test_w2_172_s5_due.py::test_s5_weekly_is_due_after_6_days_not_5`, `test_w2_172_s5_due.py::test_s5_monthly_is_due_after_28_days_not_27`, `test_w2_172_s5_due.py::test_s5_the_exit_code_is_4_on_usage` | no `due`: exit 4 where 0 or 1 is required, no `MODE`/`DUE`/`REASON` lines |\n",
      "tokens": 379
    },
    {
      "id": "4f2f37ed69dba9810dd216a2",
      "path": "governance/project/orchestration/packages/MEMORY-AUDIT-1.md",
      "text": "## 4 The schedule\n- **Weekly: Monday at 21:00**, the machine's clock (Europe/London). It runs for about 3.5 hours and ends near 00:30 (E).\n- **Why Monday 21:00.**\n  - It is clear of the nightly's window (04:00 to 08:00, its check to 09:00) and of the digests (09:00 and 18:00) and the\n    20:00 capacity brief. It ends before the quiet hours (02:00 to 07:30).\n  - A week of merges is in before it, so the \"changed\" half has weight. Its digest block is ready for Tuesday 09:00, with\n    the week's days left to fix, and the next audit, a week later, is the verdict on the fixes (DEC-1101 (1)).\n  - The usage week resets on Sunday at 09:00, so the audit's spend falls early in the week's allowance.\n- **How it runs.** One crontab line starts `memaudit_cron.sh`, which asks `due` and starts the cycle only when an audit is\n  due (W2-172). The cron line never changes when the rhythm does. It is **class (b)** in `class-rules.yaml` (the\n  `crontab` row), not (O): your yes, then the operator agent applies it (ACT-MEMORY-AUDIT-CRON-1, `ACT-DRAFTS.md`).\n  The briefs' install is **class (O)**: your yes, then your operator by hand (ACT-MEMORY-AUDIT-INSTALL-1).\n",
      "tokens": 289
    },
    {
      "id": "69337829cad5dbf8ba5ac291",
      "path": "governance/project/orchestration/packages/MEMORY-AUDIT-1/ACT-DRAFTS.md",
      "text": "## ACT-MEMORY-AUDIT-CRON-1: the weekly line\n- **Class: (b)**, not (O): the `crontab` row of `class-rules.yaml` is class (b), control. The brief that asked for this\n  package said (O); the table decides. By the rule table: the owner's yes, then the operator agent applies it from its\n  queue (as ACT-CLAUDE-COPIES-2 was).\n- **The line** (one added; the crontab's other lines stay as they are):\n  ```\n  0 21 * * 1 /usr/bin/bash /home/usain/Dynamic-Agentic-Engineering-OS/governance/project/orchestration/tools/memaudit_cron.sh >> /home/usain/gov-os-runs/indep/memaudit-cron.out 2>&1  # DEC-1125 (2): the memory audit; `due` decides weekly or monthly\n  ```\n  The machine's clock is Europe/London, as the nightly's.\n- **Before it:** W2-170, W2-171, W2-172 and W2-173 merged; ACT-MEMORY-AUDIT-INSTALL-1 applied; the baseline line written\n  (`python3 -m gov.memaudit baseline`); the dry cycle on planted roots passed (W2-172's evidence).\n- **Undo:** the line removed (a commented copy is kept in the ACT's backup, as DEC-1049's were).\n- **What it does when it fires:** `memaudit_cron.sh` runs `due`; when none is due it logs one line and exits 0; when due\n",
      "tokens": 288
    },
    {
      "id": "c8be5bf3b50c2b232c5f31cc",
      "path": "governance/project/orchestration/packages/MEMORY-AUDIT-P1.md",
      "text": "### 2.3 Around the tickets (the CTO's work, not tickets)\n\n- **ACT-MEMORY-AUDIT-CRON-1** (class (b), crontab), for Gov OS. The CTO builds it after W2-187 merges, and it is\n  reviewed, given the owner's yes and applied by the operator before 11-23. It installs one line: Mondays 21:00,\n  `memaudit_cron.sh --repo <Gov OS>`. That line runs the maintenance pass, the standing run and, when due, the fresh\n  cycle.\n- **The standing set's writer brief variant.** The approved writer brief weights fresh questions toward recent change;\n  the standing set needs a broad sample of about 80. A variant, hashed, goes to the owner for approval (class O,\n  `indep-briefs`; DEC-1101 (2)). Then the independent writer and checker write it, in at most two rounds, before 11-23.\n- **Records** (DEC-851):\n  - DEC-1179 in the register;\n  - \"Changed by: DEC-1179\" on DEC-1074, 1097, 1098, 1101, 1125, 1126 and 1176;\n  - the re-baseline marks of \u00a75.5 on W2-88, W2-170, W2-171 and W2-172;\n  - DECIDED-NOT-DONE rows;\n  - the WBS and plan rows for W2-187 and W2-188;\n  - the next status block naming both tickets with DEC-1179 (DEC-1169 (2)).\n\n",
      "tokens": 280
    },
    {
      "id": "02a4e9dc689b8a8af00f3276",
      "path": "docs/changes/W2-172-evidence.md",
      "text": "## What was built\n\n- `src/gov/memaudit/schedule.py`: the clock seam (`GOV_MEMAUDIT_NOW`), the runs folder rule, the store link and its head,\n  the churn of a commit, the active-and-stable rule (`decide`), and the subcommands `due`, `status` and `baseline`.\n- `src/gov/memaudit/driver.py`: `run` (items 2 to 5): the refusals of item 3, the lock, `STARTS.log`, the twelve steps as\n  child processes, the canary retry, the USED boundary, the gate wait, `HISTORY.jsonl`, `COUNTS.json`.\n- `src/gov/memaudit/digest.py`: the `figures` reader (item 6) and the digest block's twelve lines (item 7).\n- `src/gov/memaudit/__main__.py`: the five new subcommands joined to the parser; the existing subcommands' code is\n  unchanged.\n- `governance/project/orchestration/tools/memaudit_cron.sh`: the cron wrapper (item 8); `grep -c crontab` is 0.\n- `tests/unit/memaudit/test_driver.py`: 11 unit cases (churn, mode rule, `due` at 5/6/27/28 days, the USED boundary,\n  the digest's twelve lines and the \"not reached\" forms, the figures reader).\n\n",
      "tokens": 257
    },
    {
      "id": "5a9e22d58ea68b00e35c61f3",
      "path": "docs/probes/DAEO-p8tv/PR-DAEO-p8tv-round-1.md",
      "text": "# Probe record: W2-172 (DAEO-p8tv), the memory audit's driver and schedule, review round 1\n\n- **What was probed.** Head `f706a77f5b7e` of `w2/W2-172`: the change from `80da3fbcca0d` (the merged red tests). That is\n  the engineer's `bf21edd96` (`run`, `due`, `baseline`, `status`, `figures` in `src/gov/memaudit/driver.py`,\n  `schedule.py`, `digest.py`, `__main__.py`, and `governance/project/orchestration/tools/memaudit_cron.sh`), the engineer's\n  `f989ca89b` (unit tests and `docs/changes/W2-172-evidence.md`), and the test designer's revision `5193add39` for\n  PKG-W2-172-TESTS-1, merged at `f706a77f5`. It was judged against the ticket's KPI lines S1-S9 and F1-F5, its Interface\n  items 1-12 with O1-O4, and the CTO's decision PKG-W2-172-TESTS-1 (GATE-1 (a), TD-1 (b), TD-2 (b)).\n- **Who probed.** A fresh read-only reviewer: role `independent-auditor`, Opus high, class C2, session\n  `05bd8c31-ea62-49a0-be0c-4e9b18491d2d`, 2026-11-12. It was started through `gov launch` under its OS sandbox. The\n  ticket lead (an orchestrator-role session) commissioned and judged it. It wrote nothing in the repository: its tripwire\n",
      "tokens": 282
    },
    {
      "id": "154afb26ac1116dbe913d3e4",
      "path": "tests/acceptance/W2-172/README.md",
      "text": "# W2-172 acceptance tests: the memory audit's driver and schedule (S1\u2013S9, F1\u2013F5)\n\nTicket `DAEO-p8tv` (W2-172), profile FULL, class C2. An independent test designer (MR-3) wrote these cases from the\nticket's KPI lines and its `## Interface` section (items 1\u201312, the CTO's answers O1\u2013O4 above it, PKG-W2-172-IFACE-1 (a)) and\nthe ticket's sources, before the implementation. Nothing of this ticket's branch was read (`src/gov/memaudit/` as it stands on\nthe tests' base holds W2-170's and W2-171's tool only; no `run`, `due`, `baseline`, `status` or `figures` driver code, no\n`memaudit_cron.sh`, no `tests/unit/memaudit/` of this ticket, DEC-820). W2-170's and W2-171's tools and acceptance suites were\nread as the Interface says: they are called, never copied or changed.\n\n**163 cases from 104 test functions in ten files**, with a support set (`w2_172_world.py`, `w2_172_git.py`,\n`w2_172_digest.py`, `w2_172_checks.py`), a conftest, and five planted programs (`launch_stub.py`, `gate_stub.py`,\n`py_shim.py`, `fake_crontab.py`, `spy/sitecustomize.py`). W2-171's world (`w2_171_world.py`, `w2_171_scenario.py`, its fake\n",
      "tokens": 279
    },
    {
      "id": "5d510bffc6c55ab7ead5c8a5",
      "path": "tests/acceptance/W2-172/README.md",
      "text": "| S9 | `test_w2_172_s9_cron_gate.py::test_s9_not_due_it_starts_nothing_exits_0_and_appends_one_line`, `test_w2_172_s9_cron_gate.py::test_s9_due_and_idle_it_starts_the_cycle_with_the_gate_and_exits_with_runs_code`, `test_w2_172_s9_cron_gate.py::test_s9_the_wrapper_exits_with_the_code_run_exits_with`, `test_w2_172_s9_cron_gate.py::test_s9_one_line_a_run_is_appended`, `test_w2_172_s9_cron_gate.py::test_s9_the_wrapper_defaults_to_the_sets_root_under_home`, `test_w2_172_s9_cron_gate.py::test_s9_the_wrapper_writes_nothing_but_the_cron_log_and_calls_no_crontab`, `test_w2_172_s9_cron_gate.py::test_s9_the_wrapper_holds_no_crontab_edit`, `test_w2_172_s9_cron_gate.py::test_s9_the_wrapper_names_its_interpreter_sets_root_and_gate_by_the_interfaces_variables`, `test_w2_172_s9_cron_gate.py::test_s9_a_busy_gate_stops_the_measure_with_gate_busy_after_the_wait_runs_out`, `test_w2_172_s9_cron_gate.py::test_s9_a_gate_that_opens_lets_the_measure_start_once`, `test_w2_172_s9_cron_gate.py::test_s9_the_gate_is_asked_before_measure_judge_and_pool_and_before_nothing_else`, `test_w2_172_s9_cron_gate.py::test_s9_without_a_gate_command_no_gate_is_asked` | no `memaudit_cron.sh` (bash exit 127, `FileNotFoundError` reading it); no `run` for the gate cases |\n",
      "tokens": 312
    },
    {
      "id": "a6fdb2695488dd79732e9d3c",
      "path": "tests/acceptance/W2-172/README.md",
      "text": "## How the tests reach the code under test\n\n- **The command line, as the callers run it** (Interface 1, 2, 8): `python3 -m gov.memaudit run|due|baseline|status|figures\n  --sets-root <root> ...` and `bash memaudit_cron.sh`, each in a child process, judged by its exit code, its printed lines\n  (`STEP <name> <command line>`, `STOPPED <step> <exit>`, `STOPPED <step> gate busy`, `REFUSED <code>`, the digest's 12\n  lines, the `due` lines, `audited` / `not audited, next due <date>`, `BASELINE <12 hex>`, `BL-*`) and the files under\n  `<runs>/indep/memaudit/` (item 4: `LOCK`, `STARTS.log`, `HISTORY.jsonl`, `cron.log`, `<A>/COUNTS.json`, `<A>/DIGEST.txt`,\n  `<A>/<step>.out|.err|.counts.json`) and `<runs>/indep/AUDITS.log`. The new modules are never imported at collection, so the\n  suite runs red by failing. Every child gets this tree's `src/` first on `PYTHONPATH` (a session fixture fails the run when\n  a child would import `gov` from elsewhere).\n- **Only the seams the Interface names:** `--launch <file>` (a planted launch script), `--store-link`, `--repo`, `--gov`,\n  `--claude`, `--gate-cmd`, and the environment `GOV_INDEP_RUNS_DIR`, `GOV_MEMAUDIT_NOW`, `GOV_MEMAUDIT_GATE_POLL_S`,\n",
      "tokens": 298
    },
    {
      "id": "5345ab703e60959b8cb8c33c",
      "path": "tests/acceptance/W2-172/test_w2_172_s9_cron_gate.py",
      "text": "def test_s9_the_wrapper_holds_no_crontab_edit(tmp_path):\n    assert SCRIPT.is_file(), \"governance/project/orchestration/tools/memaudit_cron.sh\"\n    counted = subprocess.run([\"grep\", \"-c\", \"crontab\", str(SCRIPT)], capture_output=True, text=True)\n    assert counted.stdout.strip() == \"0\", counted\n    assert subprocess.run([\"bash\", \"-n\", str(SCRIPT)], capture_output=True).returncode == 0\n",
      "tokens": 97
    },
    {
      "id": "bd6b40038c3d810170c8c496",
      "path": "tests/acceptance/W2-172/test_w2_172_s9_cron_gate.py",
      "text": "\"\"\"S9 and F4's wrapper half: the cron wrapper ``memaudit_cron.sh`` and the gate (Interface item 8).\n\nThe wrapper runs ``due`` and starts the cycle only when an audit is due, with the pinned interpreter\n(``GOV_MEMAUDIT_PYTHON``, else ``/usr/bin/python3``) and the sets root (``GOV_MEMAUDIT_SETS_ROOT``, else\n``$HOME/gov-os-eval``); not due: no start, exit 0; due: ``run --sets-root <root> --gate-cmd <gate>`` and the exit of ``run``;\none JSON line a run in ``<R>/cron.log``: ``{\"at\",\"due\",\"mode\",\"reason\",\"started\",\"exit\"}``. It holds no ``crontab``\n(the crontab is class (O), an ACT): ``grep -c crontab`` of the wrapper is 0 and a planted ``crontab`` first on PATH is\nnever called. The planted interpreter (``py_shim.py``) answers ``-m gov.memaudit due|run`` from a plan and logs the calls.\n\nThe gate: before steps 7, 8 and 11 (``measure``, ``judge``, ``pool``) ``run`` calls ``--gate-cmd`` with no arguments (exit 0\nopen, else busy), polling every ``GOV_MEMAUDIT_GATE_POLL_S`` seconds for at most ``GOV_MEMAUDIT_GATE_MAX_S`` (default 3600)\nand then stopping ``STOPPED <step> gate busy`` (a stop at that step, exit 2). The busy case runs the real driver without\n",
      "tokens": 291
    },
    {
      "id": "8f66cb5ab6c9c9ab1d6180dc",
      "path": "tests/acceptance/W2-172/w2_172_world.py",
      "text": "from datetime import datetime, timedelta, timezone\nfrom pathlib import Path\n\nHERE = Path(__file__).resolve().parent\nACCEPT = HERE.parent\nsys.path.insert(0, str(ACCEPT / \"W2-171\"))  # W2-171's helpers: imported, never changed\n\nimport w2_171_scenario as S171  # noqa: E402\nimport w2_171_world as W171  # noqa: E402\n\nTREE = HERE.parents[2]\nSRC = Path(os.environ.get(\"W172_SRC\") or (TREE / \"src\")).resolve()\nWRAPPER = Path(os.environ.get(\"W172_WRAPPER\") or (TREE / \"governance\" / \"project\" / \"orchestration\" / \"tools\"\n                                                   / \"memaudit_cron.sh\"))  # the env names: only to show the suite sound\nUTC = timezone.utc\nNOW = \"2026-11-10T12:00:00Z\"           # 12 hours after the audit commit's committer time\nAUDIT_TIME = datetime(2026, 11, 10, tzinfo=UTC)\nAUDIT = \"memory-audit-20261110\"\nBRIEF_DIR = \"governance/project/indep-briefs/memory-audit\"\nBRIEFS = (\"writer\", \"checker\", \"auditor\")\nSTEPS = [\"writer-1\", \"preflight\", \"checker-1\", \"writer-2\", \"checker-2\", \"void\", \"measure\", \"judge\", \"auditor\",\n         \"classes\", \"pool\", \"figures\"]\nGLOBS = [\"src/gov/retrieval/**\", \"src/gov/retrieve/**\", \"src/gov/store/**\", \"src/gov/codeintel/**\",\n",
      "tokens": 294
    },
    {
      "id": "DAEO-c1uz",
      "path": ".tickets/DAEO-c1uz.md",
      "text": "  - 'The couplings imports and coverage cannot see are declared in the test map and followed: text reads (W1-42 reads src/gov/cli/main.py and kernel templates; W1-30''s r11 reads serial-only.txt), a separate process (src/gov/retrieval/rerank_worker.py to W1-19''s real-model file, W1-21''s dev-tier file and tests/unit/semantic/test_rerank_process.py), the two hook copies (to W1-29, W1-49, W2-62, tests/unit/hooks; the session-start and PreCompact hooks also to W1-31, W1-37, W1-38, tests/unit/telemetry), fixture inputs (the live path map and the gitleaks configurations, to W1-16, W1-17, W1-19, W1-20, W1-21, W1-22, W1-24 and W2-54; W1-18''s unit-file listing), declared checks to W1-26, and the named lines of the synthesis''s section 4; W1-07''s three contract files run on every close [P-IS-1 (a)]'\n  - 'The serial-only tests are scoped by the same selection: a scoped close runs the serial cases of the suites it selected, one at a time, and the record says which [DEC-889 item 1]'\n",
      "tokens": 248
    },
    {
      "id": "ADR-0002",
      "path": "docs/adr/ADR-0002-architecture-and-stack.md",
      "text": "  runtime.\n- **VRAM.** The budget is 14,255 MiB: the GPU less a 2 GB headroom (DEC-1032 (1), DEC-1076 (4)). The two embedders\n  come first (about 5.6 GB together), the shared reranker second (about 4.8 GB, up to 6.4 GB under load, read on 2026-11-02, before it released its memory\n  after each request); nothing may\n  push the embedders off the GPU (DEC-1031 (1)-(2), DEC-1043 (2)). Measured on window 4: 8,404 MiB peak through\n  E0; about 9.4 GB under a burst of 20 searches at once (G1). The embedders stay loaded, so the GPU does not return to\n  an empty baseline when idle. The spill floor is 2,048 MiB (DEC-1084); experiments carry a backstop at 15.5 GB and\n  take the GPU one job at a time (DEC-1067).\n- **Disk.** \u2248 11.9 GB at S0b2; not re-measured. The reranker trial's downloads are kept as they are for now\n  (DEC-1070 (1), DEC-1079).\n- **Processes.** Two shared embedding servers (Ollama) and one shared reranker service, all on the GPU. On this\n  repository, by the CTO's tools: the dispatcher watches each model's layers on the GPU and the servers' crashes\n  (DEC-1030), and the servers restart by class from their committed configurations, without an ACT (DEC-1057 (4)).\n",
      "tokens": 296
    },
    {
      "id": "a927d6cf482e0fe5bfdf891f",
      "path": "docs/assessment/2026-10/I-SYNTHESIS.md",
      "text": "  - files read as text: W1-42 reads `src/gov/cli/main.py` and kernel templates; W1-30's r11 reads `serial-only.txt` (I2 \u00a74.1);\n  - fixture inputs that are not code: the live path map and the gitleaks configurations, copied into W1-16, W1-17, W1-19, W1-20, W1-21, W1-22, W1-24 and W2-54; W1-18 lists the working tree's unit files (I3 \u00a74.1 item 6);\n  - W1-28's file scan, which runs every suite's whole-tree copier: goes if P-I1-4 is taken (I1 \u00a74.1);\n  - the live cases depend on the installed CLI and the network: select them on a change of the CLI's pin, or run them in the nightly only (I1 \u00a74.1).\n- **W1-01's MR-3 whole-history test** would rarely be selected: keep it in the nightly and every full run (I1 \u00a74.1).\n- **A valid case W2-66 will turn red:** W1-30's `test_regression_includes_other_acceptance_folders`. Name it for W2-66's test designer (I2 F9).\n- **The record-reading set:** P-IS-2.\n- **Worksteal and per-test limits:**\n  - worksteal waits until the nested runs are gone (DEC-892 a; P-IS-3);\n  - pytest-timeout with the `signal` method, the limit above the slowest test; 900 s held in the trial (DEC-892 b; the tool trials).\n",
      "tokens": 285
    },
    {
      "id": "60da65d185f2c87ce82323e7",
      "path": "docs/assessment/2026-10/I3-retrieval-context-resume.md",
      "text": "   Planted faults P14a and P14b (finding 3) show which test notices a change in each copy. Both `template/governance/kernel/hooks/**` and `src/gov/hooks/**` map to W1-29, W1-49, W2-62 and `tests/unit/hooks`. The session-start and PreCompact hooks are also run by W1-31, W1-37, W1-38 and `tests/unit/telemetry`, and vendored by W1-06 (a search of `tests/` for the file names). The hooks run as separate processes, so coverage cannot see these suites either.\n6. **Inputs that are not code but feed the fixtures.** The live path map and the gitleaks configuration are copied into the fixtures of W1-16, W1-17, W1-19, W1-21, W1-22, W1-24 and W2-54 (for example `w1_17_support.py:401-408`); W1-20 copies the gitleaks template too, with a path map of its own (`w1_20_support.py:48, 430`). W1-18 lists every service, socket and timer unit of the working tree, untracked ones included (`w1_18_support.py:86-93`). None of these is a record in DEC-891's list, so, unless W2-66 declares them record-only, a change to them changes the code fingerprint and runs the suites. The map needs `governance/project/path-map.yaml` (already in the shared core) and the gitleaks configurations to point to those suites.\n\n",
      "tokens": 300
    },
    {
      "id": "WAVE-2-LIST",
      "path": "docs/plan/WAVE_2_LIST.md",
      "text": "| W2-L434 | The test map's upkeep: a folder target still resolves after its record-reading file moved away (R5); the map's literal paths are not checked at the head (R6); an inherited, guarded or aliased case is judged gone, so the close runs in full (R9, the safe side); who corrects the map when a target is retired or renamed | engineer | W2-68 takes the map's upkeep and checks every target and literal path at the head; until then a close widens (P1, DEC-912) and the orchestrator corrects the map by a record edit. | W2-66's reviews, 2026-10-24 (probe `docs/probes/DAEO-c1uz/PR-DAEO-c1uz.md`; ordinary work: no; fails open (R9: yes; other)) |\n| W2-L435 | Fixture inputs that no coupling takes to their readers: scanner configurations (W1-40, W2-50, W2-69), the template path map (W2-50, W2-58, W2-69), the check declaration (W2-69) (R7) | engineer | Each is coupled to its readers (W2-68). | W2-66's reviews, 2026-10-24 (probe `docs/probes/DAEO-c1uz/PR-DAEO-c1uz.md`; ordinary work: no; fails open) |\n",
      "tokens": 252
    },
    {
      "id": "ef0bd3d40f0e9788cbd6554f",
      "path": "docs/probes/DAEO-c1uz/PR-DAEO-c1uz.md",
      "text": "  - A change to `template/governance/kernel/checks/secrets-indexing.yaml` leaves out W2-69, which reads the check's command and time limit.\n- **What should have happened:** the map couples each input to the suites that read it (KPI 3's fixture inputs).\n- `Ordinary work: no, because none of these inputs has changed in Wave 2 (the gitleaks configurations last on 2026-10-04, the check declaration on 2026-10-10, the template path map on 2026-10-08), no open ticket holds either gitleaks configuration, and the open tickets that hold the other two change what these suites override or do not read (W2-06's KPIs move checks between tiers, while W2-69 reads only the declaration's command and time limit; W2-23 adds namespaces for adoption moves, while W2-50 and W2-69 set their own docs and src namespaces, W2-58 adds evaluation sets, and the loaders refuse no overlap).`\n- `Consequence: fails open`\n\n",
      "tokens": 225
    },
    {
      "id": "fc9deac66566656dd02c848c",
      "path": "docs/probes/DAEO-c1uz/PR-DAEO-c1uz.md",
      "text": "### R6: The map's literal paths are not checked at the head (low)\n- **What was done:** read how shared-core members and coupling paths are matched; ran the live selection.\n- **What happened:**\n  - P1 checks targets only. A shared-core member named by its file (the eight retrieval modules, `src/gov/config/loader.py`, `src/gov/tasks/tickets.py`, `src/gov/store/loader.py`, `src/gov/cli/main.py`, `src/gov/cli/errors.py`) or a coupling path named by its file (`src/gov/retrieval/rerank_worker.py`, `src/gov/retrieval/retrieve_check.py`, the gitleaks configurations) would match nothing after a rename.\n  - The rename's own close sees the old path and runs full or the coupled suites. Later changes to the renamed module run scoped.\n- **What should have happened:** a literal map path that names no file at the head widens the run, or is named, as a target does.\n- `Ordinary work: no, because no source file the map names has been renamed or moved in this repository's history: the only rename under src/, template/ and tests/ is W2-69's tests/unit/secrets/ folder, and the only deletion under src/ is a hook pair the hook patterns cover.`\n- `Consequence: fails open`\n\n",
      "tokens": 292
    },
    {
      "id": "dd26f6053d854d31bd9a0a04",
      "path": "docs/probes/DAEO-g29a/PR-DAEO-g29a.md",
      "text": "# Probe record: W2-113 (DAEO-g29a)\n\n```verdict\nticket: DAEO-g29a\nhead: 6542b7ec525b\nround: 1\nverdict: PASS\nblocking: 0\n```\n\n- **What was probed:** Stage A0's new coordination ticket and roster key, and the guard's install refusal when the\n  rule cannot run, at 6542b7ec525b (code of a322b1f94, the engineer's commit). The reviewer was an independent\n  auditor (Opus, read-only), and ran everything as code on planted products in its own TMPDIR, using this worktree's\n  `src`:\n  - I1 end to end: a product generated with copier and `rulesync generate`, committed, then `gov adopt --lite --stage A0`.\n  - The hook's decisions: 35 session forms \u00d7 4 commands, 140 calls.\n  - 29 roster variants for I2 (i)/(ii) and I2 (iii) (`tk` missing).\n  - 6 `tk` stand-ins for A0's failure paths, plus A0 run twice, a ticket with the same title already there, and `.tickets/` git-ignored.\n  - success-2's words in 7 configurations, each tried by a CTO guess and by an engineer, plus the adopted product without `tk`.\n  - W2-110's acceptance suite and unit tests with W2-113's unit tests (252 passed).\n  - Scope: `git diff --name-only 4ede6c3fee3d..6542b7ec525b`.\n\n",
      "tokens": 287
    },
    {
      "id": "b58960263bdad960763e74f4",
      "path": "docs/probes/DAEO-rmbe/PR-DAEO-rmbe-reprobe-1.md",
      "text": "- **Verdict: pass.** Classification (DEC-809): F1, the renamed case's failure output, is yes / other. No finding is \"yes\" with \"fails open\" or \"loses work\", and no change in scope lets the check pass anything it refused at `e00fd14a26be`. The lead's judgement agrees. F1 is a row: it fails closed, and W2-71's card already aims at the cause.\n- **The earlier record's findings and classification stand.** They are: wrapped key word (no / fails open); double-spaced block (no / fails open); many markers (no / other); vanished file (yes / other). No change in scope touches them. The code under test, the check's declaration and the gitleaks configurations are unchanged since `e00fd14a26be`.\n\n",
      "tokens": 173
    },
    {
      "id": "bf91aef0b89b6886deaa3134",
      "path": "governance/project/orchestration/packages/ADR-0002-REFRESH/ADR-0002-architecture-and-stack.draft",
      "text": "  runtime.\n- **VRAM.** The budget is 14,255 MiB: the GPU less a 2 GB headroom (DEC-1032 (1), DEC-1076 (4)). The two embedders\n  come first (about 5.6 GB together), the shared reranker second (about 4.8 GB, up to 6.4 GB under load, read on 2026-11-02, before it released its memory\n  after each request); nothing may\n  push the embedders off the GPU (DEC-1031 (1)-(2), DEC-1043 (2)). Measured on window 4: 8,404 MiB peak through\n  E0; about 9.4 GB under a burst of 20 searches at once (G1). The embedders stay loaded, so the GPU does not return to\n  an empty baseline when idle. The spill floor is 2,048 MiB (DEC-1084); experiments carry a backstop at 15.5 GB and\n  take the GPU one job at a time (DEC-1067).\n- **Disk.** \u2248 11.9 GB at S0b2; not re-measured. The reranker trial's downloads are kept as they are for now\n  (DEC-1070 (1), DEC-1079).\n- **Processes.** Two shared embedding servers (Ollama) and one shared reranker service, all on the GPU. On this\n  repository, by the CTO's tools: the dispatcher watches each model's layers on the GPU and the servers' crashes\n  (DEC-1030), and the servers restart by class from their committed configurations, without an ACT (DEC-1057 (4)).\n",
      "tokens": 296
    },
    {
      "id": "1a19313555039b408f20476a",
      "path": "governance/project/orchestration/packages/REVIEW-BUNDLE-2026-10-22.md",
      "text": "  - 'The couplings imports and coverage cannot see are declared in the test map and followed: text reads (W1-42 reads src/gov/cli/main.py and kernel templates; W1-30''s r11 reads serial-only.txt), a separate process (src/gov/retrieval/rerank_worker.py to W1-19''s real-model file, W1-21''s dev-tier file and tests/unit/semantic/test_rerank_process.py), the two hook copies (to W1-29, W1-49, W2-62, tests/unit/hooks; the session-start and PreCompact hooks also to W1-31, W1-37, W1-38, tests/unit/telemetry), fixture inputs (the live path map and the gitleaks configurations, to W1-16, W1-17, W1-19, W1-20, W1-21, W1-22, W1-24 and W2-54; W1-18''s unit-file listing), declared checks to W1-26, and the named lines of the synthesis''s section 4; W1-07''s three contract files run on every close [P-IS-1 (a)]'\n  - 'The serial-only tests are scoped by the same selection: a scoped close runs the serial cases of the suites it selected, one at a time, and the record says which [DEC-889 item 1]'\n",
      "tokens": 248
    },
    {
      "id": "ef34318734859d9fbb9c738a",
      "path": "governance/project/test-map.yaml",
      "text": "    suites: [\"tests/acceptance/W1-29/\", \"tests/acceptance/W1-49/\", \"tests/acceptance/W2-62/\", \"tests/unit/hooks\"]\n    why: \"the two hook copies, run as separate processes (I3 \u00a74.1 item 5)\"\n  - paths: [\"template/governance/kernel/hooks/sessionstart.py\", \"template/governance/kernel/hooks/precompact.py\"]\n    suites: [\"tests/acceptance/W1-31/\", \"tests/acceptance/W1-37/\", \"tests/acceptance/W1-38/\", \"tests/unit/telemetry\"]\n    why: \"the session-start and PreCompact hooks are also run by these suites (I3 \u00a74.1 item 5)\"\n  - paths: [\"governance/project/path-map.yaml\", \".gitleaks.toml\", \"template/.gitleaks.toml\"]\n    suites: [\"tests/acceptance/W1-16/\", \"tests/acceptance/W1-17/\", \"tests/acceptance/W1-20/\",\n             \"tests/acceptance/W1-22/\", \"tests/acceptance/W1-24/\", \"tests/acceptance/W2-54/\"]\n    why: \"fixture inputs: the live path map and the gitleaks configurations are copied into these suites' fixtures (I3 \u00a74.1 item 6); W1-19 and W1-21 left out by DEC-1061 item 9 (T-6)\"\n  # DEC-1061 item 9 (DEC-1052 T-6): the real-model suites are selected by a model-path change only: the embedder (its\n",
      "tokens": 275
    },
    {
      "id": "b676482624972959c611d0e1",
      "path": "tests/acceptance/W1-15/README.md",
      "text": "| **C2.** The check is not green on a store holding a secret the project's file shelters (KPI success 4, failure 1, CAP-38.b) | `test_the_check_is_not_green_on_a_store_with_a_secret_the_configuration_shelters[4]` | 4 red: the check exits 0. |\n\nHow these tests decide:\n\n- **C1.** Before the filter is asked, the test runs the `gitleaks` binary by hand over the planted folder, twice:\n  with the template's rules it reports the planted file and only it; with the shelter it reports nothing. So the\n  shelter is one the scanner honours. Then the planted file must be absent from what the filter returns and the\n  clean neighbour present. The call must succeed: the rules are there, so the filter can decide, and the keep-true\n  cases require it to let files without a secret through under each of the four configurations.\n- **C2.** **The check reads the project's `.gitleaks.toml`.** Its public behaviour shows it: with the same store\n  the check fails under the template's file (the premise each case asserts) and is green once the file shelters the\n  secret; and it is not green when the file holds no rules (B2). So each case plants the secret in a packet under\n",
      "tokens": 291
    },
    {
      "id": "25c47bc69972bf5a3c69c390",
      "path": "tests/acceptance/W1-15/w1_15_support.py",
      "text": "\n\n# Two gitleaks configurations that are valid TOML and hold no rule at all.\nRULELESS_CONFIGS = {\n    \"empty-file\": \"\",\n    \"defaults-off\": 'title = \"no rules\"\\n\\n[extend]\\nuseDefault = false\\n',\n}\n\n\n# --------------------------------------------------------------------------\n# Sheltering configurations (DEC-298): ways a project's .gitleaks.toml makes the scanner stay silent on a secret\n# --------------------------------------------------------------------------\n\n",
      "tokens": 117
    }
  ],
  "supplementary_query": "The standing hidden set: each repository's memory judged end to end every week on the same questions at 95 %, counts only, with a monthly fresh set as the check against fitting, a weekly maintenance pass, and the audit's state per repository (MEMORY-AUDIT G1, G2, G3, G5 and G4's code)\nS1 A standing set: `python3 -m gov.memaudit standing declare --set <name> --repo <dir>` records one standing set for the repository: its name, its digest (`LC_ALL=C sha256sum *.yaml | sha256sum` over the kept questions), n with the nonexistent-id questions apart, the sha256 of the writer's and checker's briefs, and the commit it was written at. A set whose questions were ever written to a `misses.jsonl` or read by an auditor is refused (`STANDING_SPENT`); an adopted repository's Wave 0 verdict set is accepted once its `USED` marker and its counts-only result record exist (W2-88 S13, S16). One standing set is live per repository; a second is refused until the first is retired [DEC-1179 (1), DEC-1176 (1), DEC-1098 (1)] Verify: planted sets: a new set is recorded with each field; a set with a planted `misses.jsonl` line is refused with `STANDING_SPENT`; a planted Wave 0 verdict set with `USED` and its record is accepted; a second live set is refused\nS2 One judged run a week: a standing run writes `runs/<set>/<ISO year>-W<week>/DECLARATION.json` and then `USED`, before any search; a second judged run of the same set in the same ISO week exits 3 and writes nothing. A run stopped by the fault rule (FRESH-80-1 \u00a73.5, `STOPPED <cause>`) before its reader run started may start once more that week; a run whose reader run started never runs again [DEC-1179 (1), DEC-1097 (1)(g)] Verify: planted runs: the file times and the ledger line show DECLARATION.json before USED before the first search; a second run the same week exits 3 with the tree byte-identical; a planted STOPPED before the reader run allows one restart and a second is refused\nS3 The same method as Gov OS's memory: a standing run uses the fresh 80's judged path unchanged: the store at the audit commit with the standard (the 0.6B through the one shared reranker, the pool on, the 6,000-token bundle widened to sections); each question's first bundle from `gov.retrieval.measure`; `judge`'s reader run as built (the pinned `prompts.py`, the reader, the cap, the A2 cut judged, A1 and A3 as data); the named grader with the second grader's agreement; the measure's matcher with source families. Every search result's store commit (W2-138) equal to the declared store's commit, else that attempt is a fault [DEC-1179 (1), DEC-1097 (1)(a), DEC-1098 (1), DEC-1092 (1)] Verify: `tests/unit/memaudit/test_prompts.py` passes unchanged; a planted standing run calls the same reader, grader and matcher functions as a fresh run (one shared code path, asserted by a spy); a planted result from another store commit makes the attempt a fault\nS4 Counts only: a standing run writes no `misses.jsonl` and launches no auditor. Only counts leave its run folder: right end to end, wrong claims, not found, the misses by outcome (wrong, incomplete, not found) and by the first gold place's rank in the first bundle (1-5, 6-20, absent), the questions dropped by the anchor check, and the figures beside (hit@5, gold in the first bundle, A1 against A2 with exact McNemar). No question id, question, gold, answer or citation of the standing set is printed, logged, written to `FIGURES.json`, `HISTORY.jsonl`, `AUDITS.log` or the digest block, or written outside its run folder (mode 0700) [DEC-1179 (2), DEC-1101 (2), DEC-1074 (1)] Verify: a planted standing run with five planted misses whose ids and texts are unique strings: no planted string appears in stdout, stderr, FIGURES.json, HISTORY.jsonl, AUDITS.log, the digest block or any file outside the run folder; no misses.jsonl exists; no auditor launch event is in the ledger\nS5 The bar at 95 %: `declare.bar(n)` gives `need_right = ceil(95 n / 100)` and `max_wrong = floor(5 n / 100)`; a verdict passes when right end to end at A2 reaches `need_right` (wrong claims stay reported and checked). It applies to standing and fresh runs alike, and the declaration's rounding text says so. On 80 judged that is 76, on 79 it is 76, on 40 it is 38 [DEC-1179 (2), DEC-1097 (1)(d) as carried forward, DEC-957] Verify: unit cases n = 40, 79, 80 give 38, 76, 76; a planted run with right = need_right - 1 is a miss and with right = need_right a pass; the digest's bar line prints the new figure; the revised W2-170, W2-171 and W2-172 cases pass, and W2-88's S15 bar case (which reads W2-170's helper `bar`) passes unedited\nS6 Staleness by count: before each standing run the pre-flight checks each question's gold anchors at the audit commit; a question whose anchor no longer resolves, or whose nonexistent id now exists, is dropped from that week's n and counted (`dropped k`); nothing in the set is edited. Fewer than 70 live questions prints `STANDING_THIN <live>` in the digest block and asks for a replacement [DEC-1179 (2), DEC-1097 (1)(f)] Verify: a planted set of 80 with 3 broken anchors: n is 77 and `dropped 3` is printed with no id; the set's digest is unchanged after the run; a planted set with 69 live questions prints STANDING_THIN 69\nS7 The monthly check against fitting: at each fresh run the tool compares the fresh set's right end to end per cent F with S, the mean of the standing set's last four weekly figures; S - F of 5 points or more writes `STANDING_FITTED` in HISTORY.jsonl and the digest block, retires the standing set (no further standing run on it; it joins the pool as a diagnostic set, counts only) and asks for the writer's replacement; F - S of 5 points or more writes `STANDING_STALE` and asks for the checker's staleness pass; with fewer than four weekly figures the check prints `drift: not yet (k of 4)` [DEC-1179 (3), DEC-1074 (4)] Verify: planted histories: S 96, F 90 retires the set and a later standing run on it is refused; S 90, F 96 prints STANDING_STALE; S 95, F 92 prints no flag; two weekly figures print `drift: not yet (2 of 4)`\nS8 The two cadences and below 95 %: the standing set's cadence is W2-172 S5's computed rule, unchanged (weekly while active, monthly once stable, back to weekly at once on a miss, a retrieval change, churn of 10 % or more or a pool regression); the fresh set is due on the first Monday 28 days or more after the last fresh run. A standing miss is a HISTORY line `miss` with its counts; the fresh set is then due at the next Monday and every Monday until a standing run passes again (then every 28 days); the maintenance pass (S10) runs at once after the miss in the same cycle; the digest block carries a `P1 memory below 95 %` line with the counts by class. Two consecutive standing misses, or one miss 5 points or more below the last passing figure, write `MEMORY_REPAIR open` in HISTORY.jsonl, and `gov.memaudit status --repair` exits 1 while it is open and 0 once a later standing run passes or the owner's decision id is given with `--residual DEC-<n>` [DEC-1179 (4), (5), DEC-1125 (2)] Verify: `tests/acceptance/W2-172/test_w2_172_s5_due.py` passes unchanged for the standing set; a planted fresh history 27 days old is not due and 28 days old is due on the Monday; planted histories: one miss makes the fresh set due next Monday and puts the P1 line in the digest; pass, miss, miss opens the repair; pass at 96 then miss at 90 opens it; `status --repair` exits 1, then 0 after a planted pass or `--residual DEC-1`\nS9 State per repository: the runs folder is `<runs>/indep/memaudit/<key>/` with `<key>` the repository's directory name, a hyphen and the first 8 hex of the sha256 of its real path, so two repositories on one machine keep separate `AUDITS.log`, `HISTORY.jsonl` and `STARTS.log`. The retrieval change that sends an audit back to weekly is, for any repository, a change of the gov pin, of the repository's `governance/project/retrieval.yaml` digest or of its path map's digest, and for Gov OS also its six retrieval globs. `pool-import --sets <name>...` seeds the pool from that repository's own sets root; with no `--sets` on Gov OS it imports Gov OS's 79 and 138 as today [DEC-1179 (5), DEC-1101 (1), DEC-1125 (2)] Verify: two planted repositories on one runs folder write to two keys and neither reads the other's history; a planted pin change on an adopted repository is a retrieval change and a change under `src/gov/retrieval/` of Gov OS is not, for it; `pool-import --sets a b` imports exactly those sets\nS10 One weekly maintenance pass before each standing run, `python3 -m gov.memaudit maintain --repo <dir>`: (1) the integration store at the main line's head, else one refresh by W2-116's `gov rebuild --integration`, a failed build leaving the last good store in service and named; (2) the store's layout current, else one `gov rebuild`; (3) `gov links --since <the last pass's commit>`: the count of new findings; (4) the count of tracked paths the path map indexes but the store holds no chunk of; (5) the standing and fresh runs' reader `not found` answers and second searches, counted; (6) the list of gold questions whose cited lines changed at the audit commit (W2-61h S4's list: question id and entry number only, never a question, answer or path) handed to the walled writer's request for re-anchoring or rewording, counted. It prints six counts in the digest block, never fails or delays the audit, and never changes one of the standard's four settings [DEC-1179 (6), DEC-1178 (1), DEC-1072 (1), DEC-1101 (1), DEC-1096] Verify: a planted repository with a store 3 commits behind is refreshed once and the head printed; a planted failing rebuild keeps the old store and names the failure; planted link findings and two unindexed paths are counted; the audit runs whatever the pass finds; the retrieval.yaml digest is unchanged after the pass; a planted set with one changed cited block and one moved unchanged block lists only the changed one, by question id and entry number, in the writer's request, with no question, answer or path text in it or in the digest\nS11 The schedule's code (G4): `memaudit_cron.sh` takes `--repo <dir>` and runs, when due, the maintenance pass, the standing run and, when the fresh set is due, the fresh cycle, in that order, within the gate's wait (W2-172 S9); A9's ACT package (`memory_sets.walls_act`) adds one step to its ACT.md with the repository's cron line (the wrapper with `--repo <that repository>`, Mondays 21:00), written as text for the repository's owner's operator and never installed [DEC-1179 (5), DEC-1101 (2), W2-88 S22] Verify: a planted due standing run and a due fresh set run in that order from one wrapper call; nothing runs when neither is due; a planted A9 run's ACT.md holds the cron line with the repository's path and no crontab is changed\nF1 A standing set's question id, question, gold, answer or citation outside its run folder, or read by any session: the auditor, the CTO, a worker or a later fix. Verify: S4's planted strings are absent from every file written outside the run folder and from every launched session's brief; no code path hands a standing run's rows to `classes`, the auditor's launch or the pool's fix judging\nF2 A standing set judged twice in one week, judged without DECLARATION.json and USED first, re-scored, or its labels changed after a figure exists. Verify: S2's planted runs; `measure --kept` on a standing run exits 3 and writes nothing; the set's digest is checked equal at every run and a planted edit is refused before any search\nF3 The standing set used to choose, adopt or reject a fix or a configuration. Verify: the tool offers no command that compares two configurations or two commits on a standing set; the standing run refuses `--decision` and any data condition\nF4 The method drifts: the reader or grader prompt, model, cap or A2 cut changed, or the standing path diverges from the fresh path. Verify: `test_prompts.py` passes unchanged; S3's spy\nF5 A fresh set's use-once behaviour changes. Verify: W2-170's S3 and F2 cases on fresh sets pass with only their bar values revised; W2-171's S5 case passes unchanged\nF6 The maintenance pass changes a setting of the standard, applies an ACT, installs a cron line or stops the audit. Verify: S10's planted runs; the module imports no crontab writer and the retrieval.yaml and path map digests are unchanged after a pass",
  "further_batch": [
    {
      "id": "0919240bd7a82e196c6603c9",
      "path": "tests/acceptance/W2-110/README.md"
    },
    {
      "id": "4cd6233c6dbff2b58764ded3",
      "path": "tests/acceptance/W2-110/README.md"
    }
  ],
  "supplementary_batches": [
    {
      "items": [
        {
          "id": "b43d3fbced602d7011fddd95",
          "path": "docs/changes/W2-172-evidence.md"
        },
        {
          "id": "a7840d80200c6984ef13ae57",
          "path": "tests/acceptance/W2-172/README.md"
        },
        {
          "id": "f68422db58a467fbb6d663ae",
          "path": "tests/acceptance/W2-172/README.md"
        },
        {
          "id": "4f2f37ed69dba9810dd216a2",
          "path": "governance/project/orchestration/packages/MEMORY-AUDIT-1.md"
        },
        {
          "id": "69337829cad5dbf8ba5ac291",
          "path": "governance/project/orchestration/packages/MEMORY-AUDIT-1/ACT-DRAFTS.md"
        },
        {
          "id": "c8be5bf3b50c2b232c5f31cc",
          "path": "governance/project/orchestration/packages/MEMORY-AUDIT-P1.md"
        },
        {
          "id": "02a4e9dc689b8a8af00f3276",
          "path": "docs/changes/W2-172-evidence.md"
        },
        {
          "id": "5a9e22d58ea68b00e35c61f3",
          "path": "docs/probes/DAEO-p8tv/PR-DAEO-p8tv-round-1.md"
        },
        {
          "id": "154afb26ac1116dbe913d3e4",
          "path": "tests/acceptance/W2-172/README.md"
        },
        {
          "id": "5d510bffc6c55ab7ead5c8a5",
          "path": "tests/acceptance/W2-172/README.md"
        }
      ],
      "limit": 10
    },
    {
      "items": [
        {
          "id": "a6fdb2695488dd79732e9d3c",
          "path": "tests/acceptance/W2-172/README.md"
        },
        {
          "id": "5345ab703e60959b8cb8c33c",
          "path": "tests/acceptance/W2-172/test_w2_172_s9_cron_gate.py"
        },
        {
          "id": "bd6b40038c3d810170c8c496",
          "path": "tests/acceptance/W2-172/test_w2_172_s9_cron_gate.py"
        },
        {
          "id": "8f66cb5ab6c9c9ab1d6180dc",
          "path": "tests/acceptance/W2-172/w2_172_world.py"
        },
        {
          "id": "DAEO-c1uz",
          "path": ".tickets/DAEO-c1uz.md"
        },
        {
          "id": "ADR-0002",
          "path": "docs/adr/ADR-0002-architecture-and-stack.md"
        },
        {
          "id": "a927d6cf482e0fe5bfdf891f",
          "path": "docs/assessment/2026-10/I-SYNTHESIS.md"
        },
        {
          "id": "60da65d185f2c87ce82323e7",
          "path": "docs/assessment/2026-10/I3-retrieval-context-resume.md"
        },
        {
          "id": "WAVE-2-LIST",
          "path": "docs/plan/WAVE_2_LIST.md"
        },
        {
          "id": "ef0bd3d40f0e9788cbd6554f",
          "path": "docs/probes/DAEO-c1uz/PR-DAEO-c1uz.md"
        }
      ],
      "limit": 10
    },
    {
      "items": [
        {
          "id": "fc9deac66566656dd02c848c",
          "path": "docs/probes/DAEO-c1uz/PR-DAEO-c1uz.md"
        },
        {
          "id": "dd26f6053d854d31bd9a0a04",
          "path": "docs/probes/DAEO-g29a/PR-DAEO-g29a.md"
        },
        {
          "id": "b58960263bdad960763e74f4",
          "path": "docs/probes/DAEO-rmbe/PR-DAEO-rmbe-reprobe-1.md"
        },
        {
          "id": "bf91aef0b89b6886deaa3134",
          "path": "governance/project/orchestration/packages/ADR-0002-REFRESH/ADR-0002-architecture-and-stack.draft"
        },
        {
          "id": "1a19313555039b408f20476a",
          "path": "governance/project/orchestration/packages/REVIEW-BUNDLE-2026-10-22.md"
        },
        {
          "id": "ef34318734859d9fbb9c738a",
          "path": "governance/project/test-map.yaml"
        },
        {
          "id": "b676482624972959c611d0e1",
          "path": "tests/acceptance/W1-15/README.md"
        },
        {
          "id": "25c47bc69972bf5a3c69c390",
          "path": "tests/acceptance/W1-15/w1_15_support.py"
        },
        {
          "id": "0919240bd7a82e196c6603c9",
          "path": "tests/acceptance/W2-110/README.md"
        },
        {
          "id": "4cd6233c6dbff2b58764ded3",
          "path": "tests/acceptance/W2-110/README.md"
        }
      ],
      "limit": 10
    }
  ],
  "dropped": [
    {
      "id": "0919240bd7a82e196c6603c9",
      "reason": "budget exceeded"
    },
    {
      "id": "4cd6233c6dbff2b58764ded3",
      "reason": "budget exceeded"
    },
    {
      "id": "role_filter",
      "reason": "withheld from engineer (ticket DAEO-0cd2): 0 paths, 0 chunks; none matched (DEC-1065 (2))"
    }
  ],
  "tokens": 71810,
  "budget": {
    "limit": 72000,
    "used": 71810
  },
  "hash": "9ab45ca678c6583154d38ea6acc62de76957c9f4afd9aa1b952a7716e88a45f3"
}

----

## Rules
- **One judged path, two modes** (the ticket's rabbit holes): the standing mode reuses `driver._Cycle`, `_refusal`,
  `_history`, `_finish`, `declare.declare`, `measure.run`, `judge.run` / `_Judge.one`, `prompts`, `matcher` and
  `figures.build` with a `week=` argument; never copy the reader path into a second module; `prompts.py` is unchanged
  (`tests/unit/memaudit/test_prompts.py` passes unchanged). The new modules are `standing.py` (I3, I4's week rule, I7,
  I8) and `maintain.py` (I10). `maintain` is never a gate: exit 0 always (4 for usage), each item bounded by its timeout.
- **Counts only (S4, F1):** a standing run writes no `misses.jsonl`, starts no `classes`, auditor, `pool` or writer;
  nothing of a standing set's questions is written outside `<sets root>/runs/<set>/` (mode 0700); `say` stays the only
  printer; no question id, question, gold, answer, citation or path of a standing set in stdout, stderr, any HISTORY,
  STANDING, MAINTAIN, COUNTS, DIGEST or log line.
- **The bar (I5):** `declare.bar` and `declare.ROUNDING` as I5 gives them, for both modes. The existing acceptance
  cases that pin 85 % (W2-170, W2-171, W2-172) are being revised in parallel by the independent test designer; they turn
  green when the designer's suite is merged. Never edit `tests/acceptance/` (it is not yours; a restore or conflict there
  is the test designer's). Update `tests/unit/memaudit/` cases that pin the old bar.
- **State per repository (I2):** `schedule.state_dir(runs, repo)` replaces `schedule.folder(runs)` everywhere; the
  driver passes `GOV_INDEP_RUNS_DIR=<key folder>` to every child.
- **G6:** show in `docs/changes/W2-187-evidence.md` (by a unit test or a planted run) what `maintain` does with a store
  at the main line's head whose layout is stale (one rebuild by the same command, else `stale kept`).
- Work test first: unit tests under `tests/unit/memaudit/` (and `tests/unit/adopt/test_w2_187*` for `walls_act`) for
  each Interface item, small and fast, planted under `tmp_path` only.
- **Size:** the ticket estimates about 700 lines (G1+G2 300-450, G3 100-150, G5 150-250, S11 about 20). If S10 and S11
  split off as W2-187b (pre-approved, DEC-1179 O8 (a)), your lead tells you; build S1-S9 first (I1-I9, I12's standing
  lines), then S10 (I10) and S11 (I11), committing between them, so a split leaves a clean S1-S9.
- **The acceptance suite and your batches:** the independent test designer writes `tests/acceptance/W2-187/` in
  parallel; your lead merges it into this worktree only while you are between batches. Commit your code and unit tests
  in batches as you go. **When `/home/usain/gov-os-worktrees/W2-187/.gov-runtime/scratch/lead/TESTS-READY` exists**
  (check after each committed batch), read `tests/acceptance/W2-187/README.md` and its helpers, and make the suite pass.
  If it does not exist once your S1-S11 code and unit tests are committed, stop and return (status DONE, with
  "acceptance suite not yet merged" in `unresolved`); your lead resumes you.
- Never stage or commit while `git status` shows a merge in progress; if your tree changes under you unexpectedly, stop
  and return saying so.
- **Every pytest through the heavy-slot gate**, TMPDIR the sandbox's own `$TMPDIR` (outside the repository and outside
  ~/gov-os-runs); make the empty HOME first with `mkdir -p /home/usain/gov-os-worktrees/W2-187/.gov-runtime/scratch/empty-home`:
  `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh env HOME=/home/usain/gov-os-worktrees/W2-187/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-187/src python3 -m pytest tests/unit/memaudit -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`
  and the same for `tests/acceptance/W2-170`, `W2-171`, `W2-172`, `W2-173`, `W2-88` and (once merged) `W2-187`, one
  folder per run. A single case: append `::<name>`. A heavy-slot or resource gate refusal is a wait: run again when it
  opens; it never counts as a refusal.
- The base-red rule: a case red on the base (5336a6fca) for a reason outside this ticket is reported, not fixed.
- Write `docs/changes/W2-187-evidence.md`: what was built, per KPI line the cases that show it and their result, the
  pytest summary lines, G6, the size in lines (`git diff --stat 5336a6fca`), and any reading of the Interface you had to
  make (with the item number).
- Anything longer than one line goes in a script under /home/usain/gov-os-worktrees/W2-187/.gov-runtime/scratch/eng/,
  run with `bash <file>` or `python3 <file>`. Literal paths only as write targets.
- **Commit** your paths only, in batches, the trailers in ONE final paragraph (a blank line between them hides `Task:`):
  `git commit -m "W2-187: <subject>" --trailer "Task: DAEO-0cd2" --trailer "Role: engineer" --trailer "Implements: DEC-1179, DEC-1176, DEC-1101, DEC-1125, DEC-1098, DEC-1097, DEC-1092, DEC-1074, DEC-1072" --trailer "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>" -- <your paths>`
  Never `Role: owner` or `Decided-by:`. No merge, no push, no edit of `.tickets/`, the register or `tests/acceptance/`.
- Refused twice for the same call by the guard, the sandbox or a hook: stop and say so; never reach the same effect by
  another command, form or file (DEC-1142 (9)).

## Return (your last message; nothing else is read)
The twelve fields, each a labelled line ("none" where nothing): task / status (DONE, PACKAGES or ESCALATION) /
work_completed / files_changed / evidence (the pytest summary lines of each folder above) / tests / discoveries / risks
/ lessons / proposed_decisions / unresolved / recommended_next_action. Then `commits:` (hash12, subject, trailers) and
`guard_refusals:` (none, or each: time | form | the hook's reason | true or false-positive).
