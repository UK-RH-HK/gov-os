# Nightly 20261113-0404: analysis of `verdict: red 99`

Analysis helper, read-only, 2026-11-13 06:35-07:05 UTC. Head of the run: `cb208f9434d7` (W2-113's close). Last night's run (20261112-0404, head `9bbef27f1d05`) had 13 parallel reds and 2 serial reds.

## What the 99 are

- The parallel phase had 102 failures: 100 failed and 2 errors. 3 passed when run alone. That leaves **99 red alone**.
- The serial phase had 2 failures: W1-19 and W2-13 latency, both `accepted-red`. Last night they were the same 2. They are old and not counted.
- **None of the 99 was red last night.** Last night's 13 parallel reds (the W2-56, W2-96 and W2-170 signal and file-access cases) all passed tonight.
- Evidence method: worktrees of the run's commit and of the merges either side of each suspect, in scratch, with `TMPDIR` in scratch. Every run went through `heavy_slot.sh`. PYTHONPATH was the worktree's `src`, absolute: a relative path breaks W2-123's child process (`ModuleNotFoundError: gov`).
- **One rerun separated the causes.** All 102 cases at `cb208f9` with Node 22's `openspec` on PATH: **97 passed and 5 failed**. Those 5 are the groups B to E below.

## Table

| Group | Count | New/old | Alone? | Cause | Evidence | Owner | Fix |
|---|---|---|---|---|---|---|---|
| **A. openspec absent → hard-block RED** (W2-66 ×66, W2-115 ×14, W1-30 ×6, W1-26 ×2, W2-02 ×2 errors, W2-77 ×2, W2-57 ×1, W1-36 ×1) | 94 | new | red alone | **The nightly's PATH has no openspec, and W2-45 made that RED.** Before W2-45, `_check_openspec` answered YELLOW when openspec was missing. W2-45 changed it to RED (`3ed6f5311`, merge `c87a2d495`, 11-12 21:42). That follows DEC-781 / W2-M265: an unmeasured hard-block check is never YELLOW. Each fixture's `gov close` or `gov check` now refuses with `CHECK_FAILED: openspec-validate RED: OPENSPEC_ABSENT "openspec is not on PATH"`. That one finding explains 85 of the failure blocks in `parallel.txt`; the rest are knock-on errors such as "no close record" or "batch wrote no run record". The nightly's PATH (`nightly_cron.sh:21`, `nightly_restart.sh:37`) names Node **18**. The merge queue (`merge_queue.py:53`), `lead_verify.sh:18` and `close_build.py:61` name Node **22**, where openspec lives, so their closes stayed green. | 4 sample cases (W2-66, W1-30, W2-02, W1-26) pass at `c87a2d495^1` and fail at `c87a2d495`, with the same environment. W2-66 limits: red at `c87a2d495` without openspec, green with Node 22 on PATH. 19 cases (W2-66 ×2, W1-30, all 14 of W2-115, W2-02, W1-26) are red at `cb208f9` without openspec and **19 passed** with it. All 102: 97 green with openspec on PATH. W2-154 is cleared: W2-66 full_widening is red at `dbb0891e8^1` without openspec and green at `dbb0891e8` with it. Node 18 crashes openspec (`SyntaxError: Invalid regular expression flags`, exit 1, which would read OPENSPEC_FAILED, still RED). Node 22 answers "Nothing to validate" (YELLOW). | The nightly wrapper, a CTO tool on a control path, so the change goes by ACT (ACT-NIGHTLY-RESTART-1 / the cron file). W2-45's change is decided and is not at fault. | **Smallest:** in `nightly_cron.sh` and `nightly_restart.sh`, change the PATH line's `node/v18.20.8/bin` to `node/v22.23.3/bin`, the same prefix as `merge_queue.py`. Do not append v22 after v18: openspec would then run on Node 18 and crash. **Durable, optional:** route a test revision (DEC-1156 (7)) so the shared close fixtures plant a stub `openspec`, and the cases stop depending on the machine. |
| **B. Unrecorded gov commands** (W1-32 `test_the_command_set_is_the_twelve_and_the_three_recorded_ones`) | 1 | new | red alone | **Four approved commands appear in `gov --help` but not in W1-07's `RECORDED_GOV_COMMANDS`.** In landing order: `dispatch` (W2-121, merge `787b097ac`, 11-12 07:46, the first to turn it red), `adapters` (W2-23, `b5a0394e3`), `session-watch` (W2-159, `4f4592021`), `wait` (W2-160, `c1f4341dc`). Each ticket recorded its command in `src/gov/check/commands.py`, not in the test's list. | Failure text: `gov has commands the command list does not record: ['adapters', 'dispatch', 'session-watch', 'wait']`. The test passes at `787b097ac^1` and fails at `787b097ac`. `gov --help` across the merges gains, in turn: none at `9bbef27` → dispatch → +adapters → +session-watch → +wait. | CTO-routed test revision (DEC-1156 (7); the same form as D-10's brief/links/plan revision, DEC-753/DEC-1109). | One test designer adds `"adapters", "dispatch", "session-watch", "wait"` to `tests/acceptance/W1-07/w1_07_support.py` `RECORDED_GOV_COMMANDS` (one DEC-542 line each, citing each ticket's approval). They also add the four to the set pinned in W1-32's first assert, at line 84. |
| **C. Rebuild now fails when the semantic store is not recreated** (W1-18 `test_with_the_server_not_answering_…`, W2-123 `test_after_the_last_failed_try_…`) | 2 | new | red alone | **W2-124 changed what a rebuild answers.** "a rebuild without its asked-for semantic store fails named" (`799b2b65f`, merge `a2f28ccf3`, 11-12 20:23) means `gov rebuild` now answers `ok:false REBUILD_FAILED` where it used to answer ok with FTS only. DEC-1150 (3) (P1-L (a)) widened W2-124 to revise 13 files of older cases. These two cases were not among them. | W1-18 and W2-123 both pass at `a2f28ccf3^1` and fail at `a2f28ccf3`. W1-18's failure: `assert None == 'recreated'` on `REBUILD_FAILED … EMBEDDER_UNAVAILABLE`. W2-123's: `envelope ok False`. Its error already states "timed out at all 3 tries … waits 0.25 s, 0.75 s". | W2-124's widening missed them. The CTO routes the test revision (DEC-1156 (7), Rewrite-Reason DEC-1027 C as in DEC-1150 (3)). | Revise the two cases so each keeps its point. W1-18: assert REBUILD_FAILED naming the semantic store and starting nothing, and check the keyword index from the result's details or a `--store lexical` rebuild. W2-123: assert REBUILD_FAILED with the tries and waits in its message, and keep the "no partial store reported built" search check. |
| **D. session_watch calls `gov plan`** (W2-136 `test_s10_no_module_of_gov_outside_plan_and_launch_imports_or_calls_gov_plan`) | 1 | new | red alone | **W2-159 calls `gov plan`, which W2-136's S10 scan forbids outside plan and launch.** `src/gov/session_watch/items.py` runs `gov plan --root … --ready` (line 86) for its open items. This is required by W2-159's own KPI S5 ("the default is the dispatcher's ready list (W2-121, `gov plan --ready`)"). W2-136's S10 case scans every `src/gov` module outside plan/ and launch/. Landed `4f4592021` (11-12 18:46). | The test passes at `4f4592021^1` and fails at `4f4592021`. Failure text: `{'src/gov/session_watch/items.py': ["'gov plan wrote no ready list…'", …]}`. | **A contradiction between two tickets' KPIs** (W2-136 S10 vs W2-159 S5). The CTO decides under the delegated rules, or it goes as a package (DEC-105: apply, defer or re-baseline). | **Smallest, if stop-check's use is advisory and not a gate:** a test revision adding `src/gov/session_watch` to S10's allowed folders, citing W2-159 S5. S10's own KPI text names close, landing, claim, readiness and hook modules, which is narrower than the case's scan of all of gov. **If it is a gate:** W2-159 reads the ready list through a configured file instead. |
| **E. A 7th kernel hook not in the template's hooks source** (W2-23 `test_s6_every_kernel_hook_exits_alike_with_a_space_in_the_project_dir`) | 1 | new | red alone | **W2-176 added `context_watch.py` to `template/governance/kernel/hooks/` (`13fd1dd34`, hand merge `3430341c4`, 11-12 15:09).** ACT-CONTEXT-WATCH-1 (`f21df9875`) wired it only into the root `.rulesync/hooks.jsonc` and `.claude/settings.json`. It never reached `template/.rulesync/hooks.jsonc`, which the case reads, and the case also pins `len(scripts) == 6`. | The test passes at `3430341c4^1` and fails at `3430341c4`. Failure text: `the settings' hook command lines do not reach the six kernel hooks: ['context_watch.py']`. | W2-176 / ACT-CONTEXT-WATCH-1 follow-up for the template, plus a CTO-routed test revision. | **(1)** Decide whether adopted projects ship the hook. If yes, add its PostToolUse (Bash) entry to `template/.rulesync/hooks.jsonc` (template, so by ACT/CIT-P as the class rules say). **(2)** Test revision: change W2-23 S6's "six" to seven, or derive the count from the template folder. (2) is needed either way. |
| **L. Timing under load** (W2-112 `test_a_request_past_its_time_limit_does_not_hold_the_search`, W2-145 S4 `[no-connection-within-connect-s]`) | 2 | new (old tests, green last night) | **passes alone**: not in the 99 | **Environment: the nightly ran beside the leads for the first time (DEC-1159 (1)).** The gate read `leads=1 load=20.0/10.1` (last night `leads=0 load=0.9/1.2`), and the slots waited 1702 s. | 4.3 s against a 4.0 s bound, and 4.1 s against 3.0 s. Both green alone in the nightly and in the 102 rerun. | Environment, under DEC-1159 (1). No ticket broke it. | Nothing to fix in code. If it recurs, route both to `tests/acceptance/serial-only.txt` (W2-154's list) so they run alone. |
| **R. Test race under load** (W2-121 `test_s1_status_runs_no_pass_and_writes_nothing`) | 1 | new (W2-121 landed 11-12 07:46, after last night) | **passes alone**: not in the 99 | **A race in the test.** It snapshots the state folder after `wait_launches(1)`, but the fake launched job writes `logs/W2-901-A5-run.json.exit` later. Under load that write lands between the two snapshots. `gov dispatch status` did not write it. | The diff in `parallel.txt` shows only the `logs` mtime and the new `logs/W2-901-A5-run.json.exit`. Green alone, and green in the 102 rerun. | W2-121's test designer, as a CTO-routed test revision (DEC-1156 (7)). | Before the first snapshot, wait for the launched job's `.exit` file, or leave `logs/*.exit` out of the snapshot. |

**Wrapper finding (no extra red):** `nightly_alone.py` turned a class-based JUnit case into a broken id, `…/test_w1_36_check_integration/TestAuditReproGovCheck.py::…`, and re-ran it as "no tests ran". It still counted the case as red-alone. The verdict happens to be right, because the case is red alone (group A), but the classification is a bug. Fix by ACT: run the nightly's pytest with `-o junit_family=xunit1` so each case carries a `file` attribute, or resolve the classname to the longest module path that exists plus `::Class`.

**Side note on DEC-781:** in this repository a real `gov check` or `gov close` is now RED on product traceability wherever Node 22 is not on PATH. That includes the CTO's own shell here, which has Node 18 first. The merge queue and lead verify avoid it by setting Node 22. DEC-781's two ways out (real openspec content, or an owner N/A decision) are still open.

## All 99 red-alone and the 3 that pass alone, by folder

Tags: [A] openspec/W2-45 + the nightly's Node 18 PATH · [B] W1-32 unrecorded commands · [C] W2-124 rebuild · [D] W2-159 vs W2-136 S10 · [E] W2-176 7th hook · [L] load (passes alone) · [R] W2-121 race (passes alone). "new" means not among last night's reds; none of the 102 was.

**W1-18** (1)

- [C] new, red alone: `test_w1_18_on_demand_start.py::test_with_the_server_not_answering_a_retrieval_answers_by_keywords_and_starts_nothing`

**W1-26** (2)

- [A] new, red alone: `test_w1_26_command.py::test_exit_0_when_all_checks_green`
- [A] new, red alone: `test_w1_26_command.py::test_warning_yellow_does_not_change_exit_code`

**W1-30** (6)

- [A] new, red alone: `test_w1_30_close.py::test_close_refuses_when_acceptance_tests_fail`
- [A] new, red alone: `test_w1_30_close.py::test_close_runs_acceptance_tests`
- [A] new, red alone: `test_w1_30_close.py::test_close_succeeds_on_green_standard_ticket`
- [A] new, red alone: `test_w1_30_close.py::test_regression_failure_blocks_close`
- [A] new, red alone: `test_w1_30_receipt.py::test_close_record_has_packet_hash`
- [A] new, red alone: `test_w1_30_receipt.py::test_close_record_has_tests_and_deviations`

**W1-32** (1)

- [B] new, red alone: `test_w1_32_command_set.py::test_the_command_set_is_the_twelve_and_the_three_recorded_ones`

**W1-36** (1)

- [A] new, red alone (the nightly re-ran a mangled id, "no tests ran"; red alone here without openspec, green with it): `test_w1_36_check_integration.py::TestAuditReproGovCheck::test_yellow_alone_does_not_make_gov_check_fail`

**W2-02** (2)

- [A] new, red alone: `test_w2_02_record_types.py::test_a_close_record_that_names_no_ticket_is_refused`
- [A] new, red alone: `test_w2_02_record_types.py::test_the_close_record_gov_close_writes_passes_core_schema`

**W2-112** (1)

- [L] new, passes alone (full run only): `test_w2_112_concurrency.py::test_a_request_past_its_time_limit_does_not_hold_the_search`

**W2-115** (14)

- [A] new, red alone: `test_w2_115_strict.py::test_the_strict_close_gives_the_recorded_verdict[caused_red-close_strict]`
- [A] new, red alone: `test_w2_115_strict.py::test_the_strict_close_gives_the_recorded_verdict[caused_red-no_close_yaml]`
- [A] new, red alone: `test_w2_115_strict.py::test_the_strict_close_gives_the_recorded_verdict[failing_acceptance-close_strict]`
- [A] new, red alone: `test_w2_115_strict.py::test_the_strict_close_gives_the_recorded_verdict[failing_acceptance-no_close_yaml]`
- [A] new, red alone: `test_w2_115_strict.py::test_the_strict_close_gives_the_recorded_verdict[green-close_strict]`
- [A] new, red alone: `test_w2_115_strict.py::test_the_strict_close_gives_the_recorded_verdict[green-no_close_yaml]`
- [A] new, red alone: `test_w2_115_strict.py::test_the_strict_close_gives_the_recorded_verdict[shared_core-close_strict]`
- [A] new, red alone: `test_w2_115_strict.py::test_the_strict_close_gives_the_recorded_verdict[shared_core-no_close_yaml]`
- [A] new, red alone: `test_w2_115_strict.py::test_the_strict_close_gives_the_recorded_verdict[unowned_red-close_strict]`
- [A] new, red alone: `test_w2_115_strict.py::test_the_strict_close_gives_the_recorded_verdict[unowned_red-no_close_yaml]`
- [A] new, red alone: `test_w2_115_strict.py::test_the_strict_close_gives_the_recorded_verdict[unplaced-close_strict]`
- [A] new, red alone: `test_w2_115_strict.py::test_the_strict_close_gives_the_recorded_verdict[unplaced-no_close_yaml]`
- [A] new, red alone: `test_w2_115_strict.py::test_the_strict_close_still_runs_the_full_regression_on_a_shared_core_change[close_strict]`
- [A] new, red alone: `test_w2_115_strict.py::test_the_strict_close_still_runs_the_full_regression_on_a_shared_core_change[no_close_yaml]`

**W2-121** (1)

- [R] new, passes alone (full run only): `test_s1_lock_off_status.py::test_s1_status_runs_no_pass_and_writes_nothing`

**W2-123** (1)

- [C] new, red alone: `test_w2_123_retry.py::test_after_the_last_failed_try_the_rebuild_states_the_tries_and_waits_and_no_partial_store_is_reported_built`

**W2-136** (1)

- [D] new, red alone: `test_w2_136_never_a_gate.py::test_s10_no_module_of_gov_outside_plan_and_launch_imports_or_calls_gov_plan`

**W2-145** (1)

- [L] new, passes alone (full run only): `test_w2_145_s4_bounds.py::test_s4_an_unanswered_search_comes_back_within_its_bound_and_logs_one_fallback_line_unranked[no-connection-within-connect-s]`

**W2-23** (1)

- [E] new, red alone: `test_w2_23_space.py::test_s6_every_kernel_hook_exits_alike_with_a_space_in_the_project_dir`

**W2-57** (1)

- [A] new, red alone: `test_w2_57_nightly_route.py::test_a_nightly_entry_is_collected_and_left_out_of_both_phases_and_a_serial_entry_runs_alone`

**W2-66** (66)

- [A] new, red alone: `test_w2_66_declared_folders.py::test_the_overlap_rule_selects_a_ticket_s_declared_folder`
- [A] new, red alone: `test_w2_66_declared_folders.py::test_the_own_suite_is_the_closing_ticket_s_declared_folder`
- [A] new, red alone: `test_w2_66_deselected_cases.py::test_a_case_left_out_by_deselection_is_named_with_why`
- [A] new, red alone: `test_w2_66_evidence.py::test_a_full_close_names_every_suite_it_ran_and_its_junit_xml_holds_every_case`
- [A] new, red alone: `test_w2_66_evidence.py::test_a_passed_close_names_its_skips_in_the_result_and_the_record`
- [A] new, red alone: `test_w2_66_evidence.py::test_a_refused_close_names_every_suite_it_left_out`
- [A] new, red alone: `test_w2_66_evidence.py::test_a_refused_close_states_its_evidence_and_says_scoped`
- [A] new, red alone: `test_w2_66_evidence.py::test_every_failing_test_is_named_with_its_failure_text_kept`
- [A] new, red alone: `test_w2_66_evidence.py::test_every_skip_is_named_with_its_reason_and_counted`
- [A] new, red alone: `test_w2_66_evidence.py::test_the_junit_xml_of_a_refused_close_holds_the_failure_text_and_the_skip`
- [A] new, red alone: `test_w2_66_followed_couplings.py::test_a_changed_helper_selects_every_suite_that_imports_it_directly_or_through_another_helper`
- [A] new, red alone: `test_w2_66_followed_couplings.py::test_a_declared_coupling_selects_its_suites_and_names_why`
- [A] new, red alone: `test_w2_66_followed_couplings.py::test_a_record_only_commit_widens_nothing`
- [A] new, red alone: `test_w2_66_followed_couplings.py::test_a_record_reading_test_turned_red_by_a_record_only_commit_refuses_the_scoped_close`
- [A] new, red alone: `test_w2_66_followed_couplings.py::test_the_record_reading_set_reads_the_pre_close_gate_s_own_check_result`
- [A] new, red alone: `test_w2_66_full_widening.py::test_a_change_to_the_path_map_runs_the_full_regression`
- [A] new, red alone: `test_w2_66_full_widening.py::test_a_change_to_the_test_map_runs_the_full_regression`
- [A] new, red alone: `test_w2_66_full_widening.py::test_a_change_under_the_shared_core_runs_the_full_regression`
- [A] new, red alone: `test_w2_66_full_widening.py::test_a_changed_file_no_mapping_places_runs_the_full_regression`
- [A] new, red alone: `test_w2_66_full_widening.py::test_a_green_record_naming_no_commit_of_the_history_leaves_the_base_unknown[no-such-commit]`
- [A] new, red alone: `test_w2_66_full_widening.py::test_a_missing_test_map_runs_the_full_regression`
- [A] new, red alone: `test_w2_66_full_widening.py::test_a_passed_full_close_is_the_base_of_the_next_scoped_close`
- [A] new, red alone: `test_w2_66_full_widening.py::test_a_red_night_is_no_base`
- [A] new, red alone: `test_w2_66_full_widening.py::test_a_shared_core_change_in_the_ticket_s_own_commit_runs_the_full_regression`
- [A] new, red alone: `test_w2_66_full_widening.py::test_a_test_map_that_cannot_be_read_runs_the_full_regression[not-yaml]`
- [A] new, red alone: `test_w2_66_full_widening.py::test_full_runs_the_full_regression_and_the_record_says_so`
- [A] new, red alone: `test_w2_66_full_widening.py::test_without_a_record_of_a_green_commit_the_base_is_unknown_and_the_run_is_full`
- [A] new, red alone: `test_w2_66_limits.py::test_a_hung_test_fails_at_the_per_test_limit_and_the_failure_names_the_limit[parallel]`
- [A] new, red alone: `test_w2_66_limits.py::test_a_hung_test_fails_at_the_per_test_limit_and_the_failure_names_the_limit[serial-afterwards]`
- [A] new, red alone: `test_w2_66_limits.py::test_the_distribution_mode_is_one_setting_and_the_runs_follow_it`
- [A] new, red alone: `test_w2_66_limits.py::test_without_pytest_timeout_the_close_does_not_pass_silently`
- [A] new, red alone: `test_w2_66_moved_files.py::test_a_file_moved_away_from_another_ticket_s_paths_selects_that_ticket_s_suite`
- [A] new, red alone: `test_w2_66_moved_files.py::test_a_file_moved_into_the_shared_core_runs_the_full_regression`
- [A] new, red alone: `test_w2_66_moved_files.py::test_a_file_moved_out_of_the_shared_core_runs_the_full_regression`
- [A] new, red alone: `test_w2_66_nightly.py::test_a_red_a_scoped_close_since_the_last_green_night_left_out_is_a_p1_package_with_the_map_corrected`
- [A] new, red alone: `test_w2_66_retention.py::test_a_passed_close_names_the_option_in_its_result_and_its_record`
- [A] new, red alone: `test_w2_66_retention.py::test_a_passing_test_s_folder_goes_and_a_failing_test_s_stays[parallel]`
- [A] new, red alone: `test_w2_66_retention.py::test_every_test_run_of_the_close_is_given_the_retention_option[acceptance]`
- [A] new, red alone: `test_w2_66_retention.py::test_every_test_run_of_the_close_is_given_the_retention_option[parallel]`
- [A] new, red alone: `test_w2_66_retention.py::test_the_refused_close_s_evidence_names_the_option`
- [A] new, red alone: `test_w2_66_scoped_selection.py::test_a_one_module_change_is_stated_scoped_never_full`
- [A] new, red alone: `test_w2_66_scoped_selection.py::test_a_scoped_close_states_its_settings_defaults`
- [A] new, red alone: `test_w2_66_scoped_selection.py::test_a_suite_the_change_cannot_reach_is_left_out_and_named_with_why[W2-cc]`
- [A] new, red alone: `test_w2_66_scoped_selection.py::test_a_suite_whose_ticket_paths_overlap_the_change_runs_and_is_named_with_why[W1-bb]`
- [A] new, red alone: `test_w2_66_scoped_selection.py::test_the_base_is_the_last_fully_green_commit`
- [A] new, red alone: `test_w2_66_scoped_selection.py::test_the_close_record_holds_the_same_evidence_block`
- [A] new, red alone: `test_w2_66_scoped_selection.py::test_the_every_close_files_run_and_are_named`
- [A] new, red alone: `test_w2_66_scoped_selection.py::test_the_head_and_the_tree_are_stated`
- [A] new, red alone: `test_w2_66_scoped_selection.py::test_the_junit_xml_holds_every_case_run_and_no_case_left_out`
- [A] new, red alone: `test_w2_66_scoped_selection.py::test_the_own_suite_runs_and_is_named`
- [A] new, red alone: `test_w2_66_scoped_selection.py::test_the_record_only_commits_since_the_base_are_inside_the_change`
- [A] new, red alone: `test_w2_66_scoped_selection.py::test_the_record_reading_set_runs_on_a_scoped_close_and_is_named`
- [A] new, red alone: `test_w2_66_scoped_selection.py::test_the_record_says_which_serial_cases_ran`
- [A] new, red alone: `test_w2_66_scoped_selection.py::test_the_scoped_close_passes`
- [A] new, red alone: `test_w2_66_scoped_selection.py::test_the_selection_keeps_the_full_runs_form_so_a_bare_conftest_import_still_collects`
- [A] new, red alone: `test_w2_66_scoped_selection.py::test_the_serial_cases_of_the_selected_suites_run_alone_and_only_those`
- [A] new, red alone: `test_w2_66_scoped_selection.py::test_the_unit_tests_run_and_are_named`
- [A] new, red alone: `test_w2_66_suiteless_tickets.py::test_a_path_only_suiteless_tickets_hold_runs_the_full_regression`
- [A] new, red alone: `test_w2_66_unresolved_targets.py::test_a_gone_coupling_target_the_change_does_not_reach_widens_nothing`
- [A] new, red alone: `test_w2_66_unresolved_targets.py::test_a_red_the_renamed_coupled_file_catches_refuses_the_close`
- [A] new, red alone: `test_w2_66_unresolved_targets.py::test_a_red_the_renamed_record_reading_case_catches_refuses_the_close`
- [A] new, red alone: `test_w2_66_unresolved_targets.py::test_a_renamed_coupling_target_widens_the_run_to_the_full_regression`
- [A] new, red alone: `test_w2_66_unresolved_targets.py::test_a_renamed_every_close_file_widens_the_run_to_the_full_regression`
- [A] new, red alone: `test_w2_66_unresolved_targets.py::test_a_renamed_record_reading_case_widens_the_run_to_the_full_regression[renamed-longer]`
- [A] new, red alone: `test_w2_66_unresolved_targets.py::test_a_renamed_record_reading_case_widens_the_run_to_the_full_regression[renamed]`
- [A] new, red alone: `test_w2_66_unresolved_targets.py::test_selected_targets_that_resolve_change_nothing`

**W2-77** (2)

- [A] new, red alone: `test_w2_77_batch.py::test_the_batch_keeps_a_hidden_worktree_s_registration_admin_folder_and_staged_index`
- [A] new, red alone: `test_w2_77_batch.py::test_the_batch_s_record_carries_the_night_s_cleanup_when_the_clone_s_removal_fails`

## Summary

1. **Tonight's verdict, `red 99`, has one main cause, and none of the 99 was red last night.** All of last night's 13 parallel reds passed. The 2 serial latency reds are the same as last night (accepted).
2. **94 of 99 (A): openspec missing from the nightly's PATH.** The nightly's PATH names Node 18; openspec exists only under Node 22.
3. W2-45 (merge `c87a2d495`, 11-12 21:42; DEC-781 / W2-M265) turned an absent openspec from YELLOW to hard-block RED. So every fixture's `gov close` or `gov check` refuses with OPENSPEC_ABSENT.
4. Proof: 4 samples are green at `c87a2d495^1` and red at `c87a2d495`. At the run's commit, 97 of the 102 failures pass once Node 22's openspec is on PATH.
5. The merge queue, `lead_verify` and `close_build` already set Node 22, which is why the tickets' closes stayed green. W2-154 is cleared (same result either side of `dbb0891e8`).
6. **Fix for A (by ACT, on the nightly wrapper):** in `nightly_cron.sh` and `nightly_restart.sh`, change PATH's `node/v18.20.8/bin` to `node/v22.23.3/bin`. Appending v22 after v18 does not work: openspec crashes on Node 18.
7. **1 (B): W1-32 command set.** `dispatch` (W2-121, first), `adapters` (W2-23), `session-watch` (W2-159) and `wait` (W2-160) are not in W1-07's recorded list. Fix: a CTO-routed test revision recording the four (DEC-1156 (7)).
8. **2 (C): W1-18 and W2-123 rebuild cases.** W2-124 (`a2f28ccf3`) made a rebuild fail when its semantic store is not recreated, and DEC-1150 (3)'s 13-file revision missed these two. Fix: a CTO-routed revision of both cases.
9. **1 (D): W2-136 S10.** W2-159's session_watch calls `gov plan --ready`, as its own KPI S5 requires, while the S10 case forbids it outside plan and launch. This is a KPI contradiction for the CTO to decide. Smallest fix: allow `src/gov/session_watch` in S10's scan.
10. **1 (E): W2-23 S6.** W2-176 added a 7th kernel hook, `context_watch.py`, that is not in `template/.rulesync/hooks.jsonc`, and the case pins 6. Fix: a test revision to 7. Separately, decide whether the template wires the hook (by ACT).
11. **3 passed alone and are not in the 99:**
    - W2-112 and W2-145 S4 (L) missed their timing bounds by 0.3 s and 1.1 s. The nightly ran beside the leads (gate load 20 vs 0.9 last night; slot wait 1702 s).
    - W2-121 S1 (R) is a race in the test itself: the launched job's `.exit` file lands between its snapshots.
12. **Wrapper bug:** `nightly_alone.py` breaks class-based ids (W1-36, "no tests ran"), though that case is genuinely red (A).
13. **Counts by cause:**

    | Cause | Count |
    |---|---|
    | openspec / Node 18 PATH | 94 |
    | W2-124 | 2 |
    | W2-121/23/159/160 commands | 1 |
    | W2-159 vs W2-136 | 1 |
    | W2-176 hook | 1 |
    | **Total red alone** | **99** |
    | Load (passes alone) | 2 |
    | W2-121 test race (passes alone) | 1 |
    | Accepted-red, serial | 2 |

14. **Expected after the fixes:** with A fixed, the next nightly should drop to about 5 reds. With B to E also fixed, about 0, apart from the timing flakes beside the leads.
15. Scratch worktrees were removed after the analysis. Nothing was committed or edited in the tracked tree.
