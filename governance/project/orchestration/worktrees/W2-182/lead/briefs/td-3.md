# Brief: independent test designer, W2-182 (DAEO-5y8d), run 2: the ticket's own acceptance folder (its README map)

You are a fresh independent test designer (role independent-test-designer), ticket DAEO-5y8d (W2-182), profile LITE,
class C1. Headless: only your last message is read. Run 1 revised eight cases in their own folders (commits 6e3697785
and 498968115, merged 1315039e6); leave those files alone. `gov accept W2-182` refused with ACCEPT_NO_TESTS because the
ticket's declared folder `tests/acceptance/W2-182/` did not exist; the CTO widened the ticket by `tests/acceptance/W2-182/**`
(DEC-1157 (12)) so that folder can map the revised cases (DEC-892: a test-revision ticket is judged on its declared
revised suites; the form of `tests/acceptance/W2-90/`).

## Where you work
| what | path |
|---|---|
| your tree (write here only) | /home/usain/gov-os-worktrees/W2-182-tests |
| branch | w2/W2-182-tests (head 23e7c4971) |
| the ticket (read-only) | /home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-5y8d.md |
| the ticket's context bundle (gov context output) | /home/usain/gov-os-worktrees/W2-182/.gov-runtime/scratch/lead/briefs/td-context-run2.md |
| the decision register (grep by id only) | /home/usain/gov-os-worktrees/W2-182-tests/docs/DECISION_REGISTER.md |
| scratch for scripts and temp folders | your sandbox's own `$TMPDIR` only |

Your allowed paths for this batch (write nothing else): `tests/acceptance/W2-182/**`.

## The task
Write `tests/acceptance/W2-182/README.md` so that `gov accept W2-182` runs exactly the revised cases, each under its KPI line:

| line | the revised case(s) (verify each node id exists on this head; use full node ids, parametrised ids in full) |
|---|---|
| B | `tests/acceptance/W1-32/test_w1_32_command_set.py::test_the_command_set_is_the_twelve_and_the_three_recorded_ones` |
| C | `tests/acceptance/W1-18/test_w1_18_on_demand_start.py::test_with_the_server_not_answering_a_retrieval_answers_by_keywords_and_starts_nothing`; `tests/acceptance/W2-123/test_w2_123_retry.py::test_after_the_last_failed_try_the_rebuild_states_the_tries_and_waits_and_no_partial_store_is_reported_built` |
| R | `tests/acceptance/W2-121/test_s1_lock_off_status.py::test_s1_status_runs_no_pass_and_writes_nothing` |
| D | `tests/acceptance/W2-136/test_w2_136_never_a_gate.py::test_s10_no_module_of_gov_outside_plan_and_launch_imports_or_calls_gov_plan` |
| E | `tests/acceptance/W2-23/test_w2_23_space.py::test_s6_every_kernel_hook_exits_alike_with_a_space_in_the_project_dir` |
| F | `tests/acceptance/W2-128/test_w2_128_rows.py::test_row_8_no_unit_carries_the_gov_accept_outside_the_sandbox_until_w2_56_line[role-lead]` and `[role-cto]` (check the real parametrised ids with `--collect-only -q`) |

Confirm this list against `git diff 2bf4430f4 1315039e6` (the run-1 revisions): every case run 1 changed must be mapped; if a
changed case is not in the table above, add it under its line and say so. Map the failure line (F1: no case lowered,
skipped or marked) the way W2-90's README maps its failure lines.

Read how `gov accept` reads a map before you write it: `src/gov/accept/runner.py` (`parse_map`, the item matching near
lines 139-320, `needed_optins`, `_folder`) and the README of `tests/acceptance/W2-90/` (a map whose items live in other
folders). If `gov accept` collects only inside the declared folder and so needs a collectable module there, add the
smallest one that runs the mapped node ids and nothing else (for example a module that re-collects them by import, as
W2-90 does if it does; read how it does it). Lower nothing; add no skip, xfail, flaky or rerun mark; touch no other folder.

The README also states, briefly: the ticket, profile, that it is a test revision (DEC-1163 (6), route (a); `Rewrite-Reason:
DEC-1163 (6)` / `DEC-1163 (1)` on the run-1 commits), each line's planted break as the ticket's verify column names it, and
the known reds: W2-23 S6 (line E) is red on this head until the template's hooks source wires `context_watch.py` (a
product-spec worker is adding it in parallel in the ticket's own tree; do not touch `template/`).

## Check it runs
Run `gov accept W2-182 --root /home/usain/gov-os-worktrees/W2-182-tests` (with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-182-tests/src`
and the env below). Expected: every mapped case runs, all green except line E's case (red until the template line). Record
the per-line counts. If `gov accept` cannot run in your sandbox (code index, network), say so with its exact refusal and
instead run the mapped node ids directly with pytest; the lead runs `gov accept` outside the sandbox.

## How you run tests
Every pytest through the heavy slot, TMPDIR the sandbox's own `$TMPDIR` (outside the repository and outside ~/gov-os-runs):
```
env PYTHONUSERBASE=/home/usain/.local HOME=/home/usain/gov-os-worktrees/W2-182-tests/.gov-runtime/scratch/empty-home PYTHONPATH=/home/usain/gov-os-worktrees/W2-182-tests/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest <node ids> -q -p no:cacheprovider -o tmp_path_retention_policy=failed
```
Run `gov accept` through the heavy slot too. If another ticket's case turns red, name it with file:line and leave it. A
resource gate's refusal is a wait: wait and retry, it does not count as a refusal.

## Searching and forms
No `gov retrieve` and no `gov context` in the sandbox: Read and Grep; search again once in different words if needed. Never
open the evaluation sets' root, held-out material or any hidden or memory-verdict folder. Write and edit with the Write and
Edit tools and absolute paths; scripts longer than one line go in `$TMPDIR`. Refused twice for the same call: stop and say
so; never work around a refusal. No merge, no push.

## Commit (your paths only)
```
git -C /home/usain/gov-os-worktrees/W2-182-tests commit -m "W2-182: its acceptance folder maps the revised cases (B, C, R, D, E, F)" --trailer "Task: DAEO-5y8d" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-1163, DEC-1156" -- tests/acceptance/W2-182
```
Never `Role: owner` or `Decided-by:`. Before you return: tracked `git status --short` empty; `git diff 23e7c4971 --stat`
names only `tests/acceptance/W2-182/` paths; no added skip/xfail/flaky/rerun.

## Return (your last message; the twelve fields, each a labelled line, "none" where nothing)
task: / status: / work_completed: / files_changed: / evidence: (gov accept's output or its refusal, per-line counts; the node-id check) / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:
Then: commits: <hash12> <subject> | trailers as committed; guard_refusals: none or a line each.
