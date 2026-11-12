# W2-157 evidence: the GPU backstop in the product (DAEO-ozyt)

Engineer, branch `w2/W2-157`. Sources: DEC-1067 (GPU safety), DEC-1068 (4), DEC-1030, DEC-1073 (4), DEC-1119, DEC-1109.

## What was built

| file | change |
|---|---|
| `src/gov/resources/backstop.py` (new) | `watch(groups, root, env=None) -> dict`: the plain poll loop (`time.sleep(every_s)`, no threads), the four triggers in order, the pause by `os.killpg(g, SIGSTOP)` of the live named groups only, the log, the one inbox item |
| `src/gov/resources/command.py` | the one option `--backstop PGID...` in the mutually exclusive mode group (`nargs="+"`, each value a decimal integer above 1, else argparse's usage error naming it); the module docstring line; `ACT_PATHS` now declares the one project path it writes (see reading R3) |
| `src/gov/resources/config.py` | `backstop_values(env)` (the three checks: `({limit_mib, every_s, embedders}, faults)`), `BACKSTOP_ENTRIES` (this machine's three entries) and `backstop_entries(env)` (the same with `$HOME` resolved). `VALUES`, `OPTIONAL`, `load()` and `template()` are untouched |
| `tests/unit/resources/test_w2_157_backstop.py` (new) | 90 cases (the last 10 are L5b's): planted groups (`start_new_session=True`), a stand-in `nvidia-smi`, stand-in HTTP servers on free ports, planted logs, a planted HOME and project |

## KPI lines and the unit tests that show them

| line | unit tests |
|---|---|
| S1 limit, poll, refuse a missing or malformed value | `test_s1_below_then_above_the_limit_pauses_at_the_second_reading` (15,800 no trip, 15,900 trip, job state T, reading logged), `test_s1_the_limit_is_exclusive` (15,872 no, 15,873 yes), `test_s1_the_limit_and_period_are_the_files`, `test_s1_the_query_is_exactly_the_interface_line`, `test_s1_a_missing_key_refuses_to_start_naming_it`, `test_s1_a_malformed_limit_refuses_to_start`, `test_a_malformed_period_refuses_to_start`, `test_a_malformed_embedder_list_refuses_to_start`, `test_a_missing_file_and_a_file_not_json_refuse_to_start`, `test_l1_a_missing_limit_is_exit_1_naming_it` |
| S2 spill | `test_s2_a_reading_within_64_mib_of_the_total_trips` (total minus 65 no trip; minus 64 and minus 63 trip) |
| S3 embedders | `test_s3_a_model_partly_off_the_gpu_trips_it`, `test_s3_a_model_wholly_on_the_gpu_does_not_trip`, `test_s3_a_partial_offload_line_written_since_the_start_trips_it` (a line before the start never counts), `test_s3_an_equal_offload_never_trips_and_a_missing_log_starts_at_zero`, `test_s3_no_answer_or_a_malformed_one_is_no_trip`, `test_s3_no_server_at_the_port_is_no_trip`, `test_s3_the_limit_comes_before_the_spill_before_the_embedder_before_the_log` |
| S4 only the named groups; refuse a bad name; ended group skipped; the inbox item; the watch ends | `test_s4_only_the_named_group_is_stopped_and_a_same_name_process_runs_on`, `test_the_signals_sent_are_killpg_stop_to_the_live_named_groups_and_nothing_else`, `test_l1_a_value_that_is_not_a_group_id_above_1_is_a_usage_error` (abc, 1, 0, -5, 2.5: exit 2, nothing written or read), `test_s4_a_group_that_has_ended_is_skipped_and_named`, `test_s4_a_job_that_ends_first_ends_the_watch_without_a_trip`, `test_s4_no_live_group_at_start_ends_at_once`, `test_s4_the_inbox_item_names_the_reason_the_groups_and_how_to_resume_or_stop`, `test_s4_the_log_lines_begin_with_a_timestamp_and_the_start_line_names_the_config`, `test_s4_the_log_is_appended_never_replaced` |
| S5 nothing else changes | `test_s5_a_run_with_no_trip_writes_only_its_log` (mtime and size of every file under the planted tree: only the log changed, no inbox folder), `test_s5_a_trip_writes_the_log_and_one_item_and_the_inbox_folder` |
| F1 a process outside the groups | `test_s4_only_the_named_group_is_stopped_...` (the unrelated same-name process is still not stopped), `test_the_signals_sent_are_killpg_...` (every `killpg` goes to a named group; `os.kill` is never called) |
| F2 a trip missed or a false trip | the S1, S2 and S3 reading cases above |
| F3 a limit from anywhere but the file | `test_the_environment_never_sets_the_limit_while_a_job_runs` (`LIMIT` set to 100 in the environment: the trip is at the file's 20,000), `test_l1_no_option_sets_the_limit_the_period_or_the_embedders` (exit 2), `test_s1_a_missing_key_...` and `test_s1_a_malformed_limit_...` (refuse, naming the key) |
| F4 any change outside the paths | `git diff --name-only w2/integrate -- . ':!tests/acceptance'` lists only this ticket's `allowed_paths` (checked below) |
| the configuration (L2) | `test_l2_the_template_is_unchanged_and_the_three_keys_are_not_gate_values`, `test_l2_load_ignores_the_three_keys`, `test_l2_this_machines_entries_are_the_constant_and_valid`, `test_l2_the_values_function_returns_values_and_faults`, `test_l2_a_planted_file_made_from_the_constant_is_accepted`, `test_the_file_may_hold_every_other_key_or_none`; W2-20's own `tests/acceptance/W2-20/test_w2_20_config.py` (the frozen `--init-config` key set) stays green |

## The lead's readings L1-L9 as applied

- **L1** `--backstop` is a member of the existing mutually exclusive group; the value type is `_group` in `command.py`; no option or variable reaches the limit, the period or the embedders (an unknown option is argparse's exit 2; `os.environ` is read only for `HOME` and `PATH`).
- **L2** `config.backstop_values`: each key `{"value", "date", "source"}` with a valid date and a non-empty source; the limit an integer of at least 1, the period a number above 0, the embedders a list of `{"port": 1-65535, "log": absolute path}`. Any fault is `GovError("RESOURCE_CONFIG_INVALID")`, exit 1, the message and `details.faults` naming each key (or `gate.json`); it is raised before anything is written or signalled.
- **L3** `nvidia-smi` found on `PATH` (the planted `env`'s), exactly `--query-gpu=memory.used,memory.total --format=csv,noheader,nounits`, once per poll; the first line `<used>, <total>`. Trip on used > limit; trip on used >= total - 64. A reading that cannot be had is logged (`no GPU reading: <why>`) and is no trip.
- **L4** `GET http://127.0.0.1:<port>/api/ps` through an opener with no proxy, a 3 s timeout; a model with `size_vram` < `size` trips, naming the port, the model and `size_vram/size`. Each log's start offset is its size at the start (0 when missing); each poll reads only whole lines appended since; a line `offloaded N/M layers to GPU` with N < M trips, naming the log's path and the matched text.
- **L5** Groups checked with `os.killpg(g, 0)` at the start (ended ones skipped and named) and at each poll's start; none live: `end: every watched group has ended (...)`, exit 0, `tripped: false`. The order of checks: limit, spill, each embedder's `/api/ps`, each embedder's log; SIGSTOP by `os.killpg` to each live named group, and to nothing else.
- **L5b** (added after review round 1's FR-1 and FR-2) When the process group of `gov` itself (`os.getpgrp()`) is among the named groups, it is paused last: the start line ends `; own group <g> named: paused last`; on a trip every other live named group is paused first (SIGSTOP, in the order named), then the TRIP line and the one inbox item are written (the item's `paused:` line lists every paused group, the own one last, then the `resume:` and `stop:` lines and `note: the backstop's own group <g> is paused last; resuming it resumes the backstop, which then ends`), then, last of all, SIGSTOP to the own group, which stops `gov` too. After `kill -CONT -- -<g>` the command ends: exit 0, `tripped: true`, `paused` holding every paused group, the own one included (last). The TRIP line's `paused groups` also lists the own group, which is paused straight after it. When the own group is not named nothing changes (no note, never signalled). Unit tests: `test_l5b_the_own_group_is_stopped_after_every_other_group_the_trip_line_and_the_item` (own group first, middle, last of three: the order of SIGSTOPs, the other two already `T`, one TRIP line and one item present when the own group is stopped), `test_l5b_the_start_line_ends_with_the_own_group_note_and_the_item_carries_the_note_line` (three positions), `test_l5b_the_own_group_named_alone_is_stopped_after_the_trip_line_and_the_item`, `test_l5b_an_ended_group_is_skipped_beside_the_own_group_which_is_still_stopped_last`, `test_l5b_when_the_own_group_is_not_named_there_is_no_note_and_it_is_never_signalled`, and `test_l5b_a_job_sharing_the_backstops_own_group_and_a_second_group_are_both_paused_then_resumed` (the real thing: `gov` in a session of its own with a `&` job in its group and a second group named after it; both stopped, log and item whole, then `kill -CONT` to the own group: exit 0, `tripped: true`, `paused` `[second, own]`). The in-process cases stand a planted group in for the own group by patching `os.getpgrp`; only the last one stops a real `gov`, in a child session.
- **L6** `$HOME/.gov-os/machine/gpu-backstop.log` (`config.machine_dir()`), appended, one line per event, each starting `YYYY-MM-DD HH:MM:SS`, in the forms the Interface gives.
- **L7** `<root>/.gov-runtime/dispatch/inbox/gpu-backstop-<YYYYmmdd-HHMMSS>.txt`, written whole (a dot-named temporary file, then `os.replace`), the folder created if absent; the lines as the Interface gives them.
- **L8** The result is the Interface's dict; `gov.resources.backstop.watch(groups, root, env=None)` is the seam.
- **L9** Reads: `nvidia-smi`'s answer, `/api/ps`, the embedder logs, `gate.json`. Writes: the log and, on a trip, the one item. No server is started, stopped or signalled.

## The operator's step for this machine

`gate.json` is not written by this ticket. The operator adds these three entries to `~/.gov-os/machine/gate.json` (the object's other keys stay as they are); `config.BACKSTOP_ENTRIES` holds them, and `config.backstop_entries()` gives them with `$HOME` resolved:

```json
"gpu_backstop_limit_mib": {"value": 15872, "date": "2026-11-04", "source": "DEC-1067 (GPU safety), DEC-1068 (4): 15.5 GiB, 15,872 MiB"},
"gpu_backstop_every_s": {"value": 5, "date": "2026-11-04", "source": "DEC-1067 (GPU safety), DEC-1068 (4): the poll every 5 seconds"},
"gpu_backstop_embedders": {"value": [{"port": 11434, "log": "/home/usain/.ollama/serve-11434.log"}, {"port": 11435, "log": "/home/usain/.ollama/serve-11435.log"}], "date": "2026-11-04", "source": "DEC-1067 (GPU safety), DEC-1068 (4), DEC-1030: the two shared embedding servers and their logs"}
```

When the query server runs on the CPU (`embedding_servers.query.device` `cpu`, a supported fallback), leave its entry (port 11435) out of `gpu_backstop_embedders`: its `size_vram` is then 0, so every poll would trip.

Until they are added, `gov resources --backstop` refuses to start, naming each missing key. Nothing else about the gate changes.

## Readings I took (each also in `unresolved`)

- **R1** The constant holds `$HOME/.ollama/serve-<port>.log`, as the Interface writes the logs. A literal `$HOME` is not an absolute path, so the check would refuse it: the operator's JSON above carries the resolved path, and `backstop_entries()` produces it. The `date` of each entry (2026-11-04) is the date of DEC-1067/DEC-1068's tool, not today's.
- **R2** A group that ended after the start but before a trip is in neither `paused` nor `skipped` (L5 names `skipped` as the groups ended at the start). A group that exists but that we may not signal (`PermissionError`) counts as live for the check and is left out of `paused`.
- **R3** `ACT_PATHS` was `()`. The command now declares `.gov-runtime/dispatch/inbox/**`, the one project path `--backstop` writes, so the declaration stays true. It is in `command.py`, an allowed path, but beyond the ticket's "the one option" note.
- **R4** A log that shrinks below its offset (rotation or truncation) is read from 0: what is there was written since the start. A partial last line is read once it is complete.
- **R5** An inbox item written within the same second as another is never overwritten: the second one gets a `-2` suffix. This is the one departure from the item's literal name, and only on a collision.
- **R6** `watch` also refuses (`RESOURCE_ARGUMENTS_INVALID`) a group that is not an integer above 1, though the command's own type already does.
- **R7** Fix after the first acceptance run (S4, L1/L5): a decimal integer above 1 beyond what `os.killpg` accepts (2**31 and up) raised `OverflowError` in `_live` and crashed the watch; `_live` now counts it as an ended group (skipped and named), and the SIGSTOP loop also catches it. Unit tests: `test_s4_a_number_no_group_can_have_is_skipped_and_named_not_a_crash` (three sizes) and `test_s4_only_numbers_no_group_can_have_end_the_watch_at_once`.

- **R8** Fix after review round 1 (FR-1, FR-2; L5b): with the backstop's own group among the named ones, the trip's SIGSTOP to it froze `gov` before it paused the groups named after it and before it wrote the TRIP line and the item. `watch` now reads `os.getpgrp()` once, pauses the other groups first, writes the line and the item, then stops the own group (L5b above). FR-5 is the sentence in the operator's step.

## Evidence run

`tests/unit/resources` and `tests/acceptance/W2-20`, with `-m "not local_only" -k "not real and not green_here and not time_limit"` and `HOME` an empty scratch folder: `tests/unit/resources`: `280 passed in 18.71s`; `tests/acceptance/W2-20`: `170 passed, 1 deselected in 84.44s (0:01:24)` (after review round 1's fix, L5b; 450 passed in all). The exclusion leaves out the real-model cases and the one deselected case (the ones named `real`, `green_here`, `time_limit`).
