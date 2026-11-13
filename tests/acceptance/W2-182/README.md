# W2-182 (DAEO-5y8d): the nightly's drift reds of 2026-11-13, fixed by test revision

Test revision under the owner's DEC-1163 (6), route (a), and (1) for line F; profile LITE, class C1. Run 1 revised the
cases in their own folders (commit `6e3697785` carries `Rewrite-Reason: DEC-1163 (6)`, commit `498968115` carries
`Rewrite-Reason: DEC-1163 (1)`, both with `Task: DAEO-5y8d`); this folder holds no revised case of its own. It maps them,
so that `gov accept W2-182` is judged on the declared revised suites (DEC-892, the form of `tests/acceptance/W2-90/`).

## How the map is run

`gov accept` runs pytest on this folder alone. `conftest.py` (this folder) points that run at the node ids this
README's tables name, each once, in the files they live in: the cases keep their own files, node ids and their own
folders' conftests and fixtures, and nothing else of those folders runs. `w2_182_support.py` reads the README for both
`conftest.py` and the failure-line case. A node id that no file holds is a collection error, which `gov accept` reports
as an error for the whole run, so a mapped case cannot drop out unseen.

## The ticket's KPI lines

Each row maps one KPI line (B is Success 1 ... F is Success 6, in the ticket's order) to the full node ids of its
cases, and gives the planted break the ticket's `Verify` names (the reviewer's check; a run of the map does not plant).

| KPI line | Tests | What the line says | Planted break (the ticket's verify column) |
|---|---|---|---|
| Success 1 (B) | `tests/acceptance/W1-32/test_w1_32_command_set.py::test_the_command_set_is_the_twelve_and_the_three_recorded_ones` | W1-32's recorded command list holds the four approved commands | an unrecorded command name added to `gov --help` in a stand-in makes it fail |
| Success 2 (C) | `tests/acceptance/W1-18/test_w1_18_on_demand_start.py::test_with_the_server_not_answering_a_retrieval_answers_by_keywords_and_starts_nothing`, `tests/acceptance/W2-123/test_w2_123_retry.py::test_after_the_last_failed_try_the_rebuild_states_the_tries_and_waits_and_no_partial_store_is_reported_built` | W1-18's and W2-123's cases expect `REBUILD_FAILED` where the asked-for semantic store is not recreated | W1-18: a retrieval that starts the server; W2-123: a retry record that is not written |
| Success 3 (R) | `tests/acceptance/W2-121/test_s1_lock_off_status.py::test_s1_status_runs_no_pass_and_writes_nothing` | W2-121 S1 takes its second snapshot only after the job's `.exit` file exists | a stand-in `status` that writes a file |
| Success 4 (D) | `tests/acceptance/W2-136/test_w2_136_never_a_gate.py::test_s10_no_module_of_gov_outside_plan_and_launch_imports_or_calls_gov_plan` | W2-136 S10 allows `src/gov/session_watch` to call gov plan | a module outside `plan/`, `launch/` and `session_watch/` calling gov plan |
| Success 5 (E) | `tests/acceptance/W2-23/test_w2_23_space.py::test_s6_every_kernel_hook_exits_alike_with_a_space_in_the_project_dir` | W2-23 S6 expects the seven kernel hooks | a planted eighth hook script with no wiring |
| Success 6 (F) | `tests/acceptance/W2-128/test_w2_128_rows.py::test_row_8_no_unit_carries_the_gov_accept_outside_the_sandbox_until_w2_56_line[role-lead]`, `tests/acceptance/W2-128/test_w2_128_rows.py::test_row_8_no_unit_carries_the_gov_accept_outside_the_sandbox_until_w2_56_line[role-cto]` | W2-128 row 8 records that the `until W2-56` line is gone from both kernel templates | the line planted back into `template/governance/kernel/templates/role-lead.md` (and the role-cto template) |
| Failure 1 | `tests/acceptance/W2-182/test_w2_182_no_lowering.py::test_no_revised_case_is_lowered_skipped_or_marked` | a revised case no longer catching what it guards, or any case lowered, skipped or marked | a skip, xfail, flaky or rerun mark added to a mapped case or to its file |

Failure 1's case is the one this folder holds: it reads the seven mapped functions' source (and each file's module-level
marks) and fails on any skip, skipif, xfail, flaky, rerun or importorskip beyond the baseline of before run 1 (W1-18's
case has always held one `pytest.skip` where `sqlite_vec` cannot be imported, commit `2a2738881`, in the file's
`BASELINE`). Planted, each of an added mark, a second skip and a module-level xfail makes it fail. That each case still fails on a planted break
of what it guards (the planted-break column) is the reviewer's check, as in W2-90; a run does not plant.

## What each case judges, in short

- B: the command list `gov --help` shows is the twelve and the recorded ones, `adapters`, `dispatch`, `session-watch`
  and `wait` (W2-23, W2-121, W2-159, W2-160), and nothing else.
- C: a rebuild whose asked-for semantic store is not recreated fails as `REBUILD_FAILED` (W2-124, DEC-1150 (3)); W1-18's
  case keeps its point (the keyword answer, nothing started), W2-123's case keeps the last failed try's record.
- R: `gov dispatch status` is judged on what it writes, after the fake launched job's `.exit` file exists (a race fixed).
- D: S10's scan allows `src/gov/session_watch` to call gov plan (W2-159 S5); every other module outside `plan/` and
  `launch/` is refused (DEC-1163 (6) D (a)).
- E: the seven kernel hooks, each exiting alike with a space in the project directory.
- F: row 8 of W2-128 records that the `gov accept` ... `until W2-56` line is gone (W2-56 closed; DEC-1163 (1)).

## Known reds

- **Line E (W2-23 S6) is red on a head without the template's hook line.** The seventh kernel hook, `context_watch.py`
  (W2-176), is wired in this repository's `.rulesync/hooks.jsonc` but not yet in `template/.rulesync/hooks.jsonc`; a
  product-spec worker adds that line in the ticket's own tree (the ticket's `template/.rulesync/hooks.jsonc` path). The
  case goes green with it. Until then `gov accept W2-182` fails line E and nothing else.
- Nothing else of the map is known red.

## The run's code

`PYTHONPATH=<tree>/src gov accept W2-182 --root <tree>`; the cases use the tree's own `src` and run through the heavy
slot. The cases that need the real model or the network are not among the mapped ones; none starts an embedder.
