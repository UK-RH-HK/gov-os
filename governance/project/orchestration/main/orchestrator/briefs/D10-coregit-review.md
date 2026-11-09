# D-10's red-fix list, item (1): the review of the `core.bare` fix's tests' half (W2-05, DAEO-0z8c)

You are a fresh, read-only independent reviewer. **Narrow scope: one revision.** READY is computed by `verdict.py`
from your block.

## What happened
- On 2026-11-04 the main repository's `.git/config` went to `core.bare = true`.
- W2-05's review R4-1 (`docs/probes/DAEO-0z8c/PR-DAEO-0z8c-dec970.md`) found the mechanism: `git bisect run`
  exports git's variables (`GIT_DIR` …), and a test that runs `git init` in its own folder then acts on the
  repository they name.
- The CTO reproduced it tonight: `GIT_DIR=<repo>/.git/worktrees/<wt> git init -q` in an empty folder sets
  `core.bare = true` in the main repository.
- The nightly's bisect already gives each step a clean environment (the code half). The tests' half, on D-10's
  red-fix list (DEC-1074 (8), DEC-1083), is that the suites' own git calls never reach a repository the caller's
  environment names.

## What to review
- **The branch:** `w2/W2-05-d10-tests` in `/home/usain/gov-os-worktrees/W2-05-d10-tests`. Read
  `git -C /home/usain/gov-os-worktrees/W2-05-d10-tests diff adec4718a..5e9cdcc8d`.
  - `b83e73b99` is the CTO's ticket commit (`tests/conftest.py` in W2-05's paths).
  - `5e9cdcc8d` is the test designer's change:
    - `tests/conftest.py` removes git's repository-local variables (`git rev-parse --local-env-vars`, with a fallback)
      at import, in every process;
    - the new `tests/unit/gitenv/test_w2_05_suite_git_env.py`, a nested pytest with `GIT_DIR` on a sacrificial
      linked worktree.
- **The designer's runs:**
  - the new case red without the change (4 failed, 1 passed: "the sacrificial repository's core.bare is now true")
    and 5 passed with it;
  - `tests/unit/gitenv` + `tests/unit/close/test_repo.py` 53 passed;
  - `tests/acceptance/W2-126` 25 passed;
  - `tests/acceptance/W2-05`: 9 reds, the same with and without the change (a read-only `/tmp` in the sandbox, and a
    `SOURCE_DIFFERS .rulesync/subagents/orchestrator.md` drift).

## Check
1. **Complete:** does the removal cover every variable that can make a test's git act on another repository
   (`GIT_DIR`, `GIT_WORK_TREE`, `GIT_INDEX_FILE`, `GIT_COMMON_DIR`, `GIT_OBJECT_DIRECTORY`, `GIT_CONFIG_PARAMETERS`,
   `GIT_CONFIG_COUNT` with its `GIT_CONFIG_KEY_n`/`VALUE_n` …)? Is it in force in the controlling process before
   xdist starts its workers, and in each worker? Could a fixture or plugin loaded before `tests/conftest.py` run git
   first?
2. **Nothing wanted is lost:** can a legitimate run need one of these variables, for example a nested gov command
   started inside a git hook, or the close's own run? Is anything restored that should not be, or removed from a
   process other than the test run's?
3. **The case proves it:** does it fail on the unchanged conftest for the stated reason, and could it pass while
   the hazard remains (for example if the nested run never loads this conftest)?
4. **Trailers:** Task, Role, Implements, Rewrite-Reason and Co-Authored-By on `5e9cdcc8d`. Only `tests/conftest.py`
   and `tests/unit/gitenv/**` changed, plus the CTO's ticket line.

KPI id for the verdict block: `core-bare-tests-half`.

## Judgement
`governance/project/briefs/JUDGEMENT.md`, word for word. Every finding carries `Ordinary work: yes|no, because …` and
`Consequence: fails open|loses work|other`, and `scope: in` only if it concerns this revision.

## Write and return
- **You write nothing** in any tree.
- You may run the tests read-only (`-p no:cacheprovider -o tmp_path_retention_policy=failed`) through
  `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh`, with
  `PYTHONPATH=<the branch's worktree>/src`, a TMPDIR folder of your own under the sandbox's TMPDIR, and
  `PYTHONUSERBASE=/home/usain/.local` if you set an empty HOME (so pytest is found).
- No GPU, no installs, never the full suite. Single simple Bash commands (DEC-1080).
- The hidden-half rule holds: never open anything under `~/gov-os-eval/` or `~/gov-os-runs/`, or any `hidden`,
  `memory-verdict` or `memory-verdict-2` folder.
- **Your record is your session's final message**, in full:
  - the twelve labelled fields of `EMG-common.md` (sandbox and `ps` checks first);
  - your answers to the checks;
  - every finding, with its two lines and its scope;
  - at the end, the fenced `verdict` block:
    `{"kpis": [{"kpi": "<id>", "verdict": "pass|fail", "findings": [...]}]}`, one entry per KPI id named above,
    each finding `{"id", "scope", "ordinary_work", "consequence"}` (ids from F1).
- Estimate: 15 minutes.
