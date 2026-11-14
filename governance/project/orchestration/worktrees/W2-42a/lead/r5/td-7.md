# Brief: independent test designer, W2-42a (DAEO-03ub), map the here-string cases in the folder's README (DEC-1164 (18))

Role: independent-test-designer. Ticket DAEO-03ub (W2-42a), profile FULL. You are a fresh test designer.
Your tree (write here only): /home/usain/gov-os-worktrees/W2-42a-tests, branch w2/W2-42a-tests, head 91922819a.
Your path: tests/acceptance/W2-42a/README.md only. Nothing else changes; no test file is edited.
Commit with (all trailers in ONE final paragraph, no blank line between them):
`git commit -m "<subject>" --trailer "Task: DAEO-03ub" --trailer "Role: independent-test-designer" --trailer "Rewrite-Reason: DEC-1164 (18), W2-42a R3" --trailer "Implements: DEC-1028, DEC-958" -- tests/acceptance/W2-42a/README.md`

## The task
The previous test designer added tests/acceptance/W2-42a/test_w2_42a_here_string.py (commit 91922819a: 31 cases; the
CTO's reopening of 2026-11-14 for R3, a write argument after a here-string, and the fallback's here-string forms).
`gov accept W2-42a` reads the folder's README map (its KPI tables) to place each case under a KPI line; the new file
is not in the map yet. Add it exactly as the earlier rounds did for `test_w2_42a_apostrophe_2.py` (read the README:
its file list near line 113, the S1 and F1 rows of the KPI table near lines 134 and 145, and the round table near
line 167):
- a file-list entry for `test_w2_42a_here_string.py` (td-6, 2026-11-14, R3 and the here-string fail-opens);
- each test function under the KPI line it proves, by full `file.py::test_name` (the writes of T it refuses and the
  unknown forms it refuses belong where the README already puts "no write missed" and "unknown form fails closed"
  cases (F1, F2, and the KPI line of the writers if one fits); the allowed and read-only guards where the README puts
  the earlier guards (S1 or the KPI line that fits));
- a round-table row: the groups and counts (R3 12 cases, 5 red; fallback 10, 7 red; read-only 9, 0 red), and
  "Red on d3ba8e50b: 12 failed, 19 passed".
Read the test file to name its functions; read src/gov/accept/runner.py (the map reader, about lines 66 to 210) if you
need to know which cell forms it reads. Then check the map reads: run
`cd /home/usain/gov-os-worktrees/W2-42a-tests && env HOME=$TMPDIR/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-42a-tests/src python3 -c "import pathlib; from gov.accept import runner; print({k: len(v) for k, v in runner._read_map(pathlib.Path('tests/acceptance/W2-42a/README.md').read_text()).items()})"`
or, if that function has another name, the map reader you find (one line; never run gov accept itself in the sandbox).
(`mkdir -p $TMPDIR/empty-home` first.) No pytest is needed.

## Return (your last message; nothing else is read)
The twelve labelled lines: task / status / work_completed / files_changed / evidence / tests / discoveries / risks /
lessons / proposed_decisions / unresolved / recommended_next_action. In `evidence`: your commit's hash (12) and the map
reader's output line. A refusal twice for the same call by the guard, the sandbox or a hook: stop and say so; never
work around it. Search with Read and Grep only (no gov retrieve, no gov context in the sandbox); search again once, in
other words. Never open the evaluation sets' root or any hidden folder. No merge in the sandbox.
