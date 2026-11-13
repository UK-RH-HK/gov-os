# W2-20 — the machine-wide resource gate: evidence (DAEO-r30l, round 3: the review's findings; round 2: the interface)

Round 1 (`8985180a3`) built every line but S16, but `gov accept W2-20` passed 39 of 164: the acceptance cases assume an
interface (the designer's README, "The interface these tests assume") round 1 could not see. Round 2 brings the product
to that interface, handed to the engineer in its brief (the ticket's round-1 point (3)); the engineer read only the
interface and `gov accept`'s results and one-line failure messages, never the cases.

**Where it lives:** `src/gov/resources/` (`config.py` the one file, `machine.py` the readings, `registry.py` the
sessions, `gate.py` the conditions and `check_disk`, `slots.py` the slots, CPU sets, thread budgets and trip-wire,
`measure.py` the sample and re-measure, `command.py` the command; `gov.resources.check_disk` for `gov close`);
`src/gov/launch/gate.py` (the start check and the launch log); `launcher.py`, `command.py`, `plan_check.py` (the
launch's enforcement and F2); `rebuild/watch.py` (each tree its own lock); `secrets` and `codeintel` (pools);
`retrieval/ollama.py` (DEC-1037). Unit tests: `tests/unit/resources/` (150 cases), `tests/unit/rebuild/test_w2_20_*`,
`tests/unit/secrets_check/test_w2_20_*`; planted machines only.

## Round 4: DEC-1105's exception round, R2-F1 only

The configuration format is unchanged (frozen from `28fbcfebf`); `src/gov/resources/config.py` and `gate.json` are
untouched. Only the servers' CPU samples changed: they are a cache, moved to the designer's round-8 interface.

| Finding | Ruling | What changed | Unit evidence (`tests/unit/resources/test_w2_20_round3.py`) |
|---|---|---|---|
| **R2-F1**: the first reading after ten quiet minutes shut the gate on cpu (a server with only expired samples was not resampled, so `embedding_cpu_now` read `null`) | fix (DEC-1105) | `machine._sample_servers`: the samples live in `~/.gov-os/machine/embedding-cpu.jsonl`, one line per server per sample, `{"time", "server", "pid", "cpu_seconds"}`. A server's **kept** samples are those of its current pid at most `KEEP_S` (600 s) old. A listening, readable server with none kept (a new process, or every sample expired) is sampled afresh first (a sample, a quarter of a second, the reading), and both samples are written; so stale samples never shut the gate. `now` is the window rate over the kept samples (unchanged rule). The p95 keeps round 7's span: the rates between a server's consecutive samples of one process over the last week (at most 500). An unreadable server still reads `null` and shuts on `cpu` (F5). Round 3's `server-cpu.json` is never read and is removed at the next reading. | `test_r2_f1_a_history_older_than_the_keep_window_is_sampled_afresh_and_the_gate_opens` (both servers' histories three hours old: `now` and p95 0.0, the gate open, a fresh pending sample and the reading's own written for each), `test_r2_f1_a_history_inside_the_keep_window_is_read_without_a_fresh_sample` (300 s: no pending sample), `test_r2_f1_expired_lines_of_another_pid_never_count`, `test_r2_f1_an_unreadable_server_with_an_expired_history_still_shuts_on_cpu`, `test_f2_a_kept_history_written_before_round_4_still_reads` (2: rounds 2 and 3's file dropped) |

**The interface's one disagreement, named:** the round-8 README computes the p95 from the kept (600 s) samples; S12
and round 7 keep it over a week. As the brief rules, the p95 keeps round 7's week; the expiry rule applies to the
current use (and to when a server is sampled afresh).

**Round 4's runs (inside the sandbox; `HOME` an empty scratch folder with only the user site's `lib` linked in):**

- `gov accept W2-20`: **170 passed, 0 failed, 1 skipped (171)**; every line passes but S16, whose one case skips (the
  CTO's run outside the sandbox).
- Unit tests, `tests/unit/resources tests/unit/launch` with `-m "not local_only" -k "not real and not green_here and
  not time_limit"`: **287 passed, 86 deselected**.

## Round 3: the independent review's findings (round 1, NOT READY on F1) and the CTO's rulings

The configuration format is unchanged (frozen from `28fbcfebf`): no key of `gate.json` is renamed, added or given
another meaning; `src/gov/resources/config.py` is untouched. No fix needed a configuration change.

| Finding | Ruling | What changed | Unit evidence (`tests/unit/resources/test_w2_20_round3.py`) |
|---|---|---|---|
| **F1** (blocking): launches that start together all passed the memory check | fix | `gov.launch.gate.StartLock`: an exclusive `flock` on `~/.gov-os/machine/launch.lock`, taken in `launcher.launch` before the start check and given back in `_run` once the session is registered (or when the launch ends without a session, in `finally`). Launches are judged one after another, each with the sessions before it counted. The descriptor is `O_CLOEXEC` (never inherited by the session); a lock not taken within 300 s, or that cannot be opened, refuses the launch (never a check run unlocked). A launch that ends before registering leaves no entry: nothing is registered before `Popen`, and a failed registration stops the session. | `test_f1_launches_started_together_admit_only_those_the_memory_rule_admits` (six forked launches, a stand-in CLI, room for three: three start, three refused on memory; with the lock replaced by a no-op the same case starts all six), `test_f1_the_check_runs_under_the_machine_wide_start_lock`, `test_f1_a_launch_that_ends_before_registering_leaves_no_entry_and_frees_the_lock`, `test_f1_a_registration_that_fails_stops_the_session_leaves_no_entry_and_frees_the_lock`, `test_f1_a_held_start_lock_refuses_after_its_wait_and_is_never_inherited` |
| **F2**: the cpu rule counted the servers twice | fix (round 7's interface) | `cpu`: `busy_cores_1m + max(0, p95(shared) - now(shared)) + max(0, p95(query) - now(query)) < nproc`. New reading `embedding_cpu_now` (`machine.servers_cpu`): `GOV_RESOURCES_EMBEDDING_CPU_NOW`, else each server's process-tree CPU over the busy cores' last minute (kept `[t, pid, ticks]` samples in `server-cpu.json`'s `window`, the same window rule as the busy cores; a server's new process, or a history from round 2 with no window, gets a short window at once). Unreadable: `null`, shut on `cpu` with `reading` `null`. | `test_f2_only_the_part_of_each_servers_p95_above_its_current_use_is_added` (4: the store rebuild opens at 12.5; the same p95 idle now shuts at 20.0; busier now than its p95 adds nothing, 20.0 shuts; 3.9 of 4 opens), `test_f2_busy_cores_alone_shut_only_at_nproc`, `test_f2_an_unreadable_current_use_shuts_on_cpu_with_a_null_reading` (4), `test_f2_the_own_current_use_is_the_servers_cpu_over_the_last_minute`, `test_f2_a_kept_history_written_before_round_3_still_reads` |
| **F4**: the trip-wire silently off without `oom_floor_bytes` | fix | `slots.run` names it on the job's stderr when the job starts (`OOM_TRIPWIRE_OFF: ... oom_floor_bytes: <the fault> (S8, S11)`); `slots.tripwire` without a usable floor stops nothing and names it in `why` (no `KeyError`); `gov resources --trip-wire` already refused naming it; the gate is shut on it (`config`, S8). The job still runs: the ruling asks for the key named, and S7 refuses a slot only on `heavy_slots`. | `test_f4_a_missing_or_malformed_trip_floor_is_named_when_a_heavy_job_starts` (3), `test_f4_a_good_trip_floor_is_not_named`, `test_f4_a_trip_wire_pass_without_its_floor_stops_nothing_and_names_it`, `test_f4_the_trip_wire_command_names_a_missing_floor` |
| **F6**: after a WSL restart, old state refused falsely | fix | (1) `registry.register` records the process's own `boot` (boot id) and `start_ticks` (from `/proc/<pid>/stat`); `registry.sessions` clears an entry whose live pid has another boot or start, or (an entry without them) started more than 5 s after the entry's `started`: a reused pid. Where it cannot be told (a planted process table, an unreadable stat) the live pid stands (counted, never dropped). (2) `machine.busy_cores` drops kept samples of another boot or with counters above today's at once, so after a restart the reading is a short window, never `null`. | `test_f6_an_entry_whose_live_pid_started_after_it_was_made_is_stale_and_cleared`, `test_f6_an_entry_made_when_its_process_ran_stays`, `test_f6_register_records_the_process_start_and_another_start_is_stale`, `test_f6_on_a_planted_process_table_the_start_is_not_judged`, `test_f6_cpu_samples_from_before_a_restart_are_dropped_at_once` (2) |
| **F8**: a plan override logged before the gate's check | fix | `_admit_lead` returns the override; `_record_plan_override` writes it (launch log and stderr) only after `_admit_start` admits the launch (open, or a recorded gate override, whose line comes first). | `test_f8_a_plan_override_for_a_lead_the_gate_refuses_is_not_logged`, `test_f8_a_plan_override_the_gate_admits_is_logged_once`, `test_f8_with_a_gate_override_both_overrides_are_logged_gate_first` |
| F3 | row (the designer revised S16; the CTO re-runs it) | nothing in the product | — |
| F5 | row, not this round | unchanged: a listening socket with no readable owner still reads as 0 cores (now and p95) | — |
| F7 | row, out of scope (tooling and the decision) | unchanged: `heavy_slot.sh`'s `/tmp` locks and the product's `~/.gov-os/machine/slots/` are two pools until the tooling moves | — |
| F9 | row, not this round | unchanged | — |
| F10 | row, not this round | unchanged: the re-measure takes the largest kept sample; nothing samples on a schedule | — |

The four launch fixtures that plant an open gate (`test_runs.py`, `test_w1_28.py`, `test_w1_32.py`,
`test_w2_136_plan_check.py`) and the resources fixture (`conftest.py`) now plant `GOV_RESOURCES_EMBEDDING_CPU_NOW` idle,
as the designer's support does, so no unit case reads the real servers.

**Round 3's runs (inside the sandbox, on `b6c6dad61` plus a style-only edit of `machine.py`; an empty `HOME` with only
the user site's `lib` linked in, since `gov accept` drops `PYTHON*` variables):**

- `gov accept W2-20`: **168 passed, 0 failed, 1 skipped (169)**; every line passes but S16, whose one case skips (the
  CTO's run outside the sandbox, `GOV_W2_20_MEASURE=1`). Round 7's new cases (the cpu rule, the frozen configuration
  format) are green.
- `gov accept W2-136`: **76 passed, 0 failed**.
- Unit tests, `tests/unit/resources tests/unit/launch tests/unit/rebuild tests/unit/secrets_check` with `-m "not
  local_only" -k "not real and not green_here and not time_limit"`: **375 passed** (202 opt-in rows deselected by
  `tests/conftest.py`); with `--optin=lifted,breadth` **576 passed**, the one case left out by the name filter being
  `test_w2_20_pool.py::test_a_real_cpu_set_bounds_the_width`. The new file alone: 31 passed.
- W2-112's socket cases were not re-run (not in this round's brief; no file of theirs changed).

## What round 2 changed (the interface)

- **The file** `~/.gov-os/machine/gate.json`: every value `{"value", "date", "source"}`; keys `memory_floor_bytes`,
  `verification_peak_bytes`, `working_size_bytes`, `rebuild_peak_bytes` (required, P-7), `disk_floor_bytes`,
  `inode_floor`, `verification_lock`, `gpu_margin`, `oom_floor_bytes`, `heavy_slots`, `gpu_shares`
  (`{"embedder_mib", "reranker_mib"}`), `thread_budget` (optional), `embedding_servers` (`shared` and `query`, each
  `cpus`, `nice`; `query.device`). No default stands in for a missing value; round 1's `disk_path` and its GPU-share
  default are gone. A fault is one `config` reason naming its key (or `gate.json`), `reading` the raw value.
- **The reading:** `registry`, `available_memory_bytes`, `sessions_live_memory_bytes`, `load_1m`, `load_15m`,
  `busy_cores_1m`, `embedding_cpu_p95`, `nproc`, `disk`, `sessions` (with `live_memory_bytes`), `cleared`, `slots`
  (`total`, `held`), `gpu`, `gpu_room_mib`, `due_for_remeasure` (key names), `gate`. Conditions only `memory`, `load`,
  `cpu`, `disk`, `inodes`, `config`, `gpu` (round 1's `sessions` and `slots` conditions gone).
- **The conditions as stated:** memory `available + live >= floor + working_size x (running + 1)` (round 1 counted a
  session at what it used, DEC-961's wording; the interface counts the working size); cpu `busy + p95(shared) +
  p95(query) < nproc` (round 1 counted the servers' p95 in place of their current use).
- **The readings' sources:** `GOV_RESOURCES_BUSY_CORES`, `GOV_RESOURCES_EMBEDDING_CPU`, `GOV_RESOURCES_DISK` name a
  file holding the value (as `GOV_RESOURCES_MEMINFO` does), else the gate's own sampling; `nvidia-smi` from `PATH`
  with the stated fields; a process's GPU kind from its command line (an `ollama*` word an embedder, `rerank` a
  reranker).
- **The slot command:** `--slot test|rebuild [--tree T] [--workers N] -- CMD`: no memory wait (round 1 waited for room
  for the job's peak, which kept planted low-memory cases from ever starting); a rebuild takes its tree's lock first;
  the thread variables set to the budget whatever the caller had; `slots.held` lists one entry per running job.
- **The trip-wire:** one pass, result `stopped`; the stop kills the job's command group, then its runner. The runner's
  own periodic pass acts only on the kernel's memory reading (a planted reading is a test's, read by its own passes).
- **Sample and re-measure:** `samples: [{pid, tree_memory_bytes, verification}]` (slot holders also `kind`);
  `--remeasure` returns `{"old": {key: value}, "new": {key: value}}` (the entries written under `written`).
- **The launch:** refusal `GovError("LAUNCH_REFUSED", "the resource gate is shut: memory: reading N, limit M (DEC-1088
  (5))")`; the override line `gov launch: OVERRIDE gate_override: DEC-NNN: <role> <ticket> started with the resource
  gate shut: ... (DEC-899)` in the launch log and on stderr; a plan override's log line holds `plan_override`, the
  decision and the ticket, and W2-136's own `OVERRIDE` line stays on stderr.
- **The query start:** its output in `~/.gov-os/machine/embedding-query.log`; one JSON line per start in
  `embedding-starts.jsonl` (`time`, `server`, `device`, `caller` `{pid, cwd, command}`).
- **The GPU's `[N/A]` (ACT-GATE-CONFIG-1 note 2):** where a kind's processes are on the GPU but their memory reads
  `[N/A]` (WSL), that kind holds its share, already inside the GPU's used memory, so nothing more is kept back for it;
  a kind with no process keeps its whole share. The free memory alone then decides: the rehearsal's 1,024 MiB start of
  kind `other` with 9.5 GB free is admitted. Unit case:
  `test_per_process_memory_that_cannot_be_read_holds_its_share_and_only_free_memory_decides`.

| Line | The KPI line (short) | How it is met | Unit evidence |
|---|---|---|---|
| S1 | `gov resources` reads memory, load and every live session from `~/.gov-os/machine/`, whichever repository | `registry.sessions()`; `gov launch` registers each session it starts and removes it at its end; `--register` for any other starter | `test_every_live_session_is_read_whichever_repository_started_it`, `test_an_open_gate_starts_the_session_and_registers_it_while_it_runs` |
| S2 | Opens or shuts with a named reason; busy cores and the load, each judged, both shown | reasons `{condition, reading, threshold}`; `busy_cores_1m` and the loads in the reading | `test_busy_cores_and_load_are_judged_each_on_its_own`, `test_the_cpu_condition_is_busy_cores_plus_both_servers_p95_below_nproc` |
| S3 | A stale entry is cleared | the read that finds a dead pid removes it and lists it in `cleared` | `test_a_stale_entry_is_cleared_and_does_not_count` |
| S4 | Disk and inode floors; launch refuses; one function a close can call | `disk`, `inodes` conditions; `gov.resources.check_disk(env=None)` | `test_the_disk_floor_and_the_inode_floor_each_shut_the_gate` (4), `test_check_disk_reads_the_env_it_is_given`, `test_an_unreadable_disk_shuts_both_for_a_start_and_a_close` (3) |
| S5 | Load opens while `min(load1, load15) < nproc` | as written | `test_the_load_opens_while_the_lesser_of_one_and_fifteen_minutes_is_below_nproc` (5) |
| S6 | Memory: the floor plus a working size per running session and the new one; nothing reserved for a run not started | as written | `test_memory_needs_the_floor_and_a_working_size_for_each_running_session_and_the_new_one`, `test_nothing_is_reserved_for_a_run_that_has_not_started` |
| S7 | Heavy jobs wait for one of the configured slots; sessions take none; each tree its own rebuild lock; the rebuild peak measured | `slots.run`; a rebuild's tree lock among the slots; `watch.tree_lock` for `gov rebuild` | `test_a_job_waits_while_every_slot_is_taken`, `test_a_rebuild_excludes_only_another_rebuild_of_the_same_tree`, `test_a_full_set_of_slots_never_refuses_a_session`, W2-76's two tests |
| S8 | All values in one file, dated and sourced; missing or malformed shuts, named; due for re-measure after seven days | `config.load()`; `--init-config` (P-3) | `test_each_missing_value_shuts_the_gate_naming_it` (12), `test_a_malformed_value_shuts_the_gate_naming_it_with_its_raw_value` (9), `test_a_value_without_its_date_or_source_is_malformed` (5), `test_a_measured_figure_older_than_seven_days_is_due_and_still_counts` (2), `test_init_config_writes_a_dated_sourced_file_with_the_decided_values_and_never_overwrites` |
| S9 | Samples with the verification lock's state; the re-measure writes the figures dated, old and new side by side | `--sample`, `--remeasure` (three figures, P-5) | `test_the_remeasure_writes_the_three_figures_dated_with_old_and_new_side_by_side`, `test_a_figure_with_no_sample_is_kept` |
| S10 | A declared need opens only with need + margin on one GPU; no `nvidia-smi` or no GPU shuts it; no need never reads the GPU | `--gpu-need-mib`; `gpu` condition | `test_a_need_opens_only_with_the_need_plus_the_margin_on_one_gpu` (2), `test_room_only_across_two_gpus_shuts`, `test_a_start_check_with_no_need_never_runs_nvidia_smi`, launch's GPU cases (3) |
| S11 | The trip-wire stops the largest heavy job below the lower floor, a finding; nothing else | `slots.tripwire` | `test_below_the_trip_floor_the_largest_heavy_job_is_stopped_and_the_stop_is_a_finding` (real processes) |
| S12 | Both servers' CPUs and priority in the file; the gate counts both p95 | `embedding_servers`; `machine.embedding_cpu` (samples in `embedding-cpu.jsonl`, round 4) | `test_a_servers_p95_is_measured_from_its_process_tree`, the cpu cases, the R2-F1 cases; W2-123's restart cap unchanged |
| S13 | The GPU measured once per check; no GPU named, never an error | `machine.gpu()` | `test_the_reading_measures_the_gpu_and_its_processes_once`, `test_no_gpu_or_an_unreadable_one_is_named_never_an_error` (3) |
| S14 | GPU shares by kind; a job that would push the embedder off waits; the room stated | `gate.gpu_room`, `gpu_room_mib` | `test_a_job_that_would_push_the_embedder_off_waits_and_the_room_is_stated` (5), the `[N/A]` case |
| S15 | A slot's thread budget for every program the job starts; the file may set it | `slots.job_env`, `budget` | `test_a_job_runs_in_its_slot_confined_with_its_budget_and_every_child_inherits_both`, `test_the_configured_thread_budget_replaces_the_derived_one`, `test_the_callers_value_never_stands` |
| S16 | Measured: one slot keeps busy cores within the share + 1, within 20 % of the time | **the CTO's run outside the sandbox** | — |
| S17 | A slot confined to its share of the CPUs outside the servers' sets | `slots.cpu_set`, `sched_setaffinity` in the child | `test_each_slot_has_its_share_of_the_cpus_outside_the_servers`, `test_two_held_slots_have_disjoint_cpu_sets_and_are_in_the_reading` |
| S18 | Pools sized to the CPU set | unchanged from round 1 | `test_w2_20_pools.py` |
| S19 | `gov launch` refuses any session while the gate is shut, naming it; one recorded override | `launcher._admit_start` | `test_each_reading_shut_refuses_the_launch_naming_it_and_starts_nothing` (12), `test_an_override_starts_it_anyway_with_one_line_in_the_launch_log_and_on_stderr` (2), `test_the_slots_refuse_a_launch_only_when_their_reading_cannot_be_taken` (2) |
| S20 | DEC-1037: the query start carries the wrapper's caps | `ollama._query_start`, `_daemon_env`, `_caller_line` | `test_w2_20_query_start.py` (10) |
| S21 | W2-136's F2: the plan check reads the main tree; a plan override in the launch log and on stderr | `plan_check.check_lead` on `store.main_root` | `test_the_check_follows_the_main_trees_tickets_and_ready_list_not_the_worktrees`, `test_a_plan_override_is_one_line_in_the_launch_log_and_the_line_on_stderr` |
| F1-F6 | | held by S15/S17, S1/S19, S4, S7, S8 and the readings, the registry's subtrees | as above; `test_no_ceiling_on_sessions`, `test_a_worker_inside_its_leads_tree_is_charged_once` |

## gov accept (inside the sandbox, on `6b2a8f9a2`)

- **W2-20: 160 passed, 3 failed, 1 skipped (164)**; round 1: 39 / 124 / 1. Every line passes but S2 (15/16), S10
  (8/9), S13 (3/4) and S16 (the one skip, the CTO's run). The three reds are cases where the stated interface and the
  case disagree (the engineer saw only their one-line messages):
  - `test_w2_20_cpu::test_s2_..._each_on_its_own_and_shows_both[busy cores high, load low]`: `AssertionError:
    {'available_memory_bytes': 68719476736, 'busy_cores_1m': 3.9, ...}`. The case plants busy 3.9, both servers' p95
    0.0, nproc 4, load 0.1, and expects the gate shut on cpu. The interface's rule (`busy + p95 + p95 < nproc`, equal
    shuts) opens at 3.9 < 4; the KPI line (S2) states no threshold. Built to the interface.
  - `test_w2_20_gpu::test_s10_a_start_with_no_declared_need_never_reads_the_gpu[a GPU planted]`: `a start with no GPU
    need read the GPU: [['--query-gpu=...'], ['--query-compute-apps=...']]`. The case makes a plain `gov resources`
    reading before the start check; the reading reads the GPU (P-6, S13; the no-GPU cases need `gpu` in the plain
    reading), the start check without a need does not. The calls listed are the reading's.
  - `test_w2_20_gpu::test_s13_the_reading_measures_gpu_memory_utilisation_and_which_processes_hold_it`: `the GPU was
    read more than once in one check (--query-gpu): [4 calls]`. The case makes two plain readings, each reading the GPU
    once (two calls: the GPUs, then their processes); the count covers both readings.
- **W2-136: 76 passed, 0 failed (every line passes)**: its launcher cases with the revised fixture, and the launch's
  plan check reading the main tree unchanged.
- Unit tests (`-m "not local_only" -k "not real and not green_here and not time_limit"`): `tests/unit/resources`,
  `launch`, `rebuild`, `secrets_check` 344 passed; `tests/unit/retrieval` 529 passed, 22 failed: W2-112's 20 socket
  cases (`PermissionError` in the sandbox, the CTO's run) and W2-91's two namespace cases
  (`test_every_tracked_path_is_in_one_namespace`, `test_the_root_files_the_overlay_and_schemas_are_embedded`), red on
  `governance/project/indep-walls/**` from the ACT-INDEP-WALLS-1 merge (`147706ae4`), not this change.

## For the owner and the CTO

- **The real gate file must be written again before W2-20 merges.** ACT-GATE-CONFIG-1 wrote round 1's file
  (`floor_bytes`, `trip_floor_bytes`, `disk_path`, the GPU shares as a list, each server's `host`). Round 2 reads the
  interface's keys, so that file now shuts the gate on `config` (every launch refused). The ACT again, from round 2's
  code: `apply.sh undo` (or move the file aside), then `gov resources --init-config` from W2-20's head; the new file's
  bytes differ from `de4fb326288d…`, so `apply.sh`'s pinned hash needs the CTO's update.
- **The working size (2.04 GiB) is below today's measured lead p95 (3.2 GB):** the CTO's `gov resources --remeasure`
  after the merge re-measures it (`--sample` over a working day first).
- **S16** is the CTO's run outside the sandbox (`GOV_W2_20_MEASURE=1`).
- **ACT to remove the interim wrapper (DEC-1037), not applied by this ticket:** (1) move `~/.local/bin/ollama` aside;
  (2) check the real binary is what an automatic start finds (`command -v ollama`, `GOV_OLLAMA_BIN`, else
  `~/.local/ollama/bin/ollama`); (3) `embedding_servers.query.device` set to `gpu` in the gate file; (4) restart the
  query server (`safe_restart("query")`) and see it capped: `Cpus_allowed_list` and niceness as configured, no
  thread-budget variable in `/proc/<pid>/environ`, one new line in `~/.gov-os/machine/embedding-starts.jsonl`, its
  output in `~/.gov-os/machine/embedding-query.log`.
- **The slots' CPU sets exclude the servers' CPU sets, as S17 says:** on this machine 8 of 20 CPUs for three slots
  (2 each); `heavy_slot.sh` chose not to exclude them. The file's `embedding_servers` sets decide it.
