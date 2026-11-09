Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-05-d10-tests/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# D-10's red-fix list, item (1): the `core.bare` fix's tests' half (W2-05, DAEO-0z8c)

You are a fresh **independent test designer**, launched under W2-05's ticket (`.tickets/DAEO-0z8c.md`, "the git
environment of every check, hook and helper"). The owner put this item on D-10's red-fix list (DEC-1074 (8),
DEC-1083); DEC-1109 (2) asks that the list be ready before D-10's full run.

## What happened, and the cause (measured)
- On 2026-11-04 at 00:31 the main repository's `.git/config` went to `core.bare = true`, one second after a
  `git bisect run` of a test in a linked worktree. The main tree lost its work tree until the value was set back.
- W2-05's review (`docs/probes/DAEO-0z8c/PR-DAEO-0z8c-dec970.md`, R4-1) found the mechanism: `git bisect run`
  exports git's own variables (`GIT_DIR` and others) to the command it runs. A test that then runs `git init` in a
  folder of its own acts on the repository those variables name.
- The CTO reproduced it today in a throwaway: with `GIT_DIR` set to a linked worktree's git folder
  (`<repo>/.git/worktrees/<wt>`), `git init -q` in an empty temp folder sets `core.bare = true` in the main
  repository's config.
- The code half is done: the nightly's bisect gives each step only the variables a run alone would see (W2-05, DEC-970).
  **The tests' half is open:** the suites' own git calls still inherit whatever `GIT_*` variables the process that
  started pytest had. So a `git bisect run pytest …` (or pytest started inside a git hook) can still re-initialise or
  move the project. Many support modules build their git environment as `{**os.environ, …}`.

## The task
1. In `tests/conftest.py`, for every process of a run (the controlling process before xdist starts its workers,
   and each worker), remove from `os.environ` git's repository-local variables: the list
   `git rev-parse --local-env-vars` prints (git 2.43 here: `GIT_ALTERNATE_OBJECT_DIRECTORIES`, `GIT_CONFIG`,
   `GIT_CONFIG_PARAMETERS`, `GIT_CONFIG_COUNT`, `GIT_OBJECT_DIRECTORY`, `GIT_DIR`, `GIT_WORK_TREE`,
   `GIT_IMPLICIT_WORK_TREE`, `GIT_GRAFT_FILE`, `GIT_INDEX_FILE`, `GIT_NO_REPLACE_OBJECTS`, `GIT_REPLACE_REF_BASE`,
   `GIT_PREFIX`, `GIT_SHALLOW_FILE`, `GIT_COMMON_DIR`), plus `GIT_CONFIG_KEY_<n>` / `GIT_CONFIG_VALUE_<n>`.
   - Ask git for the list at run time, with a fixed fallback if git cannot answer. Decide this and say why.
   - Restore nothing at the end: the run's process is the run's.
   - A test that sets such a variable itself (with `monkeypatch`, as `tests/unit/close/test_repo.py` does) keeps
     working.
   - The conftest must not import `gov`: a nested run may not have it on its path.
   - Add one bullet to the conftest's docstring header, as each earlier rule has.
2. Add a case under `tests/unit/gitenv/` (for example `test_w2_05_suite_git_env.py`) that proves it end to end:
   - make a sacrificial repository with a linked worktree under `tmp_path`;
   - run a nested pytest (`sys.executable -m pytest`, this repository's `tests/conftest.py` in force, `-p no:cacheprovider`)
     with `GIT_DIR` set to that worktree's git folder;
   - its one planted test runs `git init -q` in its own `tmp_path` with an environment of `{**os.environ}`;
   - afterwards the sacrificial repository's config still reads `core.bare = false`, and its refs and HEAD are
     unchanged.
   - Show the case **red without your conftest change** (run it once against the unchanged conftest, for example by
     a stash in your own worktree, and report the failure line), then green with it.
3. Check nothing else moves:
   - `tests/unit/gitenv`, `tests/unit/close/test_repo.py`, `tests/unit/test_conftest*.py` (if any), W2-05's acceptance
     folder `tests/acceptance/W2-05/` and `tests/acceptance/W2-126/` (if present), each run through the heavy slot;
   - report the counts. A case red before and after for another reason is named, not fixed.
4. Every commit carries `--trailer "Rewrite-Reason: DEC-1074 (8): the tests' half of the core.bare fix; the suites' git calls inherited git's GIT_* variables from a bisect or hook around the run"`.

## Where you work
- Your worktree: `/home/usain/gov-os-worktrees/W2-05-d10-tests`, branch `w2/W2-05-d10-tests`. It is integrate at
  `adec4718a`, plus the CTO's ticket commit `b83e73b99` (`tests/conftest.py` in W2-05's paths).
- Write only `tests/conftest.py` and `tests/unit/gitenv/**`.
- Do not read W2-05's implementation (`src/gov/util/gitenv.py` and its callers): DEC-820 (c). You do not need it.
- Run through the heavy slot (`EMG-common.md`), with:
  - `PYTHONPATH=/home/usain/gov-os-worktrees/W2-05-d10-tests/src` and `TMPDIR=/tmp/gov-os-emg-w205d10`;
  - `python3 -m pytest <paths> -q -p no:cacheprovider -o tmp_path_retention_policy=failed`.

## Rules
- `EMG-common.md` holds. The hidden-half rule: never open anything under `~/gov-os-eval/` or `~/gov-os-runs/`, or
  any `hidden`, `memory-verdict` or `memory-verdict-2` folder. No GPU, no model, no installs, never the full suite.
- Commit on `w2/W2-05-d10-tests` only, with `--trailer "Task: DAEO-0z8c" --trailer "Implements: DEC-1109, DEC-1074"`
  `--trailer "Role: independent-test-designer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`
  plus the Rewrite-Reason trailer. Never merge, push, amend or rebase.
- Estimate: 30 minutes. Return the twelve fields, short:
  - the variables removed and how the list is got;
  - the new case red before and green after, with its failure line;
  - every run's counts;
  - the head commit.
