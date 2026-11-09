# W2-20 — the machine-wide resource gate: evidence (DAEO-r30l, the rebuild under DEC-1097 (8))

Built on `w2/W2-20` (today's `w2/integrate` with the designer's cases, `a71d9670e`). The 10-17 build (`w2/W2-20-1017`)
was read for its interface only: its reading variables (`GOV_RESOURCES_MEMINFO`, `_LOADAVG`, `_NPROC`), its registry
layout (`~/.gov-os/machine/sessions/<pid>.json`), `gov resources --check` / `--register`, exit 3 and
`RESOURCE_GATE_SHUT` are kept; its code (DEC-742's weights and session ceiling, gone by DEC-983) is replaced.

**Where it lives:** `src/gov/resources/` (`config.py` the one file, `machine.py` the readings, `registry.py` the
sessions, `gate.py` the conditions, `slots.py` the slots, budgets, CPU sets and trip-wire, `measure.py` the re-measure,
`command.py` the command); `src/gov/launch/gate.py` (the start check and the launch log); `launcher.py`, `command.py`,
`plan_check.py` (the launch's enforcement and F2); `rebuild/watch.py` (each tree its own lock); `secrets` and
`codeintel` (pools); `retrieval/ollama.py` (DEC-1037). Unit tests: `tests/unit/resources/` (118 cases),
`tests/unit/rebuild/test_w2_20_tree_lock.py`, `tests/unit/secrets_check/test_w2_20_pools.py`; planted machines only.

| Line | The KPI line (short) | How it is met | Unit evidence |
|---|---|---|---|
| S1 | `gov resources` reads memory, load and every live session from `~/.gov-os/machine/`, whichever repository | `registry.sessions()` reads `sessions/<pid>.json`; `gov launch` registers each session it starts (pid, repository, ticket, role) and removes it at its end; `gov resources --register` for any other starter | `test_every_live_session_is_read_whichever_repository_started_it`, `test_an_open_gate_starts_the_session_and_registers_it_while_it_runs` |
| S2 | Opens or shuts with a named reason; busy cores over the last minute and the load, both shown | each reason `{condition, reading, threshold, why}`, `describe()` in words; busy cores from two `/proc/stat` readings a minute apart (`cpu-stat.json` history; with no history, a quarter-second window), shown with `busy_window_s`; counters that do not advance shut it | `test_busy_cores_over_the_last_minute_shut_the_gate_and_both_figures_are_shown`, `test_idle_cores_with_a_high_load_shut_on_load_alone`, `test_cpu_counters_that_do_not_advance_shut_the_gate` |
| S3 | A stale entry (dead PID) is cleared | the read that finds a dead pid removes its entry and lists it in `cleared`; an unreadable entry shuts the gate | `test_a_stale_entry_is_cleared_by_the_read_that_finds_it`, `test_an_unreadable_entry_shuts_the_gate` |
| S4 | Disk and inode floors (100 GiB, 10,000,000) from the file; `gov launch` refuses below either; one function a close can call | conditions `disk` and `inodes` on `statvfs(disk_path)`; `gate.check_disk()` for W2-07 / W2-66 to call | `test_the_disk_floor_and_the_inode_floor_each_shut_the_gate`, `test_check_disk_is_one_function_a_close_can_call`, `test_each_reading_shut_refuses_the_launch_naming_it_and_starts_nothing[disk/inodes]` |
| S5 | Load opens while `min(load1, load15) < nproc` | as written; `nproc` the machine's online CPUs, never the caller's CPU set | `test_the_load_opens_while_the_lesser_of_one_and_fifteen_minutes_is_below_nproc` (5 cases) |
| S6 | Memory: MemAvailable plus the sessions' live memory at least the floor plus a working size per session and the new one; nothing reserved for a run not started | have = MemAvailable + live; need = floor + each running session at what it uses, at least its working size (DEC-961's wording) + the newcomer's working size | `test_memory_opens_with_room_for_every_running_session_and_the_new_one`, `test_nothing_is_reserved_for_a_run_that_has_not_started`, `test_a_session_using_more_than_its_working_size_counts_at_what_it_uses` |
| S7 | Heavy jobs wait for one of the configured slots; sessions take none; no other ceiling; each tree its own rebuild lock; the rebuild peak counted like a test run's | `gov resources --slot test\|rebuild -- <cmd>`: a slot lock under `~/.gov-os/machine/slots/`, then room for the job's own peak (verification or rebuild); a full set never refuses a session (P-2); `watch.tree_lock()` per tree | `test_a_job_waits_while_every_slot_is_taken`, `test_a_job_waits_for_memory_room_for_its_own_peak`, `test_a_heavy_job_asks_for_room_for_its_own_peak`, `test_a_full_set_of_slots_never_refuses_a_session`, `test_w2_20_tree_lock.py` (4) |
| S8 | All values in one file, each dated and sourced; missing or malformed shuts the gate naming it; a measured figure over seven days old named due | `config.load()`: `{"value","date","source"}` per value (the servers' section dated per server); every fault a `config` reason; `due_for_remeasure`; `gov resources --init-config` writes this machine's from the decisions and never overwrites (P-3); `rebuild_peak_bytes` required (P-7) | `test_each_missing_value_shuts_the_gate_naming_it` (12), `test_a_malformed_value_shuts_the_gate_naming_it` (8), `test_a_value_without_date_or_source_shuts_the_gate`, `test_a_measured_figure_older_than_seven_days_is_due_for_remeasure_and_still_counts`, `test_init_config_writes_a_dated_sourced_file_and_never_overwrites` |
| S9 | The re-measure: samples of each session's tree memory with the verification lock's state; writes the verification peak, the working size (and the rebuild peak, P-5) dated, old and new side by side | `gov resources --sample` (sessions, lock state, slot holders with kind) and `--remeasure` | `test_the_remeasure_writes_the_three_figures_dated_with_old_and_new_side_by_side`, `test_a_figure_with_no_sample_is_kept_and_said_so` |
| S10 | GPU, minimal: a declared need opens only with need + 10 % free; no `nvidia-smi` or no GPU shuts such a start; no need never reads the GPU | `--gpu-need-mib` on `gov launch` and `gov resources --check`; `gpu_margin` from the file | `test_a_start_with_a_need_opens_only_with_the_need_plus_the_margin_free`, `test_no_nvidia_smi_shuts_a_start_that_declares_a_need`, `test_a_start_with_no_declared_need_never_reads_the_gpu` |
| S11 | The trip-wire: below the lower floor, the largest heavy job named and stopped, a finding; nothing else stopped | each slot's runner checks every 5 s; `slots.tripwire()` stops the largest slot job's process group and appends `OOM_TRIPWIRE` to `findings.jsonl`; also `gov resources --trip-wire` | `test_below_the_trip_floor_the_largest_heavy_job_is_stopped_and_the_stop_is_a_finding` (real processes: the larger job stopped, the smaller job and a session untouched) |
| S12 | Both embedding servers' CPUs and priority in the file, read by their start (W2-123); the gate counts their CPU p95 | `embedding_servers.{shared,query}` with `host`, `cpus`, `nice`, date, source (W2-123's reader unchanged); each reading samples each server's process tree on its port, and the CPU condition counts the p95 in place of the current use | `test_the_servers_p95_is_counted_in_place_of_their_current_use`, `test_a_server_p95_is_measured_from_its_process_tree`; the restart cap: W2-123's `test_w2_123_embedding_cap.py` still green |
| S13 | The GPU measured: memory used and total, utilisation, holders (embedder, reranker, other), read once per check; no GPU named, never an error | `machine.gpu()`: one `--query-gpu` read per check (holders from `--query-compute-apps`, named if unreadable) | `test_the_reading_measures_the_gpu_and_its_holders_once`, `test_a_machine_with_no_gpu_is_named_in_the_reading_never_an_error` |
| S14 | GPU shares (embedder, then one reranker, then the rest); a job that would push the embedder off waits or runs on the CPU; the answer states the room it saw | `gpu_shares` in priority order (DEC-1032's default); `gate.gpu_room()` keeps the unheld part of each higher share and the headroom | `test_a_job_that_would_push_the_embedder_off_waits_and_the_room_is_stated` |
| S15 | A slot's thread budget for every program the job starts, the share over its workers, at least 1, from the machine; never raised by an inherited value; the file may set it | `slots.job_env()`: Go, OpenMP, MKL, OpenBLAS, Rayon, numexpr (2), Accelerate; `thread_budget` optional in the file | `test_a_job_runs_in_its_slot_confined_with_its_budget_and_every_child_inherits_both` (job and grandchild), `test_an_inherited_value_never_raises_the_budget`, `test_the_configured_thread_budget_replaces_the_derived_one` |
| S16 | Measured: a planted suite of all-CPU programs in one slot stays within the share + 1; within 20 % of the time without (time-bound programs, P-4) | **the CTO's run outside the sandbox** (a measurement of the whole machine's busy cores cannot be taken from inside the launch sandbox, DEC-1012) | — (the confinement itself is unit-tested under S15 and S17) |
| S17 | A slot confined to its share of the CPUs, derived from the machine and the slots, outside the servers' CPU sets | `slots.shares()`; the job started with `sched_setaffinity` in the child before it runs; a set that cannot be applied refuses the run | `test_the_shares_divide_the_cpus_outside_the_servers_evenly_and_contiguously`, `test_servers_covering_every_cpu_are_not_excluded_and_it_is_said`, the run test under S15 |
| S18 | The product's pools sized to the CPU set (`gov.secrets` included) | `gov.secrets.pool_size()` (the scan's rule: affinity, within `GOV_HEAVY_THREAD_BUDGET`); the code index's pool uses it | `test_w2_20_pools.py` (3) |
| S19 | `gov launch` refuses any session, lead or worker, while the gate is shut on any reading, naming it; one recorded override in the launch log | `launcher._admit_start` for both paths, `RESOURCE_GATE_SHUT`, exit 3; `--gate-override DEC-NNN` (`launch(..., gate_override=)`) written to `~/.gov-os/machine/launch.log` and the same line to stderr; a log that cannot be written refuses (P-1) | `test_each_reading_shut_refuses_the_launch_naming_it_and_starts_nothing` (12), `test_an_override_starts_it_anyway_with_one_line_in_the_launch_log_and_on_stderr` (2), `test_an_override_that_names_no_decision_is_refused` (4), `test_an_unreadable_slot_refuses_the_launch_naming_the_slots` |
| S20 | DEC-1037: `ensure_query_available(start=True)` carries the wrapper's caps: CPUs and priority (as today), device from the file, no slot budget inherited, own log, one caller line per start | `ollama._query_start`, `_daemon_env`, `_caller_line`; logs `~/.gov-os/machine/query-server.log` and `query-starts.log` (or the section's `log`, `start_log`) | `test_w2_20_query_start.py` (11: one case per device and caller value, a planted budget, the logs, a malformed device) |
| S21 | W2-136's F2: the plan check reads the main tree's tickets and ready list from a lead worktree; a plan override in the launch log and on stderr | `plan_check.check_lead` and `ready_path` on `store.main_root(root)` (relative `GOV_PLAN_READY` against the main tree, P-8); `_admit_lead` writes through `gate.record` | `test_the_check_follows_the_main_trees_tickets_and_ready_list_not_the_worktrees`, `test_a_relative_ready_list_variable_is_read_against_the_main_tree`, `test_a_plan_override_is_one_line_in_the_launch_log_and_the_line_on_stderr` |
| F1 | A heavy job's children use more CPUs than its share | held by S15's budget and S17's CPU set (inherited by every descendant) | S15, S17 |
| F2 | Another repository's session counts; a start while shut is refused with the reading | the registry is machine-wide; refusals carry the reading in the error's details | S1, S19 |
| F3 | A launch or close below either floor; disk without inodes | S4 | S4 |
| F4 | A fixed ceiling on leads or sessions other than the slots | none: the gate has no session count (DEC-983); a full set of slots never refuses a session | `test_a_full_set_of_slots_never_refuses_a_session` |
| F5 | A value not from the file, or a reading that cannot be taken treated as met | no defaults: every value from the file; every unreadable reading (memory, load, CPU counters, disk, registry, slots, GPU for a need) is a reason | `test_unreadable_memory_shuts_the_gate`, `test_an_unreadable_load_shuts_the_gate`, `test_an_unreadable_disk_shuts_both`, `test_cpu_counters_that_do_not_advance_shut_the_gate` |
| F6 | A worker's memory charged twice | each session's tree less every other session's subtree | `test_a_worker_inside_its_leads_tree_is_charged_once` |

## Measured on this machine (inside the sandbox)

- `gov resources --init-config` then `gov resources` on a scratch HOME (2026-11-09): load 1.36 / 3.03 on 20
  processors, 1.14 busy cores over 1.0 s, have 14.9 GB against need 5.4 GB, the disk 886 GB and 64.6 M inodes free,
  3 slots none held, the GPU named unreadable ("GPU access blocked by the operating system", the sandbox): open.
- A slot's job under that file ran on CPUs 0-1 with `OMP_NUM_THREADS=2` (20 CPUs less the servers' 8-19 = 0-7, three
  slots: 0-1, 2-4, 5-7).

## For the owner and the CTO

- **S16** is the CTO's run outside the sandbox: a planted suite of all-CPU programs through
  `gov resources --slot test -- ...` and without it, busy cores sampled from `/proc/stat`.
- **ACT to remove the interim wrapper (DEC-1037), not applied by this ticket:** (1) once this change is pinned, move
  `~/.local/bin/ollama` aside (`mv ~/.local/bin/ollama ~/.local/bin/ollama.wrapper-retired`); (2) check the real
  binary is what an automatic start now finds: `command -v ollama` (PATH order) or `GOV_OLLAMA_BIN`, else
  `~/.local/ollama/bin/ollama`; (3) set `embedding_servers.query.device` to `gpu` in `~/.gov-os/machine/gate.json`
  (the wrapper's `~/.ollama/query-server-device` reads `gpu` today); (4) restart the query server through
  `safe_restart("query")` (or let an automatic start happen) and see it capped: the listener's
  `/proc/<pid>/status` `Cpus_allowed_list` is the configured set, its niceness the configured one, no
  `OMP_NUM_THREADS` in `/proc/<pid>/environ`, one new line in `~/.gov-os/machine/query-starts.log`, and its output
  in `~/.gov-os/machine/query-server.log`.
- **The slots' CPU sets exclude the servers' CPU sets, as S17 says.** On this machine that leaves 8 of 20 CPUs for
  three slots; `heavy_slot.sh` chose not to exclude them (its header, EMG-gitleaks' measure). The file's
  `embedding_servers` sets decide it: narrowing them widens the slots.
- **Each tree its own rebuild lock (S7) changes `watch.settings()`'s default**, so two asserts in W2-76's unit tests
  (`tests/unit/rebuild/test_w2_76_watch.py:33`, `test_w2_76_lock_override.py:46,48`), which pin the machine-wide
  `/tmp/gov-os-rebuild.lock`, go red. They are outside this ticket's paths. Options (DEC-105): (a) apply now, the
  two files' asserts changed to `watch.tree_lock(tmp_path)` with this change (recommended: S7 and DEC-1001 (d) say so);
  (b) defer the per-tree default, keeping S7's half unmet; (c) re-baseline S7.
- **Every launch now passes the gate (S19):** unit tests that start launches without planting an open gate
  (`tests/unit/launch/test_w2_136_plan_check.py`, `test_launcher.py`, `test_w1_32.py` and similar) are refused by it,
  as the ticket foresaw for W2-136's acceptance cases (G-1). They are outside this ticket's paths: their fixtures need
  an open gate planted (a dated, sourced `gate.json` under their temporary HOME and planted readings).
