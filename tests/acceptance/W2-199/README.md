# W2-199 acceptance tests: the run-time tool, slice 2 (the machine-aware dispatcher and load balancer)

Ticket DAEO-rt2s (W2-199), profile FULL. Written by the independent test designer (MR-3) from the ticket's ten success
lines (as amended at `3e5a1fd36`), two failure lines and its `## Interface` section, before any implementation, on the base `543021090`. The code
read is the integrated public surface (`gov.cli.main`, `gov resources`, `gov dispatch`, `gov.resources.machine`,
`gov.dispatch.limits`, slice 1's acceptance support), never this ticket's branch. The scratch `heavy_slot.sh` of the main
tree was read as the behaviour the wrapper replaces.

## How they run

    env TMPDIR=$(mktemp -d) PYTHONPATH=<worktree>/src \
      python3 -m pytest tests/acceptance/W2-199 -q -p no:cacheprovider -o tmp_path_retention_policy=failed

75 cases (65 functions), each 1 to 15 s: child `gov` processes (`python3 -m gov.cli.main`), a stub `nvidia-smi`, real `sh`
commands that write a marker file; no model, no network, never the real `~/.gov-os`, never the machine's real load. Run
through the machine's heavy slot (the tests start their own `gov resources` children, which are nested runs only where a
test says so: every child's environment is built from scratch, so `GOV_HEAVY_ADMITTED` of the outer slot never reaches
them). All are acceptance tests; none is `local_only`. Waits are bounded and say what did not happen: the admission's
poll and sample periods are 0.2 s (`GOV_ADMISSION_POLL_S`, `GOV_ADMISSION_SAMPLE_S`), a hold is checked for 1 to 3 s, a
start is waited for 3 to 8 s, a held command stops by itself after 20 s.

## What is planted

- **`w2_199_support.Machine`**: slice 1's fixture machine (`w2_121c_support.Box`, imported unchanged) with: a `HOME` in
  `tmp_path`; `PATH` of `<stubs>:/usr/local/bin:/usr/bin:/bin` (the stub folder also holds a `python3` that runs the
  test's interpreter, for the wrapper); `GOV_RESOURCES_NPROC` (the default profile is **20 CPUs**, 64 GiB, a 24,576 MiB
  GPU; the 8-CPU / 16 GiB and 32-CPU / 64 GiB profiles are slice 1's); `GOV_RESOURCES_MEMINFO`; **`GOV_RESOURCES_LOADAVG`**
  naming a file the test rewrites whole (`Machine.load(13.0)`; the run re-reads it at each poll), the load being 3.0
  unless a test says; and the configuration file `~/.gov-os/machine/gate.json` (`heavy_slots: 2` by default, one with
  none where a test says, a measured verification peak of 1 GiB so the RAM term does not bind).
- **The `nvidia-smi` stand-in** answers the two queries `gov.resources.machine.gpu` sends from a `gpu.conf` the test
  rewrites (`Machine.gpu(total, used)`), or is absent (`Machine.no_gpu()`).
- **A job** (`Machine.start`): `gov resources --slot <kind> [options] -- sh -c <script>` as a child process; the script
  appends its name to an order file, writes its environment to `<name>.env` (by a rename: the marker), holds until
  `<name>.release` exists and exits with a code. Concurrency is those children and marker files; no `sleep` is a test's
  synchronisation: every wait is a poll with a bound.
- **The runtime log** is read from `~/.gov-os/runtime/log.jsonl` (whole lines checked), `state.json` from the same folder,
  messages straight from `~/.gov-os/inbox/<address>/messages.jsonl`, slot locks from `~/.gov-os/machine/slots/` (a lock is
  held when a non-blocking `flock` on it fails). A log is planted for RT-1 (jobs with `ready`, `wait`, `admitted`, `started`,
  `ended` events at times relative to the real clock) and for the margin (`ended` events with a `peak_per_worker`).
- **The slot CPU sets** are read from the jobs themselves (`GOV_HEAVY_CPUS` of the run in slot 1, 2, 3), never computed.
  The `--held 1,2` case is skipped on a machine where fewer than 3 CPUs are usable.
- **The invariant sweep** (success 3): one process calls gov's entry point (`gov.cli.main.main(["dispatch", "limits",
  "--json"])`) 183 times (CPUs 4 to 64 x margins 1.0, 1.5, 2.0), planting `GOV_RESOURCES_NPROC` and the log between calls.
- **The wrapper** (success 10) runs as `bash governance/project/orchestration/tools/heavy_slot.sh ...` with the fixture
  `HOME` and `PYTHONPATH` (a copy of it beside a planted `heavy_slots.conf` for the no-conf case).

## KPI line to tests

KPI ids name the ticket's lines by position (success 1 to 10, failure 1 and 2), the RT id beside each as a note. Every
item is a test function (a parametrised one covers all its rows). "Red on the base": what fails on `543021090`.

| KPI id | tests | expected red reason |
|---|---|---|
| S1 (RT-3) | `test_w2_199_s1_admission.py::test_s1_load_13_holds_the_start_names_the_wait_once_then_3_starts_it_and_the_exit_code_is_the_commands` | the command starts at load 13 (no load admission) |
| S1 (RT-3) | `test_w2_199_s1_admission.py::test_s1_load_11_9_under_the_start_threshold_starts_at_once_and_12_1_does_not` | the command starts at load 12.1 (the 11.9 half alone is already met on the base, so the case holds both sides) |
| S1 (RT-3) | `test_w2_199_s1_admission.py::test_s1_a_load_exactly_at_start_below_holds_the_start` | the command starts at load 12.0 |
| S1 (RT-3) | `test_w2_199_s1_admission.py::test_s1_a_run_that_can_never_fit_workers_times_margin_within_the_headroom_is_held_by_the_start_threshold_alone` | the command starts at load 12.5 (no load admission) |
| S1 (RT-3) | `test_w2_199_s1_admission.py::test_s1_a_start_held_by_the_load_is_polled_until_the_reading_allows_it_not_once` | the command starts at load 13 |
| S2 (RT-3) | `test_w2_199_s2_threshold.py::test_s2_limits_json_gives_start_below_0_6_of_the_cpus_and_load_limit_the_cpus` | no `start_below` / `load_limit` in `gov dispatch limits --json` |
| S2 (RT-3) | `test_w2_199_s2_threshold.py::test_s2_the_text_form_prints_start_below_load_limit_and_margin_with_their_rules` | no line names `start_below`, `load_limit`, `margin` |
| S2 (RT-3) | `test_w2_199_s2_threshold.py::test_s2_state_json_carries_both_limits_and_follows_the_planted_machine` | no `start_below` in state.json |
| S2 (RT-3) | `test_w2_199_s2_threshold.py::test_s2_the_override_sets_start_below_and_a_load_of_6_holds_where_the_default_does_not` | `GOV_HEAVY_START_BELOW` is not read |
| S3 (RT-3) | `test_w2_199_s3_slots_workers.py::test_s3_the_formulas_on_the_two_planted_profiles` | slice 1's `0.15` / `0.9` formulas (workers_per_slot 7 on 8 CPUs, 4 slots and 7 workers on 32) |
| S3 (RT-3) | `test_w2_199_s3_slots_workers.py::test_s3_a_measured_verification_peak_binds_the_slots_by_its_ram_term` | `workers_per_slot` 14 from `0.9 x CPUs`, not 6 |
| S3 (RT-3) | `test_w2_199_s3_slots_workers.py::test_s3_the_invariant_holds_for_every_cpu_count_from_4_to_64_with_margins_1_1_5_and_2` | no `start_below` / `load_limit` in the limits (4 CPUs: workers_per_slot 3 with the keys missing) |
| S3 (RT-3) | `test_w2_199_s3_slots_workers.py::test_s3_a_run_on_the_20_cpu_profile_with_a_file_with_no_heavy_slots_gets_4_workers_and_two_slots` | a file with no `heavy_slots` refuses the run (`RESOURCE_SLOT_REFUSED`) |
| S3 (RT-3) | `test_w2_199_s3_slots_workers.py::test_s3_workers_option_wins_over_the_derived_count` | the default workers are 1, not `workers_per_slot` 4 (the `--workers 2` half is already met on the base) |
| S3 (RT-3) | `test_w2_199_s3_slots_workers.py::test_s3_gov_heavy_workers_in_the_environment_sets_the_workers` | `GOV_HEAVY_WORKERS` is not read (1, not 3) |
| S3 (RT-3) | `test_w2_199_s3_slots_workers.py::test_s3_the_configuration_files_heavy_slots_3_still_gives_three_slots` | the runs get 1 worker, not `workers_per_slot` 4 (three slots from the file are already given on the base) |
| S3 (RT-3) | `test_w2_199_s3_slots_workers.py::test_s3_gov_heavy_slots_1_gives_one_slot_even_against_the_file` | `GOV_HEAVY_SLOTS` is not read: the second run starts |
| S4 (RT-3) | `test_w2_199_s4_margin.py::test_s4_a_job_raising_the_load_from_3_to_9_in_a_4_worker_run_leaves_the_measured_ended_event` | no runtime log: no `ready` event for the run |
| S4 (RT-3) | `test_w2_199_s4_margin.py::test_s4_a_peak_over_the_limit_is_counted_in_over_limit_s_and_named_once_on_stderr` | no runtime log: no `ready` event for the run |
| S4 (RT-3) | `test_w2_199_s4_margin.py::test_s4_five_ended_jobs_of_1_2_to_2_4_per_worker_give_the_rules_margin_and_fewer_workers` | no `margin` in `gov dispatch limits --json` (`<missing>`) |
| S4 (RT-3) | `test_w2_199_s4_margin.py::test_s4_margin_is_the_90th_percentile_of_the_last_20_jobs_and_never_under_1` | no `margin` |
| S4 (RT-3) | `test_w2_199_s4_margin.py::test_s4_a_measured_heavier_job_shrinks_the_next_runs_workers` | no margin: the control run's workers are 1, not 4, and nothing shrinks |
| S5 (RT-3) | `test_w2_199_s5_nested.py::test_s5_an_inner_run_with_one_slot_held_and_a_load_of_40_exits_5_within_5_s_and_the_outer_with_it` | no `nested` event in the runtime log (0, not 1) |
| S5 (RT-3) | `test_w2_199_s5_nested.py::test_s5_the_inner_run_inherits_the_outers_slot_cpus_workers_and_admitted_mark` | the job's environment has no `GOV_HEAVY_ADMITTED=1` (empty) |
| S5 (RT-3) | `test_w2_199_s5_nested.py::test_s5_a_run_with_the_admitted_mark_set_runs_at_once_at_load_40_with_every_slot_held_and_takes_no_slot` | no `nested` event |
| S6 (RT-3) | `test_w2_199_s6_slot_set.py::test_s6_each_kind_runs_its_command_and_exits_with_the_commands_code` | no `started` events in the runtime log; `measure` is not a kind (exit 2) |
| S6 (RT-3) | `test_w2_199_s6_slot_set.py::test_s6_held_1_2_gives_twice_the_workers_the_union_of_the_two_cpu_sets_and_takes_no_lock` | the run is refused: a file with no `heavy_slots` (`RESOURCE_SLOT_REFUSED`), so no derived three slots |
| S6 (RT-3) | `test_w2_199_s6_slot_set.py::test_s6_a_priority_waiter_is_served_before_an_ordinary_one_whichever_came_first` | the run is not held (the slot count is the file's 2, `GOV_HEAVY_SLOTS` is not read): its command starts |
| S6 (RT-3) | `test_w2_199_s6_slot_set.py::test_s6_a_priority_waiter_killed_is_ignored_and_its_file_removed_so_the_ordinary_waiter_starts` | the ordinary waiter starts at once (`GOV_HEAVY_SLOTS` is not read) |
| S6 (RT-3) | `test_w2_199_s6_slot_set.py::test_s6_two_priority_runs_holding_two_of_three_slots_cap_a_third_and_an_ordinary_run_takes_the_free_slot` | the run is refused: a file with no `heavy_slots` (`RESOURCE_SLOT_REFUSED`), so no derived three slots |
| S7 (RT-7) | `test_w2_199_s7_runtime_state.py::test_s7_a_pass_with_one_run_held_by_the_load_and_one_running_lists_each_and_the_planted_readings` | no `wait` event of the held run (the run is not held) |
| S7 (RT-7) | `test_w2_199_s7_runtime_state.py::test_s7_the_runtime_folder_holds_state_json_and_log_jsonl_only` | no `started` event in the runtime log (the folder listing alone is already met on the base) |
| S7 (RT-7) | `test_w2_199_s7_runtime_state.py::test_s7_a_finished_run_reads_ready_admitted_started_ended_with_one_job_id_and_the_common_fields` | no `ready` event |
| S7 (RT-7) | `test_w2_199_s7_runtime_state.py::test_s7_a_run_held_by_the_load_logs_one_load_wait_with_room_false_between_ready_and_admitted` | the run is not held (its command starts at load 13) |
| S7 (RT-7) | `test_w2_199_s7_runtime_state.py::test_s7_a_run_held_for_a_slot_logs_a_slots_wait` | the second run is not held (`GOV_HEAVY_SLOTS` is not read) |
| S7 (RT-7) | `test_w2_199_s7_runtime_state.py::test_s7_a_run_held_behind_a_live_priority_waiter_logs_a_priority_wait_with_room_true` | an ordinary run takes the free slot beside a live priority registration |
| S7 (RT-7) | `test_w2_199_s7_runtime_state.py::test_s7_a_run_with_gov_msg_address_sends_one_wake_message_naming_kind_and_exit_code` | no wake message in `lead:DAEO-x`'s inbox |
| S7 (RT-7) | `test_w2_199_s7_runtime_state.py::test_s7_a_run_without_gov_msg_address_sends_no_message` | no `ended` event in the log (the guard that the case is not vacuous) |
| S8 (RT-1) | `test_w2_199_s8_waits.py::test_s8_a_15_minute_wait_on_load_with_room_false_is_listed_and_is_no_finding` | no `gov dispatch waits` (exit 2) |
| S8 (RT-1) | `test_w2_199_s8_waits.py::test_s8_a_job_whose_last_wait_says_room_true_and_has_not_started_11_minutes_later_exits_3_naming_it` | no `gov dispatch waits` (exit 2, not 3) |
| S8 (RT-1) | `test_w2_199_s8_waits.py::test_s8_the_over_option_sets_the_limit_default_600` | no `gov dispatch waits` (exit 2) |
| S8 (RT-1) | `test_w2_199_s8_waits.py::test_s8_only_the_intervals_after_a_room_true_wait_count_as_with_room` | no `gov dispatch waits` (exit 2) |
| S8 (RT-1) | `test_w2_199_s8_waits.py::test_s8_a_real_run_held_3_s_by_a_planted_load_waited_3_to_6_s_with_no_room` | the run is not held (its command starts at load 13) |
| S9 (RT-4) | `test_w2_199_s9_gpu.py::test_s9_a_gpu_kind_without_gpu_need_mib_is_refused_with_exit_2_and_nothing_runs` | `embedder` / `reranker` are no kinds (exit 2, no `RESOURCE_ARGUMENTS_INVALID`) |
| S9 (RT-4) | `test_w2_199_s9_gpu.py::test_s9_a_need_within_the_budget_is_admitted_at_once_with_its_need_in_the_environment` | the kinds are invalid (exit 2) |
| S9 (RT-4) | `test_w2_199_s9_gpu.py::test_s9_a_need_over_the_budget_waits_with_a_gpu_event_then_starts_when_the_gpu_frees` | the kinds are invalid (exit 2) |
| S9 (RT-4) | `test_w2_199_s9_gpu.py::test_s9_with_no_nvidia_smi_the_run_is_refused_with_exit_3_the_refusal_text_and_no_command` | the kinds are invalid (exit 2, not 3) |
| S9 (RT-4) | `test_w2_199_s9_gpu.py::test_s9_nothing_offers_or_selects_the_cpu_in_the_runs_environment` | the kinds are invalid (exit 2) |
| S9 (RT-4) | `test_w2_199_s9_gpu.py::test_s9_three_watch_passes_below_the_budget_log_three_gpu_events_with_spill_false` | the pass logs no `gpu` event |
| S9 (RT-4) | `test_w2_199_s9_gpu.py::test_s9_a_gpu_over_its_budget_is_a_spill_in_the_gpu_event` | the pass logs no `gpu` event |
| S10 (RT-3) | `test_w2_199_s10_wrapper.py::test_s10_the_wrapper_is_60_lines_or_fewer` | `heavy_slot.sh` does not exist in this branch |
| S10 (RT-3) | `test_w2_199_s10_wrapper.py::test_s10_the_commands_own_exit_code_comes_back_0_included` | `heavy_slot.sh` does not exist |
| S10 (RT-3) | `test_w2_199_s10_wrapper.py::test_s10_a_command_that_cannot_start_ends_with_the_products_code_never_213` | `heavy_slot.sh` does not exist |
| S10 (RT-3) | `test_w2_199_s10_wrapper.py::test_s10_the_command_sees_its_workers_slot_cpus_and_the_admitted_mark` | `heavy_slot.sh` does not exist |
| S10 (RT-3) | `test_w2_199_s10_wrapper.py::test_s10_held_1_passes_through_and_prints_the_per_slot_workers` | `heavy_slot.sh` does not exist |
| S10 (RT-3) | `test_w2_199_s10_wrapper.py::test_s10_the_gov_heavy_variables_map_to_the_products` | `heavy_slot.sh` does not exist |
| S10 (RT-3) | `test_w2_199_s10_wrapper.py::test_s10_a_callers_pytest_xdist_auto_num_workers_is_mapped_to_workers` | `heavy_slot.sh` does not exist |
| S10 (RT-3) | `test_w2_199_s10_wrapper.py::test_s10_a_heavy_slots_conf_beside_the_script_is_not_read` | `heavy_slot.sh` does not exist |
| F1 | `test_w2_199_f1_nothing_lost.py::test_f1_a_run_killed_while_it_waits_for_the_load_starts_nothing_and_leaves_nothing` | the run is not held (its command starts at load 13) |
| F1 | `test_w2_199_f1_nothing_lost.py::test_f1_a_priority_run_killed_while_it_waits_for_a_slot_leaves_no_registration_and_no_lock` | no `prio-<pid>` registration file for the waiter |
| F1 | `test_w2_199_f1_nothing_lost.py::test_f1_a_run_whose_command_is_killed_frees_its_slot_and_logs_ended_with_the_code` | no `ended` event (0, not 1) |
| F1 | `test_w2_199_f1_nothing_lost.py::test_f1_a_nested_run_with_every_slot_held_ends_at_once` | no `jobs` in state.json (the nested run's own prompt end is already met on the base) |
| F1 | `test_w2_199_f1_nothing_lost.py::test_f1_a_refused_run_with_no_gpu_ends_at_once_and_leaves_nothing` | `embedder` is no kind (exit 2, not 3) |
| F2 | `test_w2_199_f2_unreadable_load.py::test_f2_a_load_that_cannot_be_read_starts_the_run_at_once_says_so_and_logs_a_problem` | the run starts but says nothing on stderr (and logs no `problem` event) |
| F2 | `test_w2_199_f2_unreadable_load.py::test_f2_the_watch_pass_names_the_unreadable_load_in_problems_and_still_runs` | `problems` does not name the load |

## Red run on the base

`543021090` with this folder, run through the machine's heavy slot (`python3 -m pytest tests/acceptance/W2-199
tests/acceptance/W2-121c/test_w2_121c_rt3_limits.py -q -p no:cacheprovider`): the 73 W2-199 cases all failed, each for its
row's reason (the run measured 55 s in all, the slowest case 8 s; no case hung, no harness error); `test_w2_121c_rt3_limits.py`
(changed here to success 3's formulas) has its 6 formula cases red (heavy_slots 4 and workers_per_slot 7 on the 32-CPU
profile, not 3 and 4) and its 5 unchanged GPU-answer cases (RT-3b) green. Cases that held a half already met on the base
(a start under the threshold, `--workers`, a file's `heavy_slots: 3`, the runtime folder's listing, a nested run's end) were
given a second half that is new, so none is green on the base.

## The test designer's readings where the Interface is open

- **Output shape.** `gov dispatch limits --json`'s `result` and state.json carry `start_below`, `load_limit` and `margin`
  in their `limits` object (`limits.derive` gains the keys); a key is also accepted at the top or in `admission`.
  state.json `jobs` holds `running` and `waiting`, each a list (or an object keyed by job id); `admission` holds
  `load_1m`, `start_below`, `load_limit`, `margin`, `room` (false at load 13 on 20 CPUs) and `binding`, a text naming the
  load when the load is what would hold a start. state.json's last GPU reading is an object holding `used_mib` and
  `spill` anywhere in it.
- **Event fields.** An event's `pid` is the `gov resources` process's own pid (the child the test started). Only the
  `load` and `gpu` waits are pinned to `room: false`; a `slots` or `priority` wait's `room` is left open (see the
  question for the ticket below). A run held on a slot logs one `slots` wait; a run with the load held logs one `load`
  wait.
- **Numbers on stderr.** The wait line is matched as `gov resources: load 13(.0)?, at or over 12(.0)?: waiting to start`
  (the number's form open). The peak over the limit is read as exactly one stderr line, apart from the wait line, that names
  `limit` and the peak (`25`); a peak under the limit names no `limit` line.
- **The margin's percentile.** With the five planted values 1.2, 1.5, 1.8, 2.1, 2.4 the 90th percentile is accepted as
  2.28 (linear) or 2.4 (nearest rank), and `workers_per_slot` must then follow the margin the command reports; cases where
  every method agrees (the last 20 all equal, a floor of 1.0, the window of 20 against 25 events) pin the rule.
- **`gov dispatch waits`.** Text output, one line per job holding its id and the two seconds (a number near the expected
  one, timestamps removed); a job not started whose pid is alive (the test's own) is waiting; the log's times are the real
  clock's.
- **Workers with a file's slot count.** A run's default workers are `workers_per_slot` of the derived `heavy_slots` (4 on
  20 CPUs), also when the file's `heavy_slots: 3` or `GOV_HEAVY_SLOTS` gives another slot count (the file or the variable
  sets "its slot count" only).
- **`prio-<pid>`.** The registration file is a file in `~/.gov-os/machine/slots/` whose name starts `prio-` and holds the
  pid (the ticket's F1 names the prefix). A capped priority run is read as no waiter: it has no registration file.
- **No CPU-naming variable** (RT-4): no variable with `CPU` in its name other than `GOV_HEAVY_CPUS`, no value `cpu`, no
  `CUDA_VISIBLE_DEVICES` of `""` or `-1`.
- **The wake message**: id `job:<job id>`, kind `wake`, its text or data holds the kind (`test`), the exit code as a whole
  number and a word or unit for the seconds it ran.
- **A refused run's "at once"** is a run that ends within 5 s; **a nested run's** is within 5 s with every slot held.
- **Not tested here**, as written in the ticket: the default poll of 15 s and sample of 5 s (a test cannot wait for them);
  "no CPU count or load figure of any machine is in the code or a configuration" (a property of the source, not a
  behaviour); and that `tests/unit/orchestration/test_dispatcher_stall*` and
  `tests/acceptance/W2-121c/test_w2_121c_s11_dispatcher_stall.py` stay green (existing suites the landing runs).

## Rulings applied (the coordinator, ticket amended at `3e5a1fd36`)

1. S9's numbers are the ticket's now (used 10,000 / need 4,000 and 19,504 / 2,000 admitted, 20,500 / 2,000 held).
2. `room` is true only for a `priority` wait and false for `load`, `gpu` and `slots`: the S7 slots case pins `room` false and
   a new case holds an ordinary run behind a planted live priority registration (`prio-<pid>` of a live process, an empty file)
   and pins reason `priority`, room true.
3. The 90th percentile for fewer than 20 jobs is the nearest rank: 2.4 for the five planted jobs (the tests still accept 2.28).
4. The key locations are the `limits` object, `jobs.running` / `jobs.waiting` lists and a `gpu` object in state.json.
5. `GOV_HEAVY_CPUS` is exempt from "no CPU-naming variable". 6. Workers stay derived from the derived `heavy_slots`.
(a) The invariant sweep checks `start_below + heavy_slots x workers_per_slot x margin <= load_limit` only where
`workers_per_slot` is above 1 (the equality with the rule still holds everywhere).
(b) The wrapper maps a caller's `PYTEST_XDIST_AUTO_NUM_WORKERS` to `--workers`: a case runs it with 1 (plain and `--held 1,2`)
and with 2.
(c) The clamp: a run whose `workers x margin` is over `load_limit - start_below` is held by the start threshold alone, so the
"load + workers x margin within the limit" half cannot bind beyond `start_below` for a run that can fit. The old S1 case that
held load 11 + 10 workers is replaced by one that admits it (and an idle machine at 30 workers) and holds load 12.5; the S4
case that held a heavier margin's start sooner is cut to the workers' shrink.

## Note
The task's "11 success lines" were 10 (S1 to S10, F1, F2).
