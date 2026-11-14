# W2-94 fix flow — two red unit cases after the fix flow, the engineer's brief (DAEO-g87r)

You are a fresh engineer (class C2) under **W2-94** (`DAEO-g87r`; the ticket, read-only:
`/home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-g87r.md`, KPI lines S11 and S12). A first engineer added a
one-question fix flow (`--fix <id> --reason <code>` on the writer's round 2) to
`governance/project/orchestration/tools/indep_launch.py` (commits `e48c99a67`, `560293740`). The fix flow's acceptance
file `tests/acceptance/W2-94/test_w2_94_fix_flow.py` and the unit file `tests/unit/orchestration/test_w2_94_fix_flow_unit.py`
pass. Two cases of the existing W2-149 suite are red. **S12 requires that suite to pass unchanged**, and you may not edit
it. Make it green by changing only the script, so that the two fix-flow files stay green.

## The failing output (heavy slot, at `94e2ad773`+`560293740`)
```
tests/unit/orchestration/test_w2_149_indep_launch.py:358: in test_help_offers_exactly_the_options_and_no_path_list
    assert opts == {"--sets-root", "--kind", "--brief", "--brief-sha256", "--commit", "--set", "--round", "--audit",
E     Extra items in the left set:
E     '--fix'
E     '--reason'
tests/unit/orchestration/test_w2_149_indep_launch.py:381: in test_documented_lines_name_only_the_sets_root
    assert len(lines) == 10
E   AssertionError: assert 11 == 10
FAILED tests/unit/orchestration/test_w2_149_indep_launch.py::test_help_offers_exactly_the_options_and_no_path_list
FAILED tests/unit/orchestration/test_w2_149_indep_launch.py::test_documented_lines_name_only_the_sets_root
```

## Constraints
- S11 still holds: the docstring keeps exactly one usage line for the fix flow that holds both `--fix` and `--reason`,
  `--kind writer` and `--round 2`, names `--sets-root` with a value (not a folder under the sets root), and holds none of
  `<`, `>`, `$`, `*`, `?`, `[`, `{`, `|`, `;`, `&` or a backquote. The W2-149 case counts the docstring lines that start
  with `python3 ` after stripping, and pins `--help`'s option list (the text before "The documented lines"). Read both
  cases and `tests/acceptance/W2-94/test_w2_94_fix_flow.py`'s S11 case before you change anything.
- The flags keep working exactly as now; only how they are documented and shown changes. The smallest change wins.
- Write only `governance/project/orchestration/tools/indep_launch.py`. No other file.

## Run (every pytest through the slot tool; if it cannot run in your sandbox, run the same pytest without it and say
so; a resource gate's refusal is a wait). Use your sandbox's own `$TMPDIR` for every temporary file.
`env HOME=<an empty folder under your $TMPDIR> PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-94-fix/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest tests/unit/orchestration/test_w2_149_indep_launch.py tests/unit/orchestration/test_w2_173_indep_launch.py tests/unit/orchestration/test_w2_178_indep_launch.py tests/unit/orchestration/test_w2_94_fix_flow_unit.py tests/acceptance/W2-94/test_w2_94_fix_flow.py -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit" --tb=short`
All must pass.

## Walls (hard)
Planted fixtures only. Never open, list, grep or print anything under `/home/usain/gov-os-eval/`,
`/home/usain/gov-os-runs/`, any folder named `hidden` outside a test's `tmp_path`, or any
`fixtures/evaluation/examin/visible` or `hidden` folder. No GPU, model, network or installs; no real `claude` session.
One simple command per Bash call; longer things in a script file under your sandbox's `$TMPDIR`. No merge. No
`gov retrieve` or `gov context`: search with Read and Grep. Refused twice for the same call by the guard, the sandbox
or a hook: stop and say so; never work around a refusal.

## Commit
`git commit -m "W2-94 (DAEO-g87r): <subject>" --trailer "Task: DAEO-g87r" --trailer "Role: engineer" --trailer "Implements: DEC-1180, DEC-1178, DEC-820" --trailer "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>" -- governance/project/orchestration/tools/indep_launch.py`

## Return (your final message, in full)
The twelve labelled fields, each one line or "none": task, status, work_completed, files_changed, evidence (each
suite's pass/fail counts and the commit hash), tests, discoveries, risks, lessons, proposed_decisions, unresolved,
recommended_next_action.
