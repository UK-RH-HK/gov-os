# Brief rev-1: independent auditor (reviewer) for DAEO-0cd2 (W2-187), review round 1, profile FULL, class C2

You are a fresh, read-only independent auditor. You review ticket DAEO-0cd2 (W2-187: the memory audit's standing hidden
set, judged every week at 95 %, counts only; the monthly fresh set as the check against fitting; the weekly maintenance
pass; the audit's state per repository; the schedule's code; the weekly secret scan and push) at the head below. You
wrote none of it and you write nothing in the repository: your findings and the verdict block are your return; your
lead writes the probe record from it. This is review round 1 of at most two (DEC-1010).

## What to probe
| what | path / value |
|---|---|
| the tree (read only) | /home/usain/gov-os-worktrees/W2-187 |
| branch, head | w2/W2-187 at 5b82d1d53868625c43a5b8b2bb58492bad3f8038 |
| base (the claim) | 5336a6fca |
| the change | `git diff 5336a6fca..5b82d1d53 -- src/gov/memaudit src/gov/adopt/memory_sets.py governance/project/orchestration/tools/memaudit_cron.sh tests/unit/memaudit tests/unit/adopt tests/acceptance/W2-170 tests/acceptance/W2-171 tests/acceptance/W2-172 tests/acceptance/W2-187 docs/changes/W2-187-evidence.md docs/probes/DAEO-0cd2` (the two `w2/integrate` merges, 530635305 and f4fdc7fa1, bring other tickets' files: out of scope) |
| the ticket (KPI lines S1-S12, F1-F7, the Approach, the method, rabbit holes, the Interface I1-I12, the gaps and routings, the amendments, and I13 at the end) | /home/usain/gov-os-worktrees/W2-187/.tickets/DAEO-0cd2.md |
| the packages and the CTO's answers | docs/probes/DAEO-0cd2/PACKAGE-W2-187-P1.md, PACKAGE-W2-187-S12.md |
| the engineer's evidence | docs/changes/W2-187-evidence.md |
| the acceptance suite's map | tests/acceptance/W2-187/README.md |
| the threat model | docs/adr/ADR-0001-threat-model.md |
| the sources (read each by id in docs/DECISION_REGISTER.md; grep the register only by id) | DEC-1182, DEC-1179, DEC-1176, DEC-1101, DEC-1125, DEC-1098, DEC-1097, DEC-1092, DEC-1074, DEC-1072, DEC-1156, DEC-1157, DEC-1010 |

**Readings settled by the CTO or the lead (judge against these):**
- **The I13 note** (the CTO, DEC-1157 (3), on I13 against W2-172 S9's unchanged files):
  - A no-declaration `push` prints `PUSH none: no declaration`, exits 0 and writes nothing. That line reaches the
    wrapper's own stdout.
  - A declared push writes its own `cron.log` line (the six keys, step `push`) and the DIGEST last line.
  - The wrapper calls `push` after any started audit step, on the live path and on today's path. Its exit stays the
    last audit step's.
- **S1, I3:** a used set's own run's `misses.jsonl` and `miss-classes.json` are skipped. A Wave 0 set lacking its
  record, or at another commit, is then `STANDING_SPENT 0`.
- **S2:** the week ledger reads `preflight, declaration, used, search`. The fresh path's pre-flight writes its own
  ledger line too.
- **S8:** a plain `status --repair` after `--residual` prints `REPAIR none` (I8's two forms).
- **The O8 (a) split of S10 and S11 was not taken.** The designer's estimate was under the trigger, and S10 and S11
  were built by then. The ticket's own source is about 1.5k insertions against est 700; size is not a finding.

**The lead's results** (do not re-run whole suites; small probes are yours):
- `gov accept W2-187` passes: 205 passed, 0 failed, every line `success-1` to `success-12` and `failure-1` to
  `failure-7` pass.
- `tests/acceptance/W2-170` 184 passed; `W2-171` 140 passed; `W2-172` 162 passed; `W2-173` 91 passed; `W2-88` 215
  passed; `tests/unit/memaudit` 354 passed.
- The scoped `lead_verify` runs in parallel.
- No QA engineer ran: the launcher has no `qa-engineer` role, so this review also carries the KPI trace. For each KPI
  line, say which tests and which code meet it, and whether a test could pass for the wrong reason.

**Look hard at:**
- counts only (S4, F1, F7): no id, question, gold, answer, citation, path or secret leaves a run folder or reaches a
  line, log, digest, ACT text or `REANCHOR` file;
- the one judged path (S3, F4): no second copy of the reader path; `prompts.py` unchanged;
- the week rule and use-once (S2, F2, F5), and fresh-path behaviour unchanged without `--week` and with no live set;
- F3: no command compares configurations;
- `maintain` never a gate and never changing a setting (S10, F6);
- the scan-then-push order and fail-closed scan (S12, F7);
- the keyed state (S9);
- writes outside `allowed_paths`.

## Held-out rules (DEC-820)
Never open the real sets root (`~/gov-os-eval`), the real runs folder (`~/gov-os-runs`, any `indep/` under it), any hidden
half or memory-verdict folder, the real crontab. Never a real model call, a real search, a real push to a real remote, or
a real gitleaks over a real repository. Probes plant everything in your sandbox's `$TMPDIR`. Any pytest goes through
`bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh env HOME=<an empty folder in $TMPDIR> PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-187/src python3 -m pytest <one file or case> -q -p no:cacheprovider -o tmp_path_retention_policy=failed`
with a Bash timeout of 3600000 ms; a heavy-slot refusal is a wait. Search with the Read, Grep and Glob tools; if the first
search does not answer, search once more in different words (DEC-1065). No `gov retrieve`, no `gov context`.

The ticket's context packet (`gov context DAEO-0cd2 --role independent-auditor`, built by your lead from the integration
store) follows; the ticket file above is authoritative where they differ.

----

{
  "ticket": "DAEO-0cd2",
  "ticket_text": "---\nid: DAEO-0cd2\nwbs_id: W2-187\nexternal-ref: W2-187\ntitle: \"The standing hidden set: each repository's memory judged end to end every week on the same questions at 95 %, counts only, with a monthly fresh set as the check against fitting, a weekly maintenance pass, and the audit's state per repository (MEMORY-AUDIT G1, G2, G3, G5 and G4's code)\"\ntype: task\nclass: implementation\nrole: engineer\nprofile: FULL\nstatus: in_progress\nstate_class: AUTHORITATIVE\npriority: 1\ncreated: 2026-11-14\ndeps: [DAEO-f58b, DAEO-rmhj]\nallowed_paths:\n- src/gov/memaudit/**\n- src/gov/adopt/memory_sets.py\n- governance/project/orchestration/tools/memaudit_cron.sh\n- tests/unit/memaudit/**\n- tests/unit/adopt/test_w2_187*\n- tests/acceptance/W2-170/test_w2_170_s3_declare.py\n- tests/acceptance/W2-170/w2_170_world.py\n- tests/acceptance/W2-171/test_w2_171_s3_judge.py\n- tests/acceptance/W2-171/w2_171_world.py\n- tests/acceptance/W2-171/w2_171_scenario.py\n- tests/acceptance/W2-171/test_w2_171_cli_layout_ledger.py\n- tests/acceptance/W2-171/test_w2_171_s5_misses_f2.py\n- tests/acceptance/W2-172/test_w2_172_s7_digest.py\n- tests/acceptance/W2-172/w2_172_world.py\n- tests/acceptance/W2-172/w2_172_git.py\n- docs/changes/W2-187-evidence.md\n- docs/probes/DAEO-0cd2/**\nreads:\n- .gov-runtime/scratch/orchestrator/drafts/memory-scope-20261113/MEMORY-AUDIT.md\n- governance/project/orchestration/packages/MEMORY-AUDIT-P1.md\n- governance/project/orchestration/packages/MEMORY-AUDIT-1.md\n- governance/project/orchestration/packages/LIFT-1/FRESH-80-1.md\n- governance/project/orchestration/packages/LIFT-1/E3-RESULT.md\n- governance/project/orchestration/packages/LIFT-1/E3-SA-RESULT.md\n- src/gov/retrieval/measure.py\n- src/gov/rebuild/integration.py\n- src/gov/links/command.py\n- src/gov/adopt/**\n- tests/acceptance/W2-170/**\n- tests/acceptance/W2-171/**\n- tests/acceptance/W2-172/**\n- tests/acceptance/W2-173/**\n- tests/acceptance/W2-88/**\nneeds:\n- src/gov/rebuild/integration.py\n- src/gov/retrieval/retrieve.py\nwaits_on:\n- ref: DAEO-f58b\n  reason: 'the maintenance pass brings the store to the main line''s head through W2-116''s double-buffered integration store (closed)'\n- ref: DAEO-rmhj\n  reason: 'the standing run checks each search result''s store commit (W2-138''s field) against the declared store; the maintenance pass reads it'\nest_loc: 700\nkpis:\n  success:\n  - 'S1 A standing set: `python3 -m gov.memaudit standing declare --set <name> --repo <dir>` records one standing set for the repository: its name, its digest (`LC_ALL=C sha256sum *.yaml | sha256sum` over the kept questions), n with the nonexistent-id questions apart, the sha256 of the writer''s and checker''s briefs, and the commit it was written at. A set whose questions were ever written to a `misses.jsonl` or read by an auditor is refused (`STANDING_SPENT`); an adopted repository''s Wave 0 verdict set is accepted once its `USED` marker and its counts-only result record exist (W2-88 S13, S16). One standing set is live per repository; a second is refused until the first is retired [DEC-1179 (1), DEC-1176 (1), DEC-1098 (1)] Verify: planted sets: a new set is recorded with each field; a set with a planted `misses.jsonl` line is refused with `STANDING_SPENT`; a planted Wave 0 verdict set with `USED` and its record is accepted; a second live set is refused'\n  - 'S2 One judged run a week: a standing run writes `runs/<set>/<ISO year>-W<week>/DECLARATION.json` and then `USED`, before any search; a second judged run of the same set in the same ISO week exits 3 and writes nothing. A run stopped by the fault rule (FRESH-80-1 \u00a73.5, `STOPPED <cause>`) before its reader run started may start once more that week; a run whose reader run started never runs again [DEC-1179 (1), DEC-1097 (1)(g)] Verify: planted runs: the file times and the ledger line show DECLARATION.json before USED before the first search; a second run the same week exits 3 with the tree byte-identical; a planted STOPPED before the reader run allows one restart and a second is refused'\n  - 'S3 The same method as Gov OS''s memory: a standing run uses the fresh 80''s judged path unchanged: the store at the audit commit with the standard (the 0.6B through the one shared reranker, the pool on, the 6,000-token bundle widened to sections); each question''s first bundle from `gov.retrieval.measure`; `judge`''s reader run as built (the pinned `prompts.py`, the reader, the cap, the A2 cut judged, A1 and A3 as data); the named grader with the second grader''s agreement; the measure''s matcher with source families. Every search result''s store commit (W2-138) equal to the declared store''s commit, else that attempt is a fault [DEC-1179 (1), DEC-1097 (1)(a), DEC-1098 (1), DEC-1092 (1)] Verify: `tests/unit/memaudit/test_prompts.py` passes unchanged; a planted standing run calls the same reader, grader and matcher functions as a fresh run (one shared code path, asserted by a spy); a planted result from another store commit makes the attempt a fault'\n  - 'S4 Counts only: a standing run writes no `misses.jsonl` and launches no auditor. Only counts leave its run folder: right end to end, wrong claims, not found, the misses by outcome (wrong, incomplete, not found) and by the first gold place''s rank in the first bundle (1-5, 6-20, absent), the questions dropped by the anchor check, and the figures beside (hit@5, gold in the first bundle, A1 against A2 with exact McNemar). No question id, question, gold, answer or citation of the standing set is printed, logged, written to `FIGURES.json`, `HISTORY.jsonl`, `AUDITS.log` or the digest block, or written outside its run folder (mode 0700) [DEC-1179 (2), DEC-1101 (2), DEC-1074 (1)] Verify: a planted standing run with five planted misses whose ids and texts are unique strings: no planted string appears in stdout, stderr, FIGURES.json, HISTORY.jsonl, AUDITS.log, the digest block or any file outside the run folder; no misses.jsonl exists; no auditor launch event is in the ledger'\n  - 'S5 The bar at 95 %: `declare.bar(n)` gives `need_right = ceil(95 n / 100)` and `max_wrong = floor(5 n / 100)`; a verdict passes when right end to end at A2 reaches `need_right` (wrong claims stay reported and checked). It applies to standing and fresh runs alike, and the declaration''s rounding text says so. On 80 judged that is 76, on 79 it is 76, on 40 it is 38 [DEC-1179 (2), DEC-1097 (1)(d) as carried forward, DEC-957] Verify: unit cases n = 40, 79, 80 give 38, 76, 76; a planted run with right = need_right - 1 is a miss and with right = need_right a pass; the digest''s bar line prints the new figure; the revised W2-170, W2-171 and W2-172 cases pass, and W2-88''s S15 bar case (which reads W2-170''s helper `bar`) passes unedited'\n  - 'S6 Staleness by count: before each standing run the pre-flight checks each question''s gold anchors at the audit commit; a question whose anchor no longer resolves, or whose nonexistent id now exists, is dropped from that week''s n and counted (`dropped k`); nothing in the set is edited. Fewer than 70 live questions prints `STANDING_THIN <live>` in the digest block and asks for a replacement [DEC-1179 (2), DEC-1097 (1)(f)] Verify: a planted set of 80 with 3 broken anchors: n is 77 and `dropped 3` is printed with no id; the set''s digest is unchanged after the run; a planted set with 69 live questions prints STANDING_THIN 69'\n  - 'S7 The monthly check against fitting: at each fresh run the tool compares the fresh set''s right end to end per cent F with S, the mean of the standing set''s last four weekly figures; S - F of 5 points or more writes `STANDING_FITTED` in HISTORY.jsonl and the digest block, retires the standing set (no further standing run on it; it joins the pool as a diagnostic set, counts only) and asks for the writer''s replacement; F - S of 5 points or more writes `STANDING_STALE` and asks for the checker''s staleness pass; with fewer than four weekly figures the check prints `drift: not yet (k of 4)` [DEC-1179 (3), DEC-1074 (4)] Verify: planted histories: S 96, F 90 retires the set and a later standing run on it is refused; S 90, F 96 prints STANDING_STALE; S 95, F 92 prints no flag; two weekly figures print `drift: not yet (2 of 4)`'\n  - 'S8 The two cadences and below 95 %: the standing set''s cadence is W2-172 S5''s computed rule, unchanged (weekly while active, monthly once stable, back to weekly at once on a miss, a retrieval change, churn of 10 % or more or a pool regression); the fresh set is due on the first Monday 28 days or more after the last fresh run. A standing miss is a HISTORY line `miss` with its counts; the fresh set is then due at the next Monday and every Monday until a standing run passes again (then every 28 days); the maintenance pass (S10) runs at once after the miss in the same cycle; the digest block carries a `P1 memory below 95 %` line with the counts by class. Two consecutive standing misses, or one miss 5 points or more below the last passing figure, write `MEMORY_REPAIR open` in HISTORY.jsonl, and `gov.memaudit status --repair` exits 1 while it is open and 0 once a later standing run passes or the owner''s decision id is given with `--residual DEC-<n>` [DEC-1179 (4), (5), DEC-1125 (2)] Verify: `tests/acceptance/W2-172/test_w2_172_s5_due.py` passes unchanged for the standing set; a planted fresh history 27 days old is not due and 28 days old is due on the Monday; planted histories: one miss makes the fresh set due next Monday and puts the P1 line in the digest; pass, miss, miss opens the repair; pass at 96 then miss at 90 opens it; `status --repair` exits 1, then 0 after a planted pass or `--residual DEC-1`'\n  - 'S9 State per repository: the runs folder is `<runs>/indep/memaudit/<key>/` with `<key>` the repository''s directory name, a hyphen and the first 8 hex of the sha256 of its real path, so two repositories on one machine keep separate `AUDITS.log`, `HISTORY.jsonl` and `STARTS.log`. The retrieval change that sends an audit back to weekly is, for any repository, a change of the gov pin, of the repository''s `governance/project/retrieval.yaml` digest or of its path map''s digest, and for Gov OS also its six retrieval globs. `pool-import --sets <name>...` seeds the pool from that repository''s own sets root; with no `--sets` on Gov OS it imports Gov OS''s 79 and 138 as today [DEC-1179 (5), DEC-1101 (1), DEC-1125 (2)] Verify: two planted repositories on one runs folder write to two keys and neither reads the other''s history; a planted pin change on an adopted repository is a retrieval change and a change under `src/gov/retrieval/` of Gov OS is not, for it; `pool-import --sets a b` imports exactly those sets'\n  - 'S10 One weekly maintenance pass before each standing run, `python3 -m gov.memaudit maintain --repo <dir>`: (1) the integration store at the main line''s head, else one refresh by W2-116''s `gov rebuild --integration`, a failed build leaving the last good store in service and named; (2) the store''s layout current, else one `gov rebuild`; (3) `gov links --since <the last pass''s commit>`: the count of new findings; (4) the count of tracked paths the path map indexes but the store holds no chunk of; (5) the standing and fresh runs'' reader `not found` answers and second searches, counted; (6) the list of gold questions whose cited lines changed at the audit commit (W2-61h S4''s list, with N2 (b), DEC-1180 (1): a heading-cited source whose section text (from its heading line to the next heading of the same or a higher level, or the end of the file) differs between the source''s own commit and the head is listed too, though its heading is still found; question id and entry number only, never a question, answer or path) handed to the walled writer''s request for re-anchoring or rewording, counted. It prints six counts in the digest block, never fails or delays the audit, and never changes one of the standard''s four settings [DEC-1179 (6), DEC-1178 (1), DEC-1072 (1), DEC-1101 (1), DEC-1096] Verify: a planted repository with a store 3 commits behind is refreshed once and the head printed; a planted failing rebuild keeps the old store and names the failure; planted link findings and two unindexed paths are counted; the audit runs whatever the pass finds; the retrieval.yaml digest is unchanged after the pass; a planted set with one changed cited block and one moved unchanged block lists only the changed one, by question id and entry number, in the writer''s request, with no question, answer or path text in it or in the digest'\n  - 'S11 The schedule''s code (G4): `memaudit_cron.sh` takes `--repo <dir>` and runs, when due, the maintenance pass, the standing run and, when the fresh set is due, the fresh cycle, in that order, within the gate''s wait (W2-172 S9); A9''s ACT package (`memory_sets.walls_act`) adds one step to its ACT.md with the repository''s cron line (the wrapper with `--repo <that repository>`, Mondays 21:00), written as text for the repository''s owner''s operator and never installed [DEC-1179 (5), DEC-1101 (2), W2-88 S22] Verify: a planted due standing run and a due fresh set run in that order from one wrapper call; nothing runs when neither is due; a planted A9 run''s ACT.md holds the cron line with the repository''s path and no crontab is changed'\n  - 'S12 The weekly secret scan and push (DEC-1182 (2)): after the weekly audit and measure (the maintenance pass, the standing run and, when due, the fresh cycle), a repository that declares its weekly push (its remote and branch, in the key I11 names) gets one full gitleaks scan of the repository, then `git push <remote> <branch>` only when that scan is clean; a scan that finds anything, fails or cannot run blocks the push and is named in `cron.log` and the digest by count and reason only; a repository that declares no push (Gov OS, DEC-1182 (1)) skips both steps, named; no scan runs in the maintenance pass''s refresh. A9''s ACT package''s step 6 names the cycle''s order (audit and measure, scan, push on a clean scan) and how the repository''s owner declares the push [DEC-1182 (2), DEC-1179 (5), DEC-1101 (2)] Verify: a planted repository with a declared bare remote and a clean tree is scanned once and pushed after its audit; a planted secret in a tracked file blocks the push (the remote unchanged) and the log names a count, never the secret; a failing or missing gitleaks blocks the push, named; a planted repository with no declaration runs neither step and says so; a planted A9 run''s ACT.md step 6 names the order'\n  failure:\n  - 'F1 A standing set''s question id, question, gold, answer or citation outside its run folder, or read by any session: the auditor, the CTO, a worker or a later fix. Verify: S4''s planted strings are absent from every file written outside the run folder and from every launched session''s brief; no code path hands a standing run''s rows to `classes`, the auditor''s launch or the pool''s fix judging'\n  - 'F2 A standing set judged twice in one week, judged without DECLARATION.json and USED first, re-scored, or its labels changed after a figure exists. Verify: S2''s planted runs; `measure --kept` on a standing run exits 3 and writes nothing; the set''s digest is checked equal at every run and a planted edit is refused before any search'\n  - 'F3 The standing set used to choose, adopt or reject a fix or a configuration. Verify: the tool offers no command that compares two configurations or two commits on a standing set; the standing run refuses `--decision` and any data condition'\n  - 'F4 The method drifts: the reader or grader prompt, model, cap or A2 cut changed, or the standing path diverges from the fresh path. Verify: `test_prompts.py` passes unchanged; S3''s spy'\n  - 'F5 A fresh set''s use-once behaviour changes. Verify: W2-170''s S3 and F2 cases on fresh sets pass with only their bar values revised; W2-171''s S5 case passes with only its bar value revised (W2-187-P1 (a), DEC-1156 (7))'\n  - 'F6 The maintenance pass changes a setting of the standard, applies an ACT, installs a cron line or stops the audit. Verify: S10''s planted runs; the module imports no crontab writer and the retrieval.yaml and path map digests are unchanged after a pass'\n  - 'F7 A push after a scan that found anything, failed or did not run; a finding''s text (a secret, a match, a line) in `cron.log`, the digest, the ACT text or the push''s output; a scan or a push at a refresh, a close or a repository that declared no push. Verify: S12''s planted runs; the module''s scan call is the only gitleaks call in the cycle'\nnon_goals:\n- 'no new measuring method: the standing run reuses the fresh 80''s judged path as W2-170 to W2-173 built it'\n- 'no change to the adopt skill or the practice record (W2-188), and no `.claude/` copy'\n- 'no cron line installed and no walls or path-map change applied: those are ACT-MEMORY-AUDIT-CRON-1 for Gov OS (the CTO''s ACT) and each adopted repository''s own ACT package'\n- 'no writing of the standing set: the independent writer and checker write it under the owner''s approved brief'\n- 'no change to the release step or the re-pin ACT: they read `status --repair` (the CTO''s ACT text)'\n- 'no DEC-1101 (1) count of \"not found\" answers from agents'' work returns: the pass counts the audit runs'' own; the work-returns count stays the CTO''s tool until a decision gives it a product home'\ndone_when: [DOD-1, DOD-2, DOD-3, DOD-4, DOD-5, DOD-6]\nsources: [DEC-1182, DEC-1179, DEC-1176, DEC-1101, DEC-1125, DEC-1126, DEC-1098, DEC-1097, DEC-1092, DEC-1074, DEC-1071, DEC-1072, DEC-1156, DEC-974, DEC-105, DAEO-61vm, DAEO-k1e2, DAEO-p8tv, DAEO-qz4p, DAEO-2bdu, DAEO-f58b, DAEO-rmhj]\nacceptance_tests: {path: tests/acceptance/W2-187/}\n---\n\n# W2-187 The standing hidden set, judged every week at 95 %, counts only\n\n**Problem.** The memory audit (W2-170 to W2-173) writes a fresh 40 each week and measures each set once; old questions\nare re-run only for retrieval figures (the pool), never against the end-to-end bar, and 95 % is printed, not judged\n(`src/gov/memaudit/declare.py:32-33`). Its state is one folder per machine with Gov OS's retrieval paths\n(`schedule.py:18-22, 48-55`). There is no weekly maintenance job. The owner's MEMORY-AUDIT (a) (2026-11-14; DEC-1179,\nprovisional) wants each repository's memory judged end to end every week on the same hidden questions, as Gov OS's was\nmeasured, at 95 %, counts only, with a monthly fresh set as the check against fitting. The reconciliation, with file and\nline for each part, is `drafts/memory-scope-20261113/MEMORY-AUDIT.md` \u00a72 and \u00a73 (G1, G2, G3, G5).\n\n**Approach.** A `standing` mode beside the fresh mode in `gov.memaudit`, sharing its judged path. What differs:\n- the per-week marker instead of the per-set lock (S2);\n- no `misses.jsonl` and no auditor, counts only (S4);\n- the pre-flight's anchor check drops by count (S6);\n- the drift comparison at each fresh run (S7);\n- the below-95 states (S8).\n\nThe bar function changes for both modes (S5). The runs folder is keyed by repository (S9). `maintain` calls the\nexisting checks (S10). The wrapper and A9's ACT text carry the schedule (S11).\n\n**The method, exactly (S3; what \"double search, agents as second rerankers\" means here).** The fresh 80's judged\nconfiguration (FRESH-80-1 \u00a73.1, DEC-1097 (1)(a), accepted by DEC-1098 (1) at 78 of 79):\n- the store with the standard;\n- the first bundle from W2-61's measure (`gov.retrieval.measure`, 6,000 tokens, items widened to sections);\n- the reader reads the whole ranked bundle and decides what answers, a second ranking after the 0.6B (E3: 114 of 138 in\n  one call, against 84 for the top 5 and 101 for 40 unranked);\n- it may search again once with its own words, the A2 cut (E2: 115 at one search, 128 at two; E3-SA: a second search\n  never lost a right answer);\n- graded by the named grader, with the second grader's agreement;\n- the citation checked by the measure's matcher.\n\n\"A second reranker\" in W2-88 S10 and its failure line means a second reranking model; it stays forbidden, and the\nreader is not one.\n\n**Test revisions (decided behaviour, DEC-1156 (7)).** S5 changes the bar the W2-170, W2-171 and W2-172 cases pin (85 %).\nThe ticket's independent test designer revises exactly the six files in `allowed_paths`, with a `Rewrite-Reason` naming\nDEC-1179 (2): about 16 lines of values and helpers. `tests/unit/memaudit/` is the engineer's.\n\n**Rabbit holes.**\n- Do not copy the reader path into a second module: one path, two modes.\n- Do not print an id \"for debugging\".\n- Do not make the maintenance pass a gate.\n- Do not decide the replacement set's content: the writer's brief does.\n- Size: about 300-450 lines for G1 and G2, 100-150 for G3, 150-250 for G5, about 20 for S11, plus tests. If the test\n  designer's suite shows it larger than about 900 lines, S10 and S11 split off as W2-187b, pre-approved by the owner\n  (DEC-1179, O8 (a)): the lead tells the CTO, who files it, and nobody waits for a P1.\n\n**Filed 2026-11-14 on the owner's decision (DEC-1179, MEMORY-AUDIT-P1; O3 (b): S8's cadence is W2-172 S5's computed rule, unchanged).** S10 gains a sixth item from DEC-1178 (1): the list of gold questions whose cited lines changed, for the walled writer, which the owner's operator handles in the Monday slot until this ticket lands.\n\n## Interface (the CTO at claim, DEC-1179 (8), DEC-1157 (3) and (12); listed for the owner's reading)\n\n- **I1, the command line (`src/gov/memaudit/__main__.py`; S1, S2, S8, S9, S10, F2, F3).** The exit map stays as it is\n  (`gov.memaudit.EXIT`: 0 ok, 1 refused, 2 stopped, 3 used, 4 usage), `say` stays the only printer, and every subcommand\n  keeps `--sets-root` (required, as today). The new and changed subcommands:\n  - `standing declare --sets-root R --set <name> [--repo D] [--runs-dir DIR] [--replaces <old>]` (I3);\n  - `standing run --sets-root R [--repo D] [--store-link P] [--gov EXE] [--claude EXE] [--gate-cmd CMD]` (I4). It has no\n    `--decision`, no `--force` and no data flag, so any of them is argparse's exit 4 (F3);\n  - `standing live --sets-root R [--repo D]`: prints `KEY <key>`, then `LIVE <set>` (exit 0) or `LIVE none` (exit 1). It\n    writes nothing;\n  - `maintain --sets-root R [--repo D] [--store-link P] [--gov EXE]` (I10);\n  - `due --fresh` (I8); `status --repair [--residual DEC-<n>]`, with `--since` required only without `--repair` (I8);\n  - `pool-import --sets <name>...` (I9);\n  - `preflight`, `declare`, `measure`, `judge` and `figures` take `--week <YYYY>-W<ww>`. With it, the step works on the\n    standing set's week folder (I2). `--audit` then names the standing set. Without `--week`, every byte of the fresh path\n    is as today.\n  - Name forms (`layout.py`): `SET_RE = memory-(audit|standing)-[0-9]{8}` (a Wave 0 verdict set keeps its\n    `memory-audit-<date>` name; a new standing set is `memory-standing-<date>`) and `WEEK_RE = [0-9]{4}-W[0-9]{2}`, the\n    ISO year and week of `schedule.now()` in UTC (the `GOV_MEMAUDIT_NOW` seam).\n\n- **I2, where things live (`layout.py`, `schedule.py`; S2, S4, S9).**\n  - `layout.paths(sets_root, name, week=None)` gives today's dict. With `week`, its `run` is\n    `<sets root>/runs/<set>/<week>/` (mode 0700, `make_run`), and `preflight`, `declaration`, `used` and `ledger` lie in\n    it. `set`, `hidden` and `map` are as today. \"Its run folder\" in S4 and F1 is `<sets root>/runs/<set>/` and everything\n    under it.\n  - `schedule.state_dir(runs, repo) -> Path` is `<runs>/indep/memaudit/<key>/`. `<key>` is\n    `os.path.basename(real) + \"-\" + sha256(real.encode()).hexdigest()[:8]`, where `real = os.path.realpath(repo)`.\n    `schedule.folder(runs)` is replaced by it everywhere (driver, due, status, baseline, maintain). The folder holds:\n    - `HISTORY.jsonl`, `STARTS.log`, `LOCK` and `cron.log`;\n    - `STANDING.jsonl` (I3) and `MAINTAIN.jsonl` (I10);\n    - `<audit>/` (a fresh run's `COUNTS.json` and `DIGEST.txt`, as today) and `standing/<set>/<week>/` (the same two files\n      for a standing run).\n  - The driver passes `GOV_INDEP_RUNS_DIR=<key folder>` to every child it starts (it passes `<runs>` today). The launch\n    script's `AUDITS.log`, `SEEDS.log` and `<kind>/<run>/counts.json` therefore land in `<key folder>/indep/`.\n    `schedule.last_audit_commit`, `driver._refusal`'s `RN-NOBASE`, `baseline` and `preflight` (through its\n    `$GOV_INDEP_RUNS_DIR` default) read them there. The launch script is unchanged.\n  - Nothing of a standing set's questions is written under `<runs>`. `STANDING.jsonl` holds the set's name, digests,\n    counts and commits only.\n\n- **I3, `standing declare` (new module `src/gov/memaudit/standing.py`: the record, the spent check, the week rule, drift\n  and repair; it calls the existing modules and copies none; S1, F1).**\n  - **The call:** `standing.declare(sets_root, name, *, repo, runs_dir, replaces=None) -> (word, counts)`.\n  - **The refusals, checked in this order, with nothing written:**\n    - `STANDING_SPENT <k>` (exit 1): some `question` of the set's `hidden/*.yaml` equals the `question` of a line in\n      any `<sets root>/runs/**/misses.jsonl`; or `<sets root>/runs/<set>/**/miss-classes.json` exists; or an\n      `AUDITS.log` line (in `<key folder>/indep/` and in `<runs-dir>/indep/`) has `audit == <name>`. `<k>` is the count\n      of matched questions, never an id.\n    - The set's own `runs/<set>/USED` exists: the set is accepted only as the repository's Wave 0 verdict set.\n      `runs/<set>/DECLARATION.json` and `runs/<set>/FIGURES.json` (its counts-only result record) must exist, and the\n      declaration's `audit_commit` must equal the commit of the first line of the repository's `AUDITS.log` (the\n      baseline W2-88 S21 writes at the verdict commit). Otherwise `STANDING_SPENT 0`. The spent check skips only that\n      Wave 0 run's own `runs/<set>/misses.jsonl` and `miss-classes.json` (see the unresolved item U1).\n    - `STANDING_LIVE <live set>`: `STANDING.jsonl` holds a live set. `--replaces <old>` lifts this only when `<old>` is\n      the live set and its last weekly HISTORY line carries `STANDING_THIN` (O5 (a)). `<old>` is then retired with\n      reason `thin` in the same write.\n    - `STANDING_BRIEFS`: no delivered writer and checker `counts.json` (`status == \"delivered\"`, `set == <name>`) is\n      found under `<runs-dir>/indep/{writer,checker}/*/` or `<key folder>/indep/{writer,checker}/*/`. `--runs-dir`\n      defaults as `preflight` defaults: `$GOV_INDEP_RUNS_DIR`, else `~/gov-os-runs`.\n    - `STANDING_FORM`: a file fails `preflight.form_ok`, or `hidden/` holds fewer than 36 files.\n  - **The write:** one `STANDING.jsonl` line:\n    `{\"event\": \"declared\", \"set\", \"set_digest\" (common.set_digest(hidden)), \"n\", \"n_apart\", \"writer_brief_sha256\",\n    \"checker_brief_sha256\", \"written_commit\" (the writer counts' commit), \"wave0\": bool, \"at\"}`.\n  - **The output:** `STANDING DECLARED <set>: n <n> apart <k> digest <12 hex> written at <12 hex>`, exit 0.\n\n- **I4, `standing run` (`driver.standing(...)` beside `driver.run`, reusing `_Cycle`, `_refusal`'s RN-LOCK, RN-REBUILD,\n  RN-SIDE and RN-STALE, `_history` and `_finish`; S2, S3, S4, S6, F2, F3, F4).**\n  - **Its children,** in order, each `python3 -m gov.memaudit <step> --sets-root R --audit <set> --week <week> ...`:\n    `preflight` (I6), `measure`, `judge`, `figures`. The gate is asked before `measure` and `judge`, as today (`GATED`).\n  - **No `classes`, auditor launch, `pool` or writer launch:** `classes` and `pool` refuse a standing set name\n    (`MS-STANDING`, exit 1), and so does `pool-import` (F1).\n  - **The week rule** (`standing.week_state(paths)`; S2) is checked before anything is written:\n    - The week folder is absent, or present without `USED`: the run goes on (the folder is re-used).\n    - `USED` present with `reader/` or `FIGURES.json`, or `USED` present with no `STOPPED`: `USED`, exit 3, nothing\n      written (no STARTS line, no digest).\n    - `STOPPED` present with no `reader/`, and `<week>.stopped/` absent: the week folder is renamed to `<week>.stopped/`\n      and the run starts once more.\n    - `STOPPED` present and `<week>.stopped/` present: `USED`, exit 3.\n  - **Before any search,** the refusals are `STANDING_NONE`, `STANDING_RETIRED` and `STANDING_DIGEST`. The last is\n    `common.set_digest(hidden)` not equal to the record's `set_digest`; then nothing is written and the week is not spent\n    (F2).\n  - **The one judged path:**\n    - `declare.declare(..., week=)` writes `DECLARATION.json`, its ledger line, then `USED`, as today. In standing mode\n      `n` is the live count from the week's `PREFLIGHT.json`; `n_set` and `dropped` are recorded beside it.\n      `DC-DROPS` is not asked.\n    - A nonstandard `retrieval.yaml` is `DC-DECISION` with no way to allow it (F3).\n    - `measure.run(..., week=)` measures the whole `hidden` part (wholeness against `n_set`) and scores the live ids.\n    - `judge.run(..., week=)` asks only the live questions, by `_Judge.one`, `prompts` and `matcher` unchanged (S3's\n      spy).\n    - `figures.build` runs as today. In standing mode `figures.write_misses` is not called, and judge's `SEARCH FAILED`\n      line prints its count with no ids (S4).\n  - **The store commit (S3; W2-138's field `result.store.commit`):** `fault.not_whole(folder, n, families,\n    store_commit=None)`. In standing mode it gives the cause `store_commit` when any kept result's `result.store.commit`\n    is absent or not the declaration's `store_commit`; that attempt is then a fault under the existing rule (one restart,\n    then `STOPPED fault`). A later search in `judge.search` from another commit is a counted search failure with an empty\n    bundle (`why` `store`).\n  - **After `figures`,** one HISTORY line:\n    `{\"kind\": \"standing\", \"set\", \"week\", \"audit\": <set>, \"commit\", \"at\", \"mode\", \"churn\", \"retrieval_28d\", \"passes\",\n    \"pool_regression\" (the last fresh line's), \"measured\": true, \"used\": true, \"n\", \"right\", \"wrong\", \"not_found\",\n    \"dropped\", \"pct\" (100 right / n), \"word\": \"pass\"|\"miss\", \"gov_pin\", \"retrieval_yaml_sha256\", \"path_map_sha256\"}`.\n    Then the states of I7 and I8, and the digest (I12).\n  - **The last stdout line** is `STANDING <week> right <r> of <n>: passes|misses`.\n  - **Exit:** 0 when the run ran (a miss is data, not a failure), 1 refused, 2 stopped, 3 week spent, 4 usage.\n\n- **I5, the bar (`declare.bar`, `declare.ROUNDING`; S5).**\n  - `bar(n) = {\"need_right\": -(-95 * n // 100), \"max_wrong\": 5 * n // 100, \"target_right\": -(-95 * n // 100)}`, which\n    gives 38, 76 and 76 for n = 40, 79 and 80.\n  - `figures.build`'s `passes` stays `right >= need_right and wrong <= max_wrong`; the second half is implied\n    (n - ceil(0.95 n) = floor(0.05 n)).\n  - `ROUNDING = \"need_right = ceil(95 n / 100); max_wrong = floor(5 n / 100); target_right = need_right; integer\n    arithmetic; standing and fresh runs alike (DEC-1179 (2))\"`.\n  - The digest's VERDICT line and `verdict_lines` print it unchanged. The revised W2-170 helper `bar` returns this dict,\n    key for key, so W2-88's S15 case passes unedited.\n\n- **I6, the standing pre-flight (`preflight.standing(sets_root, name, *, week, commit, repo) -> (word, counts)`; S6,\n  F2).**\n  - **Each question is loaded alone** through `matcher.questions(sets_root, set, \"hidden\", root, only=<stem>)`, a new\n    one-file form. `root` is the store link's worktree at the audit commit. A load fault drops that one question, never\n    the set.\n  - **A question is dropped** when some entry of its `sources` has every alternative unresolved (`q[\"unresolved\"]` names\n    `entry n`, or `entry n.m` for every `m`), or when it is a nonexistent-id question and `preflight.id_exists` finds its\n    id.\n  - **The write:** `PREFLIGHT.json` in the week folder:\n    `{\"mode\": \"standing\", \"ok\", \"n_set\", \"n\", \"dropped\", \"dropped_ids\", \"n_apart\", \"set_digest\", \"files_sha256\"}`. Ids\n    stay in the run folder. `declare.preflighted` reads the same `files_sha256`.\n  - **The output** is the single line `PRE-FLIGHT standing: n <n> of <n_set>; dropped <k>`, with no id. `ok` is false\n    only for `STANDING_DIGEST`. Nothing in the set is edited or moved, so `void` is never called.\n  - **Fewer than 70 live questions** puts `STANDING_THIN <live>` in the HISTORY line's `word` list and in the digest\n    (O5 (a)).\n\n- **I7, the check against fitting at each fresh run (`standing.drift(state, fresh_fig) -> dict`, called in `driver.run`\n  after `figures`; S7).**\n  - **The figures:** F is `100 * right / n` of the fresh run; S is the mean `pct` of the live set's last four standing\n    measured lines.\n  - **Fewer than four lines** gives `drift: not yet (k of 4)`.\n  - **S - F >= 5:**\n    - a HISTORY line `{\"kind\": \"drift\", \"word\": \"STANDING_FITTED\", \"S\", \"F\", \"set\"}`;\n    - a `STANDING.jsonl` line `{\"event\": \"retired\", \"reason\": \"fitted\"}`;\n    - a later `standing run` on that set is `STANDING_RETIRED`, exit 1.\n  - **F - S >= 5:** the word is `STANDING_STALE`; nothing is retired.\n  - **The retired set as a diagnostic set (counts only):** `pool.run` re-measures each retired set in place, retrieval\n    only, into `<sets root>/runs/<set>/diagnostic-<audit>/`. It prints `POOL DIAGNOSTIC <set> hit5 <k> of <n>; full <k>`\n    and never copies its files into `memory-pool/` (S4).\n  - **With no live standing set,** `driver.run` writes its lines without `kind`, exactly as today.\n\n- **I8, the two cadences, the miss and the repair (`schedule.py`, `standing.py`; S8).**\n  - **The standing cadence:** `due` (its three lines and exit codes unchanged) is `schedule.decide(repo, state, head, at,\n    lines)`, unchanged, over the live set's own standing lines. With no live set it reads the lines with no `kind`, which\n    is W2-172's unedited S5 case. STARTS.log lines gain `\"kind\": \"standing\"|\"fresh\"` once a set is live.\n  - **The fresh cadence:** `due --fresh` prints `MODE fresh`, `DUE yes|no next <yyyy-mm-dd>` and\n    `REASON first|28d|miss|wait`.\n    - `first`: no fresh start.\n    - `miss`: the live set's last standing measured line has `passes: false` and no fresh start in the current ISO week.\n    - `28d`: today is on or after the first Monday on or after (last fresh start's date + 28 days).\n    - With no live set it answers as `due`.\n  - **A miss** is the standing HISTORY line with `\"word\": \"miss\"`. The P1 digest line is in I12.\n  - **The repair:** after each standing measured line, a HISTORY line\n    `{\"kind\": \"repair\", \"word\": \"MEMORY_REPAIR open\", \"set\", \"week\"}` is written when none is open and either:\n    - this line and the previous standing line are both misses; or\n    - this line is a miss and the last passing `pct` minus this `pct` is 5 or more.\n\n    A later pass writes `MEMORY_REPAIR closed`.\n  - **`status --repair`:** prints `REPAIR open since <week>` (exit 1) or `REPAIR none` (exit 0). With\n    `--residual DEC-<n>` it appends `{\"kind\": \"repair\", \"word\": \"MEMORY_REPAIR residual\", \"decision\": \"DEC-<n>\"}`,\n    prints `REPAIR residual DEC-<n>` and exits 0. A malformed id is exit 4.\n\n- **I9, a retrieval change per repository, and `pool-import --sets` (`schedule.retrieval_changed`, `pool.importing`;\n  S9).**\n  - `retrieval_changed(repo, since, until, gov=None)` keeps today's diff over the six globs for every repository. In an\n    adopted repository the four code globs match nothing it tracks, so only `retrieval.yaml` and the path map count there.\n  - It adds `gov-pin` when `declare.gov_pin(gov or ~/.local/bin/gov)` differs from the last HISTORY line's `gov_pin`. A\n    line without the field (W2-172's planted lines) is no trigger.\n  - `pool-import --sets a b` imports exactly those sets' `hidden` parts (and `visible` where present) from that sets\n    root, leaving out nonexistent-id questions as today. It has no 79/138 count check. Each set is imported once\n    (`runs/memory-pool/IMPORTED-<set>.json`; `MS-IMPORTED` names it again). A standing set name is `MS-STANDING`. With\n    no `--sets`, the import is today's, byte for byte.\n\n- **I10, `maintain` (new module `src/gov/memaudit/maintain.py`; S10, F6).**\n  - **Its six items,** each bounded by a timeout (`GOV_MEMAUDIT_MAINTAIN_TIMEOUT_S`, default 1800 for a build, 300\n    otherwise):\n    1. **The store:** `schedule.head_of(store_link)` against `git rev-parse <mainline>`. When behind, one\n       `<gov> rebuild --integration <mainline branch>`. A failure keeps the store in service and is named:\n       `kept <12 hex> (refresh exit <c>)`.\n    2. **The layout:** `gov.store.layout.found_of` on `<link>/.gov-runtime/store.db`, read-only. When not None, one\n       rebuild by the same command, else named `stale kept`.\n    3. **The links:** `<gov> links --since <the last MAINTAIN line's commit> --json` in the repository; the count of new\n       findings. On a first pass it runs from the mark with no `--since`; a refusal is `none`.\n    4. **Unindexed paths:** tracked paths of the link worktree that `gov.retrieval.lexical.kept_out` does not keep out,\n       less the distinct `path` values of `lexical_chunk` in its store; the count.\n    5. **Not found and second searches:** from the latest standing week folder's and the latest fresh run's\n       `reader/*.json`, the rows with `final_verdict == \"not_found\"` and the rows with a non-empty `searches`; two\n       counts.\n    6. **The changed cited lines:** for every set the sets root's path map declares, except standing sets (live or\n       retired), `matcher.questions(sets_root, set, part, link)`'s `unresolved` entries. This is W2-61h S4's list:\n       re-anchoring runs in memory, so a block moved unchanged is not listed. With N2 (b) (DEC-1180 (1)), a heading-cited source whose section text (from its heading line to the next heading of the same or a higher level, or the end of the file) differs between the source's own commit and the head is listed too, though its heading is still found, though `matcher` resolves it; an entry is listed once. One request per set with at least one\n       entry goes to `<sets root>/runs/<set>/REANCHOR-<week>.json` (mode 0600, written whole; the folder made 0700 by\n       `layout.make_run`):\n\n       `{\"week\", \"audit_commit\", \"set\", \"changed\": [{\"id\", \"entry\"}], \"count\"}`\n\n       It holds no question, answer or path. This mirrors the auditor's walled input, which the launch script takes from\n       `runs/<audit>/` (kinds.yaml `auditor.input: [set, misses]`). Count: the total.\n  - **The write:** one `MAINTAIN.jsonl` line in the key folder: the week, the commit, the six items, and the sha256 of\n    `retrieval.yaml` and of the path map before and after (equal, F6).\n  - **The output:** one line,\n    `MAINTAIN 1 store <word> 2 layout <word> 3 links <k> 4 unindexed <k> 5 not_found <a> second <b> 6 reanchor <k>`.\n  - **Exit 0 always,** except 4 for usage. The module imports no crontab writer, applies no ACT and never writes\n    `retrieval.yaml` or the path map.\n\n- **I11, the schedule's code (`memaudit_cron.sh`, `memory_sets.walls_act`; S11).**\n  - **The wrapper:**\n    - It takes `--repo <dir>` (default: the cwd's top level), runs `cd` into it, and keeps its variables\n      (`GOV_MEMAUDIT_PYTHON`, `GOV_MEMAUDIT_SETS_ROOT`, `GOV_INDEP_RUNS_DIR`, `GOV_MEMAUDIT_GATE`).\n    - It first calls `standing live --repo`. Exit 0 gives the live path: `due` and `due --fresh`; then `maintain` when\n      either is due; `standing run --gate-cmd` when `due`; `maintain` once more when that run's last line ends `misses`\n      (S8 R4); and `run --gate-cmd` when `due --fresh`, in that order.\n    - Any other exit gives today's path, byte for byte (`due`, then `run`). That keeps W2-172 S9's shim cases green:\n      the shim passes `standing live` to the real interpreter, which answers `LIVE none`.\n    - `cron.log` is `<key folder>/cron.log` (the `KEY` line), else `$RUNS/indep/memaudit/cron.log`. Its line's six keys\n      are unchanged. The exit is the last started step's.\n  - **The ACT text:** `walls_act(out, *, sets_root, audit, made, blind, repo=None)`. `repo` defaults to the git top level\n    of `out`, which A9 writes inside the repository; `fabric.py` stays unchanged. ACT.md gains step 6:\n\n    `6. Install the weekly memory audit's cron line for this repository (Mondays 21:00; never installed by adoption):\n    \\`0 21 * * 1 GOV_MEMAUDIT_SETS_ROOT=<sets_root> <GOV_OS>/governance/project/orchestration/tools/memaudit_cron.sh\n    --repo <repo>\\``\n\n    It is text only; no crontab is read or written.\n\n- **I12, the digest lines (`digest.py`; S4, S6, S7, S8, S10).**\n  - **A standing run's block** (`standing/<set>/<week>/DIGEST.txt`, and on stdout):\n    - `STANDING <set> week <week> commit <12>`;\n    - `VERDICT right <r> of <n>; wrong <w>; not found <f>; bar <need> right: passes|misses`;\n    - `MISSES outcome wrong <a> incomplete <b> not_found <c>; rank 1-5 <x> 6-20 <y> absent <z>`;\n    - `QUESTIONS live <n> of <n_set>; dropped <k>` (and `STANDING_THIN <live>` below 70);\n    - `BESIDE hit5 <k> of <n_gold>; first bundle <k>; A1 <a> A2 <b>: <g> gains <l> losses, exact McNemar p <p>`;\n    - the I10 `MAINTAIN` line;\n    - `P1 memory below 95 %: wrong <a> incomplete <b> not_found <c>` on a miss, else `P1 none`;\n    - `REPAIR open|none`;\n    - `NEXT standing <date> <mode>; fresh <date>`;\n    - `STOP ...` and `OWNER ...` as W2-172's lines.\n  - **A fresh run's twelve lines are unchanged.** After them come `DRIFT S <s> F <f>: none|STANDING_FITTED|STANDING_STALE`\n    (or `DRIFT not yet (k of 4)`) and the latest `MAINTAIN` line, with a live set only. The revised W2-172 S7 case counts\n    them.\n  - **No line** holds a question id, question, gold, answer, citation or path of a standing set.\n\n- **How the code-bound clauses read:**\n  - **S1's command** is `standing declare` with `--sets-root` required, as every subcommand. \"The sha256 of the writer's\n    and checker's briefs\" is the `brief_sha256` of their delivered `counts.json`. \"The commit it was written at\" is the\n    writer counts' `commit`. \"Ever written to a misses.jsonl\" is matched by question text.\n  - **S2's \"writes nothing\"** covers the sets root, the key folder and stdout's digest (only the `USED` line is printed).\n  - **S4's \"AUDITS.log\"** is the repository's `<key folder>/indep/AUDITS.log`, which a standing run never touches.\n  - **S5's \"the revised W2-170, W2-171 and W2-172 cases\"** are the six files in `allowed_paths`, plus the two helpers in\n    Gap G1.\n  - **S9's \"keep separate AUDITS.log\"** is met with the launch script's AUDITS.log at `<key folder>/indep/AUDITS.log`\n    (I2), not `<key folder>/AUDITS.log`, because the launch script fixes `$GOV_INDEP_RUNS_DIR/indep/`. \"For Gov OS also its\n    six retrieval globs\" is the six globs applied to every repository, as I9 says.\n  - **S10's \"six counts\"** are one field per item; items 1 and 2 print a state word, item 5 two numbers. \"Cited lines\n    changed\" is `gov.retrieval.measure`'s `unresolved` (a block not found once at the audit commit).\n  - **S10 and S8's \"runs at once after the miss\"** is the wrapper's second `maintain` in the same cycle.\n  - **S11's \"within the gate's wait\"** is `--gate-cmd` on both `standing run` and `run`.\n  - **F2's `measure --kept` on a standing run:** a name with a `STANDING.jsonl` record or a week folder prints `USED`,\n    exit 3, nothing written.\n\n- **Gaps (a KPI that cannot be met inside `allowed_paths` as filed):**\n  - **G1 (S9 against S5, S8 and W2-172's unedited cases).** Moving the state to `<runs>/indep/memaudit/<key>/` breaks\n    W2-172's s1, s2-s4, s6, s8 and s9 cases and the f1-f4 cases. They read it through `self.mem` and `self.audits_log` in\n    `tests/acceptance/W2-172/w2_172_world.py` (lines 281-282) and `w2_172_git.py` (lines 43-44). Neither helper is in\n    `allowed_paths`, and S8 requires `test_w2_172_s5_due.py` unchanged. The fix keeps every W2-172 test file unchanged:\n    add the two helpers to `allowed_paths` for the test designer, about four lines (the key, `mem`, `audits_log`), with a\n    `Rewrite-Reason` naming DEC-1179 (5). That is a path case the CTO routes under DEC-1156 (7).\n  - **G2 (S10 (6)'s hand-off).** The tool writes the request (I10). Staging it into a writer's wall needs a `reanchor`\n    input in `governance/project/indep-walls/kinds.yaml` and the matching staging in\n    `governance/project/orchestration/tools/indep_launch.py`, which are walls and control paths (an ACT). Until then the\n    owner's operator hands it over in the Monday slot, as the ticket's last paragraph says.\n\n- **The CTO's routings at claim (DEC-1156 (7), DEC-1157 (12); listed for the owner's reading):** G1: `tests/acceptance/W2-172/w2_172_world.py` and `w2_172_git.py` are added to `allowed_paths` for the test designer (about four lines: the key, `mem`, `audits_log`; `Rewrite-Reason: DEC-1179 (5)`); every W2-172 test file stays unchanged. G2: until an ACT adds a `reanchor` input to the walls (`kinds.yaml`, `indep_launch.py`), the owner's operator carries `REANCHOR-<week>.json` to the walled writer in the Monday slot (DEC-1179 (6), DEC-1178 (1)). U1: a Wave 0 verdict set's own run's `misses.jsonl` and `miss-classes.json` do not spend it (the package's \u00a75.3: W2-187 S1 accepts a used Wave 0 verdict set). U2: `maintain` item (6) leaves standing sets out; their stale questions drop by count (S6). G6 (a same-head refresh of a stale-layout store) is the engineer's to show in evidence.\n\n**Amended 2026-11-14 (the CTO within purpose, DEC-1157 (12); the owner's N2 (b), DEC-1180 (1)):** S10 (6) and I10 item 6 also list a heading-cited source whose section text (from its heading line to the next heading of the same or a higher level, or the end of the file) differs between the source's own commit and the head is listed too, though its heading is still found, matching W2-61h S4's list. The lead brings this in at its next merge of `w2/integrate`; the test designer's S10 cases take it with `Rewrite-Reason: DEC-1180 (1)`.\n\n**Path case 2026-11-14 by the CTO (DEC-1156 (7); listed for the owner's reading): W2-187-P1 (a).** Two more W2-171 acceptance files pin the 85 % bar (`test_w2_171_cli_layout_ledger.py:120-121`, `test_w2_171_s5_misses_f2.py:82`; `docs/probes/DAEO-0cd2/PACKAGE-W2-187-P1.md`). Both are added to `allowed_paths` for the independent test designer (bar values only, `Rewrite-Reason: DEC-1179 (2)`), and F5's \"W2-171's S5 case passes unchanged\" now reads \"with only its bar value revised\", as it already did for W2-170. The behaviour guarded is unchanged; a narrow check covers it.\n\n**Amended 2026-11-14 by the CTO within the owner's DEC-1182 (2) (listed for the owner's reading): S12 and F7, the weekly secret scan and push.** EXAMIN gets one full gitleaks scan a week, before its weekly push, in this weekly cycle: audit and measure, then the scan, then the push only on a clean scan; never a scan at a close or a refresh (EXAMIN's `secrets.yaml` holds `scan: off`). I11 gains: the wrapper, after its last audit step, reads the repository's push declaration (I11 names the key; absent means no push), runs `gitleaks detect` over the repository once, and pushes only on its exit 0; A9's ACT.md step 6 states that order. The running lead was not told (no mechanism): its next round takes S12 and F7 with the path case W2-187-P1 (a).\n\n**Interface for S12 and F7, 2026-11-14 by the CTO at the lead's package W2-187-S12 (DEC-1052, DEC-1157 (3); `docs/probes/DAEO-0cd2/PACKAGE-W2-187-S12.md` on `w2/W2-187`, items 1-6 as recommended; listed for the owner's reading). I13, the weekly scan and push:**\n- **The declaration (I11's key):** the cron line's environment, `GOV_MEMAUDIT_PUSH=\"<remote> <branch>\"`, written by the repository's owner in ACT.md step 6's line. Absent or empty means no push. No new file in the repository; Gov OS declares nothing (DEC-1182 (1)).\n- **The code:** `python3 -m gov.memaudit push --sets-root R [--repo D] [--gitleaks EXE]` in `src/gov/memaudit/push.py`; `say` stays the only printer, and this module's scan call is the only gitleaks call (F7). The wrapper calls it as its last step.\n- **The scan:** `gitleaks detect --source <repo> --no-banner --redact --report-format json --report-path <a 0600 temporary file outside the repository>`; the tool counts the report's entries, then deletes the report. Exit 0 is clean; exit 1 with entries is `findings <k>`; any other exit, a timeout (`GOV_MEMAUDIT_SCAN_TIMEOUT_S`, default 600) or no binary is `scan failed <reason word>`. The binary: `--gitleaks`, else `$GOV_MEMAUDIT_GITLEAKS`, else `gitleaks` on PATH.\n- **The output (counts and reason words only):** one stdout line: `PUSH none: no declaration` (exit 0); `PUSH pushed <remote> <branch> <12 hex>` (exit 0); `PUSH blocked: findings <k>` (exit 1); `PUSH blocked: scan failed <word>` (exit 1); `PUSH failed: git push exit <c>` (exit 2; git's own output kept in a 0600 file in the key folder, never printed). The same line is the last line of the cycle's latest `DIGEST.txt` in the key folder, and one more `cron.log` line with the six keys unchanged and the step named `push`.\n- **Where it runs:** only in the wrapper's weekly cycle, after the audit steps that ran, and only when a standing or fresh step started that cycle; never in `maintain`, at a refresh or at a close. A cycle where nothing was due runs neither the scan nor the push.\n- **A9's ACT.md step 6** adds: \"The cycle runs the audit and measure, then one gitleaks scan, then `git push` only on a clean scan; declare the push with `GOV_MEMAUDIT_PUSH=\"<remote> <branch>\"` on this line; leave it out for no push.\"\n- S12 and F7 stay in W2-187 (no split: a new ticket needs the owner's P1, DEC-974).\n\n**I13 amended 2026-11-14 18:37 by the CTO, at the lead's reading (DEC-1157 (3); listed for the owner's reading).** The literal I13 cannot hold with W2-172 S9's unchanged cases (exactly one cron.log line and nothing else written on today's path; the wrapper exits with run's code). So: (1) `push` writes its own cron.log line (the six keys, step `push`) and its DIGEST line only when a push is declared, that is, when the scan or push started; (2) a no-declaration `push` prints `PUSH none: no declaration`, exits 0 and writes nothing, and that line reaches the wrapper's own stdout so the cron's output names the skip (S12 \"skips both steps, named\"); (3) the wrapper calls `push` after any started audit step, today's path included; (4) the wrapper's exit stays the last audit step's. W2-172's files are unchanged; W2-187's two no-declaration cases are revised by its test designer to match.\n",
  "authority": [
    {
      "id": "DEC-1182",
      "sha256": "87df9dfa3621ef948a58832e0740866208a60b3d5730cd13dba71568bd288c14",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "87df9dfa3621ef948a58832e0740866208a60b3d5730cd13dba71568bd288c14",
      "reason": "declared in sources",
      "tokens": 6726
    },
    {
      "id": "DEC-1179",
      "sha256": "d86bc27f560c2e8f7214bdf6d276afc4672611a6e6b048c8b43489b4bc3dc130",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "d86bc27f560c2e8f7214bdf6d276afc4672611a6e6b048c8b43489b4bc3dc130",
      "reason": "declared in sources",
      "tokens": 1335
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
      "sha256": "fdca12fad82da62fba5e4bf85f2f7fea8748a4d79996b6bf0cf3d17c8183d0ae",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "fdca12fad82da62fba5e4bf85f2f7fea8748a4d79996b6bf0cf3d17c8183d0ae",
      "reason": "declared in sources",
      "tokens": 914
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
      "sha256": "a6b92dce76c7a7e1f6287df3f07a565621cb2f25014f8b47e8eb989d5995ed87",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "a6b92dce76c7a7e1f6287df3f07a565621cb2f25014f8b47e8eb989d5995ed87",
      "reason": "declared in sources",
      "tokens": 8965
    },
    {
      "id": "DAEO-k1e2",
      "sha256": "7c6af00f3a949a364d7c7877262d979f4d08a7fbe95102879f6e70c3713ecfbc",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "7c6af00f3a949a364d7c7877262d979f4d08a7fbe95102879f6e70c3713ecfbc",
      "reason": "declared in sources",
      "tokens": 8185
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
      "sha256": "2af623a6d9e0ee85d0a8d33d02e43ac3cdf55ed13e4836dd9f1076941ad71773",
      "authority": "task",
      "lifecycle": "in_progress",
      "constraint": "2af623a6d9e0ee85d0a8d33d02e43ac3cdf55ed13e4836dd9f1076941ad71773",
      "reason": "declared in sources",
      "tokens": 13607
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
      "id": "DEC-1182",
      "sha256": "87df9dfa3621ef948a58832e0740866208a60b3d5730cd13dba71568bd288c14",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "87df9dfa3621ef948a58832e0740866208a60b3d5730cd13dba71568bd288c14",
      "reason": "declared in sources",
      "tokens": 6726
    },
    {
      "id": "DEC-1179",
      "sha256": "d86bc27f560c2e8f7214bdf6d276afc4672611a6e6b048c8b43489b4bc3dc130",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "d86bc27f560c2e8f7214bdf6d276afc4672611a6e6b048c8b43489b4bc3dc130",
      "reason": "declared in sources",
      "tokens": 1335
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
      "sha256": "fdca12fad82da62fba5e4bf85f2f7fea8748a4d79996b6bf0cf3d17c8183d0ae",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "fdca12fad82da62fba5e4bf85f2f7fea8748a4d79996b6bf0cf3d17c8183d0ae",
      "reason": "declared in sources",
      "tokens": 914
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
      "sha256": "a6b92dce76c7a7e1f6287df3f07a565621cb2f25014f8b47e8eb989d5995ed87",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "a6b92dce76c7a7e1f6287df3f07a565621cb2f25014f8b47e8eb989d5995ed87",
      "reason": "declared in sources",
      "tokens": 8965
    },
    {
      "id": "DAEO-k1e2",
      "sha256": "7c6af00f3a949a364d7c7877262d979f4d08a7fbe95102879f6e70c3713ecfbc",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "7c6af00f3a949a364d7c7877262d979f4d08a7fbe95102879f6e70c3713ecfbc",
      "reason": "declared in sources",
      "tokens": 8185
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
      "sha256": "2af623a6d9e0ee85d0a8d33d02e43ac3cdf55ed13e4836dd9f1076941ad71773",
      "authority": "task",
      "lifecycle": "in_progress",
      "constraint": "2af623a6d9e0ee85d0a8d33d02e43ac3cdf55ed13e4836dd9f1076941ad71773",
      "reason": "declared in sources",
      "tokens": 13607
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
      "id": "DAEO-h2k3",
      "path": ".tickets/DAEO-h2k3.md",
      "text": "independent check of the revision (DEC-1154); then the owner's operator's walled re-run, expecting 7 passed with h03\non the list. The hidden half is never read by any launched session; its cases are proven on planted sets roots only.\n\n**N2 (b), 2026-11-14 (the owner, DEC-1180 (1)):** the changed-lines list also holds a heading-cited source whose section text (from its heading line to the next heading of the same or a higher level, or the end of the file) differs between the source's own commit and the head is listed too, though its heading is still found; an entry is listed once even when two of its alternatives changed (row N1, fixed in the same flow, DEC-1180 (4)). One more test revision by an independent test designer (`w2_61h_support.py`, the README, the case files only where needed; `Rewrite-Reason: DEC-1180 (1)`), proved on planted data, then a narrow independent check (`docs/probes/DAEO-h2k3/PR-DAEO-h2k3-n2.md`). W2-61h closes on this revision and the owner's operator's walled re-run. (The merge queue closed it at c1cb5285c with the F3 land; it stays open for this, status in_progress.)\n\n",
      "tokens": 278
    },
    {
      "id": "DEC-1180",
      "path": "docs/DECISION_REGISTER.md",
      "text": "### DEC-1180 \u2014 The afternoon of 2026-11-14: N2 (b), changed heading-cited sections listed for the walled writer; q02's fix by a one-question fix flow, run today (W2-94 reopened); the EXAMIN CTO starts tonight after the re-pin and the operator's setup; no deferral\n- **Status:** ACCEPTED (owner, 2026-11-14 ~13:35 to ~13:50, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-11-14)`; (4) standing) \u00b7 **Under:** DEC-1178, DEC-1179, DEC-974, DEC-1156 (8), DEC-1157\n- **Decision:**\n  - (1) **N2 (b) (W2-61h's F3 revision, the owner's reading of \"lines changed\"):** W2-61h's check also lists a heading-cited source whose section text changed since the source's own commit, even when its heading is still found at HEAD, by question id and entry number only. W2-61h gets one test revision (its designer's support file and README) and a narrow independent check; W2-187's S10 item (6) and its Interface I10 item 6 take the same rule (the CTO within purpose, DEC-1157 (12)). W2-61h closes on that revision plus the owner's operator's walled re-run.\n",
      "tokens": 283
    },
    {
      "id": "4fcadaf3f8da46268265fc58",
      "path": "docs/probes/DAEO-h2k3/PR-DAEO-h2k3-f3.md",
      "text": "task: DAEO-h2k3, the narrow independent check of the S4/F3 revision (DEC-1178 (1), DEC-1154)\nstatus: done, judgement pass\nwork_completed: probed head `dda647a49` (confirmed with `rev-parse`) against DEC-1178 (1), the ticket's S4 and F3 lines and its \"Reopened 2026-11-14\" paragraph; ran the visible side; planted a throwaway hidden sets root and ran the hidden S4 case against it\nfiles_changed: none (`git status --porcelain` is empty; throwaway files only under `$TMPDIR/probe`)\nevidence: commands and counts are in the record below\ntests: visible folder 22 passed, 7 skipped, 9 deselected; the hidden S4 case on planted roots in four variants; the hidden-module skip checks\ndiscoveries: N1 to N3, all rows\nrisks: none blocking\nlessons: none\nproposed_decisions: none\nunresolved: N2 is the owner's reading if they want heading-cited sections on the list\nrecommended_next_action: the owner's operator's walled re-run (expected 7 passed, with h03 on the list)\n\n---\n\nreviewer_session: 4312c571-0b45-4a28-a4f6-8bad354a8f06 (read from the sandbox's task path)\n\n**What I probed and found sound**\n",
      "tokens": 273
    },
    {
      "id": "70b6669acfd83d5ab086c3c4",
      "path": "docs/probes/DAEO-h2k3/PR-DAEO-h2k3-f3.md",
      "text": "# Narrow check of W2-61h's S4/F3 revision (DEC-1178 (1))\n\nThe lead's triage: N1, N2 and N3 are rows (none is in scope with ordinary work yes and fails open or loses work); no\nround. N1 (an entry listed twice when two alternatives both changed) and N3 (no planted anchor-miss red for q21-q24)\nare rows for the next test-design pass on this set; N2 (a heading-cited section rewritten under a heading still found\nis not listed) is the owner's reading of \"lines changed\", named in the lead's return.\n\nThe reviewer's return, word for word:\n\n**Sandbox check (Step 0):** (a) passed: writing `/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-h2k3` was refused (`OSError: Read-only file system`), so no file was created. (b) passed: `git hash-object -w --stdin` exited 0 (object `1ae28402a`) and `git update-index --refresh` exited 0. **`ps` check:** no ollama or llama-server process is running.\n\ntask: DAEO-h2k3, the narrow independent check of the S4/F3 revision (DEC-1178 (1), DEC-1154)\nstatus: done, judgement pass\n",
      "tokens": 253
    },
    {
      "id": "740f7c64cfe8935fbf07fad8",
      "path": "docs/probes/DAEO-h2k3/PR-DAEO-h2k3-f3.md",
      "text": "  Consequence: other (the repeat is cosmetic; the list still holds file names and entry numbers only and nothing fails).\n  Reversed by: a reading that the list is per alternative rather than per entry.\n\n- **N2 (scope: in): a rewritten heading-cited section is not listed.** A source cited by heading, whose heading is still found at HEAD but whose section text changed, is not put on the list. DEC-1178 (1) says \"a block whose lines changed is listed\". The designer narrowed the list to what the measure would count as not found, and documented this in the README's \"changed rule\" row.\n  Ordinary work: yes, because cited sections are edited in ordinary work.\n  Consequence: other (the maintenance list can miss a rewritten section; the S4 check neither fails open nor loses work, and the operator's cross-check judges whether the section still answers).\n  Reversed by: the owner reading \"lines changed\" as \"what the measure cannot re-anchor\".\n\n",
      "tokens": 237
    },
    {
      "id": "ef6f9c353cbc2b0936e2bc76",
      "path": "docs/probes/DAEO-h2k3/PR-DAEO-h2k3-n2.md",
      "text": "---\ntype: probe\ntask: DAEO-h2k3\nkind: \"narrow independent check (DEC-1154) of the N2 (b) and N1 test revision under DEC-1180 (1), (4): a heading-cited section rewritten under a heading still found is listed; a section moved unchanged is not; an entry is listed once; not a round, DEC-1010\"\nreviewer_session: \"0791247d-c8a3-4af8-b9cc-c2befd0648a1 (nc-3, independent-auditor, claude-opus-5-5, high, C2; read from the launch log)\"\nimplementer_session: \"e4e7eb41-d905-414a-9b4d-90e1b1fdc91d (td-5, independent-test-designer, claude-sonnet-5-5, high, C2; commit 70aa3a6b7ba3e8c348e2b6a8f502873013f84ab8)\"\nreviewer_wrote_nothing: true\ncommissioned_by: orchestrator\njudged_by: orchestrator\njudgement: pass\nprobed_commit: dbe1236733f9d63ccccf8fc5435fbdba41617603\ndate: 2026-11-14\ndecisions_applied: [DEC-1180, DEC-1178, DEC-1154, DEC-1084, DEC-828]\n---\n\n",
      "tokens": 212
    },
    {
      "id": "c6f2a2d177cb489bbfd84da0",
      "path": "tests/acceptance/W2-134/README.md",
      "text": "## Not covered by a test\n\n- **A block found more than once at the measured root.** S1 says the block is \"found once\", and `repin_gold.py`\n  treats more than one place as unresolved. The CTO later settled this as unresolved; no case was added for it.\n- **The floor's exact edge (S5).** The cases keep a margin and do not judge a gold of exactly 24 characters or one\n  just under the floor.\n- **The families line under `--json` (S6),** and whether `<n>` counts globs or matched files.\n- **A heading-cited source.** A heading found at the root governs, as today, and S4's q02 checks that this is\n  unchanged. A heading not found that falls back to its lines is not re-anchored by any case.\n- **An alternative's entry number (`k.j`)** in the naming.\n",
      "tokens": 187
    },
    {
      "id": "041a52e7f221d0a7980a8154",
      "path": "tests/acceptance/W2-61h/README.md",
      "text": "| F1 | H `test_s5_f1_...`; H `test_s6_...`; the measured-role skip | As S5 and S6: no route by a tree, a commit, a run clone or the measure; a measured session's own run of these tests reads nothing hidden |\n| F2 | V `test_f2_no_new_visible_question_repeats_lens_b_s_twenty_or_another_new_one`; H `test_f2_no_hidden_question_repeats_a_visible_one` | No new question equals, case, spacing and punctuation aside, one of lens B's 20 or another of the set. A **paraphrase** is not judged by a test: it rests on the writer's independence (S2's record) and the brief it wrote to |\n| F3 (re-worded, DEC-1178 (1)) | as S4 | A gold source that does not hold its answer at its own commit (path not a file there; heading or lines no span there; for q21-q24 the anchor missing from the span there) is red. A block or section that moved or changed at HEAD is **no failure**: a moved one is not listed, a changed one (lines, or a heading-cited section's text) is listed once per entry by file name and entry number only |\n\n**Not covered by a test, named:** S3's \"at least 2 whose naive answer is superseded\" (a fact of the hidden text\n",
      "tokens": 281
    },
    {
      "id": "0c7b3ec117b38d984e610bbb",
      "path": "tests/acceptance/W2-61h/README.md",
      "text": "# the owner's operator's walled run (DEC-1178 (1)): the hidden form alone, unmeasured, with the list shown\nenv -u GOV_ROLE -u GOV_TICKET GOV_EVAL_SETS_ROOT=$HOME/gov-os-eval PYTHONPATH=<tree>/src \\\n  python3 -m pytest tests/acceptance/W2-61h/test_w2_61h_hidden_form.py -p no:cacheprovider -rA\n```\n\n**The changed-lines list (DEC-1178 (1), DEC-1180 (1)).** S4's hidden and visible cases never fail for a cited block\nwhose lines changed at HEAD, or a heading-cited section whose text changed; they list it, once per entry. The list is a `GoldBlockChanged` warning, one per case: pytest's default summary prints\nit for a passing and a failing run alike, under \"warnings summary\", in the form `W2-61h S4 maintenance list (DEC-1178\n(1), DEC-1180 (1)): N cited block(s) or section(s) changed at HEAD, for the walled writer: h03.yaml entry 2; ...` (file name and entry number\nonly; no flag is needed, and `-rA` is the walled command's flag for the pass or fail line per case). Nothing is\nwritten to a file. Under `-W error` the same line is printed to standard output instead, so the list never fails a\ncase. The operator's record quotes the warning's line; no line means no changed block.\n\n",
      "tokens": 296
    },
    {
      "id": "1e8647524a58650309e08c7b",
      "path": "tests/acceptance/W2-61h/README.md",
      "text": "| S4 (re-worded, DEC-1178 (1)) | V `test_s4_f3_every_new_visible_gold_source_resolves_at_head`; V `test_f3_each_new_visible_gold_source_holds_its_answer`; V `test_s4_f3_judges_each_source_at_its_own_commit_on_planted_data`; V `test_s4_no_new_visible_source_names_the_set_s_own_files`; H `test_s4_f3_every_hidden_gold_source_resolves_at_head` | **Each gold source is judged at its own commit** (the alternative's `commit`, else the question's): the path is a file there and its heading or lines are a span there by the measure's rule (`span_of`, the designer's copy of `_span`); else it is **red**, named by file name and entry number only. A source that names no commit at all is judged at HEAD. **At HEAD, a block that moved unchanged is no fault** (the same lines, or exactly one other place: W2-134's re-anchor and `repin_gold.py`'s). **A block whose lines changed, or a heading-cited section whose text changed, is listed once per entry, never failed** (see the rule below) as a `GoldBlockChanged` warning in the default summary. For q21-q24 the designer also checks that the span at the source's own commit holds a string from its answer (`ANCHORS`); that a hidden source holds its answer is the operator's cross-check, not a test |\n",
      "tokens": 310
    },
    {
      "id": "21978452c683cd6a91ab4f8c",
      "path": "tests/acceptance/W2-61h/README.md",
      "text": "**Planted proofs, by outcome only.**\n\n- *Visible module, always run* (the planted two-commit repository, ten questions, the same `judge_all` the real cases\n  use): (a) p01 moved unchanged: passes, not listed. (b) p02 lines changed (also p06 and p07 as before): passes,\n  listed. (c) p03 and p05, never held at their own commit: red, `p03.yaml source entry 1` and `p05.yaml source entry 1`\n  only, no planted text, path or span in any message. (d) p04 the control: passes, not listed. (e) p08, a\n  heading-cited section rewritten under its unchanged heading: passes, **listed**. (f) p09, a heading-cited section that\n  moved unchanged (four lines inserted above, trailing whitespace put on one of its lines): passes, **not listed**.\n  (g) p10, one entry of three changed alternatives (lines rewritten, lines found twice away, the section rewritten)\n  then a control entry: **listed once**, `p10.yaml entry 1`. The list is `p02, p06, p07, p08, p10`, each entry 1. Run\n  against the previous revision's `judge_sources` the same case is red twice over: p08 is missing and p10 appears twice.\n",
      "tokens": 272
    },
    {
      "id": "4889c31e4d462ecca60de49a",
      "path": "tests/acceptance/W2-61h/README.md",
      "text": "## DEC-1180 (1), (4): N2 (b) and N1 (2026-11-14; `Rewrite-Reason: DEC-1180 (1)`)\n\nThe owner read \"lines changed\" as (b): a heading-cited source whose section text changed since the source's own commit\nis listed too, though its heading is still found at HEAD (the earlier revision returned early on a heading found). A\nnarrow check also found row N1: two changed alternatives of one entry listed the entry twice. Revised by an\nindependent test designer in `w2_61h_support.py`'s `judge_sources` (the hidden and the visible S4 cases both use it);\nno hidden file was read, every proof below is on planted data:\n\n1. **The section rule.** A heading found at HEAD no longer ends the judgement: the section `span_of` resolves at the\n   source's own commit and at HEAD (heading line to the line before the next heading of the same or a higher level,\n   or the end of the file) are compared, and a difference lists the entry. A section that moved unchanged is not\n   listed. A heading that is not a `#` heading spans the width its `lines` state, and that span is compared.\n2. **\"Text differs\"** is line-by-line equality with each line's trailing whitespace stripped and the section's\n",
      "tokens": 294
    },
    {
      "id": "246d11f318a5fc0a8094c9ad",
      "path": "tests/acceptance/W2-61h/test_w2_61h_visible_new.py",
      "text": "def _plant_two_commits(tmp_path):\n    \"\"\"A planted repository with two commits and a planted sets root (a folder of question YAMLs, in no work tree).\n    Every planted word carries ``zqxw`` so a leak into any output is found. Commit 1 holds each cited block; commit 2\n    is the HEAD the check reads. Questions (file: what happened to its block between the two commits):\n    p01 moved unchanged (6 lines inserted above); p02 changed (its lines rewritten); p03 never held its answer at its\n    own commit (the heading it cites exists only from commit 2 on); p04 the control (lines appended below, the block\n    steady); p05 never held it either (its path is a file only from commit 2 on); p06 changed (the block gone from\n    its lines, found twice elsewhere); p07 changed (its file deleted). DEC-1180 (1) adds p08 (a heading-cited section\n    rewritten under its unchanged heading: changed), p09 (a heading-cited section moved unchanged, 4 lines inserted\n    above it and trailing blanks put on one of its lines: not changed) and p10 (one entry of three alternatives, all\n    changed, then an unchanged control entry).\"\"\"\n    repo = tmp_path / \"repo\"\n    docs = repo / \"docs\"\n",
      "tokens": 294
    },
    {
      "id": "aaff117542049a71f170ff86",
      "path": "tests/acceptance/W2-61h/test_w2_61h_visible_new.py",
      "text": "def test_s4_f3_every_new_visible_gold_source_resolves_at_head():\n    \"\"\"DEC-1178 (1): each gold source of q21-q24 is judged at its own commit (its ``commit``, else the question's):\n    the path is a file there and its heading or lines are a span there, else it is red. At HEAD a cited block that\n    moved unchanged is no fault; one whose lines changed, or a heading-cited section whose text changed under a heading\n    still found (DEC-1180 (1)), is not failed, it is listed once by question file and entry number\n    (a ``GoldBlockChanged`` warning in the default summary, for the walled writer).\"\"\"\n    faults, changed = s.judge_all(_new())\n    s.notify_changed(changed)\n    assert not faults, \"\\n\".join(faults)\n",
      "tokens": 179
    },
    {
      "id": "cf93cc6385aaca25154282fc",
      "path": "tests/acceptance/W2-61h/test_w2_61h_visible_new.py",
      "text": "def test_s4_f3_judges_each_source_at_its_own_commit_on_planted_data(tmp_path):\n    \"\"\"DEC-1178 (1) and DEC-1180 (1), (4) on planted data, with the support function the real hidden and visible\n    cases use: a block that moved unchanged at HEAD (p01) passes and is not listed; a block whose lines changed (p02;\n    also p06, found twice away from its lines, and p07, its file gone) passes and is listed by file and entry number\n    only; a source that never held its answer at its own commit (p03's heading, p05's path: both exist only at HEAD)\n    is red, named by file and entry number only; the control (p04) passes and is not listed. N2 (b): a heading-cited\n    section rewritten under its unchanged heading (p08) passes and is listed; one that moved unchanged (p09, lines\n    inserted above, trailing whitespace on a line) passes and is not listed. N1: an entry whose three alternatives all\n    changed (p10) is listed once. No planted question, answer, category, path, heading or span text is in any\n    message. The list shows as a warning in the default summary; an empty list shows nothing.\"\"\"\n    repo, sets = _plant_two_commits(tmp_path)\n",
      "tokens": 287
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
    },
    {
      "id": "0919240bd7a82e196c6603c9",
      "path": "tests/acceptance/W2-110/README.md",
      "text": "| `test_an_orchestrator_whose_ticket_is_what_the_key_holds_is_refused` \u00d7 9 | `GOV_TICKET` holds the key's words exactly: `DAEO-gone`, `P-99`, `\"\"`, `\"   \"` and `\"7\"`, or is unset while the key is null, missing, or in a roster that is not there (`no-roster`, `as-generated`) | R1 |\n| `test_every_session_s_install_is_refused_and_told_how_to_set_the_key` \u00d7 12 sessions \u00d7 2 (`no-roster`, `unparsable`) | the CTO by WBS id; its orchestrator subagent; a lead; an orchestrator with no ticket; the six other roles on their own tickets; no role; an orchestrator subagent in an engineer's session | R1 for the 5 orchestrator sessions, R3 for the 7 others, in each of the 2 configurations |\n| `test_without_a_roster_every_install_of_the_cto_is_refused` \u00d7 5 | each install | R1 |\n| `test_without_a_roster_the_cto_is_refused_in_every_permission_mode` \u00d7 6 | never an `ask`, in any mode | R1 |\n| `test_the_product_as_generated_names_no_coordination_ticket` | the generated product's roster, if the template ships one, sets no ticket: the key is the project's, set at adoption (an empty key is allowed) | **green**: the template ships no roster |\n\n",
      "tokens": 284
    },
    {
      "id": "4cd6233c6dbff2b58764ded3",
      "path": "tests/acceptance/W2-110/README.md",
      "text": "| `test_sudo_is_refused_to_every_other_session` \u00d7 7 | `sudo pip install requests`: the lead, the engineer, research in its folder, no role, the CTO's orchestrator subagent, and the would-be CTO in `no-roster` and `unparsable` |\n| `test_the_research_exception_holds_with_or_without_the_key` \u00d7 4 configurations \u00d7 2 forms | research on `DAEO-rsc1`, with `cwd` in `experiments/exp-1` or as `cd experiments/exp-1 && pip3 install requests` from the root, gets no decision (let through, DEC-163) in `key-by-id`, `no-roster`, `no-key` and `unparsable` |\n| `test_a_frozen_product_refuses_every_install_the_cto_s_included` \u00d7 6 | `key-by-id-frozen`: the CTO (by id and by WBS id), its orchestrator subagent, the lead, the engineer and research in its folder are all refused |\n| `test_a_bash_call_that_installs_nothing_is_decided_as_before` \u00d7 4 sessions \u00d7 3 commands | no decision for the CTO and the lead in `key-by-id`, the CTO in `no-roster` and the engineer in `unparsable`: a broken key changes installs only |\n| `test_the_cto_s_install_that_writes_where_the_guard_refuses_stays_refused` | `pip3 install requests > .gov-runtime/records.jsonl` by the CTO is refused, not asked: the rule only escalates |\n\n",
      "tokens": 300
    },
    {
      "id": "43f46818b689a10d7318f6cb",
      "path": "tests/acceptance/W2-113/README.md",
      "text": "| `names-by-wbs` | `coordination_ticket: P-01` | none | I2 (i) |\n| `other-content` | comments, a `roles:` block, `budget_per_ticket: 12`; no key | none | I2 (ii) |\n| `no-tk` | none | `governance/kernel/bin/tk` removed (committed) | I2 (iii): A0 completes, creates no ticket and no key, says so in its record; the guard stays closed (run 3: was \"A0 refuses\") |\n\nSuccess 2 uses W2-110's configurations of the same generator (`no-key`, `no-roster`, `as-generated`,\n`names-no-ticket-by-id`, `names-no-ticket-by-wbs`), each with the sessions \"the orchestrator on `DAEO-c0rd`\" and \"an\nengineer on `DAEO-eng1`\". Adoption is not needed there.\n\nInstalls: `pip3 install requests` and `npm i left-pad` (one per class of the install rule; W2-110 covers the rest).\n\n",
      "tokens": 189
    },
    {
      "id": "1168ef12eb7219ee8157cbce",
      "path": "tests/acceptance/W2-59/README.md",
      "text": "  temporary folder. Nothing depends on a pin's versioned path.\n- **The project under check**: a temporary git repository built from scratch with `git init`; its files are\n  written by the case or are single named files of this worktree (check declarations, hook programs, the template\n  path map, the gitleaks configurations). No folder of the repository is copied.\n- **`gov --version` from this worktree's code** (KPI 5): `python3 -m gov.cli.main --version` with\n  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-59/src` set in that one subprocess.\n- Every other subprocess runs with `PYTHONPATH` removed, `HOME` temporary and a `PATH` the case writes. Run 2's\n  cases then add, on purpose, a worker's `PYTHONPATH` naming a decoy folder of the case (never this worktree's\n  `src`): the session's inherited variable under test.\n\nThe `gov.__file__` line, as run for this suite:\n\n    $ PYTHONPATH=/home/usain/gov-os-worktrees/W2-59/src python3 -c \"import gov; print(gov.__file__)\"\n    /home/usain/gov-os-worktrees/W2-59/src/gov/__init__.py\n\n**Instrumentation and decoys.** Only the stand-in is instrumented, after its install, never the wheel: a `.pth` file\n",
      "tokens": 288
    },
    {
      "id": "a8302497d7c2c35e9ad4a9b1",
      "path": "tests/acceptance/W2-59/README.md",
      "text": "    /home/usain/gov-os-worktrees/W2-59/src/gov/__init__.py\n\n**Instrumentation and decoys.** Only the stand-in is instrumented, after its install, never the wheel: a `.pth` file\nin its site folder leaves `pin-python-<pid>` when its interpreter starts; its installed `gov/__init__.py` leaves\n`pin-gov-<pid>` when its package is imported. Decoys leave markers of their own: a `python3` (which goes on to the\nreal interpreter) and a `gov` first on `PATH`, a `gov` package under the project's `src/` (its schema check edited to\nreport `W259_TREE_EDIT` and exit 1), a `gov` package at the project's root. Every marker folder's absolute path is\nwritten into the decoy itself, so no marker depends on an environment variable reaching the process (W2-05's\nunmerged `git_env(root)` may change the checks' environment). At the place a lookup from the installed package's\nlocation leads to (three folders above the installed `gov/retrieval/` module: the repository root for a source\ncheckout, `<venv>/lib/python3.X` for the install), decoys are planted: canary declarations with a query of their\nown in both kernel layouts, and a path map and gitleaks configurations that cannot be read.\n\n",
      "tokens": 295
    },
    {
      "id": "ee5caf56e3b60ba24a7c49b0",
      "path": "tests/acceptance/W2-66/test_w2_66_live_test_map.py",
      "text": "def test_a_fixture_input_change_does_not_reach_the_real_model_suites(test_map, path):\n    \"\"\"T-6 (DEC-1061 item 9): the path map's and the gitleaks configurations' coupling leaves out W1-19 and W1-21.\"\"\"\n    reached = [t for entry in _couplings(test_map) if _placed(entry[\"paths\"], path) for t in entry[\"suites\"]]\n    wrong = [t for t in reached for suite in FIXTURE_INPUTS_NOT_REACHING[1]\n             if t.rstrip(\"/\") == suite or t.startswith(suite + \"/\")]\n    assert not wrong, f\"a change of {path} still reaches the real-model suites through a coupling: {wrong}\"\n",
      "tokens": 142
    },
    {
      "id": "93e0ef990b2e8661cb2c1dc1",
      "path": "governance/project/orchestration/packages/LIFT-1/FRESH-80-RESULT.md",
      "text": "## What follows (DEC-1097)\n- K9's memory line (its home under W2-32 S9) is met; K9's other lines stand (D9-FATES \u00a73).\n- After the 80: W2-139 and W2-140 (held until now); Q07 and Q14 re-worded before any re-measure of the 138; the\n  rubric's version 3; the glossary's redesign, declared, then retested on the 138; the P2 items (ADR-0002, P-SELECT-GRAPH,\n  the 150-id sitting).\n- A product row: the product does not read the nonexistent-id form as an id, so DEC-1071 (5)'s stop cannot fire for\n  it (lexical `ids_in`); found at the pre-flight.\n\n**Basis:** question 1 (memory judged by what agents answer, on a set used once, the configuration chosen beforehand).\n",
      "tokens": 166
    },
    {
      "id": "249b917ed5a7dc6cead63101",
      "path": "governance/project/orchestration/packages/W2-88-STANDARD-1.md",
      "text": "  - 'S13 The fresh verdict set, used once: 80 questions, written by the same independent writer and checker under the same rubric, blind, before the first measure of the tuning set. None of its gold sources is a gold source of the tuning set. It is held outside every worktree in a folder of mode 700, declared in the path map''s evaluation_sets with every role but the orchestrator refused, and the guard refuses the measured roles a read of the set and of its run folder (as ACT-GUARD-SETS-1). It is used once, as FRESH-80-1 did. First a counts-only pre-flight: the set''s digest, how its anchors resolve at the measured commit, and whether each nonexistent id still exists nowhere. Then the checker''s staleness pass at that commit. Then a declaration, committed before any search, naming the configuration (S10), the commit, the denominator with nonexistent-id questions apart, the bar and how it rounds (S14), any data conditions as data only, and the fault rule (FRESH-80-1 \u00a73.5). Then a control on the tuning set. A USED marker is written before the first search, and the runner refuses to start once it exists. The result record gives counts only. Verify: the declaration''s commit is earlier than the USED marker; a planted USED makes the runner refuse; a planted read of the set by a measured role is refused by the guard [DEC-1098 (1), DEC-1097 (1)(b), (1)(g), DEC-1097 (2), DEC-1092 (4), DEC-1078 (3), DEC-1074 (1)] [added, DEC-1098 (1)]'\n",
      "tokens": 363
    },
    {
      "id": "DAEO-f6x3",
      "path": ".tickets/DAEO-f6x3.md",
      "text": "# W2-146 The id reader reads every declared id form\n\nThe owner's DEC-1099 (2) answer (6): the nonexistent-id row filed as its own ticket now, before the first adoption.\n\n- **The defect:** the product's id reader (`gov.retrieval.lexical.ids_in`) reads only tokens of its one built-in\n  shape (`ID_SHAPE`: a capital letter, then at least one hyphen and a part, with a digit somewhere). A repository\n  whose ids take another form (no hyphen, lower case, an underscore, a space) names ids that the reader does not read\n  as ids, so `gov retrieve`'s stop (`_nowhere` in `src/gov/retrieve/command.py`) never sees them, and DEC-1071 (5)'s\n  `UNRESOLVED_IDS` cannot fire for a question naming a nonexistent id in such a form. Found at the fresh 80's\n  pre-flight (`governance/project/orchestration/packages/LIFT-1/FRESH-80-RESULT.md`, \"What follows\"); an adopted\n  repository will have more such forms (W2-88-STANDARD-1 \u00a75).\n- **The fix (W2-88-STANDARD-1 \u00a75):** the id forms read from the path map, beside the built-in shape. The forms used\n  by this repository's own records need no declaration; whether this repository's path map declares any form is the\n  CTO's record change, not this ticket's.\n",
      "tokens": 298
    },
    {
      "id": "DAEO-f6x3",
      "path": ".tickets/DAEO-f6x3.md",
      "text": "  by this repository's own records need no declaration; whether this repository's path map declares any form is the\n  CTO's record change, not this ticket's.\n- **Until it lands:** W2-88's S12 and S14 score the nonexistent-id question on the reader's \"not found\", apart from\n  the bar, and record the stop as \"not applicable\" (W2-88-STANDARD-1 \u00a75).\n- **Tests first:** an independent test designer writes `tests/acceptance/W2-146/` from these lines on planted id\n  forms, before the engineer starts. No hidden or spent question's form is named in a test or a record.\n- **Overlaps:** `src/gov/retrieve/command.py` is also written by W2-116 (`DAEO-f58b`) and W2-138 (`DAEO-rmhj`), both\n  in progress; `src/gov/retrieval/**` by W2-32 (`DAEO-0pyc`), closing at the lift. `gov plan` orders them; the second\n  to merge merges back. `gov.links` has its own `ids_in` (`src/gov/links/check.py`), not touched here.\n- **Profile STANDARD:** a narrow change to what the reader reads, with no change when no form is declared (S4). It\n  touches the stop that keeps unrelated evidence from being offered, so a fault fails open: hence tests first and an\n  independent review.\n",
      "tokens": 290
    },
    {
      "id": "DEC-1078",
      "path": "docs/DECISION_REGISTER.md",
      "text": "### DEC-1078 \u2014 The verdict set of 80 (`memory-verdict-2`) ready: the writer's checks pass, the cross-check closed after two rounds; unused until the next decision point; source families for the rubric's next version\n- **Status:** ACCEPTED (owner, 2026-11-05 evening, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-11-05)`) \u00b7 **Under:** DEC-1074 (3), DEC-1075, DEC-1076, DEC-1010 \u00b7 **Source:** the owner's report of the writer's and checker's lines (ACT-MSET-3 section 6, ACT-MSET-4 section 6)\n- **Decision:**\n  - **(1) The set is ready.** The writer's final checks: sources 179, path missing 0, heading on no line 0, heading on\n    more than one line 0; unresolved 0 (179 heading-anchored); 80 new questions, 0 overlapping an earlier set's gold\n    source; categories callers 8, code-paraphrase 7, contract 8, decision 15 of 13, exact-string 8, failure-memory 2\n    of 4, history 2, kernel-template 7, multi-file 6, nonexistent-id 1, plan 8, ticket 8: total 80 of 80, PASS\n    (failure-memory short by 2, moved to `decision`, as quota (A) of DEC-1075 (2) allows). The CTO's own check at\n",
      "tokens": 295
    },
    {
      "id": "DEC-1085",
      "path": "docs/DECISION_REGISTER.md",
      "text": "    completes what is decided before any experiment below. Anything needing the owner's decision goes to the owner.\n  - (2) **W2-134** is filed: the engineer's ticket for W2-61h S8, small, tests first.\n  - (3) **The two-reranker cells** are measured as planned. Adopting one would change DEC-1043's one shared reranker,\n    so adoption comes to the owner.\n  - (4) **Vocabulary: no 4B embedder for now.** The search-again mechanism is tested instead. When an agent's first\n    search does not answer the question, it searches again in different words, then settles as not found. It is\n    tested with two attempts and with three. The test shows how many misses each recovers, at what cost in tokens and\n    time, and how often an agent claims an answer that is wrong (the nonexistent-id questions included).\n  - (5) **If it works,** the CTO proposes how it becomes a practice for the agents (skills, role templates through\n    W2-128, hooks if needed), as a package. Nothing goes into the skills or roles before the owner approves.\n  - (6) **Then the end-to-end experiments, designed as a package, nothing run before the owner approves.** On the 138\n",
      "tokens": 288
    },
    {
      "id": "DEC-1099",
      "path": "docs/DECISION_REGISTER.md",
      "text": "  - (2) **W2-88-STANDARD-1:** (1) S10 to S17 and the three failure lines as written; (2) (c): EXAMIN's copy at W2-27\n    is the practice's first full run, with no separate proof repository; what goes wrong is fixed there, and the\n    repositories adopted after EXAMIN follow the practice as fixed; (3) (a): a tuning set of 80 in two halves, the\n    second reporting only; (4) the writers are sessions outside the system, opened by the owner's operator; (5) the\n    set tools and the practice record added to W2-88's allowed paths; (6) the nonexistent-id row filed as its own\n    ticket now.\n  - (3) **FORECAST-W2-1's five proposals:** W2-82 after W2-27; the sandbox experiment beside D-10; W2-88 answered now;\n    G1's fewer scored pairs deferred until after EXAMIN's copy; W2-15a closed together with W2-32. **W2-139 and W2-140\n    merged before D-10**, so they close at the lift.\n- **Basis:** question 2 (the guard proven before it is widened, the held-out halves sealed) and question 1 (the memory\n  standard carried to EXAMIN as the practice's first full run).\n\n",
      "tokens": 267
    },
    {
      "id": "25e9e47dd34d103718b30647",
      "path": "docs/audit/memory-measure-new-hidden.md",
      "text": "| Supersession with a superseded naive answer | at least 2 (at least 2 required). The earlier audit counted at least 4 among the 24; the 16 add none | PASS |\n\n**Category table** (the `category` values, which sum to 40):\n\n| Category | Count | At least | Result |\n|---|---|---|---|\n| decision | 5 | 6 | short 1 |\n| contract | 4 | 4 | met |\n| plan | 4 | 4 | met |\n| ticket | 4 | 4 | met |\n| exact-string | 4 | 4 | met |\n| callers | 3 | 4 | short 1 |\n| code-paraphrase | 2 | 3 | short 1 |\n| kernel-template | 3 | 3 | met |\n| multi-file | 3 | 3 | met |\n| failure-memory | 5 | 3 | met |\n| history | 2 | 1 | met |\n| nonexistent-id | 1 | 1 | met |\n\n**R5-QUOTA** on `decision`, `callers` and `code-paraphrase`, one short each. This is the shortfall the operator\nnoted and the brief says the owner accepted. I found no register entry that records that acceptance; recording it\nunder DEC-1069 is recommended. Items 2 to 5 (domains, subsystems, tags and supersession) all pass.\n\n",
      "tokens": 242
    },
    {
      "id": "bd10d8a0a2addf42b14fc4e3",
      "path": "docs/audit/memory-measure-new-visible.md",
      "text": "### Category table\n\nThe writer's category table (R5 item 6, for information on the visible half) is correct: it sums to 40, with\n`exact-string`, `callers`, `kernel-template`, `multi-file`, `history` and `nonexistent-id` short. With q36 kept as\n`kernel-template`, the table is unchanged.\n\n**R5 verdict: PASS for the 40, with no margin on the plan, lessons or retrieval.** The next visible additions should\nbe the writer's proposed 2 exact-string, 1 callers, 1 history and 1 nonexistent-id questions, plus one plan question\nfor headroom. None of them should be on retrieval.\n\n",
      "tokens": 144
    },
    {
      "id": "6522f9fd3dc61c99ff7ea9bb",
      "path": "docs/probes/DAEO-h2k3/PR-DAEO-h2k3-narrow-count-floor.md",
      "text": "**What I probed and found sound** (head `82b5cf19854da1d38699c6889bd8feb6957ec1cb` confirmed; `git status --porcelain` empty at start and end)\n- **Count:** `HIDDEN_COUNT = 39`. Its comment is true: DEC-1069 (4)'s 40 (h01-h24 and h25-h40) less h10, which DEC-1171 (2) retired, until the walled writer's replacement brings it back to 40. This matches DEC-1171 (2) and the ticket's S1 line (\"39 hidden files while h10 sits in retired-hidden/ \u2026 40 once the walled writer's replacement lands\"). The S1 count case compares the file count with `HIDDEN_COUNT` exactly, and still fails on any non-`.yaml` entry.\n- **Retired place:** `R5_RETIRED = {\"callers\": 1}` sits directly below `R5_SHORT`, exactly as ordered. `R5_QUOTAS` and `R5_SHORT` are unchanged.\n- **S3's floors**, computed from the module: decision 5, contract 4, plan 4, ticket 4, exact-string 4, **callers 2**, code-paraphrase 2, kernel-template 3, multi-file 3, failure-memory 3, history 1, nonexistent-id 1. They sum to 36. The R5 table sums to 40; less the retired place, 39.\n- **S3 on synthetic in-memory maps** (no path touched; counts only):\n  - green at exactly the floors (36 maps);\n  - green at the floors padded to 39;\n",
      "tokens": 296
    },
    {
      "id": "21ca703798f2a54858ec30b1",
      "path": "docs/research/W2-88-memory-practice.md",
      "text": "| Reranker: the 4B at 24 reranked | trial | 36/40 | 32/39 | not yet (DEC-1079) | 112/138; 9 gains, 4 losses, p 0.27; 2.84 s alone, 33 s at 20 at once |\n| No reranker (the fused order alone) | trial | 35/40 | 28/39 | \u2014 | 95/138: the reranker is +12 net (21 lifted, 9 pushed out, p 0.04); without it the sets' spread is 33.3 against 17.2 |\n| **W2-92 built: the stated links in the product** | w4-92 | 33/40 | 34/39 | **yes**, merged | the 79 67 = the control 67, MRR 0.6306 against 0.6242; drift 0 \u2192 190 of 190 |\n| W2-32 built: v456 as five pool settings, pool on / off | w4-32b / c | 34/40 / 36/40 | 32/39 / 30/39 | pending (wording) | 107 / 108 of 138; the halves' gap 2.9 / 13.1; 1.20 / 1.48 s a call |\n\nNight one's survey (63 variants on all 48) and night two's (32 on the visible half) also found:\n- **Losers:** pool quotas, a global pool, an embedder instruction, a reranker instruction, authority \u00d72.\n- **Neutral:** route agreement, a blend.\n- **Speed:** every method within 0.08 s.\n\n**From m6-M1 on, the figures are judged on the 79** (h24, the nonexistent-id question, scored apart): adopted when\nthe 79 do not fall and the halves' gap does not widen, then by MRR over the 79.\n\n",
      "tokens": 297
    },
    {
      "id": "403ecbfffccc91dfe952adcf",
      "path": "governance/project/indep-briefs/memory-audit/checker.md",
      "text": "### 5a. The set (R5), counted from the questions as you judge them\n- Governing domain of each question (the domain of its main entry's governing source): code (`src/**`, the kernel\n  hooks), decisions (the register), tickets (`.tickets/**`), plan (`docs/plan/**`), contract (`docs/contract/**`,\n  `docs/charter/**`). A source elsewhere (a lesson, a role file, a skill) counts in none of the five, only in the tags\n  (kernel template; failure or lesson memory).\n- Each of the five domains has at least 4 of the 40. No subsystem has more than 10: retrieval and the context packet,\n  the guard, the close and the nightly, checkpoints and resume, rebuild and the secrets scan, launch and the sandbox,\n  releases and install (count a question for what its asked fact is about).\n- At least 2 supersession questions whose naive answer is superseded; at least 2 kernel roles or skills; at least 3\n  failure or lesson questions, each citing a lesson or failure record.\n- The categories' counts are exactly: decision 6, contract 4, plan 4, ticket 4, exact-string 4, callers 4,\n  code-paraphrase 3, kernel-template 3, multi-file 3, failure-memory 3, history 1, nonexistent-id 1.\n",
      "tokens": 292
    }
  ],
  "supplementary_query": "The standing hidden set: each repository's memory judged end to end every week on the same questions at 95 %, counts only, with a monthly fresh set as the check against fitting, a weekly maintenance pass, and the audit's state per repository (MEMORY-AUDIT G1, G2, G3, G5 and G4's code)\nS1 A standing set: `python3 -m gov.memaudit standing declare --set <name> --repo <dir>` records one standing set for the repository: its name, its digest (`LC_ALL=C sha256sum *.yaml | sha256sum` over the kept questions), n with the nonexistent-id questions apart, the sha256 of the writer's and checker's briefs, and the commit it was written at. A set whose questions were ever written to a `misses.jsonl` or read by an auditor is refused (`STANDING_SPENT`); an adopted repository's Wave 0 verdict set is accepted once its `USED` marker and its counts-only result record exist (W2-88 S13, S16). One standing set is live per repository; a second is refused until the first is retired [DEC-1179 (1), DEC-1176 (1), DEC-1098 (1)] Verify: planted sets: a new set is recorded with each field; a set with a planted `misses.jsonl` line is refused with `STANDING_SPENT`; a planted Wave 0 verdict set with `USED` and its record is accepted; a second live set is refused\nS2 One judged run a week: a standing run writes `runs/<set>/<ISO year>-W<week>/DECLARATION.json` and then `USED`, before any search; a second judged run of the same set in the same ISO week exits 3 and writes nothing. A run stopped by the fault rule (FRESH-80-1 \u00a73.5, `STOPPED <cause>`) before its reader run started may start once more that week; a run whose reader run started never runs again [DEC-1179 (1), DEC-1097 (1)(g)] Verify: planted runs: the file times and the ledger line show DECLARATION.json before USED before the first search; a second run the same week exits 3 with the tree byte-identical; a planted STOPPED before the reader run allows one restart and a second is refused\nS3 The same method as Gov OS's memory: a standing run uses the fresh 80's judged path unchanged: the store at the audit commit with the standard (the 0.6B through the one shared reranker, the pool on, the 6,000-token bundle widened to sections); each question's first bundle from `gov.retrieval.measure`; `judge`'s reader run as built (the pinned `prompts.py`, the reader, the cap, the A2 cut judged, A1 and A3 as data); the named grader with the second grader's agreement; the measure's matcher with source families. Every search result's store commit (W2-138) equal to the declared store's commit, else that attempt is a fault [DEC-1179 (1), DEC-1097 (1)(a), DEC-1098 (1), DEC-1092 (1)] Verify: `tests/unit/memaudit/test_prompts.py` passes unchanged; a planted standing run calls the same reader, grader and matcher functions as a fresh run (one shared code path, asserted by a spy); a planted result from another store commit makes the attempt a fault\nS4 Counts only: a standing run writes no `misses.jsonl` and launches no auditor. Only counts leave its run folder: right end to end, wrong claims, not found, the misses by outcome (wrong, incomplete, not found) and by the first gold place's rank in the first bundle (1-5, 6-20, absent), the questions dropped by the anchor check, and the figures beside (hit@5, gold in the first bundle, A1 against A2 with exact McNemar). No question id, question, gold, answer or citation of the standing set is printed, logged, written to `FIGURES.json`, `HISTORY.jsonl`, `AUDITS.log` or the digest block, or written outside its run folder (mode 0700) [DEC-1179 (2), DEC-1101 (2), DEC-1074 (1)] Verify: a planted standing run with five planted misses whose ids and texts are unique strings: no planted string appears in stdout, stderr, FIGURES.json, HISTORY.jsonl, AUDITS.log, the digest block or any file outside the run folder; no misses.jsonl exists; no auditor launch event is in the ledger\nS5 The bar at 95 %: `declare.bar(n)` gives `need_right = ceil(95 n / 100)` and `max_wrong = floor(5 n / 100)`; a verdict passes when right end to end at A2 reaches `need_right` (wrong claims stay reported and checked). It applies to standing and fresh runs alike, and the declaration's rounding text says so. On 80 judged that is 76, on 79 it is 76, on 40 it is 38 [DEC-1179 (2), DEC-1097 (1)(d) as carried forward, DEC-957] Verify: unit cases n = 40, 79, 80 give 38, 76, 76; a planted run with right = need_right - 1 is a miss and with right = need_right a pass; the digest's bar line prints the new figure; the revised W2-170, W2-171 and W2-172 cases pass, and W2-88's S15 bar case (which reads W2-170's helper `bar`) passes unedited\nS6 Staleness by count: before each standing run the pre-flight checks each question's gold anchors at the audit commit; a question whose anchor no longer resolves, or whose nonexistent id now exists, is dropped from that week's n and counted (`dropped k`); nothing in the set is edited. Fewer than 70 live questions prints `STANDING_THIN <live>` in the digest block and asks for a replacement [DEC-1179 (2), DEC-1097 (1)(f)] Verify: a planted set of 80 with 3 broken anchors: n is 77 and `dropped 3` is printed with no id; the set's digest is unchanged after the run; a planted set with 69 live questions prints STANDING_THIN 69\nS7 The monthly check against fitting: at each fresh run the tool compares the fresh set's right end to end per cent F with S, the mean of the standing set's last four weekly figures; S - F of 5 points or more writes `STANDING_FITTED` in HISTORY.jsonl and the digest block, retires the standing set (no further standing run on it; it joins the pool as a diagnostic set, counts only) and asks for the writer's replacement; F - S of 5 points or more writes `STANDING_STALE` and asks for the checker's staleness pass; with fewer than four weekly figures the check prints `drift: not yet (k of 4)` [DEC-1179 (3), DEC-1074 (4)] Verify: planted histories: S 96, F 90 retires the set and a later standing run on it is refused; S 90, F 96 prints STANDING_STALE; S 95, F 92 prints no flag; two weekly figures print `drift: not yet (2 of 4)`\nS8 The two cadences and below 95 %: the standing set's cadence is W2-172 S5's computed rule, unchanged (weekly while active, monthly once stable, back to weekly at once on a miss, a retrieval change, churn of 10 % or more or a pool regression); the fresh set is due on the first Monday 28 days or more after the last fresh run. A standing miss is a HISTORY line `miss` with its counts; the fresh set is then due at the next Monday and every Monday until a standing run passes again (then every 28 days); the maintenance pass (S10) runs at once after the miss in the same cycle; the digest block carries a `P1 memory below 95 %` line with the counts by class. Two consecutive standing misses, or one miss 5 points or more below the last passing figure, write `MEMORY_REPAIR open` in HISTORY.jsonl, and `gov.memaudit status --repair` exits 1 while it is open and 0 once a later standing run passes or the owner's decision id is given with `--residual DEC-<n>` [DEC-1179 (4), (5), DEC-1125 (2)] Verify: `tests/acceptance/W2-172/test_w2_172_s5_due.py` passes unchanged for the standing set; a planted fresh history 27 days old is not due and 28 days old is due on the Monday; planted histories: one miss makes the fresh set due next Monday and puts the P1 line in the digest; pass, miss, miss opens the repair; pass at 96 then miss at 90 opens it; `status --repair` exits 1, then 0 after a planted pass or `--residual DEC-1`\nS9 State per repository: the runs folder is `<runs>/indep/memaudit/<key>/` with `<key>` the repository's directory name, a hyphen and the first 8 hex of the sha256 of its real path, so two repositories on one machine keep separate `AUDITS.log`, `HISTORY.jsonl` and `STARTS.log`. The retrieval change that sends an audit back to weekly is, for any repository, a change of the gov pin, of the repository's `governance/project/retrieval.yaml` digest or of its path map's digest, and for Gov OS also its six retrieval globs. `pool-import --sets <name>...` seeds the pool from that repository's own sets root; with no `--sets` on Gov OS it imports Gov OS's 79 and 138 as today [DEC-1179 (5), DEC-1101 (1), DEC-1125 (2)] Verify: two planted repositories on one runs folder write to two keys and neither reads the other's history; a planted pin change on an adopted repository is a retrieval change and a change under `src/gov/retrieval/` of Gov OS is not, for it; `pool-import --sets a b` imports exactly those sets\nS10 One weekly maintenance pass before each standing run, `python3 -m gov.memaudit maintain --repo <dir>`: (1) the integration store at the main line's head, else one refresh by W2-116's `gov rebuild --integration`, a failed build leaving the last good store in service and named; (2) the store's layout current, else one `gov rebuild`; (3) `gov links --since <the last pass's commit>`: the count of new findings; (4) the count of tracked paths the path map indexes but the store holds no chunk of; (5) the standing and fresh runs' reader `not found` answers and second searches, counted; (6) the list of gold questions whose cited lines changed at the audit commit (W2-61h S4's list, with N2 (b), DEC-1180 (1): a heading-cited source whose section text (from its heading line to the next heading of the same or a higher level, or the end of the file) differs between the source's own commit and the head is listed too, though its heading is still found; question id and entry number only, never a question, answer or path) handed to the walled writer's request for re-anchoring or rewording, counted. It prints six counts in the digest block, never fails or delays the audit, and never changes one of the standard's four settings [DEC-1179 (6), DEC-1178 (1), DEC-1072 (1), DEC-1101 (1), DEC-1096] Verify: a planted repository with a store 3 commits behind is refreshed once and the head printed; a planted failing rebuild keeps the old store and names the failure; planted link findings and two unindexed paths are counted; the audit runs whatever the pass finds; the retrieval.yaml digest is unchanged after the pass; a planted set with one changed cited block and one moved unchanged block lists only the changed one, by question id and entry number, in the writer's request, with no question, answer or path text in it or in the digest\nS11 The schedule's code (G4): `memaudit_cron.sh` takes `--repo <dir>` and runs, when due, the maintenance pass, the standing run and, when the fresh set is due, the fresh cycle, in that order, within the gate's wait (W2-172 S9); A9's ACT package (`memory_sets.walls_act`) adds one step to its ACT.md with the repository's cron line (the wrapper with `--repo <that repository>`, Mondays 21:00), written as text for the repository's owner's operator and never installed [DEC-1179 (5), DEC-1101 (2), W2-88 S22] Verify: a planted due standing run and a due fresh set run in that order from one wrapper call; nothing runs when neither is due; a planted A9 run's ACT.md holds the cron line with the repository's path and no crontab is changed\nS12 The weekly secret scan and push (DEC-1182 (2)): after the weekly audit and measure (the maintenance pass, the standing run and, when due, the fresh cycle), a repository that declares its weekly push (its remote and branch, in the key I11 names) gets one full gitleaks scan of the repository, then `git push <remote> <branch>` only when that scan is clean; a scan that finds anything, fails or cannot run blocks the push and is named in `cron.log` and the digest by count and reason only; a repository that declares no push (Gov OS, DEC-1182 (1)) skips both steps, named; no scan runs in the maintenance pass's refresh. A9's ACT package's step 6 names the cycle's order (audit and measure, scan, push on a clean scan) and how the repository's owner declares the push [DEC-1182 (2), DEC-1179 (5), DEC-1101 (2)] Verify: a planted repository with a declared bare remote and a clean tree is scanned once and pushed after its audit; a planted secret in a tracked file blocks the push (the remote unchanged) and the log names a count, never the secret; a failing or missing gitleaks blocks the push, named; a planted repository with no declaration runs neither step and says so; a planted A9 run's ACT.md step 6 names the order\nF1 A standing set's question id, question, gold, answer or citation outside its run folder, or read by any session: the auditor, the CTO, a worker or a later fix. Verify: S4's planted strings are absent from every file written outside the run folder and from every launched session's brief; no code path hands a standing run's rows to `classes`, the auditor's launch or the pool's fix judging\nF2 A standing set judged twice in one week, judged without DECLARATION.json and USED first, re-scored, or its labels changed after a figure exists. Verify: S2's planted runs; `measure --kept` on a standing run exits 3 and writes nothing; the set's digest is checked equal at every run and a planted edit is refused before any search\nF3 The standing set used to choose, adopt or reject a fix or a configuration. Verify: the tool offers no command that compares two configurations or two commits on a standing set; the standing run refuses `--decision` and any data condition\nF4 The method drifts: the reader or grader prompt, model, cap or A2 cut changed, or the standing path diverges from the fresh path. Verify: `test_prompts.py` passes unchanged; S3's spy\nF5 A fresh set's use-once behaviour changes. Verify: W2-170's S3 and F2 cases on fresh sets pass with only their bar values revised; W2-171's S5 case passes with only its bar value revised (W2-187-P1 (a), DEC-1156 (7))\nF6 The maintenance pass changes a setting of the standard, applies an ACT, installs a cron line or stops the audit. Verify: S10's planted runs; the module imports no crontab writer and the retrieval.yaml and path map digests are unchanged after a pass\nF7 A push after a scan that found anything, failed or did not run; a finding's text (a secret, a match, a line) in `cron.log`, the digest, the ACT text or the push's output; a scan or a push at a refresh, a close or a repository that declared no push. Verify: S12's planted runs; the module's scan call is the only gitleaks call in the cycle",
  "further_batch": [
    {
      "id": "efd5e025e2b60e569b826bf9",
      "path": "governance/project/indep-briefs/memory-audit/checker.md"
    },
    {
      "id": "2746d3d80f7dcc10ba5dfc4d",
      "path": "governance/project/indep-briefs/memory-audit/writer.md"
    },
    {
      "id": "37818f14f7aa7460dbee6249",
      "path": "governance/project/indep-briefs/memory-audit/writer.md"
    },
    {
      "id": "8e2383192ff2fa0938be62a5",
      "path": "governance/project/indep-briefs/memory-audit/writer.md"
    },
    {
      "id": "17db5dc37447bb9d18963d92",
      "path": "governance/project/orchestration/DECISIONS-IN-FORCE.md"
    },
    {
      "id": "fb64b06917ace89571e115c7",
      "path": "governance/project/orchestration/DECISIONS-IN-FORCE.md"
    },
    {
      "id": "0ca03c080edbe1f1cbbf0b09",
      "path": "governance/project/orchestration/packages/ACT-MSET-1.md"
    },
    {
      "id": "b9486bf0d2461d7b950a5240",
      "path": "governance/project/orchestration/packages/ACT-MSET-3.md"
    },
    {
      "id": "122141124be2cba2bd88fe87",
      "path": "governance/project/orchestration/packages/DECIDED-NOT-DONE.md"
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
          "id": "02a4e9dc689b8a8af00f3276",
          "path": "docs/changes/W2-172-evidence.md"
        },
        {
          "id": "5a9e22d58ea68b00e35c61f3",
          "path": "docs/probes/DAEO-p8tv/PR-DAEO-p8tv-round-1.md"
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
          "id": "DAEO-h2k3",
          "path": ".tickets/DAEO-h2k3.md"
        },
        {
          "id": "DEC-1180",
          "path": "docs/DECISION_REGISTER.md"
        },
        {
          "id": "4fcadaf3f8da46268265fc58",
          "path": "docs/probes/DAEO-h2k3/PR-DAEO-h2k3-f3.md"
        },
        {
          "id": "70b6669acfd83d5ab086c3c4",
          "path": "docs/probes/DAEO-h2k3/PR-DAEO-h2k3-f3.md"
        },
        {
          "id": "740f7c64cfe8935fbf07fad8",
          "path": "docs/probes/DAEO-h2k3/PR-DAEO-h2k3-f3.md"
        },
        {
          "id": "ef6f9c353cbc2b0936e2bc76",
          "path": "docs/probes/DAEO-h2k3/PR-DAEO-h2k3-n2.md"
        }
      ],
      "limit": 10
    },
    {
      "items": [
        {
          "id": "c6f2a2d177cb489bbfd84da0",
          "path": "tests/acceptance/W2-134/README.md"
        },
        {
          "id": "041a52e7f221d0a7980a8154",
          "path": "tests/acceptance/W2-61h/README.md"
        },
        {
          "id": "0c7b3ec117b38d984e610bbb",
          "path": "tests/acceptance/W2-61h/README.md"
        },
        {
          "id": "1e8647524a58650309e08c7b",
          "path": "tests/acceptance/W2-61h/README.md"
        },
        {
          "id": "21978452c683cd6a91ab4f8c",
          "path": "tests/acceptance/W2-61h/README.md"
        },
        {
          "id": "4889c31e4d462ecca60de49a",
          "path": "tests/acceptance/W2-61h/README.md"
        },
        {
          "id": "246d11f318a5fc0a8094c9ad",
          "path": "tests/acceptance/W2-61h/test_w2_61h_visible_new.py"
        },
        {
          "id": "aaff117542049a71f170ff86",
          "path": "tests/acceptance/W2-61h/test_w2_61h_visible_new.py"
        },
        {
          "id": "cf93cc6385aaca25154282fc",
          "path": "tests/acceptance/W2-61h/test_w2_61h_visible_new.py"
        },
        {
          "id": "DAEO-c1uz",
          "path": ".tickets/DAEO-c1uz.md"
        }
      ],
      "limit": 10
    },
    {
      "items": [
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
        },
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
        }
      ],
      "limit": 10
    },
    {
      "items": [
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
        },
        {
          "id": "43f46818b689a10d7318f6cb",
          "path": "tests/acceptance/W2-113/README.md"
        },
        {
          "id": "1168ef12eb7219ee8157cbce",
          "path": "tests/acceptance/W2-59/README.md"
        },
        {
          "id": "a8302497d7c2c35e9ad4a9b1",
          "path": "tests/acceptance/W2-59/README.md"
        },
        {
          "id": "ee5caf56e3b60ba24a7c49b0",
          "path": "tests/acceptance/W2-66/test_w2_66_live_test_map.py"
        },
        {
          "id": "93e0ef990b2e8661cb2c1dc1",
          "path": "governance/project/orchestration/packages/LIFT-1/FRESH-80-RESULT.md"
        }
      ],
      "limit": 10
    },
    {
      "items": [
        {
          "id": "249b917ed5a7dc6cead63101",
          "path": "governance/project/orchestration/packages/W2-88-STANDARD-1.md"
        },
        {
          "id": "DAEO-f6x3",
          "path": ".tickets/DAEO-f6x3.md"
        },
        {
          "id": "DAEO-f6x3",
          "path": ".tickets/DAEO-f6x3.md"
        },
        {
          "id": "DEC-1078",
          "path": "docs/DECISION_REGISTER.md"
        },
        {
          "id": "DEC-1085",
          "path": "docs/DECISION_REGISTER.md"
        },
        {
          "id": "DEC-1099",
          "path": "docs/DECISION_REGISTER.md"
        },
        {
          "id": "25e9e47dd34d103718b30647",
          "path": "docs/audit/memory-measure-new-hidden.md"
        },
        {
          "id": "bd10d8a0a2addf42b14fc4e3",
          "path": "docs/audit/memory-measure-new-visible.md"
        },
        {
          "id": "6522f9fd3dc61c99ff7ea9bb",
          "path": "docs/probes/DAEO-h2k3/PR-DAEO-h2k3-narrow-count-floor.md"
        },
        {
          "id": "21ca703798f2a54858ec30b1",
          "path": "docs/research/W2-88-memory-practice.md"
        }
      ],
      "limit": 10
    },
    {
      "items": [
        {
          "id": "403ecbfffccc91dfe952adcf",
          "path": "governance/project/indep-briefs/memory-audit/checker.md"
        },
        {
          "id": "efd5e025e2b60e569b826bf9",
          "path": "governance/project/indep-briefs/memory-audit/checker.md"
        },
        {
          "id": "2746d3d80f7dcc10ba5dfc4d",
          "path": "governance/project/indep-briefs/memory-audit/writer.md"
        },
        {
          "id": "37818f14f7aa7460dbee6249",
          "path": "governance/project/indep-briefs/memory-audit/writer.md"
        },
        {
          "id": "8e2383192ff2fa0938be62a5",
          "path": "governance/project/indep-briefs/memory-audit/writer.md"
        },
        {
          "id": "17db5dc37447bb9d18963d92",
          "path": "governance/project/orchestration/DECISIONS-IN-FORCE.md"
        },
        {
          "id": "fb64b06917ace89571e115c7",
          "path": "governance/project/orchestration/DECISIONS-IN-FORCE.md"
        },
        {
          "id": "0ca03c080edbe1f1cbbf0b09",
          "path": "governance/project/orchestration/packages/ACT-MSET-1.md"
        },
        {
          "id": "b9486bf0d2461d7b950a5240",
          "path": "governance/project/orchestration/packages/ACT-MSET-3.md"
        },
        {
          "id": "122141124be2cba2bd88fe87",
          "path": "governance/project/orchestration/packages/DECIDED-NOT-DONE.md"
        }
      ],
      "limit": 10
    }
  ],
  "dropped": [
    {
      "id": "0ca03c080edbe1f1cbbf0b09",
      "reason": "budget exceeded"
    },
    {
      "id": "122141124be2cba2bd88fe87",
      "reason": "budget exceeded"
    },
    {
      "id": "17db5dc37447bb9d18963d92",
      "reason": "budget exceeded"
    },
    {
      "id": "2746d3d80f7dcc10ba5dfc4d",
      "reason": "budget exceeded"
    },
    {
      "id": "37818f14f7aa7460dbee6249",
      "reason": "budget exceeded"
    },
    {
      "id": "8e2383192ff2fa0938be62a5",
      "reason": "budget exceeded"
    },
    {
      "id": "b9486bf0d2461d7b950a5240",
      "reason": "budget exceeded"
    },
    {
      "id": "efd5e025e2b60e569b826bf9",
      "reason": "budget exceeded"
    },
    {
      "id": "fb64b06917ace89571e115c7",
      "reason": "budget exceeded"
    }
  ],
  "tokens": 89947,
  "budget": {
    "limit": 90000,
    "used": 89947
  },
  "hash": "6f2767383cb01175ac47b930b835cae8160e5efd96eddeb149aa15f23fd30bdf"
}

----

## Judgement rules (governance/project/briefs/JUDGEMENT.md, carried word for word)

## Judgement rules: the w2 prompt's section 14, word for word (owner, DEC-801 to DEC-803, DEC-807 to DEC-809)

Every reviewer, probe and auditor brief you write carries this section and the two bullets after it, word for word. You judge your own reviewers' findings by the same rules, and every finding in a probe record you commit keeps its two lines.

- **The threat model is ADR-0001's** (`docs/adr/ADR-0001-threat-model.md`): the Gov OS guards against honest agent mistakes, plausible accidents and drift in ordinary work, not against a deliberate adversary with the owner's privileges. Machinery against an adversary the design cannot stop produces endless review loops.
- **Every finding is judged by two questions, word for word:**
  1. "Can an honest agent hit this in ordinary work?"
  2. "Does it fail open or lose work?"
- **Only a finding with "yes" to both justifies a round.** A finding that needs a deliberate construction (a link planted at a protected name, git environment variables set by hand such as `GIT_OBJECT_DIRECTORY` or alternates, replace refs, an opaque interpreter used to evade the guard) is a row for the Wave 3 hardening pass, never a new round (DEC-801). A finding marked "no" on the first question is a row automatically.
- **Every finding in a probe or audit record carries two lines:** `Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other` (DEC-808).
- **No extra round on its own:** when a ticket will resume anyway, its accepted fixes ride along in that resume (DEC-802).
- **Feature-gated risks:** a risk that exists only when a feature is switched on is an entry criterion of the ticket that switches it on (DEC-803).
- **Packages:** every package that proposes a round states the classification of its findings on one line, before the recommendation (DEC-809).
- These rules go, word for word, into every reviewer, probe and auditor brief (A3, and every audit brief of W2-25, W2-28, W2-30 and W2-47).

From brief A3 (reviewer), word for word:
- Judge against ADR-0001's threat model (section 14): honest agent mistakes and plausible accidents in ordinary work, not deliberate adversaries. Ask of every finding, word for word: "Can an honest agent hit this in ordinary work?" and "Does it fail open or lose work?"
- Every finding carries two lines: `Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other`. A finding marked "no" is a row for the Wave 3 hardening pass, never a round; only "yes" with "fails open" or "loses work" fails the probe.
- **How reviews converge (owner, standing, DEC-1010 item 1; in force for the CTO, every lead, reviewer and QA engineer):**
  - **A moderator, not a circle of reviewers:** the QA engineer (or the Senior Engineer; until the three layers start, the CTO) triages every finding against the ticket's own scope and KPIs. A finding outside the scope, or one that needs an unusual construction, becomes a Wave 3 row, never a round.
  - **A finding blocks only if it is in scope, reachable in ordinary work, and fails open or loses work.** Everything else lands as a recorded row.
  - **At most two review rounds.** If something still blocks after that, it goes to the owner once, with options; no more routine exceptions.
  - **READY is computed by code, not declared by an agent:** each reviewer returns a structured verdict per KPI line, a fenced `verdict` block in the probe record: `{"kpis": [{"kpi": "<line id>", "verdict": "pass|fail", "findings": [{"id": "F1", "scope": "in|out", "ordinary_work": "yes|no", "consequence": "fails open|loses work|other"}]}]}`; the close (and the merge queue's pre-check) computes READY from it: no finding that is in scope, ordinary work yes and fails open or loses work. A lead never writes a verdict over a reviewer's.

## Return (your last message; nothing else is read)
The twelve fields, each a labelled line ("none" where nothing): task / status (DONE, PACKAGES or ESCALATION) /
work_completed / files_changed (none) / evidence / tests / discoveries / risks / lessons / proposed_decisions /
unresolved / recommended_next_action. Then:
- **The KPI trace:** one row per line S1-S12 and F1-F7: the tests, the code, and traced or not.
- **What was probed and found sound,** each with the probe you ran.
- **Each finding** as a described behaviour (never code): what was done, what happened, what should have happened, file
  and line, `Ordinary work: yes|no, because …`, `Consequence: fails open|loses work|other`, scope in or out.
- **The verdict:** `pass` or `fail` for the round, by the rules above (only an in-scope finding with ordinary work yes
  and fails open or loses work fails it).
- **The fenced `verdict` block LAST,** exactly in this form, one entry per KPI line (success-1 … success-12,
  failure-1 … failure-7):
  ```verdict
  {"kpis": [{"kpi": "success-1", "verdict": "pass", "findings": []}, ...]}
  ```
Then `guard_refusals:` (none, or each: time | form | the hook's reason | true or false-positive). Refused twice for the
same call by the guard, the sandbox or a hook: stop and say so; never reach the same effect by another form
(DEC-1142 (9)).
