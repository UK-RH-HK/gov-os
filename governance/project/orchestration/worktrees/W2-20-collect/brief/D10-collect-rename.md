Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-20-collect/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# D-10 blocker: five unit test files share a basename with acceptance files, so the whole tree fails to collect (W2-20 DAEO-r30l, W2-148 DAEO-xafn)

You are a fresh **independent test designer** (RUBRIC-2: W2-148's operator tests are C3, so Opus at high). A
rename only: no test's content or meaning changes. D-10's full run waits on you; be quick (target 15 minutes).

## The behaviour to fix
At w2/integrate `6cc09c7ea`, `pytest tests --collect-only` ends "Interrupted: 5 errors during collection" (import file
mismatch: same basename, no `__init__.py`):
- `tests/unit/resources/test_w2_20_gate.py`, `test_w2_20_launch.py`, `test_w2_20_query_start.py`, `test_w2_20_slots.py`
  against `tests/acceptance/W2-20/` files of the same names;
- `tests/unit/operator/test_w2_148_trial.py` against `tests/acceptance/W2-148/test_w2_148_trial.py` (ACT-OPERATOR-1's
  review O2 already asked for distinct names).

## The task
1. `git mv` each of the five **unit** files (never the acceptance ones) to a unique basename that keeps its meaning,
   e.g. `test_w2_20_unit_gate.py`, `test_w2_20_unit_launch.py`, `test_w2_20_unit_query_start.py`,
   `test_w2_20_unit_slots.py`, `test_w2_148_unit_trial.py`. Check no other test file anywhere already has the new name.
2. Fix every reference to the old unit paths that code or tests read: `git grep -n` for each old name (outside
   `tests/acceptance/`); update references in tests, conftest files, test maps (`governance/project/test-map.yaml`,
   any selection lists `tests/*.txt`), and the file's own usage docstring (e.g. `test_w2_148_trial.py` line 6). Do not
   edit tickets, packages, reviews or evidence docs (records: the CTO's); list those you found.
3. Prove it: from the worktree root,
   `env -u PYTEST_ADDOPTS -u PYTEST_PLUGINS PYTHONPATH=$PWD/src python3 -m pytest tests --collect-only -q -p no:cacheprovider --no-header 2>&1 | tail -3`
   must end with a count and **no** "errors during collection" (if HOME is empty in your sandbox, set
   `PYTHONUSERBASE=/home/usain/.local`); then run the five renamed files once
   (`... python3 -m pytest <the five> -q -p no:cacheprovider --no-header -o tmp_path_retention_policy=failed`): the same
   pass/fail counts as before the rename (run them once on the old names first, one file at a time, to have the
   before counts).
4. Two commits (one per ticket), never amend/merge/push:
   - the four W2-20 files: `--trailer "Task: DAEO-r30l" --trailer "Implements: DEC-1122" --trailer "Role: independent-test-designer" --trailer "Rewrite-Reason: D-10: unit files shared basenames with tests/acceptance/W2-20, so the whole tree failed collection; renamed, content unchanged" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`;
   - the W2-148 file: the same with `Task: DAEO-xafn` and the W2-148 reason.

## Where you work
- Worktree `/home/usain/gov-os-worktrees/W2-20-collect`, branch `w2/W2-20-collect`, at `6cc09c7ea`.
- Write only the five files' renames and the references in step 2 (tests and test maps). `TMPDIR` a folder of your
  own under the sandbox's TMPDIR.

## Rules
- `EMG-common.md` holds, its hidden-half rule included. No GPU, no installs, no test runs beyond step 3. Never
  `git worktree prune`. Single simple Bash commands. Any wait by pid only, never a name match.
- Row W2-L423's rule: under `.gov-runtime/`, commit hashes as 12 digits and none of that rule's keywords.
- Return the twelve fields, short: old and new names, references changed, the collect-only tail, before/after counts,
  the two commits.
