# W2-172 acceptance tests: the memory audit's driver and schedule (S1–S9, F1–F5)

Ticket `DAEO-p8tv` (W2-172), profile FULL, class C2. An independent test designer (MR-3) wrote these cases from the
ticket's KPI lines and its `## Interface` section (items 1–12, the CTO's answers O1–O4 above it, PKG-W2-172-IFACE-1 (a)) and
the ticket's sources, before the implementation. Nothing of this ticket's branch was read (`src/gov/memaudit/` as it stands on
the tests' base holds W2-170's and W2-171's tool only; no `run`, `due`, `baseline`, `status` or `figures` driver code, no
`memaudit_cron.sh`, no `tests/unit/memaudit/` of this ticket, DEC-820). W2-170's and W2-171's tools and acceptance suites were
read as the Interface says: they are called, never copied or changed.

**163 cases from 104 test functions in ten files**, with a support set (`w2_172_world.py`, `w2_172_git.py`,
`w2_172_digest.py`, `w2_172_checks.py`), a conftest, and five planted programs (`launch_stub.py`, `gate_stub.py`,
`py_shim.py`, `fake_crontab.py`, `spy/sitecustomize.py`). W2-171's world (`w2_171_world.py`, `w2_171_scenario.py`, its fake
`gov` and `claude`) is imported from `tests/acceptance/W2-171/` (put on `sys.path` by `w2_172_world.py`), never changed.

## How the tests reach the code under test

- **The command line, as the callers run it** (Interface 1, 2, 8): `python3 -m gov.memaudit run|due|baseline|status|figures
  --sets-root <root> ...` and `bash memaudit_cron.sh`, each in a child process, judged by its exit code, its printed lines
  (`STEP <name> <command line>`, `STOPPED <step> <exit>`, `STOPPED <step> gate busy`, `REFUSED <code>`, the digest's 12
  lines, the `due` lines, `audited` / `not audited, next due <date>`, `BASELINE <12 hex>`, `BL-*`) and the files under
  `<runs>/indep/memaudit/` (item 4: `LOCK`, `STARTS.log`, `HISTORY.jsonl`, `cron.log`, `<A>/COUNTS.json`, `<A>/DIGEST.txt`,
  `<A>/<step>.out|.err|.counts.json`) and `<runs>/indep/AUDITS.log`. The new modules are never imported at collection, so the
  suite runs red by failing. Every child gets this tree's `src/` first on `PYTHONPATH` (a session fixture fails the run when
  a child would import `gov` from elsewhere).
- **Only the seams the Interface names:** `--launch <file>` (a planted launch script), `--store-link`, `--repo`, `--gov`,
  `--claude`, `--gate-cmd`, and the environment `GOV_INDEP_RUNS_DIR`, `GOV_MEMAUDIT_NOW`, `GOV_MEMAUDIT_GATE_POLL_S`,
  `GOV_MEMAUDIT_GATE_MAX_S`, `GOV_MEMAUDIT_PYTHON`, `GOV_MEMAUDIT_SETS_ROOT`, `GOV_MEMAUDIT_GATE`. W2-170's and W2-171's
  subcommands (`preflight`, `void`, `measure`, `judge`, `classes`, `pool`) **run for real** under the driver, fed by W2-171's
  fake `gov` and fake `claude`; faults are planted the way W2-171's world plants them (two degraded attempts give `measure`
  exit 2 after USED; a store whose head is not the audit commit gives `DC-STORE`, `measure` exit 1 before USED).
- **Everything is planted under pytest's `tmp_path`:** the sets root (W2-171's: its own path map, the control set, the pool),
  the repository (W2-171's three commits plus a fourth that edits the three approved briefs, so the working tree's briefs differ
  from those at the audit commit and `git show <C>` is what must be hashed), the integration store's link (a git worktree of the
  planted repository, detached at the audit commit, with a planted `.gov-runtime/store.db`), the runs folder `launch-log/`
  (`GOV_INDEP_RUNS_DIR`, holding `indep/AUDITS.log`), the planted launch script, gate, interpreter shim and `crontab`, `HOME`.
  Never the real sets root, runs folder, HOME, crontab, a real search, a real model call or a GPU; never an evaluation set's
  hidden half.
- **The planted launch script** (`launch_stub.py`) logs its argv, answers per step and per call from a plan (`exit`, `cost`,
  `sleep`, `revise`/`reject` ids and `revise_n`/`rejected_n` counts for a checker, `remove` ids for a writer, `rewrite_commit`),
  prints one noise line and the counts object (`indep-counts.schema.json`'s keys) as its last line, and on a delivery writes what
  the real script writes: the writer's set and a `SEEDS.log` line, the checker's `XCHECK-r<n>.md`, the auditor's
  `miss-classes.json` (the five classes in turn over the misses' ids) and the `AUDITS.log` line.
- **Whole audits are run once per session** (`conftest.ran`) and read by many cases: `words` (scenario W2-171 `words`: 40
  questions, the planted words, a first checker pass with a revision so the two second-round steps run, a pool that fell from
  the last audit's), `clean` (no miss, a clean first pass, the pool as it was) and `five37` (a set of 37 after the second pass
  rejected three; the scaled bar; no earlier pool figure). The cases that must write copy the world.
- **The three witnesses of what the driver did** (S1, F1): the `STEP` lines it printed; the planted launch script's own call
  ledger; and a file-access spy (`spy/sitecustomize.py`, a `sys.addaudithook` loaded by every child) whose `subprocess.Popen`
  lines of the driver's own process (`python -m gov.memaudit run`) give the commands it really started, in order, and whose
  `open`, `os.listdir`, `os.scandir` and `os.walk` lines under the sets root must be none for the driver itself and are present
  for the launch script's process and for `preflight` (the spy is shown to see).
- **Path hygiene (S1, F1):** every path the test's world builds and that can appear on a printed command line (`sets`,
  `repo`, `link`, `stub`, `gov`, `claude`, `gate_stub`, `shim`) holds none of `fixtures/`, `runs/`, `indep-walls/` or `hidden`
  (`say`'s own refusal word); `conftest.clean_paths` asserts it before each world is used, and the planted runs folder is
  `launch-log`. The repository's own location (`W.SRC`) and the interpreter (`sys.executable`) are not the world's: a clone
  under `gov-os-runs/` (the merge queue's) is legal. The greps over printed lines and child argv (`W.forbidden_in_text`,
  `W.forbidden_in_argv`) skip exactly one thing, the `sys.executable` token (the `<py>` first word of a step line, the first
  element of an argv), and fail on a word anywhere else. Rewrite-Reason: the merge queue's clone path (21:19 ejection).
- **No network, no GPU, no model, no store but the planted file.** No case is marked `local_only`; no test, class, parameter id
  or file name holds `real`, `green_here` or `time_limit`. The only cases that wait are the two gate cases (a poll of 1 second,
  at most 2 and 30), the two-runs-at-once case (a launch stub that sleeps 4 seconds) and the polls of the latter, all bounded.

Run from the ticket's worktree (empty `HOME` and a `TMPDIR` outside the repository and outside the real runs folder, through
the heavy-slot gate):

    TMPDIR=<tmp> bash <orchestrator>/tools/heavy_slot.sh env HOME=<empty folder> PYTHONUSERBASE=<user base> \
      PYTHONPATH=<worktree>/src python3 -m pytest tests/acceptance/W2-172 -q -p no:cacheprovider \
      -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"

`W172_SRC` and `W172_WRAPPER` (unset by default) name another tree's `src/` and wrapper: they exist only to show the suite
sound against a prototype outside the repository (below).

## Readings of the Interface these cases take (where its words leave a choice)

- **Launch lines:** the printed `STEP` line of a launch holds exactly the flags `--sets-root --kind --brief --brief-sha256
  --commit --set` and `--round` (writer, checker) or `--audit` (auditor), compared as flag/value pairs, not in a fixed order; the
  auditor's line carries `--commit` and `--brief-sha256` like the others and no `--round`.
- **The USED boundary (item 5):** `measure` exit 1 (the `DC-` refusals) is a stop before USED (no owner line, no `HISTORY.jsonl`
  line); exit 2 is after USED.
- **`due` reasons (item 9):** `start` for no measured line at all; for one or two measured lines either `start` or `active` is
  accepted; `active` for three measured lines of which one fails a condition while no trigger holds; the four triggers
  `churn`, `retrieval`, `verdict`, `pool` are asserted only when each holds alone over three otherwise stable lines.
  "The last audit's commit" is planted as the same commit in the last `HISTORY.jsonl` line, the last `STARTS.log` line and the last
  `AUDITS.log` line, so any of the three readings passes. Weekly `next` is the last start plus 6 days, monthly plus 28
  (asserted where not due).
- **The digest** (item 7): the 12 lines are matched by one regular expression each (`w2_172_digest.py`). The exact interval is
  compared to the oracle in percent within 0.06 points, whatever its decimals; `COST` must list the launch steps (the counts'
  `session.cost_usd`, 0.25 each in these worlds) and `judge` (the `spent <usd> USD` of its own line) and may list other steps at
  0.00; the `QUESTIONS` codes are read as `<CODE> <n>` pairs after a `; `; for a stop or a refusal a figure line may be `<WORD>
  not reached` (the cases that stop before `judge` require it for `VERDICT`, `HIT5`, `MISSES` and `POOL`); `STOP` is `STOP <step>
  exit <code>` or, for the gate, `STOP <step> gate busy` (the exit code of that stop is not fixed by the Interface).
- **`COUNTS.json`** (item 4): the cases read `audit`, `commit`, `force`, `mode`, `steps` (`step`, `exit`, `retried`), `stop`
  (`step`, `exit`, `used`; null when none), `refused` (null or absent when none), `cost`. `HISTORY.jsonl`'s line has exactly the
  ten keys of item 4; `churn` of the first whole audit is 1.0 (the planted history puts every tracked path in the 28 days before
  the audit commit) and `retrieval_28d` true.
- **`figures`** (item 6): its keys are not fixed; the cases check one JSON line, exit 0, nothing written, no planted word, and a
  missing file is still a JSON line.
- **The wrapper's gate default (item 8; PKG-W2-172-TESTS-1 GATE-1 (a), DEC-1112 (3)):** the driver splits `--gate-cmd`'s
  value with `shlex.split` and runs the words as given, so the default `gov resources --check` works as it is; the Interface's
  "called with no arguments" reads "run as its words" (a one-word value, as the planted gate, gets none). The cases give the
  wrapper a gate through `GOV_MEMAUDIT_GATE` (a stub) and test the default only by the wrapper's text (`resources --check`,
  not `gate_check.py`); no case runs a multi-word `--gate-cmd` through the driver.
- **Refusal folders and `RN-NAME` (PKG-W2-172-TESTS-1 TD-2 (b), DEC-1112 (3)):** a refusal writes `COUNTS.json` into
  `<R>/<A>/` where it did not exist (item 3), which makes `<R>/<A>/` exist. `RN-NAME` is judged by `STARTS.log` (a line naming
  `<A>`: an audit started), not by the folder or by a refusal's `COUNTS.json`, so a refused run can be retried on the same date.
  `test_s4_a_second_start_on_the_same_date_is_refused_rn_name_and_writes_nothing_there` and the `RN-NAME` pair of
  `test_s2_the_first_check_that_fails_refuses` plant the `STARTS.log` line (and the folder, as a first audit leaves it);
  `test_s4_a_refused_run_is_not_a_start_and_the_same_date_can_be_retried` retries after `RN-NOBASE` and `RN-REBUILD` without
  removing the folder. The older cases that remove the folder between a refusal and a start (`forget`) keep doing so, which is
  harmless. `C.refused_without_a_start(..., had_folder=True)` still means "the audit's folder existed before the run".
- **`--force` in the digest (PKG-W2-172-TESTS-1 TD-1 (b), DEC-1112 (3)):** the 12-line digest does not record `--force`; item
  1's "recorded in the counts and the digest" is corrected to the counts only. The cases check `COUNTS.json`'s `force` and
  `STARTS.log`'s `force`, and that the digest still has exactly 12 lines; none looks for the word in the digest.
- **Not run:** the real launch script with W2-149's stub `claude` (optional in the brief): not done, because planting a walls
  template and the owner's approved list under the planted repository is not cheap; the planted launch script carries the
  interface the driver sees (argv, exit codes 0/10–22, the counts line, the `AUDITS.log` line on an auditor's delivery).

## KPI map

| KPI | tests | expected red reason |
|---|---|---|
| S1 | `test_w2_172_s1_cycle.py::test_s1_a_set_with_revisions_runs_the_twelve_steps_in_this_order`, `test_w2_172_s1_cycle.py::test_s1_a_clean_set_goes_straight_from_the_first_checker_to_the_measure`, `test_w2_172_s1_cycle.py::test_s1_every_launch_line_names_only_the_sets_root_the_brief_and_its_hash_at_the_audit_commit`, `test_w2_172_s1_cycle.py::test_s1_the_printed_command_lines_hold_no_folder_of_the_sets_root`, `test_w2_172_s1_cycle.py::test_s1_the_auditor_runs_also_when_there_is_no_miss_with_an_empty_misses_file`, `test_w2_172_s1_cycle.py::test_s1_the_auditor_gets_the_judges_misses`, `test_w2_172_s1_cycle.py::test_s1_the_children_are_kept_in_the_audits_folder_and_nothing_a_child_says_is_printed`, `test_w2_172_s1_cycle.py::test_s1_the_second_round_runs_exactly_when_the_first_checkers_counts_say_revise_or_reject`, `test_w2_172_f1_f4_access.py::test_s1_figures_prints_one_json_line_of_numbers_and_writes_nothing`, `test_w2_172_f1_f4_access.py::test_s1_figures_of_an_audit_with_no_files_is_a_json_line_and_exit_0`, `test_w2_172_f1_f4_access.py::test_s1_the_runs_folder_is_never_a_flag_and_the_sets_root_is_required`, `test_w2_172_f1_f4_access.py::test_s1_run_prints_through_say_only_never_a_path_under_the_sets_root`, `test_w2_172_s5_due.py::test_s5_each_new_subcommand_has_a_help_that_exits_0` | `gov.memaudit` has no `run`, `due`, `baseline`, `status` or `figures`: argparse refuses the subcommand (exit 4, `ERROR: UsageError`); no `STEP` line, no ledger, no digest; the staged whole audits give exit 4 where 0 is required |
| S2 | `test_w2_172_s2_s4_refusals.py::test_s2_a_fresh_commit_that_is_an_ancestor_starts_and_names_the_audit_by_the_date`, `test_w2_172_s2_s4_refusals.py::test_s2_the_audit_commit_is_the_commit_the_link_names_not_the_repositorys_head`, `test_w2_172_s2_s4_refusals.py::test_s2_a_commit_more_than_24_hours_old_is_refused_and_nothing_is_built`, `test_w2_172_s2_s4_refusals.py::test_s2_a_commit_on_a_side_branch_is_refused_rn_side`, `test_w2_172_s2_s4_refusals.py::test_s2_the_integrate_branch_is_the_main_line_when_it_exists`, `test_w2_172_s2_s4_refusals.py::test_s2_a_store_being_rebuilt_is_a_held_lock_not_a_file`, `test_w2_172_s2_s4_refusals.py::test_s2_run_refuses_rn_nobase_while_the_audits_log_has_no_line`, `test_w2_172_s2_s4_refusals.py::test_s2_the_first_check_that_fails_refuses`, `test_w2_172_s2_s4_refusals.py::test_f3_every_refusal_prints_its_code_and_is_not_a_started_audit`, `test_w2_172_s6_baseline.py::test_s6_run_refuses_rn_nobase_until_a_baseline_is_written` | no `run`: exit 4, no `REFUSED <code>`, no `STARTS.log` line, no `STEP` |
| S3 | `test_w2_172_s3_stops.py::test_s3_a_launch_exit_other_than_0_or_16_stops_the_cycle_with_one_call_and_no_retry`, `test_w2_172_s3_stops.py::test_s3_exit_16_then_0_goes_on_with_the_same_command_line`, `test_w2_172_s3_stops.py::test_s3_exit_16_twice_stops_after_exactly_two_calls`, `test_w2_172_s3_stops.py::test_s3_exit_16_at_a_later_launch_is_retried_too`, `test_w2_172_s3_stops.py::test_s3_a_preflight_that_refuses_is_a_stop_at_preflight_with_its_exit_1`, `test_w2_172_s3_stops.py::test_s3_a_void_audit_is_a_stop_at_void_with_its_exit_2`, `test_w2_172_s3_stops.py::test_s3_a_measure_refused_before_usd_is_a_stop_before_used`, `test_w2_172_s3_stops.py::test_s3_a_fault_after_used_is_a_line_to_the_owner_and_the_set_is_not_run_again` | no `run`: exit 4 where 2 is required; no `STOPPED` line, no `COUNTS.json`, no digest |
| S4 | `test_w2_172_s2_s4_refusals.py::test_s4_a_second_start_while_the_lock_is_held_is_refused_rn_lock`, `test_w2_172_s2_s4_refusals.py::test_s4_two_runs_at_once_the_second_is_refused_and_the_lock_is_released_when_the_first_ends`, `test_w2_172_s2_s4_refusals.py::test_s4_a_start_within_5_days_of_the_last_is_refused_unless_force_is_given`, `test_w2_172_s2_s4_refusals.py::test_s4_force_lifts_only_the_5_day_refusal`, `test_w2_172_s2_s4_refusals.py::test_s4_a_second_start_on_the_same_date_is_refused_rn_name_and_writes_nothing_there`, `test_w2_172_s2_s4_refusals.py::test_s4_a_refused_run_is_not_a_start_and_the_same_date_can_be_retried` | no `run`: no refusal printed, no `STARTS.log` line; the two-runs-at-once case sees no first launch |
| S5 | `test_w2_172_s5_due.py::test_s5_with_no_audit_yet_it_is_weekly_and_due_for_the_start`, `test_w2_172_s5_due.py::test_s5_fewer_than_three_measured_lines_is_weekly`, `test_w2_172_s5_due.py::test_s5_three_audits_each_stable_with_the_rest_met_is_monthly`, `test_w2_172_s5_due.py::test_s5_only_measured_lines_count_and_only_the_last_three`, `test_w2_172_s5_due.py::test_s5_a_store_link_named_by_rebuild_yaml_on_the_main_line_is_the_default`, `test_w2_172_s5_due.py::test_s5_a_churn_of_40_percent_is_weekly_at_once`, `test_w2_172_s5_due.py::test_s5_churn_of_10_percent_or_more_is_the_trigger_9_is_not`, `test_w2_172_s5_due.py::test_s5_the_paths_the_exclusion_file_names_never_count_in_the_churn`, `test_w2_172_s5_due.py::test_s5_a_change_to_a_retrieval_path_since_the_last_audit_is_weekly_at_once`, `test_w2_172_s5_due.py::test_s5_a_retrieval_change_before_the_last_audit_is_not_a_trigger`, `test_w2_172_s5_due.py::test_s5_a_last_verdict_below_the_bar_is_weekly_at_once`, `test_w2_172_s5_due.py::test_s5_a_last_pool_regression_is_weekly_at_once`, `test_w2_172_s5_due.py::test_s5_one_of_the_last_three_audits_failing_a_condition_keeps_it_weekly`, `test_w2_172_s5_due.py::test_s5_churn_just_under_5_percent_in_each_of_the_three_is_stable`, `test_w2_172_s5_due.py::test_s5_weekly_is_due_after_6_days_not_5`, `test_w2_172_s5_due.py::test_s5_monthly_is_due_after_28_days_not_27`, `test_w2_172_s5_due.py::test_s5_the_exit_code_is_4_on_usage` | no `due`: exit 4 where 0 or 1 is required, no `MODE`/`DUE`/`REASON` lines |
| S6 | `test_w2_172_s6_baseline.py::test_s6_an_empty_log_takes_one_line_in_the_launch_scripts_form`, `test_w2_172_s6_baseline.py::test_s6_a_log_present_but_empty_is_empty`, `test_w2_172_s6_baseline.py::test_s6_the_first_audits_changed_list_starts_at_the_baseline_commit`, `test_w2_172_s6_baseline.py::test_s6_a_second_baseline_while_an_audit_line_exists_is_refused_and_writes_nothing`, `test_w2_172_s6_baseline.py::test_s6_a_line_written_by_an_audit_is_a_line_too`, `test_w2_172_s6_baseline.py::test_s6_a_commit_not_in_the_repository_is_refused_and_nothing_is_written`, `test_w2_172_s6_baseline.py::test_s6_the_commit_flag_is_required` | no `baseline`: exit 4, nothing appended, no `BASELINE`/`BL-` line |
| S7 | `test_w2_172_s7_digest.py::test_s7_the_digest_is_twelve_lines_in_order_each_matching_its_form_and_is_printed`, `test_w2_172_s7_digest.py::test_s7_the_audit_the_mode_the_verdict_and_the_retrieval_figures`, `test_w2_172_s7_digest.py::test_s7_a_set_of_37_prints_the_scaled_bar`, `test_w2_172_s7_digest.py::test_s7_the_misses_by_class_rank_bucket_and_namespace`, `test_w2_172_s7_digest.py::test_s7_the_pool_beside_the_last_audits_and_any_regression`, `test_w2_172_s7_digest.py::test_s7_the_retrieval_paths_changed_since_the_last_audit_come_from_git`, `test_w2_172_s7_digest.py::test_s7_the_questions_kept_and_dropped_by_code`, `test_w2_172_s7_digest.py::test_s7_the_cost_per_step_in_usd`, `test_w2_172_s7_digest.py::test_s7_the_next_due_date_and_the_closing_lines`, `test_w2_172_s7_digest.py::test_s7_the_counts_the_history_and_the_start_of_a_whole_audit` | no `run`: the staged whole audits exit 4; no `DIGEST.txt`, no `COUNTS.json`, no `HISTORY.jsonl` |
| S8 | `test_w2_172_s8_status.py::test_s8_a_measured_audit_after_the_last_retrieval_change_is_audited`, `test_w2_172_s8_status.py::test_s8_a_measured_audit_at_the_last_retrieval_change_is_audited`, `test_w2_172_s8_status.py::test_s8_a_measured_audit_before_the_last_retrieval_change_is_not_audited`, `test_w2_172_s8_status.py::test_s8_an_audit_that_was_not_measured_does_not_count`, `test_w2_172_s8_status.py::test_s8_no_audit_at_all_is_not_audited`, `test_w2_172_s8_status.py::test_s8_some_line_is_enough`, `test_w2_172_s8_status.py::test_s8_the_last_change_is_the_latest_of_the_six_globs_since_the_commit`, `test_w2_172_s8_status.py::test_s8_no_retrieval_change_since_the_commit_is_audited_whatever_the_history`, `test_w2_172_s8_status.py::test_s8_each_of_the_six_globs_is_a_retrieval_path`, `test_w2_172_s8_status.py::test_s8_a_change_to_a_path_outside_the_six_globs_is_not_a_retrieval_change`, `test_w2_172_s8_status.py::test_s8_status_writes_nothing_and_starts_no_audit`, `test_w2_172_s8_status.py::test_s8_since_is_required` | no `status`: exit 4, neither `audited` nor `not audited` printed |
| S9 | `test_w2_172_s9_cron_gate.py::test_s9_not_due_it_starts_nothing_exits_0_and_appends_one_line`, `test_w2_172_s9_cron_gate.py::test_s9_due_and_idle_it_starts_the_cycle_with_the_gate_and_exits_with_runs_code`, `test_w2_172_s9_cron_gate.py::test_s9_the_wrapper_exits_with_the_code_run_exits_with`, `test_w2_172_s9_cron_gate.py::test_s9_one_line_a_run_is_appended`, `test_w2_172_s9_cron_gate.py::test_s9_the_wrapper_defaults_to_the_sets_root_under_home`, `test_w2_172_s9_cron_gate.py::test_s9_the_wrapper_writes_nothing_but_the_cron_log_and_calls_no_crontab`, `test_w2_172_s9_cron_gate.py::test_s9_the_wrapper_holds_no_crontab_edit`, `test_w2_172_s9_cron_gate.py::test_s9_the_wrapper_names_its_interpreter_sets_root_and_gate_by_the_interfaces_variables`, `test_w2_172_s9_cron_gate.py::test_s9_a_busy_gate_stops_the_measure_with_gate_busy_after_the_wait_runs_out`, `test_w2_172_s9_cron_gate.py::test_s9_a_gate_that_opens_lets_the_measure_start_once`, `test_w2_172_s9_cron_gate.py::test_s9_the_gate_is_asked_before_measure_judge_and_pool_and_before_nothing_else`, `test_w2_172_s9_cron_gate.py::test_s9_without_a_gate_command_no_gate_is_asked` | no `memaudit_cron.sh` (bash exit 127, `FileNotFoundError` reading it); no `run` for the gate cases |
| F1 | `test_w2_172_f1_f4_access.py::test_f1_the_driver_opens_lists_and_names_nothing_under_the_sets_root`, `test_w2_172_f1_f4_access.py::test_f1_the_spy_does_see_what_the_launch_script_writes_into_the_sets_root`, `test_w2_172_f1_f4_access.py::test_f1_the_driver_runs_nothing_but_the_launch_script_and_the_subcommands_and_git`, `test_w2_172_s1_cycle.py::test_s1_the_printed_command_lines_hold_no_folder_of_the_sets_root`, `test_w2_172_s1_cycle.py::test_s1_every_launch_line_names_only_the_sets_root_the_brief_and_its_hash_at_the_audit_commit` | the staged whole audit exits 4: no driver process, no `Popen` line, no `STEP` line |
| F2 | `test_w2_172_s7_digest.py::test_f2_no_question_gold_answer_answer_or_source_path_reaches_the_digest_the_output_or_a_log`, and the stop's digest inside `test_w2_172_s3_stops.py::test_s3_a_fault_after_used_is_a_line_to_the_owner_and_the_set_is_not_run_again` | no `run`: nothing written to grep; the staged audit exits 4 |
| F3 | `test_w2_172_s2_s4_refusals.py::test_s4_a_start_within_5_days_of_the_last_is_refused_unless_force_is_given`, `test_w2_172_s2_s4_refusals.py::test_s4_a_second_start_while_the_lock_is_held_is_refused_rn_lock`, `test_w2_172_s2_s4_refusals.py::test_f3_every_refusal_prints_its_code_and_is_not_a_started_audit`, `test_w2_172_s3_stops.py::test_f3_a_stop_before_used_leaves_the_set_unmeasured_and_the_next_audit_starts_a_new_set`, `test_w2_172_s3_stops.py::test_s3_a_fault_after_used_is_a_line_to_the_owner_and_the_set_is_not_run_again` | as S3 and S4 (F3 is covered by S4's refusals and S3's stop before USED: the Verify names them) |
| F4 | `test_w2_172_f1_f4_access.py::test_f4_a_whole_run_leaves_the_repositorys_guard_path_map_claude_and_template_as_committed`, `test_w2_172_f1_f4_access.py::test_f4_neither_the_driver_nor_the_wrapper_calls_the_crontab`, `test_w2_172_f1_f4_access.py::test_f4_the_driver_writes_only_under_its_own_folder_and_the_children_write_theirs`, `test_w2_172_s9_cron_gate.py::test_s9_the_wrapper_holds_no_crontab_edit`, `test_w2_172_s9_cron_gate.py::test_s9_the_wrapper_writes_nothing_but_the_cron_log_and_calls_no_crontab` | the staged whole audit exits 4; no wrapper file |
| F5 | `test_w2_172_f5_paths.py::test_f5_the_branch_changes_only_paths_the_ticket_allows` | **skipped** on the tests' branch (and on any branch but `w2/W2-172`, DECIDED-NOT-DONE row 171) with the reason named; judges the ticket's branch after the merge |

## Expected red on today's integrated code

Run on this tree (no new subcommand, no wrapper): **162 of 163 cases fail, none passes and 1 is skipped (F5)**. Every case that calls `run`, `due`, `baseline`, `status`, `figures` or the wrapper fails
(argparse refuses the subcommand: exit 4, `ERROR: UsageError`; the wrapper is missing); F5 is skipped. No case is green today:
the four cases that would pass on exit 4 alone (`--sets-root`, `--commit` or `--since` required, `due` usage) first check that
the subcommand exists (`--help` exits 0).

## How the suite was shown sound

The world, the planted programs, the oracles and every case were run against a **throwaway prototype of the driver, the four
subcommands, `figures` and the wrapper that the designer wrote from the Interface in a scratch folder outside the repository**
(a copy of `src/` with one extra module and a five-line dispatch; never committed, not the engineer's work and not a reading of
it): with it **160 cases pass and F5 is skipped**; the prototype first failed two cases that were right to fail (it opened
`DROPS.json` under the sets root itself, and it made `<store link>.lock` beside the link), which also showed the file-access spy
and the write-confinement case sound. That shows the cases are consistent among themselves, the planted programs
and W2-170's and W2-171's tools as they stand; it says nothing about the engineer's code.

The revision batch of PKG-W2-172-TESTS-1 (TD-1 (b), TD-2 (b), GATE-1 (a); DEC-1112 (3)) changed the `RN-NAME` plants of two
cases and added one (two cases with its parameters); it was shown red on this tree (the nine changed or added cases fail with
exit 4, the driver missing) and was **not** re-run against the throwaway prototype, whose `RN-NAME` check judges by the folder.
