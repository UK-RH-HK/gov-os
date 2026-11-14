
## Your unit tests
`tests/unit/orchestration/test_w2_94_fix_flow_unit.py`: the argument refusals (17, nothing built); the three staged
inputs and the wall's file list on a `--dry` run; the sample read from the latest delivered round-1 run's archive; a
good delivery replacing only `hidden/<id>.yaml` (sha256 of every other planted set file unchanged; the archive's
`<run>/replaced-hidden/<id>.yaml`); one refusal each at delivery (20) and the stop (21) leaving the set unchanged; the
counts' `fix` key; the variant's front matter (no `sample:`) accepted. Keep it compact.

## Order of work
1. Implement; add the unit tests; run them, and run the three existing launcher suites unchanged (S12):
   `tests/unit/orchestration/test_w2_149_indep_launch.py`, `test_w2_173_indep_launch.py`, `test_w2_178_indep_launch.py`.
2. Commit (your two paths only).
3. Write `/home/usain/gov-os-worktrees/W2-94-fix/.gov-runtime/scratch/lead/en-1.between` with one line `between` when
   you are between batches (after the commit), and check every few minutes for the file
   `/home/usain/gov-os-worktrees/W2-94-fix/.gov-runtime/scratch/lead/TESTS-READY`. Do not wait more than 25 minutes
   for it: if it has not appeared, return with what you have. When it appears (it names the merge commit; it is in your
   branch then; never run git merge yourself), run `tests/acceptance/W2-94/test_w2_94_fix_flow.py` and make it pass by
   changing the script only. If a case cannot pass without going beyond the interface above, or the case and the
   interface disagree, stop and name the case; do not widen the change and do not edit the case.
4. Commit again if you changed anything.

Pytest, every run (if the slot tool cannot run in your sandbox, run the same pytest without it and say so; a resource
gate's refusal is a wait, not a refusal):
`env HOME=<an empty folder under your $TMPDIR> PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-94-fix/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest <files> -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit" --tb=short`
Use your sandbox's own `$TMPDIR` for every temporary file.

## Walls (hard)
- Planted fixtures only. Never open, list, grep or print anything under `/home/usain/gov-os-eval/`,
  `/home/usain/gov-os-runs/`, any folder named `hidden` outside a test's `tmp_path`, or any
  `fixtures/evaluation/examin/visible` or `hidden` folder. You need none of them. No real `claude` session.
- No GPU, model, network or installs. One simple command per Bash call; longer things in a script file under your
  sandbox's `$TMPDIR` (`/tmp` is read-only in the sandbox). No merge. No `gov retrieve` or `gov context`: search with
  Read and Grep, and search again once in different words if the first does not answer.
- Refused twice for the same call by the guard, the sandbox or a hook: stop and say so; never work around a refusal.

## Commit
Your paths only, every trailer in ONE final paragraph (the `--trailer` flags do that):
`git commit -m "W2-94 (DAEO-g87r): <subject>" --trailer "Task: DAEO-g87r" --trailer "Role: engineer" --trailer "Implements: DEC-1180, DEC-1178, DEC-820" --trailer "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>" -- governance/project/orchestration/tools/indep_launch.py tests/unit/orchestration/test_w2_94_fix_flow_unit.py`

## Return (your final message, in full)
The twelve labelled fields, each one line or "none": task, status, work_completed, files_changed, evidence (each
suite's pass/fail counts and the commit hashes), tests, discoveries (any point where the interface and the code or the
variant disagree), risks, lessons, proposed_decisions, unresolved, recommended_next_action.
