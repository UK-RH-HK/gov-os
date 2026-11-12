# W2-45 acceptance tests: `gov check` runner semantics and scale (DAEO-neam)

Ticket `DAEO-neam` (W2-45), profile STANDARD, class C2. Written by the independent test designer from the ticket's five
KPI lines and its `## Interface` (DEC-1052, P-W2-45-1 accepted as a whole, DEC-729), before and beside the
implementation. Nothing here reads the ticket's implementation; the base's `src/gov/check/runner.py` was read as it
stands on `w2/integrate`.

## How the tests run

- **Through public interfaces only**: `gov check --json --root <tmp project>` run as a process
  (`python3 -m gov.cli.main`), its API-0002 envelope (a green run: `result`; a red run, exit code 3: `error.details`; both
  forms are read), the check entries by id, their findings by code, `elapsed_s` / `time_limit_s`, the exit code. No
  private name of the runner is imported.
- **How they find the code** (DEC-732): `w2_45_support.py` takes `SRC` from its own location
  (`Path(__file__).resolve().parents[3] / "src"`), the repository the test file sits in, and puts it first on the
  `PYTHONPATH` of every `gov` process. No fixed path, no installed copy. Once merged into
  `/home/usain/gov-os-worktrees/W2-45` the tests exercise that tree's code.
- **Every project is a temporary git repository built from scratch** under `tmp_path` (declared checks as YAML files in
  `template/governance/kernel/checks/`, planted scripts run as `python3 <path>` or a plain shell command, a path map
  with `policies:`). The one file taken from this repository is the real `core-authority.yaml` declaration (S1).
- **Deterministic, no network.** S1 measures wall time and is load-sensitive; its 20,000-commit repository is built with
  `git fast-import` in about a second. The S3 openspec case builds a `PATH` of one folder holding links to `git`,
  `python3`, `sh` and `bash` only, so it does not depend on openspec or gitleaks being installed.
- No test, class or file name holds `real`, `green_here` or `time_limit`.

Run: `PYTHONPATH=<repo>/src python3 -m pytest tests/acceptance/W2-45 -q -p no:cacheprovider` (through the heavy-job slot).

## Map: KPI line, tests, expected red reason on the base

Node ids are relative to `tests/acceptance/W2-45/`. A test marked *(guard)* passes on the base and on the change; it
holds a part of the KPI line that is already true and must stay true.

| KPI id | tests | expected red reason on the base |
|---|---|---|
| S1 (W2-H018): the decision checker runs within the `gov check` budget on 200 decisions and 20,000 commits | `test_s1_decision_checker_scale.py::test_s1_decision_checker_runs_within_the_gov_check_budget_on_200_decisions_and_20000_commits` | core-authority does not end inside the 60 s limit on the planted repository (the whole `gov check` takes about 60.6 s); its entry has no `elapsed_s` / `time_limit_s` (`None, None`) and its finding is `CHECK_FAILED`, not a time. |
| | `test_s1_decision_checker_scale.py::test_s1_the_decision_checker_answered_and_did_not_fail` | the entry's finding is `CHECK_FAILED` ("did not end within its time limit"): the decision checker did not answer. |
| | `test_s1_decision_checker_scale.py::test_s1_the_planted_repository_has_200_decisions_and_20000_commits` *(guard, fixture check)* | none: it passes on the base. |
| S2 (W2-M129, W2-M212): exit 0 with findings or with "unmeasured" is not green | `test_s2_not_green.py::test_s2_exit_zero_with_a_finding_in_the_success_form_is_not_green` | `{"ok": true, "result": {"findings": [..]}}` on exit 0 is read as no finding: GREEN. |
| | `test_s2_not_green.py::test_s2_exit_zero_with_unmeasured_in_a_json_mapping_is_red_with_its_reason` | `{"unmeasured": true, ...}` on exit 0 is read as a finding with no `code` (the mapping itself): no `CHECK_UNMEASURED`. |
| | `test_s2_not_green.py::test_s2_exit_zero_with_unmeasured_in_the_result_of_the_success_form_is_red` | the success form with `unmeasured` in its result is GREEN. |
| | `test_s2_not_green.py::test_s2_exit_zero_with_the_word_unmeasured_in_plain_output_is_red` | non-JSON output with "unmeasured" on exit 0 is GREEN. |
| | `test_s2_not_green.py::test_s2_exit_zero_with_unmeasured_of_a_warning_check_is_yellow_not_green` | no `CHECK_UNMEASURED` finding (the mapping itself is the finding). |
| | `test_s2_not_green.py::test_s2_exit_zero_with_a_finding_is_red_not_green` *(guard)* | none: a JSON list of findings on exit 0 is RED on the base. |
| | `test_s2_not_green.py::test_s2_exit_zero_with_a_finding_of_a_warning_check_is_yellow` *(guard)* | none: passes on the base. |
| | `test_s2_not_green.py::test_s2_clean_check_exiting_zero_is_green_in_every_form` *(guard: success form with empty findings, no output, plain text without "unmeasured")* | none: the clean check is GREEN on the base. |
| | `test_s2_not_green.py::test_s2_a_clean_check_is_green_beside_a_check_that_is_not` | the unmeasured check beside it is GREEN, not RED. |
| S3 (W2-M130, W2-M265): an absent tool of a hard-block check is red, not yellow | `test_s3_absent_tool.py::test_s3_openspec_absent_from_the_path_is_red` | `openspec-validate` with openspec off `PATH` is YELLOW (`OPENSPEC_ABSENT`). |
| | `test_s3_absent_tool.py::test_s3_the_finding_is_tool_absent_and_names_the_first_word_of_the_command` | exit 127 is `CHECK_FAILED` ("exited with code 127"), no `CHECK_TOOL_ABSENT`. |
| | `test_s3_absent_tool.py::test_s3_exit_code_127_is_an_absent_tool_and_red_for_a_hard_block_check` | as above: `CHECK_FAILED`, not `CHECK_TOOL_ABSENT`. |
| | `test_s3_absent_tool.py::test_s3_absent_tool_of_a_warning_check_is_yellow` | the finding is `CHECK_FAILED`, not `CHECK_TOOL_ABSENT` (status YELLOW already). |
| | `test_s3_absent_tool.py::test_s3_absent_tool_of_a_hard_block_check_is_red_never_yellow` *(guard)* | none: a declared hard-block check whose tool is absent is RED on the base (by `CHECK_FAILED`). |
| | `test_s3_absent_tool.py::test_s3_a_tool_that_is_present_is_not_reported_absent` *(guard)* | none: passes on the base. |
| S4 (W2-M211, W2-M259): a hard-block key is covered only by a check of hard-block tier | `test_s4_tier_coverage.py::test_s4_hard_block_key_covered_only_by_a_warning_check_is_refused_naming_the_key` | no `policy-security` result: a warning declaration that `enforces` the key covers it. |
| | `test_s4_tier_coverage.py::test_s4_the_finding_lists_the_covering_checks` | no `policy-security` result. |
| | `test_s4_tier_coverage.py::test_s4_the_same_key_covered_by_a_hard_block_check_is_accepted` *(guard)* | none: passes on the base. |
| | `test_s4_tier_coverage.py::test_s4_one_hard_block_check_among_warning_checks_covers_the_key` *(guard)* | none. |
| | `test_s4_tier_coverage.py::test_s4_a_hard_block_key_nothing_covers_keeps_policy_not_covered` *(guard)* | none: `POLICY_NOT_COVERED` is unchanged. |
| | `test_s4_tier_coverage.py::test_s4_a_warning_key_may_be_covered_by_a_warning_check` *(guard)* | none. |
| S5 (W2-M151): the time limit is stated and tested | `test_s5_timeout.py::test_s5_the_runner_result_states_the_default_limit` | the runner's result has no top-level `time_limit_s`. |
| | `test_s5_timeout.py::test_s5_every_check_result_has_its_time_and_its_limit` | the check entry has no `time_limit_s` (`KeyError`). |
| | `test_s5_timeout.py::test_s5_built_in_checks_carry_their_time_and_their_limit_too` | `openspec-validate` has no `elapsed_s`. |
| | `test_s5_timeout.py::test_s5_a_check_past_its_limit_is_stopped_and_reported_timed_out` | the finding is `CHECK_FAILED` ("did not end within its time limit"), not `CHECK_TIMED_OUT`; no `time_limit_s`. |
| | `test_s5_timeout.py::test_s5_a_grandchild_holding_the_pipe_does_not_keep_the_runner_waiting` | `CHECK_FAILED`, not `CHECK_TIMED_OUT` (and the run may wait for the grandchild's pipe). |
| | `test_s5_timeout.py::test_s5_the_whole_process_group_of_a_timed_out_check_is_stopped` | `CHECK_FAILED`, not `CHECK_TIMED_OUT`. |
| | `test_s5_timeout.py::test_s5_a_timed_out_warning_check_is_yellow` | `CHECK_FAILED`, not `CHECK_TIMED_OUT` (status YELLOW already). |
| | `test_s5_timeout.py::test_s5_a_check_inside_its_limit_is_not_timed_out` | the entry has no `time_limit_s` (`KeyError`). |

## What the Interface leaves open (not tested)

- A JSON mapping with `"unmeasured": false`, or a mapping with neither `findings` nor `ok`, on exit 0.
- An OSError on start (only exit 127 is planted), and the exact message texts.
- The roll-up of `elapsed_s` into families, the value of `elapsed_s` of a not-applicable check, and the budget of any
  check other than core-authority.
- Whether `gov check`'s total time is bounded; only the timed-out cases are bounded, below 10 s.
