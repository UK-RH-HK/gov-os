# W2-159 acceptance tests: `gov session-watch stop-check waiter|idle`

Ticket DAEO-6lid (W2-159), profile STANDARD, class C2. Written by the independent test designer (MR-3) from the ticket's KPI
lines S1 to S5 and F1 to F4 and its `## Interface` section (accepted as a whole, P-W2-159-2 (a)), with the lead's reading of
the Interface (brief td-1), before any implementation. Nothing of `src/gov/session_watch/`, `tests/unit/session_watch/` or
the engineer's branch was read; the code read is `w2/integrate`'s (`src/gov/cli/main.py`'s convention, the dispatcher's
`status.json` in `src/gov/dispatch/run.py`, `gov plan --ready`'s form in `src/gov/plan/render.py`) and the reference scripts
`stop_waiter_check.py` and `stop_idle_check.py` (read for behaviours and planted forms; no test targets them).

## How they run

    mkdir -p /tmp/w2-159-td && env TMPDIR=/tmp/w2-159-td HOME=<an empty folder> PYTHONUSERBASE=$HOME_REAL/.local \
      PYTHONPATH=<worktree>/src bash <heavy_slot.sh> python3 -m pytest tests/acceptance/W2-159 -q -p no:cacheprovider \
      -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"

About 10 s for the 84 cases (a child process per run of a check, no sleeps, no model, no network). The filter leaves out
nothing: no case is named with `real`, `green_here` or `time_limit` and none is marked `local_only`. On the mode-000 case:
`test_s1_a_session_file_with_mode_000_says_nothing` is skipped when the tests run as root.

## What is planted (never a live session, never `/proc`, never a hook in any `.claude/`)

Everything is under the test's `tmp_path` (`w2_159_support.Watch`). `Watch.run(check)` runs
`python -B -m gov.cli.main session-watch stop-check <waiter|idle> --root <root>` as a child process with the tree under test's
`src` on `PYTHONPATH`, the hook's JSON on standard input (`session_id`, `transcript_path`, `stop_hook_active`, `cwd`,
`hook_event_name`, and `last_assistant_message` where a case sets it), a clean environment (no `GOV_*` or `GIT_*` of the
running session; `HOME` a temporary folder) and the Interface's test overrides. It asserts for every run: exit 0; standard
output empty or one JSON object whose keys are only `decision` (always `"block"`, with a non-empty `reason`), `reason`,
`systemMessage`.

| planted | form |
|---|---|
| configuration | `<root>/governance/project/session-watch.yaml`, `session_watch:` with `waiter_commands`, `waiter_arm`, `standby_max_age_h`, `pid_globs`, `items` |
| registered session | `<root>/.gov-runtime/session-watch/session.txt` (the id and a newline); another id, no file, a folder in its place, mode 000 |
| stand-by note | `standby.txt`, its age its mtime, set with `os.utime` against `GOV_SESSION_WATCH_NOW` |
| state, log | `state.json` (read back as `{"waiter": ..., "idle": ...}`), `stop-check.log` (tab-separated lines; the new lines of a run are read back) |
| clock | `GOV_SESSION_WATCH_NOW` = one fixed epoch second per test run; every age (stand-by note, status file, pid start, agent transcript) is relative to it |
| process list | `GOV_SESSION_WATCH_PS`: a JSON list of `{pid, cmdline, start, state, fds}` (see "The one open interface point") |
| pid files | `<root>/.gov-runtime/jobs/launch/job1.pid` (default glob) or a configured `pid_globs` path; mtime just after the process start; `<name>.exit` beside it where a case plants one |
| dispatcher status | `<root>/.gov-runtime/dispatch/status.json` in W2-121's schema (`outcome`, `exit_code`, `running`, `running_jobs`, `pending_starts`, `gate.open`, `gate.disk.open`), mtime set |
| background agents | `GOV_SESSION_WATCH_SUBAGENTS` folder: `agent-<name>.meta.json` (`finished` or not) and `agent-<name>.jsonl` (mtime set) |
| background tasks | `GOV_SESSION_WATCH_TASKS` folder: `<name>.output` held open by a process of the planted list (`fds`) |
| transcript | JSON lines: a `user` entry with a string `content` (a prompt, a turn), `assistant` entries with a `text` item, a tool call and its `tool_result` user entry, `isMeta`, `wakeupSource`, `turnOrigin` entries |
| open items | file source, reader `lines` (`items/open.txt`); reader `swreader_w2159.items:read_items` (a package planted under the test's folder and put on `PYTHONPATH`; it records the path it was called with); the default dispatcher source with a fake `gov` program (`GOV_SESSION_WATCH_GOV`, a shell script that records its argv and writes a ready list to the file after `--ready`) |

## The interface the tests assume (where the ticket's Interface and brief td-1's reading are silent: nothing is chosen here)

All of the ticket's Interface items 1 to 6, plus the lead's reading of the KPI lines as stated in brief td-1: the registered
session (`session.txt`'s stripped text) is the only one the checks act for; a turn, once a turn and errors as the reference
defines them (the transcript read back to the last prompt-like `user` entry, its `uuid` the turn's key; the state recording
per check the session and the turn it blocked); the idle check's order (session, IDLE-REASON, the bound, running, a
legitimate wait from the status, the items); the waiter's reason naming the inbox waiter and the `waiter_arm` string as
configured; an item's id is the ticket id (second column) for the dispatcher source. Words the tests look for in a
`systemMessage` and the log, case-insensitive, one per wait: `gate` (gate shut), `disk` (disk gate shut), `full` (machine
full), `owner` (every remaining item on the owner), `running|pid|job` (a running job; `agent`, `task` for those two kinds;
`running|launch|job|pending|start` for the status's three keys), `stale` (a pid or task past 3 h). A block's reason names each
unblocked item by `DAEO-uNNN` and no waiting or closed one.

### The one open interface point

`GOV_SESSION_WATCH_PS`: Interface item 6 says "a JSON list of {pid, cmdline, start, state, fds} in place of /proc". The
reference it was named after (`GOV_STOPIDLE_PROC`) holds the PATH of a file containing the list. The tests set the variable
to the path of a file holding the list (`w2_159_support.PS_AS_FILE = True`); one switch there makes it the JSON text
instead. The ticket's Interface should say which.

## KPI lines, tests, and the outcome on `w2/integrate` (today: no `gov session-watch`)

Run as above on the integrated code: **84 collected, 84 red**, none skipped. Every red fails for the reason in the last
column; none fails on a premise or an error in the test. Against a throwaway model of the command (kept out of the
repository, not the engineer's) all 84 pass, and three mutations of it (a stale pid counted as running; no once-a-turn
bound; the stand-by note always honoured) each turn the cases that name them red.

| KPI id | tests | expected red reason |
|---|---|---|
| S1 | `test_s1_waiter.py::test_s1_waiter_absent_blocks_naming_the_waiter_and_its_arm_command`<br>`test_s1_waiter.py::test_s1_waiter_arm_defaults_to_the_first_waiter_command`<br>`test_s1_waiter.py::test_s1_a_running_waiter_says_nothing[first-command]`<br>`test_s1_waiter.py::test_s1_a_running_waiter_says_nothing[second-command]`<br>`test_s1_waiter.py::test_s1_a_process_that_only_resembles_the_waiter_does_not_count`<br>`test_s1_waiter.py::test_s1_a_stand_by_note_younger_than_the_limit_says_nothing`<br>`test_s1_waiter.py::test_s1_a_stand_by_note_older_than_the_limit_blocks_again`<br>`test_s1_waiter.py::test_s1_the_stand_by_limit_is_the_configured_one[note-past-a-1h-limit]`<br>`test_s1_waiter.py::test_s1_the_stand_by_limit_is_the_configured_one[note-within-a-4h-limit]`<br>`test_s1_waiter.py::test_s1_another_sessions_id_says_nothing`<br>`test_s1_waiter.py::test_s1_no_session_file_says_nothing`<br>`test_s1_waiter.py::test_s1_a_session_file_that_is_a_folder_says_nothing`<br>`test_s1_waiter.py::test_s1_a_session_file_with_mode_000_says_nothing`<br>`test_s1_waiter.py::test_s1_without_waiter_commands_the_check_says_nothing[unset]`<br>`test_s1_waiter.py::test_s1_without_waiter_commands_the_check_says_nothing[empty]` | every case fails at `gov: error: argument <command>: invalid choice: 'session-watch'` (the check must exit 0; it exits 2): there is no `gov session-watch` yet |
| S2 | `test_s2_idle.py::test_s2_unblocked_items_and_nothing_running_block_naming_each_item`<br>`test_s2_idle.py::test_s2_without_a_status_file_unblocked_items_still_block`<br>`test_s2_idle.py::test_s2_gate_shut_lets_the_turn_end_and_names_the_gate`<br>`test_s2_idle.py::test_s2_disk_gate_shut_lets_the_turn_end_and_names_the_disk`<br>`test_s2_idle.py::test_s2_machine_full_lets_the_turn_end_and_names_it`<br>`test_s2_idle.py::test_s2_every_remaining_item_waiting_on_the_owner_lets_the_turn_end_and_names_the_owner`<br>`test_s2_idle.py::test_s2_an_item_waiting_on_the_owner_beside_an_unblocked_one_still_blocks`<br>`test_s2_idle.py::test_s2_a_live_pid_file_under_three_hours_is_a_running_job`<br>`test_s2_idle.py::test_s2_a_running_entry_in_a_fresh_status_is_a_running_job[running]`<br>`test_s2_idle.py::test_s2_a_running_entry_in_a_fresh_status_is_a_running_job[running_jobs]`<br>`test_s2_idle.py::test_s2_a_running_entry_in_a_fresh_status_is_a_running_job[pending_starts]`<br>`test_s2_idle.py::test_s2_a_running_entry_in_a_status_older_than_five_minutes_is_not_used`<br>`test_s2_idle.py::test_s2_a_pid_past_three_hours_is_named_stale_and_not_counted`<br>`test_s2_idle.py::test_s2_a_stale_pid_beside_a_legitimate_wait_is_named_in_the_message`<br>`test_s2_idle.py::test_s2_a_pid_file_with_an_exit_file_beside_it_is_not_running`<br>`test_s2_idle.py::test_s2_a_pid_whose_process_is_not_alive_is_not_running[absent]`<br>`test_s2_idle.py::test_s2_a_pid_whose_process_is_not_alive_is_not_running[zombie]`<br>`test_s2_idle.py::test_s2_a_pid_whose_process_is_not_alive_is_not_running[exited]`<br>`test_s2_idle.py::test_s2_pid_files_are_found_by_the_default_glob_at_any_depth_under_gov_runtime`<br>`test_s2_idle.py::test_s2_pid_files_are_found_by_the_configured_globs_only`<br>`test_s2_idle.py::test_s2_a_pid_file_outside_the_configured_globs_is_not_counted`<br>`test_s2_idle.py::test_s2_the_dispatchers_status_is_used_only_when_at_most_five_minutes_old[4-min-old-used]`<br>`test_s2_idle.py::test_s2_the_dispatchers_status_is_used_only_when_at_most_five_minutes_old[10-min-old-not-used]`<br>`test_s2_idle.py::test_s2_a_live_background_agent_is_a_running_job`<br>`test_s2_idle.py::test_s2_a_finished_or_long_silent_agent_is_not_running[finished]`<br>`test_s2_idle.py::test_s2_a_finished_or_long_silent_agent_is_not_running[silent-40-min]`<br>`test_s2_idle.py::test_s2_a_live_background_task_is_a_running_job`<br>`test_s2_idle.py::test_s2_a_background_task_past_three_hours_is_named_stale_and_not_counted`<br>`test_s2_idle.py::test_s2_a_task_output_file_no_process_holds_open_is_not_running` | same: `invalid choice: 'session-watch'` |
| S3 | `test_s3_once_a_turn.py::test_s3_a_planted_turn_blocks_once_then_never_again_until_a_new_turn[waiter]`<br>`test_s3_once_a_turn.py::test_s3_a_planted_turn_blocks_once_then_never_again_until_a_new_turn[idle]`<br>`test_s3_once_a_turn.py::test_s3_stop_hook_active_never_blocks[waiter]`<br>`test_s3_once_a_turn.py::test_s3_stop_hook_active_never_blocks[idle]`<br>`test_s3_once_a_turn.py::test_s3_the_bound_is_kept_in_the_state_file[waiter]`<br>`test_s3_once_a_turn.py::test_s3_the_bound_is_kept_in_the_state_file[idle]`<br>`test_s3_once_a_turn.py::test_s3_the_two_checks_share_one_state_file_and_each_keeps_its_own_bound`<br>`test_s3_once_a_turn.py::test_s3_a_tool_result_does_not_start_a_new_turn[waiter]`<br>`test_s3_once_a_turn.py::test_s3_a_tool_result_does_not_start_a_new_turn[idle]`<br>`test_s3_once_a_turn.py::test_s3_a_scheduled_wakeup_entry_starts_a_new_turn[wakeupSource-waiter]`<br>`test_s3_once_a_turn.py::test_s3_a_scheduled_wakeup_entry_starts_a_new_turn[wakeupSource-idle]`<br>`test_s3_once_a_turn.py::test_s3_a_scheduled_wakeup_entry_starts_a_new_turn[turnOrigin-waiter]`<br>`test_s3_once_a_turn.py::test_s3_a_scheduled_wakeup_entry_starts_a_new_turn[turnOrigin-idle]`<br>`test_s3_once_a_turn.py::test_s3_a_meta_user_entry_without_an_origin_does_not_start_a_new_turn[waiter]`<br>`test_s3_once_a_turn.py::test_s3_a_meta_user_entry_without_an_origin_does_not_start_a_new_turn[idle]`<br>`test_s3_once_a_turn.py::test_s3_an_idle_reason_line_ends_the_turn_is_logged_and_does_not_carry_into_the_next_turn`<br>`test_s3_once_a_turn.py::test_s3_an_idle_reason_in_an_earlier_turn_does_not_end_this_one`<br>`test_s3_once_a_turn.py::test_s3_an_idle_reason_in_the_hook_inputs_last_assistant_message_ends_the_turn`<br>`test_s3_once_a_turn.py::test_s3_an_idle_reason_line_is_found_among_the_turns_assistant_text_items` | same: `invalid choice: 'session-watch'` |
| S4 | `test_s4_errors.py::test_s4_an_unreadable_state_file_ends_the_turn_names_the_error_and_logs_it[garbage-waiter]`<br>`test_s4_errors.py::test_s4_an_unreadable_state_file_ends_the_turn_names_the_error_and_logs_it[garbage-idle]`<br>`test_s4_errors.py::test_s4_an_unreadable_state_file_ends_the_turn_names_the_error_and_logs_it[folder-waiter]`<br>`test_s4_errors.py::test_s4_an_unreadable_state_file_ends_the_turn_names_the_error_and_logs_it[folder-idle]`<br>`test_s4_errors.py::test_s4_an_unreadable_state_file_is_not_an_error_for_another_session[waiter]`<br>`test_s4_errors.py::test_s4_an_unreadable_state_file_is_not_an_error_for_another_session[idle]`<br>`test_s4_errors.py::test_s4_a_missing_state_file_is_an_empty_state_not_an_error[waiter]`<br>`test_s4_errors.py::test_s4_a_missing_state_file_is_an_empty_state_not_an_error[idle]`<br>`test_s4_errors.py::test_s4_a_stand_by_note_does_not_let_the_idle_check_end_the_turn`<br>`test_s4_errors.py::test_s4_an_unusable_gov_program_is_named_and_does_not_block`<br>`test_s4_errors.py::test_s4_a_missing_item_file_is_named_and_does_not_block` | same: `invalid choice: 'session-watch'` |
| S5 | `test_s5_sources.py::test_s5_the_dispatcher_is_the_default_source_and_its_batch_1_is_named`<br>`test_s5_sources.py::test_s5_the_dispatcher_source_runs_gov_plan_with_root_and_ready`<br>`test_s5_sources.py::test_s5_a_plan_with_nothing_in_batch_1_leaves_no_unblocked_item`<br>`test_s5_sources.py::test_s5_a_file_source_with_the_lines_reader_names_the_same_items`<br>`test_s5_sources.py::test_s5_the_lines_reader_with_every_item_waiting_or_closed_leaves_none_unblocked`<br>`test_s5_sources.py::test_s5_a_file_source_with_a_module_reader_names_the_same_items`<br>`test_s5_sources.py::test_s5_a_module_reader_with_only_owner_waits_and_closed_items_leaves_none_unblocked`<br>`test_s5_sources.py::test_s5_the_file_sources_path_is_relative_to_the_root`<br>`test_s5_sources.py::test_s5_the_code_names_nothing_of_this_repository` | the cases that run the command: `invalid choice: 'session-watch'`; the search case: `src/gov/session_watch does not exist: the check is not built` (it asserts the folder exists first; it fails, it does not skip) |
| F1 | S3's planted-turn cases (a second and a third call in the same turn say nothing): `test_s3_once_a_turn.py::test_s3_a_planted_turn_blocks_once_then_never_again_until_a_new_turn[waiter]`, `test_s3_once_a_turn.py::test_s3_a_planted_turn_blocks_once_then_never_again_until_a_new_turn[idle]`, `test_s3_once_a_turn.py::test_s3_stop_hook_active_never_blocks[waiter]`, `test_s3_once_a_turn.py::test_s3_stop_hook_active_never_blocks[idle]`, `test_s3_once_a_turn.py::test_s3_the_two_checks_share_one_state_file_and_each_keeps_its_own_bound`; and S2's one case per legitimate wait: `test_s2_idle.py::test_s2_gate_shut_lets_the_turn_end_and_names_the_gate`, `test_s2_idle.py::test_s2_disk_gate_shut_lets_the_turn_end_and_names_the_disk`, `test_s2_idle.py::test_s2_machine_full_lets_the_turn_end_and_names_it`, `test_s2_idle.py::test_s2_every_remaining_item_waiting_on_the_owner_lets_the_turn_end_and_names_the_owner`, `test_s2_idle.py::test_s2_a_live_pid_file_under_three_hours_is_a_running_job` | listed under S2 and S3 (not duplicated) |
| F2 | S4's planted unreadable state file, both checks: `test_s4_errors.py::test_s4_an_unreadable_state_file_ends_the_turn_names_the_error_and_logs_it[garbage-waiter]`, `test_s4_errors.py::test_s4_an_unreadable_state_file_ends_the_turn_names_the_error_and_logs_it[garbage-idle]`, `test_s4_errors.py::test_s4_an_unreadable_state_file_ends_the_turn_names_the_error_and_logs_it[folder-waiter]`, `test_s4_errors.py::test_s4_an_unreadable_state_file_ends_the_turn_names_the_error_and_logs_it[folder-idle]`, and the two cases that take "any error" as written: `test_s4_errors.py::test_s4_an_unusable_gov_program_is_named_and_does_not_block`, `test_s4_errors.py::test_s4_a_missing_item_file_is_named_and_does_not_block` | listed under S4 |
| F3 | S5's search of `src/gov/session_watch` for this repository's names: `test_s5_sources.py::test_s5_the_code_names_nothing_of_this_repository` | listed under S5 |
| F4 | not a test: the lead's check (`git diff --name-only` of the ticket's branch against its base lists only paths matched by `allowed_paths`) | none |

Not a KPI line of its own: the hyphenated route (P-W2-159-1 (a)): `test_route.py::test_route_gov_session_watch_help_exits_0`
(red: `invalid choice: 'session-watch'`, exit 2).

Counts by KPI line: S1 15, S2 29, S3 19, S4 11, S5 9, route 1 (84 in all; F1, F2 and F3 are the S2, S3, S4 and S5 cases above).

## Not tested, by design

- The hook's registration in a project's settings and the session-start hook that writes `session.txt` (owner's ACTs).
- Points the ticket's Interface and the lead's reading leave open, so no case plants them (named in the return's
  `unresolved`): the form of `GOV_SESSION_WATCH_PS` (above); that the waiter check itself prints nothing at all (the cases
  assert no block) in its once-a-turn and `stop_hook_active` calls; an `IDLE-REASON` line's effect on the waiter check; the
  `gov plan` exit code (the reference ignores 1) and a plan whose output holds no batch; a stale status file's `running`
  tickets being subtracted from batch 1; the exact words naming each wait; a log line for a call that says nothing.
- A configuration file that does not exist or does not parse (named in the ticket as a residual: out of the check's reach).
