Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-56-d10r2-tests/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# D-10 run 1's red group C (20 cases): the conftest hides codebase-memory-mcp from suites that need it (DAEO-wnnz, W2-56)

You are a fresh **independent test designer**, launched under W2-56's ticket (`.tickets/DAEO-wnnz.md`): W2-56
(`8c399ea3e`) added `_CBM_SUITES` to `tests/conftest.py`. D-10 (DEC-1122 (3)) needs the fix before run 2.

## The red
`tests/conftest.py` takes `codebase-memory-mcp` off `PATH` for every case outside `_CBM_SUITES = {"W1-16", "W1-20"}`
(`_without_tool`, about line 564). Three suites need the real tool and now fail at integrate's head `c9742b08910a`:
- `tests/acceptance/W1-41/` (16: `test_w1_41_verdict.py` 7, `_path_map.py` 5, `_migration.py` 3, `_unknown.py` 1):
  `gov adopt --lite --stage A3` answers `ADOPT_CODE_GRAPH_UNREADABLE ... [Errno 2] No such file`;
- `tests/acceptance/W2-69/` (3, serial: `test_w2_69_deleted_text_after_rebuild.py`, `test_w2_69_review_rebuild_root_and_held_store.py` x2):
  `gov rebuild` reports the code-graph store `not_recreated`;
- `tests/acceptance/W1-06/test_w1_06_digests.py` (1): `codebase-memory-mcp is not on this machine: its recorded sha256 cannot be compared`.
The tool is installed (`~/.local/bin/codebase-memory-mcp`).

## The task
1. Let these cases see the real tool again, in the way that keeps W2-56's purpose (the other suites stay without
   it): most likely W1-41, W2-69 and W1-06 join `_CBM_SUITES`, or the cases that need it are marked so (a narrower
   scope is better if it is as simple). Read W2-56's reason for the list first (`docs/changes/W2-56-CIT-E.md`, the
   commit) and keep it. Lower no expectation.
2. Run, through the heavy slot (`EMG-common.md`), with `PYTHONPATH=<your tree>/src`:
   `python3 -m pytest tests/acceptance/W1-41 tests/acceptance/W1-06/test_w1_06_digests.py tests/acceptance/W1-16 tests/acceptance/W1-20 tests/unit/codeintel -q -p no:cacheprovider -o tmp_path_retention_policy=failed`,
   then W2-69's three cases alone (serial: `-p no:xdist`). Report counts before and after; another cause is named, not fixed.
3. One line in the conftest's comment (why the suites are listed).

## Where you work
- Worktree `/home/usain/gov-os-worktrees/W2-56-d10r2-tests`, branch `w2/W2-56-d10r2-tests` (from integrate at
  `c9742b08910a`). Write only `tests/conftest.py`, and the three suites' files only if the narrower marking needs it.

## Rules
- `EMG-common.md` holds. Never open anything under `~/gov-os-eval/`, `~/gov-os-runs/`, or any `hidden`,
  `memory-verdict` or `memory-verdict-2` folder. No installs, never the full suite.
- Commit on your branch only, with `--trailer "Task: DAEO-wnnz" --trailer "Implements: DEC-1122"
  --trailer "Role: independent-test-designer" --trailer "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>"`.
  Never merge, push, amend or rebase.
- Estimate: 25 minutes. Return the twelve fields, short: the change, counts before and after, the head commit.
