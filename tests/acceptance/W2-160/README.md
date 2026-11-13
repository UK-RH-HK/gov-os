# W2-160 acceptance tests: `gov wait` and `gov session-watch helper-watch`

Ticket DAEO-fd0p (W2-160), profile STANDARD, class C2. Written by the independent test designer (MR-3) from the ticket's KPI
lines S1 to S4 and F1 to F4 and its Interface (I1 `gov wait`, I2 the helper watch: section "P-W2-160-1 decided", PKG-W2-160-IFACE-1),
before any implementation. Nothing of `src/gov/wait/`, `src/gov/session_watch/helper_watch.py`, `tests/unit/wait/` or
`tests/unit/session_watch/test_w2_160*` was read. The code read is `w2/integrate`'s (W2-159's `config.py`, `state.py` and `command.py`;
`gov.cli.main`'s convention) and the reference scripts `wait_for.sh` and `helper_watch.py` (read for behaviours and planted forms; no
test targets them; where they differ from the KPI lines or I1/I2, the KPI lines and I1/I2 rule).

## How they run

    mkdir -p $TMPDIR/w2-160-td && env TMPDIR=$TMPDIR/w2-160-td HOME=<an empty folder> PYTHONUSERBASE=$HOME_REAL/.local \
      PYTHONPATH=<worktree>/src bash <heavy_slot.sh> python3 -m pytest tests/acceptance/W2-160 -q -p no:cacheprovider \
      -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"

About 15 s for the 66 cases (a child process per run of a command; the only waits are S1's 2-second stand-in job, the 1-second
bounds of the RUNNING cases and the 2-pass loop case). The filter leaves out nothing: no case is named with `real`, `green_here` or
`time_limit` and none is marked `local_only`. A case skips only where `/proc` cannot show a zombie (`test_s2_a_zombie_job_counts_as_gone`,
`test_s3_a_zombie_worker_is_gone`).

## What is planted (never a live session, never a hook, never `~/.claude`)

Everything is under the test's `tmp_path` (`w2_160_support.Wait`, `Watch`, `Procs`). Both commands run as a child process,
`python -B -m gov.cli.main wait ...` and `... session-watch helper-watch --root <root> --once ...`, with the tree under test's `src` on
`PYTHONPATH`, a clean environment (no `GOV_*` or `GIT_*` of the running session; `HOME` a temporary folder) and the Interface's test
hooks. Stand-in processes are small Python children, killed and reaped by the pid held in the `procs` fixture's teardown (never by name).

| planted | form |
|---|---|
| exit file | `<base>.exit` (the number and a newline; `abc`; empty; a code over 255); a stand-in job writes it atomically after 2 s |
| pid file | `<base>.pid` holding a pid: a killed-and-reaped stand-in (gone), a running one (alive), a zombie (a child killed, never reaped by its parent, state `Z` in `/proc`), a second process of the same command line left running beside a killed one |
| log, tail | `<base>.log`, `<base>.json` (launcher lines, then one `{"type":"result","session_id",..,"is_error",..,"num_turns",..,"result"}` object), `<base>.txt`, `<base>.summary`; `GOV_WAIT_LOG`, `GOV_WAIT_LINES`, `GOV_WAIT_EVERY` (0.2) |
| registered session | `<root>/.gov-runtime/session-watch/session.txt` (the id and a newline); absent for the no-session case |
| helpers | `GOV_SESSION_WATCH_SUBAGENTS` folder holding `agent-<id>.jsonl` (JSON lines: `type`, ISO-UTC `timestamp`, `message`) and `agent-<id>.meta.json` (`description`, `agentType`, and `finished: true` when finished); or, with the variable unset, `<HOME>/.claude/projects/<root's path, each char not a letter, digit or `-` as `-`>/<session>/subagents/` |
| error entries | an assistant entry with `isApiErrorMessage: true`; one with `apiError: "ECONNRESET"` alone; the client's synthetic form (`model: "<synthetic>"`, fixed text); bookkeeping entries (`queue-operation`) after the error; an error followed by a normal reply |
| workers | `<root>/.gov-runtime/jobs/launch/<name>.pid|.exit|.json` (default `pid_globs`), `.gov-runtime/a/b/c/` (any depth), or a configured `pid_globs` folder; `.json` holds two launcher lines then the result object |
| clock | `GOV_SESSION_WATCH_NOW` = one fixed epoch second per test; every file's mtime (`os.utime`) and every entry's `timestamp` are relative to it; where "no entry for 30 minutes" could be read from the entry's `timestamp` or the file's mtime, both agree (both old for a stalled case, both fresh for a healthy one) |
| text canary | `CANARY-7f3a91c4d2b8e605-<label>` is the text of every planted message: user prompts, assistant text, tool inputs, tool results, error entries (not the synthetic form) and every worker `.json`'s `result` |
| configuration | `<root>/governance/project/session-watch.yaml`, `session_watch:` with `pid_globs` (a list of globs; `5` for the configuration error) |

The first-pass plant (`plant_all`) holds seven conditions and four healthy subjects in one root: helpers `apierr01` (`isApiErrorMessage`),
`apierr02` (`apiError` only), `stall01` (not finished, last entry 31 minutes old); workers `wk-gone` (dead pid, no `.exit`), `wk-exit3`
(`.exit` 3), `wk-iserr` (`.exit` 0, result `is_error: true`), `wk-apistat` (`.exit` 0, result `api_error_status: 529`); healthy:
`fin01` (finished, fresh), `live01` (not finished, fresh), `wk-run` (live pid, no `.exit`), `wk-clean` (`.exit` 0, clean result).

## KPI lines, tests and the expected red on today's code (no `gov wait`, no `helper-watch` action)

Red here: **66 collected, 66 red**, none skipped. Each fails for the reason in the last column; none fails on an error of
the test (a collection error or a fixture fault). Against a throwaway model of I1 and I2 (kept out of the repository, not the engineer's)
all 66 pass, and twelve mutations of it (dedup keyed by the minute count; a message's text copied into the item; the wait ignoring
the pid; a stray lock file written; a `["ps", ...]` list in the source; the window ignored for transcripts and for pid files; no cap; no
modulo; stalled regardless of `finished`; an old exit file counted) each turn the case that names them red.

| KPI id | tests | expected red reason |
|---|---|---|
| S1 | `test_s1_wait.py::test_s1_a_job_writing_its_exit_file_after_two_seconds_has_its_code_printed_and_returned`<br>`test_s1_wait.py::test_s1_a_never_written_exit_file_at_max_s_1_is_running_exit_124_inside_the_bound`<br>`test_s1_wait.py::test_s1_an_empty_exit_file_is_not_an_exit_file_yet`<br>`test_s1_wait.py::test_s1_a_max_s_over_570_is_capped_and_says_so_on_stderr[9999-True]`<br>`test_s1_wait.py::test_s1_a_max_s_over_570_is_capped_and_says_so_on_stderr[571-True]`<br>`test_s1_wait.py::test_s1_a_max_s_over_570_is_capped_and_says_so_on_stderr[570-False]`<br>`test_s1_wait.py::test_s1_a_max_s_over_570_is_capped_and_says_so_on_stderr[1-False]`<br>`test_s1_wait.py::test_s1_the_exit_code_is_the_jobs_code_modulo_256[0-0]`<br>`test_s1_wait.py::test_s1_the_exit_code_is_the_jobs_code_modulo_256[3-3]`<br>`test_s1_wait.py::test_s1_the_exit_code_is_the_jobs_code_modulo_256[255-255]`<br>`test_s1_wait.py::test_s1_the_exit_code_is_the_jobs_code_modulo_256[256-0]`<br>`test_s1_wait.py::test_s1_the_exit_code_is_the_jobs_code_modulo_256[300-44]`<br>`test_s1_wait.py::test_s1_a_json_log_prints_the_result_objects_session_id_and_is_error`<br>`test_s1_wait.py::test_s1_the_summary_file_is_printed_when_there`<br>`test_s1_wait.py::test_s1_the_tail_is_the_last_30_lines_of_the_log_by_default`<br>`test_s1_wait.py::test_s1_gov_wait_lines_sets_the_tail_length`<br>`test_s1_wait.py::test_s1_the_log_is_the_first_of_log_json_txt_that_exists[.log]`<br>`test_s1_wait.py::test_s1_the_log_is_the_first_of_log_json_txt_that_exists[.json]`<br>`test_s1_wait.py::test_s1_the_log_is_the_first_of_log_json_txt_that_exists[.txt]`<br>`test_s1_wait.py::test_s1_gov_wait_log_names_the_tail_file_instead`<br>`test_s1_wait.py::test_s1_a_job_with_no_log_still_returns_its_code` | every case that runs the command fails at `gov: error: argument <command>: invalid choice: 'wait'` (exit 2, not the case's code) |
| S2 | `test_s2_gone.py::test_s2_a_job_killed_before_writing_its_exit_file_is_gone_exit_125_within_a_poll_period`<br>`test_s2_gone.py::test_s2_a_second_process_of_the_same_command_line_does_not_keep_the_wait_alive`<br>`test_s2_gone.py::test_s2_a_zombie_job_counts_as_gone`<br>`test_s2_gone.py::test_s2_a_live_job_without_its_exit_file_is_running_not_gone`<br>`test_s2_gone.py::test_s2_a_job_that_wrote_its_exit_file_and_then_exited_is_done_not_gone`<br>`test_s2_gone.py::test_s2_a_live_pid_does_not_hold_back_a_written_exit_file`<br>`test_s2_gone.py::test_s2_an_exit_file_holding_no_number_is_exit_2`<br>`test_s2_gone.py::test_s2_a_max_s_that_is_not_a_number_is_exit_2`<br>`test_s2_gone.py::test_s2_no_arguments_is_exit_2` | every case that runs the command fails at `gov: error: argument <command>: invalid choice: 'wait'` (exit 2, not the case's code); the three exit-2 cases fail for it too (they assert `invalid choice` is absent from stderr, since an unknown command also exits 2) |
| S3 | `test_s3_helper_watch.py::test_s3_one_item_per_condition_each_naming_its_subject_and_none_for_the_healthy`<br>`test_s3_helper_watch.py::test_s3_a_second_pass_writes_no_new_item_at_the_same_clock_or_a_little_later`<br>`test_s3_helper_watch.py::test_s3_the_state_file_and_the_log_record_each_pass`<br>`test_s3_helper_watch.py::test_s3_a_condition_that_drops_out_of_one_pass_and_comes_back_is_not_reported_twice`<br>`test_s3_helper_watch.py::test_s3_no_registered_session_means_no_helper_is_looked_at`<br>`test_s3_helper_watch.py::test_s3_a_helper_that_recovered_after_an_api_error_is_not_reported`<br>`test_s3_helper_watch.py::test_s3_entries_that_are_not_messages_after_the_error_do_not_hide_it`<br>`test_s3_helper_watch.py::test_s3_the_clients_synthetic_error_form_is_found`<br>`test_s3_helper_watch.py::test_s3_a_helper_not_finished_is_stalled_after_stale_min_minutes[29-min-under-the-default]`<br>`test_s3_helper_watch.py::test_s3_a_helper_not_finished_is_stalled_after_stale_min_minutes[31-min-over-the-default]`<br>`test_s3_helper_watch.py::test_s3_a_helper_not_finished_is_stalled_after_stale_min_minutes[31-min-but-finished]`<br>`test_s3_helper_watch.py::test_s3_a_helper_not_finished_is_stalled_after_stale_min_minutes[15-min-over-stale-min-10]`<br>`test_s3_helper_watch.py::test_s3_a_helper_not_finished_is_stalled_after_stale_min_minutes[15-min-under-stale-min-20]`<br>`test_s3_helper_watch.py::test_s3_an_exit_file_counts_only_if_not_older_than_the_start_less_every[exit-file-600s-old-every-300]`<br>`test_s3_helper_watch.py::test_s3_an_exit_file_counts_only_if_not_older_than_the_start_less_every[exit-file-100s-old-every-300]`<br>`test_s3_helper_watch.py::test_s3_an_exit_file_counts_only_if_not_older_than_the_start_less_every[exit-file-600s-old-every-1000]`<br>`test_s3_helper_watch.py::test_s3_each_helper_item_carries_its_last_entrys_type_or_time`<br>`test_s3_helper_watch.py::test_s3_pid_files_are_found_by_the_default_glob_at_any_depth_under_gov_runtime`<br>`test_s3_helper_watch.py::test_s3_the_configured_pid_globs_replace_the_default`<br>`test_s3_helper_watch.py::test_s3_a_pid_globs_of_the_wrong_kind_is_a_configuration_error_exit_1_naming_the_key`<br>`test_s3_helper_watch.py::test_s3_a_zombie_worker_is_gone`<br>`test_s3_helper_watch.py::test_s3_a_live_worker_with_no_exit_file_is_not_reported`<br>`test_s3_helper_watch.py::test_s3_a_clean_exit_with_a_clean_result_is_not_reported`<br>`test_s3_helper_watch.py::test_s3_helpers_default_to_the_claude_projects_folder_of_the_root`<br>`test_s3_helper_watch.py::test_s3_the_loop_ends_after_max_with_one_ended_line_and_writes_each_item_once` | every case fails at `gov session-watch: error: argument stop-check: invalid choice: 'helper-watch'` (the case expects exit 0, or exit 1 for the configuration error; it gets 2) |
| S4 | `test_s4_reads_and_writes.py::test_s4_a_planted_message_text_is_never_in_an_item_the_state_the_log_or_the_output`<br>`test_s4_reads_and_writes.py::test_s4_only_the_inbox_the_state_file_and_the_log_are_new_or_changed`<br>`test_s4_reads_and_writes.py::test_s4_an_error_found_writes_nothing_else_either`<br>`test_s4_reads_and_writes.py::test_s4_only_a_transcript_whose_last_entry_is_inside_the_window_is_looked_at[25h-old-window-24]`<br>`test_s4_reads_and_writes.py::test_s4_only_a_transcript_whose_last_entry_is_inside_the_window_is_looked_at[23h-old-window-24]`<br>`test_s4_reads_and_writes.py::test_s4_only_a_transcript_whose_last_entry_is_inside_the_window_is_looked_at[25h-old-window-48]`<br>`test_s4_reads_and_writes.py::test_s4_a_stalled_helper_older_than_the_default_window_is_not_looked_at`<br>`test_s4_reads_and_writes.py::test_s4_a_pid_file_older_than_the_window_is_skipped[pid-file-25h-old]`<br>`test_s4_reads_and_writes.py::test_s4_a_pid_file_older_than_the_window_is_skipped[pid-file-23h-old]`<br>`test_s4_reads_and_writes.py::test_s4_the_helper_watch_matches_no_process_by_name`<br>`test_s4_reads_and_writes.py::test_s4_gov_wait_matches_no_process_by_name` | every case fails at `gov session-watch: error: argument stop-check: invalid choice: 'helper-watch'` (the case expects exit 0, or exit 1 for the configuration error; it gets 2); the two source searches fail at `src/gov/wait does not exist: gov wait is not built` and `src/gov/session_watch/helper_watch.py does not exist: the helper watch is not built` (each asserts the file or folder exists first: it fails, it does not skip) |
| F1 | `test_s1_wait.py::test_s1_a_never_written_exit_file_at_max_s_1_is_running_exit_124_inside_the_bound`<br>`test_s2_gone.py::test_s2_a_job_killed_before_writing_its_exit_file_is_gone_exit_125_within_a_poll_period`<br>`test_s2_gone.py::test_s2_a_second_process_of_the_same_command_line_does_not_keep_the_wait_alive` | listed under S1 and S2 (not duplicated) |
| F2 | `test_s4_reads_and_writes.py::test_s4_a_planted_message_text_is_never_in_an_item_the_state_the_log_or_the_output`<br>`test_s4_reads_and_writes.py::test_s4_the_helper_watch_matches_no_process_by_name`<br>`test_s4_reads_and_writes.py::test_s4_gov_wait_matches_no_process_by_name` | listed under S4 (not duplicated) |
| F3 | `test_s3_helper_watch.py::test_s3_a_second_pass_writes_no_new_item_at_the_same_clock_or_a_little_later`<br>`test_s3_helper_watch.py::test_s3_the_state_file_and_the_log_record_each_pass`<br>`test_s3_helper_watch.py::test_s3_a_condition_that_drops_out_of_one_pass_and_comes_back_is_not_reported_twice` | listed under S3 (not duplicated) |

F4 (a change outside the ticket's `allowed_paths`) is the lead's check (`git diff --name-only`), not a test.

## What the cases assert (the lead's reading where I1/I2 are silent)

- `gov wait`: the code, `wait: DONE exit <n>`, `RUNNING`, `GONE` (and the pid) on standard output; `capped at 570` (and the value) on
  standard error; the tail by its lines (the last 30 by default, `GOV_WAIT_LINES`), the first of `<base>.log`, `.json`, `.txt` that
  exists, `GOV_WAIT_LOG` instead; for a JSON log the result object's `session_id`, the word `is_error` with its value `true` and the end of
  its `result`; `<base>.summary`. An exit file that is empty is not yet an exit file. Timing: `RUNNING` at `<max-s>` 1 ends in 0.9 to 6 s;
  `GONE` ends in under 6 s with `<max-s>` 20 (poll period 0.2 s).
- The three exit-2 cases (`abc`, `x`, no arguments) also assert `invalid choice` is not on standard error, so that an unknown command's exit
  2 is not taken for the command's own.
- The helper watch: one item per condition in `<root>/.gov-runtime/dispatch/inbox/`, named `<yyyymmdd-HHMMSS>-helper-watch[-<n>].txt`,
  naming the helper's id or the worker's base name (its log is `<base>.json`) and no other planted subject; standard output one
  `HELPER_WATCH item <path>` per item written, no more; nothing for the healthy; nothing on a later pass (same clock and clock +120 s);
  a condition that drops out of a pass and comes back is not reported again (the state only grows); the state file after a no-change pass
  is as it was; the log has one JSON line per pass naming the items that pass wrote.
- The conditions: `api-error` (the last assistant, user or system entry; entries of other types after it do not hide it; a normal reply
  after it clears it); `stalled` (not finished and no entry for `--stale-min` minutes: 29 min no, 31 min yes, 31 min finished no,
  `--stale-min 10` and 20); `worker gone` (no `.exit`, pid gone, a zombie counts); `worker ended with an error` (`.exit` not 0, or the
  last JSON object's `is_error` or `api_error_status`); an exit file counts only when its mtime is at or after the clock less `--every`
  (600 s old no and 100 s old yes at 300; 600 s old yes at 1000). The window: a transcript whose last entry is 25 h old is skipped and
  23 h is looked at with `--window-h 24`; 25 h is looked at with 48; a pid file's mtime likewise.
- Safety: the canary is found 0 times in an item, the state file, the log, standard output or standard error, over two passes; a snapshot
  of the root, HOME, the temporary folder and the session folder (path, size, mtime) before and after each pass shows only files under
  `.gov-runtime/dispatch/inbox/`, `helper-watch-state.json` and `helper-watch.log` new or changed (so no lock file); the code of
  `src/gov/session_watch/helper_watch.py` and of every `.py` under `src/gov/wait/` holds no process-name match (below).
- The source search reads the CODE: string constants (docstrings left out), names, attributes and imports of the parsed file; whole tokens
  `pgrep pkill killall pidof psutil proc.sh /cmdline /comm`, the string `"ps"` and `ps -`. A comment or a docstring that names one (to say it is
  not used) is no hit.

## Not tested, by design

- F4 (the lead's).
- The default and ceiling 570 s as a real wait (a 570-second test); the cap is shown by the line on standard error for 571 and above and the
  absence of it at 570 and below.
- `gov wait`'s `num_turns` (the cases do not assert its value or its label), and the exact words of every line I1 does not quote.
- `<base>` of an exit file whose name does not end in `.exit`; a pid file that holds no number; a pid file with no `.exit` and an unreadable
  `.json`.
- Workers when `session.txt` is missing (I2 settles only that no helper is looked at).
- Whether `--once` prints the "ended" line (I2 gives it for `--max` only).
- The item's text beyond the name and a last-line hint (the entry's type or its timestamp); the synthetic form's fixed text may or may not be
  copied into the item (the case asserts only that the helper is named).
- The check/commands.py line and the help listing (the lead's check).
