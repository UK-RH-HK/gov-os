# W2-121c acceptance tests: the run-time tool, slice 1

Ticket DAEO-5rgj (W2-121c), profile FULL. Written by the independent test designer (MR-3) from the ticket's ten success
lines, two failure lines and its `## Interface` section, before any implementation, on the base `61629dda8`. The code
read is the integrated public surface (`gov.cli.main`, `gov dispatch`, `gov.resources.machine`, the registry,
`gov launch` and its acceptance harnesses), never this ticket's branch.

## How they run

    env TMPDIR=$(mktemp -d) HOME=<an empty folder> PYTHONUSERBASE=$HOME_REAL/.local PYTHONPATH=<worktree>/src \
      python3 -m pytest tests/acceptance/W2-121c -q -p no:cacheprovider -o tmp_path_retention_policy=failed -n 6

52 cases, each a few seconds (child `gov` processes, stubs, real `sleep` processes; no model, no network, no real
`claude`, never the real `~/.gov-os`). No wait is longer than 10 s: `gov msg wait` runs with `--timeout` 2 to 9. All are
acceptance tests; none is `local_only`.

## What is planted

- **`w2_121c_support.Box`**: one fixture machine under `tmp_path`: a `HOME`, a `TMPDIR`, a stub folder first on a `PATH`
  of `<stubs>:/usr/local/bin:/usr/bin:/bin` (the machine's own `nvidia-smi` in `/usr/lib/wsl/lib` is never reached),
  `GOV_RESOURCES_NPROC`, and `GOV_RESOURCES_MEMINFO` naming a planted file with `MemTotal:` and `MemAvailable:`.
  The `nvidia-smi` stand-in answers the two queries `gov.resources.machine.gpu` sends (`--query-gpu=...` with total,
  used, free, utilisation; `--query-compute-apps=...` empty), or fails (exit 9, the driver message), or is absent.
- Every `gov` runs as `python3 -m gov.cli.main ...` in a plain folder with no `dispatch.yaml`.
- **Registry entries** are written as the registry writes them (`~/.gov-os/machine/sessions/<pid>.json`, whole), with
  `boot` and `start_ticks` read from `/proc` as `gov.resources.machine.identity` reads them, for real `sleep` processes
  (ended and reaped where the case needs an end).
- **Concurrency** (8 senders, 2 readers; 4 senders of one id): child processes calling gov's entry point
  (`gov.cli.main.main`) in a loop after one go file appears.
- **No process left behind**: the pass runs under a wrapper that is a child subreaper (`PR_SET_CHILD_SUBREAPER`); what
  the pass left running is the wrapper's live children half a second after the pass returned.
- **`gov launch`** (RT-2a, RT-8, F1's first case): W2-184's support module and, through it, W2-60a's, imported
  unchanged (W2-184's fixture project with role tables and `criticality.yaml`, or without the file; a C2 engineer
  ticket; W2-60a's recording stand-in CLI and open resource gate). A small wrapper in front of the stand-in captures the
  session's own registry entry while it runs and can hold the session until a release file appears.
- Messages are read straight from `messages.jsonl` (no mark moved); `state.json` and `log.jsonl` straight from
  `~/.gov-os/runtime/`.

## KPI line to tests

KPI ids name the ticket's lines by position (success 1 to 10, failure 1 and 2), the RT id beside each as a note.
Every item is a test function (a parametrised one covers all its rows). "Red on the base": what fails on `61629dda8`.

| KPI id | tests | expected red reason |
|---|---|---|
| S1 (RT-6a) | `test_w2_121c_rt6_inbox.py::test_rt6a_a_send_appends_one_json_line_and_two_reads_print_it_once` | no `gov msg` (exit 2, invalid choice 'msg') |
| S1 (RT-6a) | `test_w2_121c_rt6_inbox.py::test_rt6a_read_json_moves_the_mark_to_the_end_of_what_it_read` | no `gov msg` (exit 2) |
| S1 (RT-6a) | `test_w2_121c_rt6_inbox.py::test_rt6a_peek_prints_without_moving_the_mark` | no `gov msg` (exit 2) |
| S1 (RT-6a) | `test_w2_121c_rt6_inbox.py::test_rt6a_the_address_defaults_to_gov_msg_address` | no `gov msg` (exit 2) |
| S1 (RT-6a) | `test_w2_121c_rt6_inbox.py::test_rt6a_no_address_and_no_gov_msg_address_is_refused` | exit 2, not 1 with `MSG_ADDRESS_MISSING` |
| S1 (RT-6a) | `test_w2_121c_rt6_inbox.py::test_rt6a_two_sessions_in_two_repositories_exchange_messages_with_no_relay` | no `gov msg` (exit 2) |
| S1 (RT-6a) | `test_w2_121c_rt6_inbox.py::test_rt6a_eight_concurrent_senders_give_400_whole_lines_each_read_exactly_once` | the concurrent sends exit 2 |
| S1 (RT-6a) | `test_w2_121c_rt6_inbox.py::test_rt6a_an_address_with_a_slash_or_dotdot_is_refused_and_nothing_is_written` | exit 2, not 1 with `MSG_ADDRESS_INVALID` |
| S2 (RT-6b) | `test_w2_121c_rt6_inbox.py::test_rt6b_the_same_id_sent_twice_leaves_one_line_the_second_a_duplicate` | no `gov msg` (exit 2) |
| S2 (RT-6b) | `test_w2_121c_rt6_inbox.py::test_rt6b_the_same_id_sent_concurrently_from_four_processes_leaves_one_line` | the concurrent sends exit 2 |
| S2 (RT-6b) | `test_w2_121c_rt6_inbox.py::test_rt6b_an_id_is_a_duplicate_only_in_its_own_inbox` | no `gov msg` (exit 2) |
| S3 (RT-7a) | `test_w2_121c_rt7_wait.py::test_rt7a_a_wake_already_unread_returns_0_at_once_printing_it_mark_unmoved` | no `gov msg` (exit 2) |
| S3 (RT-7a) | `test_w2_121c_rt7_wait.py::test_rt7a_a_wake_sent_2_s_after_the_wait_began_returns_0_within_5_s` | no `gov msg` (exit 2) |
| S3 (RT-7a) | `test_w2_121c_rt7_wait.py::test_rt7a_only_notices_unread_keeps_waiting_and_exits_124_at_the_timeout` | no `gov msg` (exit 2) |
| S3 (RT-7a) | `test_w2_121c_rt7_wait.py::test_rt7a_every_wake_already_read_exits_124_at_the_timeout` | no `gov msg` (exit 2) |
| S4 (RT-7b) | `test_w2_121c_rt7_watch_pass.py::test_rt7b_after_five_passes_the_runtime_folder_holds_state_json_and_log_jsonl_only` | no `gov msg watch` (exit 2) |
| S4 (RT-7b) | `test_w2_121c_rt7_watch_pass.py::test_rt7b_a_pass_while_the_lock_is_held_exits_4_and_writes_nothing` | no `gov dispatch watch` (exit 2) |
| S4 (RT-7b) | `test_w2_121c_rt7_watch_pass.py::test_rt7b_no_process_of_the_pass_is_alive_after_it_returns` | no `gov msg watch` (exit 2) |
| S5 (RT-2a) | `test_w2_121c_rt2_launch_end.py::test_rt2a_the_end_is_one_wake_message_to_the_launching_address_naming_role_ticket_and_exit_code` | no wake message in `lead:DAEO-x`'s inbox within 5 s of the end |
| S5 (RT-2a) | `test_w2_121c_rt2_launch_end.py::test_rt2a_without_gov_msg_address_the_end_message_goes_to_cto` | no wake message in `cto`'s inbox within 5 s of the end |
| S6 (RT-2b) | `test_w2_121c_rt2_watch_ends.py::test_rt2b_a_session_that_ends_between_two_passes_gives_one_message_after_the_second` | no `gov dispatch watch` (exit 2) |
| S6 (RT-2b) | `test_w2_121c_rt2_watch_ends.py::test_rt2b_an_entry_dead_at_the_first_pass_gives_one_message_to_cto_without_notify` | no `gov dispatch watch` (exit 2) |
| S6 (RT-2b) | `test_w2_121c_rt2_watch_ends.py::test_rt2b_a_pid_that_now_belongs_to_another_process_is_an_end` | no `gov dispatch watch` (exit 2) |
| S6 (RT-2b) | `test_w2_121c_rt2_watch_ends.py::test_rt2b_a_pid_watch_gives_one_message_when_the_process_is_gone` | no `gov msg watch` (exit 2) |
| S6 (RT-2b) | `test_w2_121c_rt2_watch_ends.py::test_rt2b_an_exit_file_watch_gives_one_message_naming_the_exit_code` | no `gov msg watch` (exit 2) |
| S6 (RT-2b) | `test_w2_121c_rt2_watch_ends.py::test_rt2b_an_end_the_launcher_already_messaged_adds_none` | no `gov msg` (exit 2) |
| S7 (RT-2c) | `test_w2_121c_rt2_stall.py::test_rt2c_a_silent_transcript_gives_one_message_per_incident` | no `gov msg watch` (exit 2) |
| S7 (RT-2c) | `test_w2_121c_rt2_stall.py::test_rt2c_a_transcript_within_the_limit_gives_none` | no `gov msg watch` (exit 2) |
| S7 (RT-2c) | `test_w2_121c_rt2_stall.py::test_rt2c_the_default_limit_is_3600_s` | no `gov msg watch` (exit 2) |
| S7 (RT-2c) | `test_w2_121c_rt2_stall.py::test_rt2c_a_folder_is_read_by_its_newest_file` | no `gov msg watch` (exit 2) |
| S8 (RT-3a) | `test_w2_121c_rt3_limits.py::test_rt3a_each_limit_follows_its_rule_on_two_planted_profiles_and_three_differ` | no `gov dispatch limits` (exit 2) |
| S8 (RT-3a) | `test_w2_121c_rt3_limits.py::test_rt3a_the_text_form_names_the_machine_and_each_limit_with_its_value_and_rule` | no `gov dispatch limits` (exit 2) |
| S8 (RT-3a) | `test_w2_121c_rt3_limits.py::test_rt3a_changing_the_planted_profile_between_two_passes_changes_state_json_limits` | no `gov dispatch watch` (exit 2) |
| S8 (RT-3a) | `test_w2_121c_rt3_limits.py::test_rt3a_a_measured_size_in_gate_json_binds_where_its_ram_term_is_smaller` | no `gov dispatch limits` (exit 2) |
| S8 (RT-3a) | `test_w2_121c_rt3_limits.py::test_rt3a_with_no_gpu_the_budget_is_0` | no `gov dispatch limits` (exit 2) |
| S9 (RT-3b) | `test_w2_121c_rt3_limits.py::test_rt3b_admit_exit_0_when_used_plus_need_stays_within_the_budget` | exit 2, not 0 (no `gov dispatch limits`) |
| S9 (RT-3b) | `test_w2_121c_rt3_limits.py::test_rt3b_wait_exit_3_with_the_reason_when_used_plus_need_exceeds_the_budget` | exit 2, not 3 (no `gov dispatch limits`) |
| S9 (RT-3b) | `test_w2_121c_rt3_limits.py::test_rt3b_with_no_gpu_the_answer_is_wait_naming_no_gpu` | exit 2, not 3 (no `gov dispatch limits`) |
| S10 (RT-8) | `test_w2_121c_rt8_launch_line.py::test_rt8_the_launch_line_names_model_effort_their_sources_the_class_and_the_rubric_file` | no stderr line naming the rubric |
| S10 (RT-8) | `test_w2_121c_rt8_launch_line.py::test_rt8_without_criticality_yaml_the_line_says_no_rubric_and_the_record_holds_null` | no stderr line naming the rubric |
| F1 | `test_w2_121c_f1_once.py::test_f1_an_end_the_launcher_messaged_and_the_pass_also_sees_is_one_message` | no `gov dispatch watch` (exit 2) |
| F1 | `test_w2_121c_f1_once.py::test_f1_an_end_present_through_several_passes_is_one_message` | no `gov dispatch watch` (exit 2) |
| F1 | `test_w2_121c_f1_once.py::test_f1_a_pass_killed_after_sending_but_before_writing_its_state_leaves_one_message` | no `gov msg watch` (exit 2) |
| F2 | `test_w2_121c_f2_problems.py::test_f2_a_fault_is_named_in_problems_and_the_log_and_the_pass_still_sends` | no `gov dispatch watch` (exit 2) |

Count per line: S1 8 functions (11 cases), S2 3, S3 4, S4 3, S5 2, S6 6, S7 4, S8 5 (6 cases), S9 3 (5 cases), S10 2,
F1 3, F2 1 (3 cases: an unreadable registry entry, a missing transcript, a failing `nvidia-smi`).

Red run on the base (`-n 6`): `52 failed in 20.23s` (and `gov accept DAEO-5rgj`: outcome fail, every line 0 passed), every case for the reason above (the command or action does not
exist, or the launcher sends and prints nothing); no harness error.

## The test designer's readings where the Interface is open

- **`gov dispatch limits --json`**: the envelope's `result` holds `machine` (`cpus`, `ram_bytes`, `gpu_total_mib`,
  `gpu_used_mib`) and `limits` (`heavy_slots`, `workers_per_slot`, `sessions_max`, `gpu_budget_mib`), the shape
  state.json gives them. Only those keys are read.
- **The text form of `gov dispatch limits`**: each limit's key and its value on one line, the four ratios of the rules
  as the ticket writes them (`0.15`, `0.9`, `0.5`, `0.875`) somewhere in the output, and the CPU count (32). RAM and
  GPU figures are not pinned in the text (their unit is open).
- **`--gpu-need-mib`'s answer** is read from the text form: the word `admit` with exit 0, the word `wait` with exit 3; a
  `wait` over budget gives its reason, read as naming the budget (`budget` or 21504); with no GPU it names `no GPU`.
  "Never offers the CPU" is read as: no phrase that offers the CPU as a place to run (run, use, fall back, instead,
  spill ... CPU) unless negated ("GPU work is not run on the CPU" is allowed); the CPU count may be printed.
- **gate.json's measured sizes** are planted in W2-20's dated form (`{"value", "date", "source"}`), in a whole gate.json
  that `gov.resources.config.load` reads with no fault.
- **"Naming" in a message** (the role, the ticket, the exit code, the label, the silent minutes) is looked for in the
  message's `text` or `data`. The exit code and the minutes as whole numbers (the minutes 120 or 121 for 2 h).
- **The exit file** holds the code as its text (`3\n`).
- **"Set back again"** (RT-2c) is to another past mtime than the first incident's (3 h, after 2 h): the stall id is
  `stall:<request id>:<mtime>`, so the same mtime twice would be the same id (see the return's note).
- **RT-2a's environment**: `GOV_MSG_ADDRESS` is read from the stand-in process's own environment. The registry entry's
  `notify` and `address` are read from the entry while the session runs (the launcher removes it at the end).
- **RT-2a's "within 5 s of the stub's end"**: polled for 5 s from `gov launch`'s return (which follows the stub's end).
- **RT-8's "one line"**: exactly one stderr line names the rubric file or says "no rubric"; with the file it names the
  model, the effort, `by criticality` (both sources), `C2` and `governance/project/criticality.yaml`; the record's
  `rubric` ends with that path. Without the file the line holds "no rubric: the role's default" and the record's
  `rubric` is null. "Before the session starts" is not observable from the stand-in and is not asserted.
- **RT-7b's log**: at least one `pass` event per pass, every line `{"at", "event", ...}`.
- **RT-7b's "writes nothing"** under a held lock: state.json and log.jsonl byte for byte, the `runtime` inbox's mark,
  and no message sent for a watch that would be due.
- **F1's killed pass** is planted as what such a kill leaves: the messages sent, and state.json put back to the bytes
  of the pass before. The next passes must not send any of the three (session end, pid watch, stall) again.
- **F2's missing transcript**: the transcript existed when the watch was registered and is gone at the pass.
