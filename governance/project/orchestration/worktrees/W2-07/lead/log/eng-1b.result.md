task: Continue W2-07 (DAEO-r9ss) on the lead's seven points: revise the outdated unit tests, tighten the decision-record rule, re-check the list rows, run every suite on the final code and classify each red, clean and measure scratch.

status: PACKAGES. Every remaining red has kind (i), (ii) or (iii); I found and fixed every kind (iv) red. P-1 (175 W1-30 cases red because their test projects are RED at `gov check`) is still with the orchestrator through you. During the final W1-30 run my scratch went over its share; I cleaned it straight away.

work_completed:
- Point 4: only a commit whose `Task:` is `decision-record` can be measured by its decision (`ac2c5283`). Any other commit that names no task stays unmeasured. Builder test added.
- Point 3: 18 unit tests revised to the new behaviour, in 4 commits of their own, each with a `Rewrite-Reason:` (list under discoveries).
- Point 5: every row re-checked against the code (states under discoveries). Taken here: W2-L196, W2-L197 (part), W2-L208 (`1caaffe9`).
- Point 6: the classification found three kind (iv) reds of mine. All three are fixed in `53ec666a`, with builder tests:
  - The repair ticket's findings fingerprint was 64 hex digits, so a W1-30 case read it as a context hash. It is now `findings-` plus 16 hex digits.
  - The collection was held to the tests' time limit (1 s in a W1-30 case). It now gets at least the default limit (`DEFAULT_TIMEOUT`).
  - A missing pytest showed as a collection error. It now gives `TEST_RUNNER_ABSENT`.
- Point 7: the `ita` folder went away with the previous launch's TMPDIR. My scratch went over its share and was cleaned (evidence).

files_changed:
- `src/gov/close/gates.py`, `src/gov/close/tool.py`, `src/gov/telemetry/counter.py`
- `tests/unit/close/test_decision_records.py` (new), `tests/unit/close/test_collection_gate.py` (new)
- `tests/unit/close/test_every_finding.py`, `test_governance_checks.py`, `test_measured.py`, `test_state.py`
- `tests/unit/telemetry/test_counter.py`
- `command.py` is unchanged in this round. I toggled it twice for diagnostic runs and restored it each time; `git status` is clean.

evidence:
- Commits this round, each with `Task: DAEO-r9ss`, `Role: engineer`, `Implements: DEC-896, DEC-868, DEC-892, DEC-898, DEC-790` (plus `DEC-663` on `1caaffe9`) and `Co-Authored-By: Claude Opus 5.5`:

  | Commit | Content | Rewrite-Reason |
  |---|---|---|
  | `ac2c5283` | decision-record rule | — |
  | `14dc054e` | test_every_finding gate phases | DEC-868 item 3 |
  | `a35b1f93` | repair-ticket KPIs in test_several_gates | KPI 8 (AR-9, W2-L209) |
  | `69d41a01` | governance-check and measured tests | DEC-868 item 3 |
  | `9c005b17` | test_state escalation commit | KPI 8 (AR-9, W2-L209) |
  | `1caaffe9` | telemetry versions | DEC-663 G (W2-L196, W2-L208) |
  | `53ec666a` | three kind (iv) fixes | — |

- The ticket has 12 commits since `e8ad70b5`: src +452/−38, tests +209/−48. The estimate was 220 lines of code, so about 2× over.
- No pre-commit hook (only `pre-commit.sample`). The code under test is this worktree's `src` (`PYTHONPATH` set per command).
- Guard refusals this round: 2, both caused by my own commands and neither retried in the same form. A Grep over `tests/acceptance` was refused (DEC-820 (c)), and a `for` loop over suite paths was refused. Across the whole ticket: 3.
- One write to a target using `$S` was refused as unresolvable; I re-ran it with the literal path.
- `gov retrieve`: not used this round; it returned `FACET_UNAVAILABLE` last round. I used Grep and Read on named files.
- Scratch: 3,718 inodes / 18 MB before the suites. After the final W1-30 run it was **650,660 inodes / 7.0 GB, over my 6 GB / 300,000 share**. The cause is pytest's three retained base folders from the W1-30 runs. I removed `pytest-of-usain` at once; the scratch is now 18 inodes / 1.9 MB. I did not measure the worktree's ignored files.

tests (final code `53ec666a`):

| Suite | Result |
|---|---|
| `tests/acceptance/W2-07` | 40 passed |
| `tests/acceptance/W2-01` | 88 passed |
| `tests/acceptance/W2-53` | 56 passed, 1 failed (ii) |
| `tests/unit/close` + `tests/unit/telemetry` | 463 passed |
| `tests/acceptance/W1-30` | 317 passed, 192 failed, 3 errors: 175 of kind (i), 19 of kind (ii), 1 of kind (iii) |
| `test_w1_30_close.py::test_collection_error_refuses_close` | passes |
| `test_w1_30_no_acceptance_tests.py` (revised) | 6 red, kind (i) |
| `pytest tests --collect-only` | 15,814/15,816 collected, no collection error |

- Diagnostic: W1-30 re-run once with the every-close `gov check` switched off (not committed) gave 25 failed, 487 passed. Every red that turns green with the check off is kind (i). The serial-only cases were not run on their own.

discoveries:
- **Reds, kind (ii): the gates stop before any test and spend no attempt (DEC-868 item 3, P-IS-4 (a)).** 20 node ids:
  - W2-53: `test_w2_53_load_sensitive.py::test_an_entry_the_owner_did_not_add_is_refused_naming_it_and_its_test_is_not_run_again`.
  - W1-30:
    - `test_w1_30_check_blocks.py::test_a_refusal_where_gov_check_blocks_is_counted`
    - `test_w1_30_governance_checks.py::test_a_refusal_for_a_red_check_is_counted`
    - `test_w1_30_close.py::test_regression_runs_to_end_all_failures_collected` (refused on `CHECKPOINT_MISSING` before the regression)
    - `test_w1_30_containment_places.py::test_an_engineer_commit_of_a_kernel_file_under_template_refuses` and `::test_an_engineer_commit_under_the_projects_governance_folder_refuses` (the pre-close `gov check` refuses before containment)
    - `test_w1_30_iteration.py::test_mixed_causes_reach_escalation`
    - `test_w1_30_r13_refused_runs.py::test_a_close_refused_for_a_failing_test_states_each_run`, `::test_a_close_refused_with_every_test_green_states_each_run_as_a_passed_close_does[a commit without Implements]` and `[no probe record]`
    - `test_w1_30_r9_every_finding.py` (8): `test_a_measured_part_is_not_said_as_not_measured`, `test_an_early_finding_does_not_hide_the_failing_acceptance_test[no-implements]` and `[no-probe-record]`, `test_one_refusal_names_every_finding_of_the_ticket`, `test_the_refusal_for_several_findings_is_counted_once`, `test_the_refusal_for_several_findings_opens_one_repair_ticket_that_lists_them_all`, `test_without_acceptance_tests_the_acceptance_run_is_said_as_not_measured`, `test_without_acceptance_tests_the_governance_checks_are_still_reported`
    - `test_w1_30_repair_ticket.py::test_the_answer_names_the_absent_ticket_tool_beside_the_finding` and `::test_the_answer_names_the_failing_ticket_tool_beside_the_finding` (the test project's RED check, run because its commits change governance files, now refuses before the failing test)
- **Reds, kind (iii): the repair ticket is committed (KPI 8):** `test_w1_30_r8_tree.py::test_a_second_close_with_the_refusals_repair_ticket_left_untracked_is_measured`. It expects the repair ticket left untracked.
- **Reds, kind (i): the test project is RED at `gov check` (P-1).** 175 node ids, all in W1-30 and grouped by file in the payload below. They include the 6 cases of the revised `test_w1_30_no_acceptance_tests.py` and the 3 setup errors in `test_w1_30_r13_long_findings.py`.
- **Unit tests revised (point 3):**
  - `test_every_finding.py::test_an_early_finding_does_not_end_the_run[*]`: before, every gate was asked and the refusal counted; after, every gate of the phase is asked, and a commit-gate finding stops the run before any test, uncounted.
  - `::test_a_finding_of_every_gate_is_in_the_one_refusal`: before, one counted refusal held every gate's finding; after, one refusal per phase (commit, pre-close, tests), and only the tests phase is counted.
  - `::test_could_not_measure_ends_the_run_at_once_uncounted_whatever_was_found_before[*]`: before, earlier findings were taken from every earlier gate; after, from earlier gates of the same phase. Its expectations are unchanged.
  - `::test_a_full_ticket_has_its_probe_gate_asked_first_and_its_finding_beside_the_others`: before, `PROBE_MISSING` sat beside a test finding and was counted; after, it sits beside the trailer finding, before any test, uncounted.
  - `::test_several_gates_are_one_refusal_counted_once_with_one_repair_ticket_that_lists_them_all`: before, "FAILED test_x" appeared once in the whole ticket; after, once in the findings and once in the KPIs.
  - `test_governance_checks.py`: the two "refuses counted" tests are renamed `…refuses_before_any_test_uncounted…` and now hold no test run and no count. `test_a_red_check_and_a_failing_test_are_one_refusal` is renamed `test_a_red_check_refuses_before_the_failing_test_is_run`: the check's finding alone, no run.
  - `test_measured.py::test_a_finding_and_could_not_measure_are_two_ways_out`: before, `CHECK_FAILED` with 4 parts, counted; after, `TRAILER_MISSING` alone, uncounted, with a repair ticket.
  - `test_state.py::test_the_third_refusal_records_where_the_escalation_began`: before, `escalated_at` was HEAD from before the refusals; after, it is the commit of the repair ticket, which holds only that ticket and whose parent is that earlier HEAD.
  - `test_counter.py::test_the_record_names_one_version_only_when_every_named_log_carries_that_one`: before, `agent` equalled exactly `{harness, version}`; after, the same harness and version, plus `version_reason` and each session's versions.
- **Rows:**
  - Fixed by this ticket:

    | Row | Commit |
    |---|---|
    | W2-H038, W2-M249 | `f00e9d39` (gate refusals uncounted) |
    | W2-H045 | `f00e9d39` |
    | W2-L209, W2-L236 | `f00e9d39` (complete, committed repair tickets) |
    | W2-M158, W2-M371 | `f00e9d39` |
    | W2-M252 | `f00e9d39`, `53ec666a` |
    | W2-M403 | `f00e9d39` |
    | W2-M166 | `f00e9d39`; the W2-07 share case passes |
    | W2-M263 | `f00e9d39`: "nothing is judged" is now a commit-gate refusal before any test, uncounted. The check itself is in `src/gov/check`, outside my paths |
    | W2-L196, W2-L208 | `1caaffe9` |
    | W2-L197, version never null | `1caaffe9` |

  - Already fixed:

    | Row | Fixed by |
    |---|---|
    | W2-L107 | `7439c6d0` / `b59d7244` (disposition and `context_hash` on the repair ticket) |
    | W2-L165 | `ec8630e2` (cut by bytes; `repair_ticket_findings_cut` set) |
    | W2-M157 | `ec8630e2` (installed kernel skills listed) |
    | W2-L124 | `e41e1df4` (larger readings counted in `counting_notes`) |
    | W2-L123 | `35904984` (the sub-agent gap named in every record; MCP 0 by DEC-507). Whether the sub-agent gap is acceptable is still a ruling to make |

  - Not taken:

    | Row | Reason |
    |---|---|
    | W2-L197 (close record carries the version) | it would change the close record's lines, which W2-66 owns |
    | W2-L108 | `tk` has no option for these fields, and `tk` is outside my paths |
    | W2-L210 | more than a small change (a record per close, the path map's escalation folder, resolving `Implements:` ids) |
    | W2-M149 | the row wants a runner error counted, against the later DEC-487/DEC-490 (could-not-measure is uncounted); not changed |
    | W2-M178 | needs instruction files as they stood at session start; more than small |
    | W2-M248 | DEC-663 H keeps the standing rule; research row |
    | W2-M276 | `src/gov/readiness`, outside my paths |
    | W2-M286 | not verified for `tk close` under an owner decision |
    | W2-M348, W2-M349 | research rows |
    | W2-M354 | orchestrator's / dev-tier row |

- Later decision over earlier one: DEC-868 item 3 replaces DEC-492's single counted refusal for the gates before the tests. DEC-487 overrides W2-M149's DEC-466 expectation.

risks:
- The collection limit is now at least `DEFAULT_TIMEOUT` (120 s), whatever `--timeout` says.
- A refused close commits, so the next close needs a rebuild first (P-2).
- The full W1-30 suite overflows a 6 GB scratch share under pytest's default retention of three base folders.

lessons:
- The guard refuses suite paths given through a shell loop variable; name each suite literally.
- A diagnostic run with the every-close `gov check` off is the quickest way to separate kind (i) reds from the rest.
- Remove `pytest-of-*` between W1-30 runs.

proposed_decisions:
- P-1 (from the previous return; you have it) is unchanged. Once the test projects' check set is green, the 175 kind (i) cases need a re-run. Confidence: medium-high.
- P-4: the 20 kind (ii) cases and the 1 kind (iii) case are W1-30/W2-53 acceptance cases. They need test-designer revisions with `Rewrite-Reason: DEC-868 item 3`, or `KPI 8` for `r8_tree`. Recommend: hand them to the test designer together with P-1. Confidence: high.

unresolved:
- P-1 and P-4.
- W2-L197's close-record part, W2-L108, W2-L210, W2-M149, W2-M178, W2-M276 and W2-M286, as listed under discoveries.
- The serial-only cases were not run separately.
- The worktree's ignored files were not measured.

recommended_next_action: Send P-1 and P-4 together to the test designer, then re-run W1-30 on `53ec666a`.

Payload: the 175 kind (i) reds, by file in `tests/acceptance/W1-30/`
```
ERROR test_w1_30_r13_long_findings.py :: test_a_refused_close_with_very_long_findings_opens_its_repair_ticket_through_the_ticket_tool; test_the_answer_names_every_finding_or_says_how_many_it_left_out; test_what_the_repair_ticket_does_not_hold_of_the_findings_is_said_in_it_and_in_the_answer
test_w1_30_close.py :: test_checkpoint_exists_before_ticket_status_changes; test_close_record_empty_skill_versions_when_none; test_close_record_exists_before_ticket_status_changes; test_close_record_has_kernel_skill_versions; test_close_record_lists_test_counts; test_close_record_lists_vendor_skill_without_version; test_close_record_unwritable_ticket_stays_open; test_close_runs_acceptance_tests; test_close_runs_containment_check; test_close_runs_regression_tests_when_present; test_close_sets_ticket_status; test_close_succeeds_on_green_standard_ticket; test_close_writes_checkpoint_on_success; test_containment_clean_within_paths; test_ticket_closed_through_ticket_tool_interface; test_ticket_commits_from_head_only; test_time_limit_is_configurable
test_w1_30_commit_models.py :: test_a_commit_with_a_co_author_line_beside_one_without_keeps_its_model; test_a_commit_without_a_co_author_line_is_listed_as_not_measured; test_commits_of_two_roles_are_listed_with_their_roles_and_models; test_no_commit_of_the_ticket_is_left_out_and_no_other_is_listed
test_w1_30_containment_places.py :: test_a_clean_ticket_has_no_finding_and_closes; test_an_engineer_commit_inside_another_tickets_paths_refuses; test_an_engineer_commit_of_a_file_at_the_projects_root_refuses; test_an_engineer_commit_of_a_test_outside_its_acceptance_folder_and_paths_refuses; test_an_engineer_commit_of_another_tickets_file_refuses
test_w1_30_context_failures.py :: test_a_decision_checker_that_cannot_run_refuses_the_close; test_a_missing_depends_on_id_refuses_the_close; test_a_missing_mandatory_input_refuses_the_close; test_a_project_without_a_record_store_refuses_the_close; test_a_refusal_for_no_record_store_is_counted; test_a_source_superseded_by_several_records_refuses_the_close; test_a_superseded_source_refuses_the_close; test_the_answer_of_a_failing_close_with_a_class_says_the_context_failed; test_the_same_project_closes_once_it_has_a_record_store; test_two_contradicting_sources_refuse_the_close
test_w1_30_disposition.py :: test_valid_disposition_builds_context_first
test_w1_30_governance_checks.py :: test_a_ticket_that_changes_no_governance_file_needs_no_check_result; test_the_close_record_of_a_ticket_that_changes_no_governance_file_claims_no_check_result
test_w1_30_iteration.py :: test_containment_refusal_counts_as_iteration; test_different_failures_still_increment_count; test_escalation_after_three_non_converging; test_escalation_already_in_force_not_counted; test_escalation_includes_reason_not_converging; test_escalation_package_has_six_options; test_escalation_package_lists_outcomes; test_fourth_attempt_runs_nothing; test_fourth_non_converging_blocked_without_owner; test_iteration_file_under_gov_runtime; test_owner_decision_id_recorded_in_count
test_w1_30_no_acceptance_tests.py :: test_a_refusal_for_no_acceptance_tests_is_counted[folder-without-a-test]; [no-folder]; test_a_refusal_for_no_acceptance_tests_opens_a_dependent_repair_ticket[folder-without-a-test]; [no-folder]; test_a_ticket_without_acceptance_tests_is_refused_and_nothing_is_closed[folder-without-a-test]; [no-folder]
test_w1_30_probe.py :: test_full_ticket_closes_with_valid_probe; test_standard_profile_closes_without_probe
test_w1_30_r10_interpreter.py :: test_the_switch_that_removes_assertions_does_not_reach_the_test_runs[1]; [2]
test_w1_30_r10_probe_records.py :: test_one_passing_probe_record_alone_closes[under the first name]; [under the second name]
test_w1_30_r10_skips.py :: test_a_close_without_skipped_tests_says_zero; test_skipped_acceptance_tests_are_counted_and_refuse_nothing; test_skipped_regression_tests_are_counted_and_refuse_nothing
test_w1_30_r10_task_names_no_ticket.py :: test_a_commit_whose_task_names_no_ticket_and_that_changes_nobodys_work_refuses_nothing
test_w1_30_r11_parallel_runs.py :: test_a_declared_case_over_the_time_limit_is_a_finding; test_a_declared_case_runs_alone_after_the_parallel_run_and_exactly_once[a case of another suite]; [a unit test file]; [an acceptance case of the ticket]; test_a_failing_case_of_the_parallel_run_is_named_as_before; test_a_failing_declared_case_is_a_finding_like_any_other[a case of another suite]; [an acceptance case of the ticket]; test_an_entry_names_a_whole_file_or_every_parameter_set_of_a_function; test_the_acceptance_run_and_the_regression_run_are_parallel; test_the_close_record_and_the_output_say_which_cases_ran_in_which_form_and_how_long; test_without_declared_cases_no_run_afterwards_is_stated; test_without_the_parallel_runner_the_ticket_closes_serially_and_says_so
test_w1_30_r11_rebuild_mode.py :: test_a_ticket_closes_on_a_store_rebuilt_without_embeddings
test_w1_30_r12_worker_setting.py :: test_a_list_entry_that_names_no_case_refuses_the_close_with_a_finding[a file that does not exist]; [a function that does not exist]; test_each_parallel_run_states_its_number_of_workers[a number]; [a path map without the setting]; [auto, written]; [no path map]; test_the_argument_wins_over_the_time_limit_a_project_writes; test_the_number_a_project_writes_is_the_number_of_workers_of_each_parallel_run[1]; [3]; test_the_setting_never_changes_the_findings; test_the_setting_never_changes_which_tests_run; test_the_time_limit_a_project_writes_is_the_limit_of_a_close_without_the_argument; test_without_the_parallel_runner_a_number_of_workers_is_accepted_and_changes_nothing
test_w1_30_r13_governance_share.py :: test_a_counter_that_cannot_measure_does_not_refuse_the_close[a named session has no log]; [ccusage is not on PATH]; test_a_part_the_counter_did_not_measure_says_so_beside_the_part_it_measured; test_no_text_of_a_session_is_in_the_record_or_in_what_the_close_prints[a close that passes]; test_the_close_record_states_the_share_of_the_sessions_the_caller_names; test_without_a_session_named_the_share_is_not_measured_and_the_ticket_closes
test_w1_30_r13_installed_skills.py :: test_a_project_with_both_layouts_lists_the_skills_of_both; test_a_skill_that_both_layouts_hold_with_one_version_is_listed_once; test_a_skill_whose_two_layouts_state_different_versions_is_listed_with_each; test_a_vendored_skill_of_an_installed_kernel_is_listed_without_a_version; test_an_installed_skill_whose_frontmatter_cannot_be_read_is_listed_as_not_measured; test_the_skills_of_an_installed_kernel_are_listed_with_their_versions
test_w1_30_r13_owner_decision_register.py :: test_a_decision_file_lifts_the_escalation_of_a_project_that_names_a_register; test_an_accepted_entry_the_owner_recorded_after_the_escalation_lifts_it; test_an_entry_of_a_file_the_path_map_does_not_name_lifts_nothing; test_an_entry_recorded_before_the_escalation_began_lifts_none; test_an_entry_that_is_not_one_accepted_entry_of_the_owner_lifts_nothing; test_an_entry_that_lifted_one_escalation_lifts_no_second; test_with_no_register_named_an_entry_lifts_nothing
test_w1_30_r13_probe_findings.py :: test_a_byte_in_the_list_that_is_not_utf8_is_a_finding_that_names_the_list[in a comment]; [in an entry]; test_a_list_entry_that_names_a_file_without_a_case_refuses_the_close[a helper module]; [a test file without a test function]; test_a_project_file_named_like_the_closes_plugin_keeps_no_failing_case_out[at the project's root]; [under src/]; test_a_run_of_the_declared_cases_with_exit_code_0_and_no_result_refuses[a failing declared case follows it]; [the only declared case]; test_after_a_run_cut_at_the_time_limit_no_process_of_it_lives_or_writes_into_the_project
test_w1_30_r13_probe_merge.py :: test_a_commit_of_the_ticket_after_the_merge_outside_its_code_does_not_refuse; test_a_merge_that_brings_exactly_the_probed_code_does_not_refuse[main stayed]; [main went on]; test_the_orchestrators_notes_after_the_merge_that_name_no_ticket_do_not_refuse
test_w1_30_r14_probe_later_commits.py :: test_a_commit_of_the_ticket_after_the_probed_one_outside_its_work_does_not_refuse[a checkpoint record]; [a register entry]; [the orchestrator's notes]; test_a_commit_of_the_ticket_in_another_acceptance_folder_does_not_refuse; test_a_merge_after_the_probed_commit_that_brings_only_files_outside_the_tickets_work_does_not_refuse; test_several_commits_of_the_ticket_after_the_probed_one_outside_its_work_do_not_refuse; test_the_merge_of_the_probed_commit_with_a_file_outside_the_tickets_work_added_in_it_does_not_refuse; test_the_probe_record_in_a_commit_that_names_the_ticket_does_not_refuse
test_w1_30_r8_commits.py :: test_a_commit_that_names_another_ticket_refuses_nothing; test_a_commit_without_trailers_that_changes_only_a_folder_that_is_none_of_the_tickets_refuses_nothing[a folder of notes]; [a source folder outside the ticket's paths]
test_w1_30_r8_escalation.py :: test_a_decision_recorded_before_the_escalation_began_lifts_none; test_a_decision_that_lifted_one_escalation_lifts_no_second; test_a_file_no_commit_holds_lifts_no_escalation; test_a_path_to_a_file_outside_the_project_lifts_no_escalation; test_a_refusal_leaves_the_counter_and_the_escalation_whole_and_nothing_beside_them; test_an_escalation_in_force_whose_counter_is_missing_blocks_and_says_so; test_the_tickets_own_checkpoint_lifts_no_escalation
test_w1_30_r8_last_step.py :: test_a_close_record_that_cannot_be_written_leaves_nothing_that_says_the_ticket_closed
test_w1_30_r8_probe_record.py :: test_a_judgement_of_pass_or_passed_is_accepted[pass]; [passed]
test_w1_30_r8_test_runs.py :: test_a_ticket_whose_only_acceptance_test_is_skipped_refuses; test_options_in_the_callers_environment_do_not_reach_the_test_runs[collect only]; [deselect the failing test]
test_w1_30_r8_tree.py :: test_a_file_git_ignores_refuses_nothing
test_w1_30_r9_every_finding.py :: test_an_early_finding_does_not_hide_the_failing_acceptance_test[containment]
test_w1_30_r9_ticket_tool.py :: test_a_clean_ticket_closes_where_the_ticket_tool_is_on_path_only; test_a_refused_close_opens_its_repair_ticket_where_the_ticket_tool_is_on_path_only; test_the_kernels_ticket_tool_is_used_where_path_holds_another
test_w1_30_receipt.py :: test_close_record_has_decisions_applied; test_close_record_has_input_ids_and_hashes; test_close_record_has_outputs; test_close_record_has_packet_hash; test_close_record_has_requirements_implemented; test_close_record_has_tests_and_deviations; test_close_record_packet_hash_matches_context; test_deviations_says_not_measured_when_unverified; test_input_hash_is_of_file_content; test_outputs_lists_files_from_ticket_commits; test_sources_resolve_through_defined_lookup; test_tests_produced_lists_ticket_own_tests; test_ticket_file_is_always_an_input; test_unmeasurable_inputs_listed_with_reason
test_w1_30_time_limit.py :: test_a_close_over_its_time_limit_is_counted; test_a_close_over_its_time_limit_opens_a_dependent_repair_ticket; test_after_three_closes_over_their_time_limit_the_next_is_blocked; test_the_third_close_over_its_time_limit_writes_the_escalation
test_w1_30_watchdog.py :: test_closing_checkpoint_written_after_checks_pass
```