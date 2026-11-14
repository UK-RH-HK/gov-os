# W2-94: make W2-149's S5 option case green again, the engineer's brief (DAEO-g87r)

You are a fresh engineer (class C3) under **W2-94** (`DAEO-g87r`; the ticket is read-only:
`/home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-g87r.md`, KPI lines S11 and S12). Worktree
`/home/usain/gov-os-worktrees/W2-94-fix`, branch `w2/W2-94-fix` (head `46eb8bf11856`). You change **one file only**:
`governance/project/orchestration/tools/indep_launch.py`. You do not change any test, the schemas, any wall or brief file,
or anything else. Under DEC-1180 (4) (standing: "a defect spotted is fixed in the same flow"), this red, which came in
with this ticket's fix flow (landed at 0b43625da), is fixed now.

## The failing output (your input)
`/home/usain/gov-os-worktrees/W2-94-fix/.gov-runtime/scratch/lead/red-w2149.txt` (read it):
```
FAILED tests/acceptance/W2-149/test_w2_149_seed_content.py::test_s5_the_argument_parser_offers_no_path_or_path_list_option
E   AssertionError: options beyond the interface's: ['--fix', '--reason']
```
The case runs `indep_launch.py --help` and collects every option-shaped word in the **whole** output.
(The same file shows a second red, `tests/unit/orchestration/test_w2_149_indep_launch.py::test_counts_schema_closes_every_object_and_string`,
caused by the S13 schema change and outside this ticket's paths: **not yours; leave it red and do not work around it.**)

## Must stay green (run each; the first is your target)
- `tests/acceptance/W2-149/test_w2_149_seed_content.py::test_s5_the_argument_parser_offers_no_path_or_path_list_option` (now red)
- `tests/acceptance/W2-149/` and `tests/acceptance/W2-173/` (whole folders)
- `tests/acceptance/W2-94/` (whole folder; its S11 cases check the docstring's fix-flow usage line)
- `tests/unit/orchestration/test_w2_149_indep_launch.py` (except the one schema case named above),
  `test_w2_173_indep_launch.py`, `test_w2_178_indep_launch.py`, `test_w2_94_fix_flow_unit.py`; among them the W2-149
  unit cases that pin the docstring's documented lines and the `--help` option list.

## Pytest, every run (a resource gate's refusal is a wait, not a refusal)
`env HOME=<an empty folder under your $TMPDIR> PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-94-fix/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest <paths> -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit" --tb=line`
If the slot tool cannot run in your sandbox, run the same pytest without it and say so. Use your sandbox's own `$TMPDIR`
for every temporary file, never a new folder under `.gov-runtime/scratch/`.

## Walls
- Never open, list, grep or print anything under `/home/usain/gov-os-eval/`, `/home/usain/gov-os-runs/`, any folder named
  `hidden` outside a test's `tmp_path`, any `fixtures/evaluation/examin/visible` or `hidden` folder, EXAMIN's real
  repository or the owner's copy. Do not read this ticket's acceptance-test code if your role file forbids it; the
  failing output and the KPI lines are enough.
- No model, network or installs. One simple command per Bash call; longer things in a script file under `$TMPDIR`. No
  merge. No `gov retrieve` or `gov context`: search with Read and Grep, and search again once in different words.
- Refused twice for the same call by the guard, the sandbox or a hook: stop and say so; never work around a refusal.

## Commit
Every trailer in ONE final paragraph (no blank line between them):
`git commit -m "W2-94 (DAEO-g87r): --help names no fix-flow flag (W2-149 S5's option case green again)" --trailer "Task: DAEO-g87r" --trailer "Role: engineer" --trailer "Implements: DEC-1180" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- governance/project/orchestration/tools/indep_launch.py`

## Return (your final message, in full)
The twelve labelled fields, each one line or "none": task, status, work_completed, files_changed, evidence (each suite's
pass/fail counts and the commit hash), tests, discoveries, risks, lessons, proposed_decisions, unresolved,
recommended_next_action.
