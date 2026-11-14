# W2-94 S13: make the failing counts-schema cases pass, the engineer's brief (DAEO-g87r)

You are a fresh engineer (class C3) under **W2-94** (`DAEO-g87r`; the ticket is read-only:
`/home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-g87r.md`, KPI line S13). Worktree
`/home/usain/gov-os-worktrees/W2-94-fix`, branch `w2/W2-94-fix` (head `382924bd3d91`). You change **one file only**:
`governance/project/orchestration/tools/indep-schemas/indep-counts.schema.json`. You do not change the launch script, any
test, any wall or brief file, or anything else.

## The failing output (your input)
The independent test designer's acceptance cases, merged at `382924bd3d91`:
`tests/acceptance/W2-94/test_w2_94_s13_counts_fix.py`: **36 failed, 3 passed**. The full output is
`/home/usain/gov-os-worktrees/W2-94-fix/.gov-runtime/scratch/lead/red-s13.txt` (read it). The failing ids:

```
test_s13_a_delivered_fix_runs_counts_validate[corrected|replaced]                 the counts schema refuses the fix key
test_s13_a_dry_fix_runs_counts_validate_with_the_action_null                      the counts schema refuses the fix key
test_s13_a_fix_run_refused_at_the_result_or_stopped_validates_with_the_action_null[refused 20 at the result|stopped 21]
test_s13_each_code_each_edge_id_and_each_action_validate[<each of the 8 codes>]   refused with code X: [('q00','corrected'), ('q00','replaced'), ('q00', None), ('q02', ...), ('q99', ...)]
test_s13_a_delivered_fix_runs_log_has_no_counts_schema_failure                    assert ['2026-11-14T...counts schema failed'] == []
test_s13_counts_only_of_a_delivered_fix_run_exits_0_and_prints_its_counts_with_fix  (17, ..., 'indep_launch: refused 17 ...')
test_s13_a_fix_object_of_another_form_is_refused[an extra key | an extra key reason | id missing | code missing |
  action missing | action another word | action Corrected | action empty | action a list | id q2 | id Q02 | id q002 |
  id q0a | id null | code unknown | code lower case | code null | fix null | fix a list | fix a string | fix empty]
                                                                                  each fails at its control: the counts schema refuses the fix key
```
Read the test file for what each case plants; the KPI line S13 in the ticket states the rule.

## Must stay green
The whole `tests/acceptance/W2-94/` folder; and unchanged: `tests/unit/orchestration/test_w2_149_indep_launch.py`,
`test_w2_173_indep_launch.py`, `test_w2_178_indep_launch.py`, `tests/unit/orchestration/test_w2_94_fix_flow_unit.py`,
and the acceptance folders `tests/acceptance/W2-149/` and `tests/acceptance/W2-173/` (they check the schema's form:
every object closed, every string a const, an enum or an anchored pattern).

## Pytest, every run (a resource gate's refusal is a wait, not a refusal)
`env HOME=<an empty folder under your $TMPDIR> PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-94-fix/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest <paths> -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit" --tb=line`
If the slot tool cannot run in your sandbox, run the same pytest without it and say so. Use your sandbox's own
`$TMPDIR` for every temporary file, never a new folder under `.gov-runtime/scratch/`.

## Walls
- Never open, list, grep or print anything under `/home/usain/gov-os-eval/`, `/home/usain/gov-os-runs/`, any folder named
  `hidden` outside a test's `tmp_path`, any `fixtures/evaluation/examin/visible` or `hidden` folder, EXAMIN's real
  repository or the owner's copy.
- No model, network or installs. One simple command per Bash call; longer things in a script file under `$TMPDIR`. No
  merge. No `gov retrieve` or `gov context`: search with Read and Grep, and search again once in different words if the
  first does not answer.
- Refused twice for the same call by the guard, the sandbox or a hook: stop and say so; never work around a refusal.

## Commit
Every trailer in ONE final paragraph (no blank line between them):
`git commit -m "W2-94 (DAEO-g87r): the counts schema takes the fix flow's optional fix object (S13)" --trailer "Task: DAEO-g87r" --trailer "Role: engineer" --trailer "Implements: DEC-1180" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- governance/project/orchestration/tools/indep-schemas/indep-counts.schema.json`

## Return (your final message, in full)
The twelve labelled fields, each one line or "none": task, status, work_completed, files_changed, evidence (each suite's
pass/fail counts and the commit hash), tests, discoveries, risks, lessons, proposed_decisions, unresolved,
recommended_next_action.
