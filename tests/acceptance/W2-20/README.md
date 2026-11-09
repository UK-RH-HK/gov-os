# W2-20 — Machine-wide resource gate: acceptance tests

Written by the independent test designer (MR-3) from the KPI lines of ticket `DAEO-r30l` (W2-20, STANDARD) as they
stand on 2026-11-09, and the decisions they cite. **Revision round of 2026-11-09 (DEC-1097 (8)):** W2-20 was built on
2026-10-17 to its first KPI lines; its ticket has since gained and changed many lines. The 10-17 cases were brought
from `w2/W2-20` unchanged (commit `fa2abff4d`), then each old case whose line changed was revised or removed in its
own commit (`Rewrite-Reason: DEC-1097 (8)`), and every new line got new cases. No implementation was read: only the
ticket, the decisions, and today's `w2/integrate` code outside W2-20's own work (the launcher, W2-136's plan check,
`gov.retrieval.ollama`, the pools of `gov.secrets` and `gov.codeintel`) and the interim wrapper `~/.local/bin/ollama`
(read, never run).

**Round 2 (2026-11-09, DEC-1097 (8), DEC-1088 (5)(b)).** A fresh test designer, from the ticket as the CTO revised it
after round 1 (`61682b3e2`): (1) the new KPI line for W2-136's F2 entry criterion got its cases, as **S21**
(`test_w2_20_plan_source.py`); (2) round 1's packages P-1 to P-6, settled in the ticket ("The designer's points
settled"), were brought into the cases where they were not already (each change its own commit,
`Rewrite-Reason: DEC-1097 (8)`; the table "Round 2's changes" below); (3) the 10-17 designer's revisions of W1-07's,
W1-26's and W1-32's cases (`173e8e97a`, `d82619c36`: the recorded `gov` commands include `resources`) were ported onto
today's versions of those files, keeping `accept` (DEC-970) and the `release` excuse (DEC-753). No implementation of
W2-20 was read; only `w2/integrate`'s code (`gov.launch.plan_check`, `launcher`, `command`, `store.main_root`,
`gov.plan.tickets`) and W2-136's suite for how a lead check is driven.

**Round 4 (2026-11-09, DEC-1097 (8)).** Against the engineer's round 2, built to the interface below, the suite
passed 160 of 164; three cases disagreed with this README's own interface or with P-6, and a fresh test designer
revised each one (table "Round 4's changes"). The interface did not change. Only the S2 example and the GPU counting
note were made explicit. No implementation of W2-20 was read.

## Run

```sh
PYTHONPATH=<tree>/src python3 -m pytest tests/acceptance/W2-20 -q -p no:cacheprovider -m "not local_only"
```

Standard library and `pytest` only. No network, no GPU, no model, no real server. About two minutes once built (the
slot cases wait a few seconds each to show a job still waiting). One case is `local_only` (S16, measured): the CTO runs
it outside the sandbox with `-m local_only` (see S16 below).

- **The code under test (DEC-732).** `gov resources` runs as `python3 -m gov.cli.main resources ...` with
  `PYTHONPATH` set to the `src/` folder of the tree that holds this suite (`w2_20_support.SRC`); the launcher, the
  pools and the server start are imported in the test's own process from the same `src/` (the runner's
  `PYTHONPATH`). `test_the_suite_runs_this_worktrees_code` checks it.
- **Nothing real is touched.** Every command runs with an environment built from scratch: a temporary `HOME` (never
  the real `~/.gov-os/machine/`), `TMPDIR`, and `PATH` = this test's stand-in folder + `/usr/local/bin:/usr/bin:/bin`,
  so neither `~/.local/bin` (the interim wrapper) nor `/usr/lib/wsl/lib` (the real `nvidia-smi`) is on it. The
  session's `GOV_ROLE` and `GOV_TICKET` are not passed on. Before a test enters its first session the suite checks
  that the registry folder the command names is inside that test's temporary home.
- **Planted machines only.** Every reading comes from a file the test writes (the variables below); the GPU from a
  stand-in `nvidia-smi` that answers from a planted state and logs its calls; the embedding server from a stand-in
  `ollama` that records its environment, CPU affinity and niceness, started on a free local port (never 11434 or
  11435). Sessions and heavy jobs are child processes the test starts, each in its own process group, killed at the
  end of every test. Memory figures that must be real (a session's live memory) come from children that hold written
  memory (64 to 256 MiB).

## The interface these tests assume

The engineer builds to this; where the ticket left a form open, the choice is the test designer's and is marked
*(choice)*; the open ones are in the decision packages at the end.

### The command

| Invocation | What it does | Exit |
|---|---|---|
| `gov resources [--json] [--root R]` | The reading (below) and the gate. Clears stale entries. Applies nothing else. | 0, open or shut |
| `gov resources --check [--gpu-need-mib N] [--gpu-kind embedder\|reranker\|other] [--json]` | **The start check** for one new session (or a job that declares a GPU need). Without `--gpu-need-mib` it never runs `nvidia-smi` (S10); a plain reading and a start check with a need read the GPU once each (S13, P-6). The cases count only the `nvidia-smi` calls of the command under test, never those of the suite's location check (a plain reading run before a test's first command). `--gpu-kind` defaults to `other`. | 0 and `ok: true` (the reading as `result`) when open; when shut, `ok: false`, `error.code` `RESOURCE_GATE_SHUT`, the reading in `error.details`, an exit code other than 0 and 2 (the same without `--json`, and the text names the broken condition) |
| `gov resources --register PID --ticket ID --session-role ROLE` | Enters a session in the machine-wide registry (its pid, repository, ticket, role). `--heavy` is no longer part of the interface (no weights, DEC-983). | 0, `ok: true` |
| `gov resources --slot test\|rebuild [--tree T] [--workers N] -- CMD...` | **A heavy job.** Waits for one of the configured machine-wide slots (a rebuild also for its tree's lock, `--tree` default the root), then runs `CMD` confined to the slot's CPU set with the slot's thread budget, and gives the slot back when `CMD` ends. *(choice)* | `CMD`'s exit code; `CMD`'s output passes through |
| `gov resources --sample [--json]` | Takes one sample of every live session's process-tree memory, noting whether a verification run holds the lock, and (P-5 (a)) one of every heavy-job slot holder's process tree, with its `kind`. Result `samples`: `[{pid, tree_memory_bytes, verification}]`, a slot holder's sample also `kind: "test"\|"rebuild"`. *(choice)* | 0 |
| `gov resources --remeasure [--json]` | Writes `verification_peak_bytes` (largest sample) and `working_size_bytes` (largest session sample outside verification) and (P-5 (a)) `rebuild_peak_bytes` (largest sample of a `rebuild` slot holder) into the configuration file, dated today, with a source; result `{"old": {the keys}, "new": {the keys}}`. A slot holder is no session: its sample is not a working size. *(choice)* | 0 |
| `gov resources --init-config [--json]` | **P-3 (a), settled.** Writes `$HOME/.gov-os/machine/gate.json`, a template holding every gate value with its date and source and this machine's values from the decisions (floor 3 GiB, DEC-942 item 2; disk 100 GiB and inodes 10,000,000, DEC-898 item 1; GPU margin 0.10, DEC-950 item 2); the gate reads it whole. Over an existing file: refuses, names `gate.json`, changes nothing. | 0 written; not 0 refused |
| `gov resources --trip-wire [--json]` | One pass of the trip-wire: below `oom_floor_bytes`, stops the heavy job (slot holder and its command's processes) whose process tree holds the most memory; result `stopped` (an object naming the job and its command) or `null`; the stop appended as one JSON line to `$HOME/.gov-os/machine/findings.jsonl`. Only slot holders are ever stopped. *(choice)* | 0 |

### The reading (`result`, or `error.details` of a refused start check)

| Key | Meaning |
|---|---|
| `registry` | Absolute path of the registry folder: `$HOME/.gov-os/machine/` or a folder inside it. |
| `available_memory_bytes` | `MemAvailable` in bytes, or `null` when it cannot be read. |
| `sessions_live_memory_bytes` | The live sessions' memory: each session's process tree, **each process counted once** (a worker inside its lead's tree is not counted again, F6). |
| `load_1m`, `load_15m` | The 1- and 15-minute loads, or `null`. |
| `busy_cores_1m` | Busy cores over the last minute, or `null`. |
| `embedding_cpu_p95` | `{"shared": cores, "query": cores}`, the two servers' CPU p95, or `null`. |
| `nproc` | The processor count. |
| `disk` | `{"free_bytes", "free_inodes"}` of the shared disk, or `null`. |
| `sessions` | The live sessions: `pid`, `repository`, `ticket`, `role`, `live_memory_bytes`. |
| `cleared` | The stale entries this read removed, same shape; `[]` when none. |
| `slots` | `{"total": heavy_slots, "held": [one entry per running heavy job]}`. |
| `gpu` | `{"available": true, "memory_used_mib", "memory_total_mib", "utilisation_pct", "processes": [{pid, kind, used_mib}]}` or `{"available": false, "reason": "..."}` (never an error). On the start check only with a GPU need. |
| `gpu_room_mib` | On a start check with a GPU need: the room the job's kind had. |
| `due_for_remeasure` | The measured keys (`verification_peak_bytes`, `working_size_bytes`) dated more than seven days ago; `[]` when none. A notice: it does not shut the gate. |
| `gate` | `{open: bool, reasons: [{condition, reading, threshold, ...}]}`; `reasons` is `[]` when open. |

### The gate

Open only when every condition holds; each broken condition is one reason with its `reading` and `threshold`.
`condition` is one of `memory`, `load`, `cpu`, `disk`, `inodes`, `config`, `gpu`. There is **no sessions condition and
no ceiling on leads or sessions** (DEC-983); heavy jobs wait for slots instead, and a session takes no slot.

- **memory (S6):** `available + sessions_live ≥ floor + working_size × (running sessions + 1)`. Reading: the left
  side; threshold: the right side. "At least": equal opens. The verification peak is not added (nothing is reserved
  for a run that has not started).
- **load (S5):** `min(load_1m, load_15m) < nproc`. Reading: the min; threshold: nproc. Equal shuts.
- **cpu (S2, S12):** `busy_cores_1m + p95(shared) + p95(query) < nproc`. Reading: the sum; threshold: nproc. Equal
  shuts. *(choice: how the servers' p95 is counted)* Busy cores alone shut it only at nproc or above: 4.0 busy of 4
  with both p95 at 0.0 shuts (S2's case); 3.9 opens.
- **disk, inodes (S4):** `free_bytes ≥ disk_floor_bytes`, `free_inodes ≥ inode_floor`. Equal opens.
- **config (S8):** one reason per value missing or malformed, naming its key (or the file, when it is missing or not
  JSON); `reading` the raw value or `null`.
- **gpu (S10, S14), start check with a need only:** some single GPU has room ≥ need × (1 + `gpu_margin`). The room
  for a job is that GPU's free memory less the unused part of the shares of the kinds before it (an `embedder`: none;
  a `reranker`: the embedder's; `other`: the embedder's and the reranker's), where a share's unused part is its share
  less what that kind's processes use on the GPU. No `nvidia-smi`, no GPU, or an unreadable answer: reason `gpu`
  with `reading` `null`.
- **Fail closed (F5):** a reading that cannot be taken is `null` and shuts the gate with its condition, `reading`
  `null`.

### Where the readings come from

| Variable | Default | Format |
|---|---|---|
| `GOV_RESOURCES_MEMINFO` | `/proc/meminfo` | `MemAvailable:` in kB |
| `GOV_RESOURCES_LOADAVG` | `/proc/loadavg` | fields 1 and 3 (1- and 15-minute) |
| `GOV_RESOURCES_NPROC` | the processor count | an integer (the gate's nproc; CPU sets use the real affinity) |
| `GOV_RESOURCES_BUSY_CORES` | the gate's own sampling of `/proc/stat` | one number: busy cores over the last minute |
| `GOV_RESOURCES_EMBEDDING_CPU` | the gate's own sampling of the two servers | JSON `{"shared": p95 cores, "query": p95 cores}` |
| `GOV_RESOURCES_DISK` | `statvfs` of the shared disk | JSON `{"free_bytes": N, "free_inodes": N}` |
| `nvidia-smi` on `PATH` | | read with `--query-gpu=<fields>` and `--query-compute-apps=<fields>`, `--format=csv[,noheader][,nounits]`; fields `memory.total`, `memory.used`, `memory.free`, `utilization.gpu`; `pid`, `process_name`, `used_memory`. Exit 6 with "No devices were found" is no GPU. |

A process's GPU kind is read from its command line *(choice)*: a word whose file name begins with `ollama` is an
`embedder`; `rerank` anywhere a `reranker`; anything else `other`.

### The configuration file: `$HOME/.gov-os/machine/gate.json`

The file `gov.retrieval.ollama` already reads for the servers' cap (`GATE_REL`). Every gate value is an object
`{"value": V, "date": "YYYY-MM-DD", "source": "text"}`; a value without its date or source, or with a date that is
not a date, is malformed. **No default stands in for a missing value** (the old defaults of DEC-742 are gone).

| Key | Value | Notes |
|---|---|---|
| `memory_floor_bytes` | integer ≥ 0 | 3 GiB on this machine (DEC-942 item 2) |
| `verification_peak_bytes` | integer ≥ 0 | measured (S9); due after seven days |
| `working_size_bytes` | integer ≥ 0 | measured (S9); due after seven days |
| `rebuild_peak_bytes` | integer ≥ 0 | measured (S9, P-5 (a)); the tests plant it in every file; whether it is required is package P-7 |
| `disk_floor_bytes` | integer ≥ 0 | 100 GiB (DEC-898 item 1) |
| `inode_floor` | integer ≥ 0 | 10,000,000 (DEC-898 item 1) |
| `verification_lock` | a path (text) | a verification run holds an exclusive `flock` on it |
| `gpu_margin` | number ≥ 0 | 0.10 |
| `oom_floor_bytes` | integer ≥ 0 | the trip-wire's floor, below `memory_floor_bytes` |
| `heavy_slots` | integer ≥ 1 | the machine-wide slots |
| `gpu_shares` | `{"embedder_mib": int ≥ 0, "reranker_mib": int ≥ 0}` | the GPU shares by kind |
| `thread_budget` | integer ≥ 1, **optional** | when present, the slot's thread budget (S15) |
| `embedding_servers` | W2-123's section: `shared` and `query`, each `cpus`, `nice` (and `parallel`, `probe_*`), plus `date` and `source`; `query` also `device`: `"gpu"` (default when absent) or `"cpu"` | the servers' cap (S12) and the query server's device (S20) |

### Heavy jobs: slots, thread budget, CPU set (S7, S15, S17)

- The slots' CPUs are the CPUs the `gov resources` process may use (`os.sched_getaffinity`) less every CPU the
  `embedding_servers` section names. Each slot's CPU set has `max(1, len(slots' CPUs) // heavy_slots)` of them; two
  slots held at once have disjoint sets (where there are CPUs enough).
- The thread budget is `max(1, len(slot's set) // workers)` (`--workers`, default 1), or `thread_budget` when the file
  sets it. Every program the job starts gets it in `GOMAXPROCS`, `OMP_NUM_THREADS`, `MKL_NUM_THREADS`,
  `OPENBLAS_NUM_THREADS`, `RAYON_NUM_THREADS`, `NUMEXPR_NUM_THREADS`, `VECLIB_MAXIMUM_THREADS` and
  `GOV_HEAVY_THREAD_BUDGET` (the variable `gov.secrets` reads), whatever the caller had (999 in the tests).
- A rebuild holds its tree's lock (the real path of `--tree`): a second rebuild of the same tree waits, a rebuild of
  another tree does not.

### The disk reading for gov close (S4)

`gov.resources.check_disk(env=None) -> {"open": bool, "reasons": [{condition, reading, threshold}], "free_bytes",
"free_inodes"}`; `env` (default `os.environ`) supplies `HOME` and `GOV_RESOURCES_DISK`. `gov close` calls it (W2-07's
or W2-66's line).

### The launch (S19)

- `gov.launch.launcher.launch(root, role, ticket, cli_args, gate_override=None, gpu_need_mib=None)`, and on the
  command line `gov launch <role> <ticket> [--gate-override DEC-NNN] [--gpu-need-mib N] [-- ...]` (P-1 (a),
  settled).
- **The slots (P-2 (a) with (c), settled):** a full set of heavy-job slots never refuses a session (S7, DEC-983); a
  launch is refused on the slots only when their reading cannot be taken (`heavy_slots` missing or malformed, named).
- Every launch, lead or worker, runs the start check before any session starts (after W2-136's plan check for a
  lead). A shut gate raises `GovError("LAUNCH_REFUSED", message)`; the message names each broken condition and its
  reading as the reading gives it (an integer of bytes or inodes, a load or a core count as a number), for example
  `the resource gate is shut: memory: reading 1073741824, limit 4294967296 (DEC-1088 (5))`; a missing configuration
  value is named by its key.
- `gate_override="DEC-NNN"` (a decision id, `DEC-` and digits; anything else is refused) starts the session anyway and
  writes **one line to `$HOME/.gov-os/machine/launch.log`** and **one line to standard error** (the launch's output,
  as W2-136's plan override prints its own), each holding `OVERRIDE`/`gate_override: DEC-NNN`, the role, the ticket and
  the conditions passed over, e.g. `gov launch: OVERRIDE gate_override: DEC-1234: engineer DAEO-wrk01 started with the
  resource gate shut: memory: reading 1073741824, limit 4294967296 (DEC-899)`.

### The plan check's source (S21, W2-136's F2 entry criterion)

- `gov.launch.plan_check.check_lead(root, ticket_id, *, ready=None)` (W2-136's function, unchanged in form) and the
  launcher's lead path (`launch(root, "orchestrator", ...)`), called with `root` a **lead worktree** (a git worktree
  of the project), read the tickets (`.tickets/`) and the approved ready list
  (`governance/project/orchestration/ready.txt`) of the **main tree**: the main worktree of `root`'s repository, as
  `gov.launch.store.main_root` finds it. Never the lead worktree's own copies. Called with the main tree, nothing
  changes (W2-136's cases).
- **A named path the dispatcher keeps:** `GOV_PLAN_READY` (W2-136's variable): absolute, that file; relative, read
  against the main tree *(choice)*, never the lead worktree.
- **A plan override** (`plan_override: <DEC-id>` on the main tree's ticket) that admits a lead writes **one line to
  `$HOME/.gov-os/machine/launch.log`** (P-1's launch log) holding `plan_override`, the decision id and the ticket
  (its id or WBS id), and keeps W2-136's one `OVERRIDE` line on standard error.

The planted trees: a main tree and a lead worktree made from it, then one commit on the main tree, so the worktree
holds yesterday's tickets and list (the table in `test_w2_20_plan_source.py`'s docstring).

### The query server's start (S20, DEC-1037)

`gov.retrieval.ollama.ensure_query_available(start=True, env=...)`, with no wrapper on `PATH`:

- CPUs and niceness from `embedding_servers.query` (as today);
- device from `embedding_servers.query.device`: `"gpu"` or absent: the server's environment has no
  `CUDA_VISIBLE_DEVICES=-1` (a caller's `-1` is removed); `"cpu"`: `CUDA_VISIBLE_DEVICES=-1`; anything else: no start,
  `started: false`, and the answer (its `warning`) names `device`;
- none of the eight thread-budget variables above in the server's environment;
- the server's standard output and error appended to `$HOME/.gov-os/machine/embedding-query.log`;
- one JSON line per start appended to `$HOME/.gov-os/machine/embedding-starts.jsonl`:
  `{"time": ISO 8601, "server": "query", "device": "gpu"|"cpu", "caller": {"pid", "cwd", "command"}}`, the caller being
  the process that called `ensure_query_available`.

The evidence names the owner ACT's steps (the wrapper removed, the real binary found on PATH, a restart seen capped);
the tests do not apply them.

### S16, measured (`local_only`)

`test_w2_20_measured.py` runs a planted suite (8 tests, each starting a program that spins one thread per
`os.cpu_count()` CPU for 3 s, ignoring its CPU set; `-n 2` when pytest-xdist is there) twice: plainly and through
`gov resources --slot test`, under the real `~/.gov-os/machine/gate.json` (read, never written). It samples busy cores
from `/proc/stat` every 0.2 s and asserts: without the slot the p95 exceeds the share + 1 (else there is no measure);
with it, at most the share + 1; and the slot's run at most 20 % slower. It prints the figures for the evidence. **The
CTO runs it outside the sandbox**, on the real machine, not inside another heavy slot; elsewhere it skips:
`GOV_W2_20_MEASURE=1 PYTHONPATH=<tree>/src python3 -m pytest tests/acceptance/W2-20/test_w2_20_measured.py -m local_only -p no:cacheprovider -s`.
The planted programs spin until a deadline, so the time compares the slot's overhead, not a fixed amount of work
(P-4, confirmed by the CTO 2026-11-09: the 20 % is measured on time-bound programs; the case is unchanged).

## KPI lines

Ids in the ticket's order (`.tickets/DAEO-r30l.md`, 2026-11-09). "New/changed" from the ticket's history
(`git log -p -- .tickets/DAEO-r30l.md`) against the 10-17 map (Success 1-3 and one failure line).

| Id | Line (short) | Since |
|---|---|---|
| S1 | `gov resources` reads memory, load and every live session from the machine-wide registry | 10-16, unchanged |
| S2 | the gate opens or shuts with a named reason; it judges busy cores as well as the load, and shows both | changed 11-01 (SMART-WORK-3) |
| S3 | a stale entry (dead PID) is cleared | 10-16, unchanged |
| S4 | the shared disk: floors of space and inodes; launch refuses; one function for gov close | new 10-22 (DEC-898) |
| S5 | load: min(1-, 15-minute) < nproc | new 10-29 (DEC-942, DEC-950) |
| S6 | memory: MemAvailable + live ≥ floor + working sizes (running + new); nothing reserved | new 10-29, changed 10-31 (DEC-961, DEC-983) |
| S7 | heavy jobs take slots; sessions none; no other ceiling; per-tree rebuild lock; the rebuild's peak | new 10-31, changed 11-01 |
| S8 | all values in one dated, sourced file; missing or malformed shuts; due after seven days | new 10-29 |
| S9 | the re-measure | new 10-29 |
| S10 | GPU, minimal: a declared need + 10 %; none read without a need | new 10-29 |
| S11 | the out-of-memory trip-wire | new 10-29, changed 10-31 |
| S12 | the embedding servers' durable CPU cap; their p95 counted at admission; a restart keeps the cap | new 11-01 (DEC-1017) |
| S13 | the GPU measured: memory, utilisation, holders; no GPU named, never an error | new 11-02 (DEC-1031) |
| S14 | the GPU scheduled by shares; the room stated | new 11-02 (DEC-1031) |
| S15 | a heavy slot's thread budget | new 11-02 (DEC-1039) |
| S16 | measured: one slot holds a CPU-hungry suite to its share + 1, within 20 % | new 11-02 (DEC-1039) |
| S17 | a heavy slot's own CPU set, outside the servers' | new 11-02 (DEC-1039) |
| S18 | the product's pools sized to the CPU set (gov.secrets included) | new 11-02 (DEC-1039, DEC-1041) |
| S19 | enforcement at launch, every session, one recorded override | new 11-06 (DEC-1088 (5)(b)) |
| S20 | the query-wrapper removal (DEC-1037) | new 11-09 (DEC-1097 (8)) |
| S21 | W2-136's F2 entry criterion: the plan check reads the main tree's tickets and ready list (or a named path), never a lead worktree's; a plan override in a launch log as well as stderr | new 11-09 (DEC-1088 (5)(b), DEC-1097 (8)), round 2 |
| F1 | a heavy job's children use more CPUs than its share | new 11-02 |
| F2 | another repository's session counts; a start while shut is refused with the reading | 10-16, unchanged |
| F3 | a launch or close below either disk floor; disk read without inodes | new 10-22 |
| F4 | any fixed ceiling on leads or sessions other than the slots | new 10-31 (DEC-983) |
| F5 | a value not from the file, or an unreadable reading treated as met | new 10-29 |
| F6 | a worker's memory charged twice | new 10-29 |

## The old cases (10-17) and what became of them

Brought unchanged from `w2/W2-20` in `fa2abff4d`; the support module and fixtures rewritten in `420b7cdc3` (the dated
configuration file, the new readings and stand-ins; `--register --heavy` and the weights gone). Each revision or
removal below is its own commit with `Rewrite-Reason: DEC-1097 (8)`.

| Old case | Fate | Why | Commit |
|---|---|---|---|
| `test_the_suite_runs_this_worktrees_code` | kept | unchanged and right | — |
| `test_the_registry_belongs_to_the_home_folder_not_to_the_repository` | kept | unchanged and right | — |
| `test_the_gate_is_open_when_every_condition_holds` | kept | unchanged and right (the support's whole configuration) | — |
| `test_W2_M188_a_start_while_the_gate_is_open_goes_ahead` | kept | unchanged and right | — |
| `test_the_reading_reports_memory_load_processors_and_the_registry_folder` | revised | no weighted count (DEC-983); the 15-minute load and busy cores shown (S2, S5) | `6a4b10af2` |
| `test_every_live_session_is_read_with_its_pid_repository_ticket_role_and_weight` | revised as `..._and_live_memory` | no weights; each session's live memory (S6) | `e3141f6f1` |
| `test_W2_M244_W2_M188_W2_M262_a_dead_pid_is_cleared_and_a_live_one_is_kept` | revised | the weighted count's line dropped | `688a5cfbf` |
| `test_W2_M244_W2_M188_W2_M262_a_stale_entry_does_not_count_against_the_gate` | revised | the memory rule's working size in place of the weight | `3f41cf3e9` |
| `test_a_session_entered_from_another_repository_counts_against_this_ones_gate` | revised | counted by the memory rule, not a weight | `3d4b0f9ff` |
| `test_W2_M244_W2_M188_a_start_while_the_gate_is_shut_is_refused_with_the_reading` | revised | the memory rule's need (floor + working size) | `943cf4918` |
| `test_W2_M244_the_refusal_without_json_has_the_same_exit_code_and_names_the_reason` | revised | the load rule against nproc | `c9bc9a1f8` |
| `test_one_broken_condition_shuts_the_gate_and_is_named_with_its_reading_and_threshold` | revised | memory, load, cpu, disk, inodes; the `sessions` case removed | `311760327` |
| `test_several_broken_conditions_are_all_named` | revised | the five current conditions | `f5747dc6e` |
| `test_exactly_at_a_threshold` | revised | memory, load, cpu, disk, inodes boundaries | `352d361da` |
| `test_a_heavy_session_counts_double_and_tips_the_count_over_the_maximum` | removed | no weighted ceiling (DEC-983, S7, F4) | `9721dd904` |
| `test_the_proposed_defaults_are_in_force_when_nothing_is_configured` | revised as `test_with_no_configuration_file_the_gate_is_shut_and_names_it` | S8: no defaults; a missing value shuts | `84cd0c7fc` |
| `test_a_reading_that_cannot_be_taken_never_opens_the_gate` | revised | the current readings (memory, load, busy cores, p95, disk) | `c906733ca` |
| `test_DEC_747_at_most_8_holds_after_the_start` | removed | DEC-742/DEC-747's ceiling superseded (DEC-983) | `07aed5068` |

## Round 2's changes (2026-11-09)

| Change | Point | Cases | Commit |
|---|---|---|---|
| new file: S21's cases | the F2 line (DEC-1088 (5)(b)) | 9 cases in `test_w2_20_plan_source.py` | `cc88ceeea` |
| support: every planted file carries a dated `rebuild_peak_bytes` | P-5 (a) | none changed in what it asserts | `a8575eda6` |
| new case: the rebuild peak from rebuild slot holders, no verification lock | P-5 (a) | `test_w2_20_remeasure.py::test_s7_s9_...` | `3418453fc` |
| new cases: `--init-config` writes the template, never overwrites | P-3 (a) | 2 in `test_w2_20_config.py` | `cc2f14f42` |
| new cases: a full set of slots never refuses a launch; an unreadable `heavy_slots` does; docstring notes P-1 (a) and P-2 | P-1 (a), P-2 (a)+(c) | 6 in `test_w2_20_launch.py` | `1562a461e` |
| none: the override already a launch option logged to `launch.log` and stderr | P-1 (a) | round 1's four override and command-line cases, unchanged | — |
| none: the measured case already uses time-bound programs | P-4 | S16's case, unchanged | — |
| none: no `nvidia-smi` without a declared need; once with one | P-6 | round 1's S10/S13 cases, unchanged | — |

## Round 4's changes (2026-11-09)

Each case below disagreed with this README's interface or with P-6, the cause was in the case, and each was revised
in its own commit (`Rewrite-Reason: DEC-1097 (8)`). The interface did not change.

| Case | Disagreement | Revision | Commit |
|---|---|---|---|
| `test_w2_20_cpu.py::test_s2_the_gate_judges_busy_cores_and_load_each_on_its_own_and_shows_both[busy cores high, load low]` | planted busy cores 3.9 of 4, both p95 0.0: the cpu rule's sum 3.9 < 4 opens, yet the case expected shut on cpu. S2's line ("judges real CPU use ... as well as the load, and shows both") names no threshold, so the README's rule stands | busy cores 4.0 of 4 (sum 4.0, equal shuts); load 0.1 still far below nproc | `8616cb090` |
| `test_w2_20_gpu.py::test_s10_a_start_with_no_declared_need_never_reads_the_gpu[a GPU planted]` | the GPU was planted before the test's first command, so the suite's location check (a plain reading, which reads the GPU once under S13/P-6) logged an `nvidia-smi` call that the case blamed on the start check | the support's new `located(repo)` runs the location check first and returns the calls so far; the case counts only the start check's calls | `4d3ddbbea` |
| `test_w2_20_gpu.py::test_s13_the_reading_measures_gpu_memory_utilisation_and_which_processes_hold_it` | the location check's reading and the reading under test were counted as one check, two reads of each query | counts only the reading under test's calls (after `located`) | `42bd8e2b1` |

Run on this branch (no product; integrate's code), same command as round 2 with an empty `HOME`: **154 failed, 9
passed, 1 deselected**, as in round 2. The three revised cases fail because the product is missing (`invalid choice:
'resources'`), and the nine greens are the same guards.

**The port (part 3)**, each file its own commit with `Rewrite-Reason: DEC-1097 (8)`: `w1_07_support.py`
(`b393e2ddd`: `resources` added after `accept`), `test_w1_07_recorded_commands.py` (`c4b57a5af`: six recorded),
`test_w1_32_command_set.py` (`f3d357e4a`: `resources` in the exact set, `release` still excused), W1-07's README
(`999b5fd1d`), W1-26's README (`800495a4e`). On integrate the cases that need `gov resources` itself are red until
W2-20 builds it: `test_w1_07_recorded_commands.py::test_a_recorded_gov_command_is_offered_and_answers_its_help[resources]`,
`test_w1_32_command_set.py::test_the_command_set_is_the_twelve_and_the_three_recorded_ones`,
`test_w1_26_recorded_commands.py::test_a_recorded_command_without_its_module_is_a_finding_that_names_it[resources]`,
`::test_with_every_module_present_the_check_has_no_finding`, `::test_a_skill_may_name_a_recorded_gov_command[resources]`
(W1-07's and W1-26's run only with `--optin=breadth`/`lifted`, DEC-1061).

## KPI line → tests → state on integrate

`w2/integrate` at `8bb10a683` (this branch's base), with this suite: **137 failed, 8 passed, 1 skipped** (146
cases; the skipped one is S16's `local_only`, which skips unless `GOV_W2_20_MEASURE=1`). Every red fails for the reason in its row; the greens are guards
of what integrate already does and must keep doing.

**Round 2**, on this branch (integrate merged at `570ba4dc0`), run as
`pytest tests/acceptance/W2-20 -m "not local_only" -k "not real and not green_here and not time_limit"` with an empty
`HOME`: **154 failed, 9 passed, 1 deselected** (164 cases; the deselected one is S16's `local_only` case; the `-k`
filter matches no case of this suite). Round 1's cases are in the same state as before; the 18 new ones are 17 red
and one green guard (S21's main-tree case).

| KPI line | Test (node id) | On integrate | Why |
|---|---|---|---|
| S1 | `test_w2_20_failure.py::test_a_session_entered_from_another_repository_counts_against_this_ones_gate` | red | `gov resources` does not exist (`invalid choice: 'resources'`, exit 2, no JSON envelope) |
| S1 | `test_w2_20_reading.py::test_the_suite_runs_this_worktrees_code` | green (guard) | DEC-732: `gov` is imported from this tree's `src/` |
| S1 | `test_w2_20_reading.py::test_the_reading_reports_memory_load_processors_and_the_registry_folder` | red | `gov resources` does not exist (`invalid choice: 'resources'`, exit 2, no JSON envelope) |
| S1 | `test_w2_20_reading.py::test_every_live_session_is_read_with_its_pid_repository_ticket_role_and_live_memory` | red | `gov resources` does not exist (`invalid choice: 'resources'`, exit 2, no JSON envelope) |
| S1 | `test_w2_20_reading.py::test_the_registry_belongs_to_the_home_folder_not_to_the_repository` | red | `gov resources` does not exist (`invalid choice: 'resources'`, exit 2, no JSON envelope) |
| S2 | `test_w2_20_cpu.py::test_s2_the_gate_judges_busy_cores_and_load_each_on_its_own_and_shows_both[busy cores high, load low]` | red | `gov resources` does not exist (`invalid choice: 'resources'`, exit 2, no JSON envelope) |
| S2 | `test_w2_20_cpu.py::test_s2_the_gate_judges_busy_cores_and_load_each_on_its_own_and_shows_both[load high, busy cores low]` | red | `gov resources` does not exist (`invalid choice: 'resources'`, exit 2, no JSON envelope) |
| S2 | `test_w2_20_cpu.py::test_s2_busy_cores_and_load_within_open_the_gate` | red | `gov resources` does not exist (`invalid choice: 'resources'`, exit 2, no JSON envelope) |
| S2 | `test_w2_20_gate.py::test_the_gate_is_open_when_every_condition_holds` | red | `gov resources` does not exist (`invalid choice: 'resources'`, exit 2, no JSON envelope) |
| S2 | `test_w2_20_gate.py::test_one_broken_condition_shuts_the_gate_and_is_named_with_its_reading_and_threshold[memory]` | red | `gov resources` does not exist (`invalid choice: 'resources'`, exit 2, no JSON envelope) |
| S2 | `test_w2_20_gate.py::test_one_broken_condition_shuts_the_gate_and_is_named_with_its_reading_and_threshold[load [W2-M262]]` | red | `gov resources` does not exist (`invalid choice: 'resources'`, exit 2, no JSON envelope) |
| S2 | `test_w2_20_gate.py::test_one_broken_condition_shuts_the_gate_and_is_named_with_its_reading_and_threshold[cpu]` | red | `gov resources` does not exist (`invalid choice: 'resources'`, exit 2, no JSON envelope) |
| S2 | `test_w2_20_gate.py::test_one_broken_condition_shuts_the_gate_and_is_named_with_its_reading_and_threshold[disk]` | red | `gov resources` does not exist (`invalid choice: 'resources'`, exit 2, no JSON envelope) |
| S2 | `test_w2_20_gate.py::test_one_broken_condition_shuts_the_gate_and_is_named_with_its_reading_and_threshold[inodes]` | red | `gov resources` does not exist (`invalid choice: 'resources'`, exit 2, no JSON envelope) |
| S2 | `test_w2_20_gate.py::test_several_broken_conditions_are_all_named` | red | `gov resources` does not exist (`invalid choice: 'resources'`, exit 2, no JSON envelope) |
| S2 | `test_w2_20_gate.py::test_exactly_at_a_threshold[memory]` | red | `gov resources` does not exist (`invalid choice: 'resources'`, exit 2, no JSON envelope) |
| S2 | `test_w2_20_gate.py::test_exactly_at_a_threshold[load]` | red | `gov resources` does not exist (`invalid choice: 'resources'`, exit 2, no JSON envelope) |
| S2 | `test_w2_20_gate.py::test_exactly_at_a_threshold[cpu]` | red | `gov resources` does not exist (`invalid choice: 'resources'`, exit 2, no JSON envelope) |
| S2 | `test_w2_20_gate.py::test_exactly_at_a_threshold[disk]` | red | `gov resources` does not exist (`invalid choice: 'resources'`, exit 2, no JSON envelope) |
| S2 | `test_w2_20_gate.py::test_exactly_at_a_threshold[inodes]` | red | `gov resources` does not exist (`invalid choice: 'resources'`, exit 2, no JSON envelope) |
| S2 | `test_w2_20_reading.py::test_the_reading_reports_memory_load_processors_and_the_registry_folder` | red | `gov resources` does not exist (`invalid choice: 'resources'`, exit 2, no JSON envelope) |
| S3 | `test_w2_20_stale.py::test_W2_M244_W2_M188_W2_M262_a_dead_pid_is_cleared_and_a_live_one_is_kept` | red | `gov resources` does not exist (`invalid choice: 'resources'`, exit 2, no JSON envelope) |
| S3 | `test_w2_20_stale.py::test_W2_M244_W2_M188_W2_M262_a_stale_entry_does_not_count_against_the_gate` | red | `gov resources` does not exist (`invalid choice: 'resources'`, exit 2, no JSON envelope) |
| S4 | `test_w2_20_disk.py::test_s4_the_disk_reading_is_one_function_gov_close_can_call[both at their floors opens]` | red | `gov.resources` does not exist (`ModuleNotFoundError`) |
| S4 | `test_w2_20_disk.py::test_s4_the_disk_reading_is_one_function_gov_close_can_call[space below its floor]` | red | `gov.resources` does not exist (`ModuleNotFoundError`) |
| S4 | `test_w2_20_disk.py::test_s4_the_disk_reading_is_one_function_gov_close_can_call[inodes below their floor [F3]]` | red | `gov.resources` does not exist (`ModuleNotFoundError`) |
| S4 | `test_w2_20_disk.py::test_s4_the_disk_reading_is_one_function_gov_close_can_call[both below]` | red | `gov.resources` does not exist (`ModuleNotFoundError`) |
| S4 | `test_w2_20_disk.py::test_s4_the_floors_are_the_configuration_files` | red | `gov.resources` does not exist |
| S4 | `test_w2_20_disk.py::test_s4_an_unreadable_disk_is_shut_for_a_close_too` | red | `gov.resources` does not exist |
| S5 | `test_w2_20_load.py::test_s5_the_load_rule_is_the_lower_of_the_1_and_15_minute_loads_below_nproc[a short peak opens]` | red | `gov resources` does not exist (`invalid choice: 'resources'`, exit 2, no JSON envelope) |
| S5 | `test_w2_20_load.py::test_s5_the_load_rule_is_the_lower_of_the_1_and_15_minute_loads_below_nproc[a falling load opens]` | red | `gov resources` does not exist (`invalid choice: 'resources'`, exit 2, no JSON envelope) |
| S5 | `test_w2_20_load.py::test_s5_the_load_rule_is_the_lower_of_the_1_and_15_minute_loads_below_nproc[just below nproc opens]` | red | `gov resources` does not exist (`invalid choice: 'resources'`, exit 2, no JSON envelope) |
| S5 | `test_w2_20_load.py::test_s5_the_load_rule_is_the_lower_of_the_1_and_15_minute_loads_below_nproc[both at nproc shuts]` | red | `gov resources` does not exist (`invalid choice: 'resources'`, exit 2, no JSON envelope) |
| S5 | `test_w2_20_load.py::test_s5_the_load_rule_is_the_lower_of_the_1_and_15_minute_loads_below_nproc[both above nproc shuts]` | red | `gov resources` does not exist (`invalid choice: 'resources'`, exit 2, no JSON envelope) |
| S5 | `test_w2_20_reading.py::test_the_reading_reports_memory_load_processors_and_the_registry_folder` | red | `gov resources` does not exist (`invalid choice: 'resources'`, exit 2, no JSON envelope) |
| S6 | `test_w2_20_memory.py::test_s6_the_running_sessions_live_memory_is_added_to_memavailable` | red | `gov resources` does not exist (`invalid choice: 'resources'`, exit 2, no JSON envelope) |
| S6 | `test_w2_20_memory.py::test_s6_each_running_session_and_the_new_one_need_a_working_size[2 running opens]` | red | `gov resources` does not exist (`invalid choice: 'resources'`, exit 2, no JSON envelope) |
| S6 | `test_w2_20_memory.py::test_s6_each_running_session_and_the_new_one_need_a_working_size[3 running shuts]` | red | `gov resources` does not exist (`invalid choice: 'resources'`, exit 2, no JSON envelope) |
| S6 | `test_w2_20_memory.py::test_s6_nothing_is_reserved_for_a_run_that_has_not_started` | red | `gov resources` does not exist (`invalid choice: 'resources'`, exit 2, no JSON envelope) |
| S6 | `test_w2_20_reading.py::test_every_live_session_is_read_with_its_pid_repository_ticket_role_and_live_memory` | red | `gov resources` does not exist (`invalid choice: 'resources'`, exit 2, no JSON envelope) |
| S7 | `test_w2_20_slots.py::test_s7_a_heavy_job_waits_for_a_machine_wide_slot[a test run waits for a test run]` | red | `gov resources` does not exist (`invalid choice: 'resources'`, exit 2, no JSON envelope) |
| S7 | `test_w2_20_slots.py::test_s7_a_heavy_job_waits_for_a_machine_wide_slot[a rebuild waits for a test run]` | red | `gov resources` does not exist (`invalid choice: 'resources'`, exit 2, no JSON envelope) |
| S7 | `test_w2_20_slots.py::test_s7_a_heavy_job_waits_for_a_machine_wide_slot[a test run waits for a rebuild]` | red | `gov resources` does not exist (`invalid choice: 'resources'`, exit 2, no JSON envelope) |
| S7 | `test_w2_20_slots.py::test_s7_the_number_of_slots_is_the_configuration_files` | red | `gov resources` does not exist (`invalid choice: 'resources'`, exit 2, no JSON envelope) |
| S7 | `test_w2_20_slots.py::test_s7_a_rebuild_excludes_only_another_rebuild_of_the_same_tree` | red | `gov resources` does not exist (`invalid choice: 'resources'`, exit 2, no JSON envelope) |
| S7 | `test_w2_20_slots.py::test_s7_a_session_takes_no_slot` | red | `gov resources` does not exist (`invalid choice: 'resources'`, exit 2, no JSON envelope) |
| S7 | `test_w2_20_slots.py::test_f4_no_fixed_ceiling_on_leads_or_sessions` | red | `gov resources` does not exist (`invalid choice: 'resources'`, exit 2, no JSON envelope) |
| S8 | `test_w2_20_config.py::test_s8_a_value_missing_shuts_the_gate_naming_it[memory_floor_bytes]` | red | `gov resources` does not exist (`invalid choice: 'resources'`, exit 2, no JSON envelope) |
| S8 | `test_w2_20_config.py::test_s8_a_value_missing_shuts_the_gate_naming_it[verification_peak_bytes]` | red | `gov resources` does not exist (`invalid choice: 'resources'`, exit 2, no JSON envelope) |
| S8 | `test_w2_20_config.py::test_s8_a_value_missing_shuts_the_gate_naming_it[working_size_bytes]` | red | `gov resources` does not exist (`invalid choice: 'resources'`, exit 2, no JSON envelope) |
| S8 | `test_w2_20_config.py::test_s8_a_value_missing_shuts_the_gate_naming_it[disk_floor_bytes]` | red | `gov resources` does not exist (`invalid choice: 'resources'`, exit 2, no JSON envelope) |
| S8 | `test_w2_20_config.py::test_s8_a_value_missing_shuts_the_gate_naming_it[inode_floor]` | red | `gov resources` does not exist (`invalid choice: 'resources'`, exit 2, no JSON envelope) |
| S8 | `test_w2_20_config.py::test_s8_a_value_missing_shuts_the_gate_naming_it[verification_lock]` | red | `gov resources` does not exist (`invalid choice: 'resources'`, exit 2, no JSON envelope) |
| S8 | `test_w2_20_config.py::test_s8_a_value_missing_shuts_the_gate_naming_it[gpu_margin]` | red | `gov resources` does not exist (`invalid choice: 'resources'`, exit 2, no JSON envelope) |
| S8 | `test_w2_20_config.py::test_s8_a_value_missing_shuts_the_gate_naming_it[oom_floor_bytes]` | red | `gov resources` does not exist (`invalid choice: 'resources'`, exit 2, no JSON envelope) |
| S8 | `test_w2_20_config.py::test_s8_a_value_missing_shuts_the_gate_naming_it[heavy_slots]` | red | `gov resources` does not exist (`invalid choice: 'resources'`, exit 2, no JSON envelope) |
| S8 | `test_w2_20_config.py::test_s8_a_value_missing_shuts_the_gate_naming_it[gpu_shares]` | red | `gov resources` does not exist (`invalid choice: 'resources'`, exit 2, no JSON envelope) |
| S8 | `test_w2_20_config.py::test_s8_a_malformed_value_shuts_the_gate_naming_it[a word for a number]` | red | `gov resources` does not exist (`invalid choice: 'resources'`, exit 2, no JSON envelope) |
| S8 | `test_w2_20_config.py::test_s8_a_malformed_value_shuts_the_gate_naming_it[a negative size]` | red | `gov resources` does not exist (`invalid choice: 'resources'`, exit 2, no JSON envelope) |
| S8 | `test_w2_20_config.py::test_s8_a_malformed_value_shuts_the_gate_naming_it[no slot at all]` | red | `gov resources` does not exist (`invalid choice: 'resources'`, exit 2, no JSON envelope) |
| S8 | `test_w2_20_config.py::test_s8_a_malformed_value_shuts_the_gate_naming_it[a margin in words]` | red | `gov resources` does not exist (`invalid choice: 'resources'`, exit 2, no JSON envelope) |
| S8 | `test_w2_20_config.py::test_s8_a_malformed_value_shuts_the_gate_naming_it[a lock that is no path]` | red | `gov resources` does not exist (`invalid choice: 'resources'`, exit 2, no JSON envelope) |
| S8 | `test_w2_20_config.py::test_s8_a_malformed_value_shuts_the_gate_naming_it[a fraction of an inode]` | red | `gov resources` does not exist (`invalid choice: 'resources'`, exit 2, no JSON envelope) |
| S8 | `test_w2_20_config.py::test_s8_a_malformed_value_shuts_the_gate_naming_it[shares that are no map]` | red | `gov resources` does not exist (`invalid choice: 'resources'`, exit 2, no JSON envelope) |
| S8 | `test_w2_20_config.py::test_s8_a_malformed_value_shuts_the_gate_naming_it[a value without its date]` | red | `gov resources` does not exist (`invalid choice: 'resources'`, exit 2, no JSON envelope) |
| S8 | `test_w2_20_config.py::test_s8_a_malformed_value_shuts_the_gate_naming_it[a value without its source]` | red | `gov resources` does not exist (`invalid choice: 'resources'`, exit 2, no JSON envelope) |
| S8 | `test_w2_20_config.py::test_s8_a_malformed_value_shuts_the_gate_naming_it[a date that is no date]` | red | `gov resources` does not exist (`invalid choice: 'resources'`, exit 2, no JSON envelope) |
| S8 | `test_w2_20_config.py::test_s8_a_malformed_value_shuts_the_gate_naming_it[a bare value, no date or source]` | red | `gov resources` does not exist (`invalid choice: 'resources'`, exit 2, no JSON envelope) |
| S8 | `test_w2_20_config.py::test_s8_a_file_that_is_not_json_shuts_the_gate` | red | `gov resources` does not exist (`invalid choice: 'resources'`, exit 2, no JSON envelope) |
| S8 | `test_w2_20_config.py::test_s8_a_measured_figure_older_than_seven_days_is_named_due_for_re_measure[8 days old is due]` | red | `gov resources` does not exist (`invalid choice: 'resources'`, exit 2, no JSON envelope) |
| S8 | `test_w2_20_config.py::test_s8_a_measured_figure_older_than_seven_days_is_named_due_for_re_measure[7 days old is not]` | red | `gov resources` does not exist (`invalid choice: 'resources'`, exit 2, no JSON envelope) |
| S8 | `test_w2_20_gate.py::test_with_no_configuration_file_the_gate_is_shut_and_names_it` | red | `gov resources` does not exist (`invalid choice: 'resources'`, exit 2, no JSON envelope) |
| S9 | `test_w2_20_remeasure.py::test_s9_samples_note_the_verification_lock_and_the_remeasure_writes_both_figures_with_the_date` | red | `gov resources` does not exist (`invalid choice: 'resources'`, exit 2, no JSON envelope) |
| S10 | `test_w2_20_gpu.py::test_s10_a_declared_gpu_need_opens_only_with_the_need_plus_the_margin_free_on_one_gpu[free 1101 for a need of 1000 opens]` | red | `gov resources` does not exist (`invalid choice: 'resources'`, exit 2, no JSON envelope) |
| S10 | `test_w2_20_gpu.py::test_s10_a_declared_gpu_need_opens_only_with_the_need_plus_the_margin_free_on_one_gpu[free 1099 shuts]` | red | `gov resources` does not exist (`invalid choice: 'resources'`, exit 2, no JSON envelope) |
| S10 | `test_w2_20_gpu.py::test_s10_a_declared_gpu_need_opens_only_with_the_need_plus_the_margin_free_on_one_gpu[the second GPU has room]` | red | `gov resources` does not exist (`invalid choice: 'resources'`, exit 2, no JSON envelope) |
| S10 | `test_w2_20_gpu.py::test_s10_a_declared_gpu_need_opens_only_with_the_need_plus_the_margin_free_on_one_gpu[room only across two GPUs shuts]` | red | `gov resources` does not exist (`invalid choice: 'resources'`, exit 2, no JSON envelope) |
| S10 | `test_w2_20_gpu.py::test_s10_no_nvidia_smi_or_no_gpu_shuts_a_start_that_declares_a_need_named[no nvidia-smi]` | red | `gov resources` does not exist (`invalid choice: 'resources'`, exit 2, no JSON envelope) |
| S10 | `test_w2_20_gpu.py::test_s10_no_nvidia_smi_or_no_gpu_shuts_a_start_that_declares_a_need_named[no GPU]` | red | `gov resources` does not exist (`invalid choice: 'resources'`, exit 2, no JSON envelope) |
| S10 | `test_w2_20_gpu.py::test_s10_no_nvidia_smi_or_no_gpu_shuts_a_start_that_declares_a_need_named[an unreadable GPU]` | red | `gov resources` does not exist (`invalid choice: 'resources'`, exit 2, no JSON envelope) |
| S10 | `test_w2_20_gpu.py::test_s10_a_start_with_no_declared_need_never_reads_the_gpu[a GPU planted]` | red | `gov resources` does not exist (`invalid choice: 'resources'`, exit 2, no JSON envelope) |
| S10 | `test_w2_20_gpu.py::test_s10_a_start_with_no_declared_need_never_reads_the_gpu[no nvidia-smi]` | red | `gov resources` does not exist (`invalid choice: 'resources'`, exit 2, no JSON envelope) |
| S11 | `test_w2_20_tripwire.py::test_s11_below_the_trip_floor_the_largest_heavy_job_is_stopped_and_nothing_else` | red | `gov resources` does not exist (`invalid choice: 'resources'`, exit 2, no JSON envelope) |
| S11 | `test_w2_20_tripwire.py::test_s11_at_or_above_the_trip_floor_nothing_is_stopped` | red | `gov resources` does not exist (`invalid choice: 'resources'`, exit 2, no JSON envelope) |
| S12 | `test_w2_20_cpu.py::test_s12_both_servers_cpu_p95_count_when_a_session_is_admitted[both within]` | red | `gov resources` does not exist (`invalid choice: 'resources'`, exit 2, no JSON envelope) |
| S12 | `test_w2_20_cpu.py::test_s12_both_servers_cpu_p95_count_when_a_session_is_admitted[the shared server's p95 tips it]` | red | `gov resources` does not exist (`invalid choice: 'resources'`, exit 2, no JSON envelope) |
| S12 | `test_w2_20_cpu.py::test_s12_both_servers_cpu_p95_count_when_a_session_is_admitted[the query server's p95 tips it]` | red | `gov resources` does not exist (`invalid choice: 'resources'`, exit 2, no JSON envelope) |
| S12 | `test_w2_20_embedding_cap.py::test_s12_a_planted_restart_of_either_server_applies_the_cap_from_the_gate_file[shared]` | green (guard) | W2-123's start already applies `embedding_servers`' CPUs and niceness (`_capped`) |
| S12 | `test_w2_20_embedding_cap.py::test_s12_a_planted_restart_of_either_server_applies_the_cap_from_the_gate_file[query]` | green (guard) | W2-123's start already applies `embedding_servers`' CPUs and niceness (`_capped`) |
| S13 | `test_w2_20_gpu.py::test_s13_the_reading_measures_gpu_memory_utilisation_and_which_processes_hold_it` | red | `gov resources` does not exist (`invalid choice: 'resources'`, exit 2, no JSON envelope) |
| S13 | `test_w2_20_gpu.py::test_s13_no_gpu_or_an_unreadable_one_is_named_in_the_answer_never_an_error[no nvidia-smi]` | red | `gov resources` does not exist (`invalid choice: 'resources'`, exit 2, no JSON envelope) |
| S13 | `test_w2_20_gpu.py::test_s13_no_gpu_or_an_unreadable_one_is_named_in_the_answer_never_an_error[no GPU]` | red | `gov resources` does not exist (`invalid choice: 'resources'`, exit 2, no JSON envelope) |
| S13 | `test_w2_20_gpu.py::test_s13_no_gpu_or_an_unreadable_one_is_named_in_the_answer_never_an_error[an unreadable GPU]` | red | `gov resources` does not exist (`invalid choice: 'resources'`, exit 2, no JSON envelope) |
| S14 | `test_w2_20_gpu.py::test_s14_a_job_that_would_push_the_embedder_off_the_gpu_waits_and_the_answer_states_the_room[a reranker within its room]` | red | `gov resources` does not exist (`invalid choice: 'resources'`, exit 2, no JSON envelope) |
| S14 | `test_w2_20_gpu.py::test_s14_a_job_that_would_push_the_embedder_off_the_gpu_waits_and_the_answer_states_the_room[a reranker that would push the embedder off]` | red | `gov resources` does not exist (`invalid choice: 'resources'`, exit 2, no JSON envelope) |
| S14 | `test_w2_20_gpu.py::test_s14_a_job_that_would_push_the_embedder_off_the_gpu_waits_and_the_answer_states_the_room[other work behind the embedder and the reranker]` | red | `gov resources` does not exist (`invalid choice: 'resources'`, exit 2, no JSON envelope) |
| S14 | `test_w2_20_gpu.py::test_s14_a_job_that_would_push_the_embedder_off_the_gpu_waits_and_the_answer_states_the_room[the embedder already loaded]` | red | `gov resources` does not exist (`invalid choice: 'resources'`, exit 2, no JSON envelope) |
| S15 | `test_w2_20_budget.py::test_s15_every_program_a_heavy_job_starts_gets_the_slots_thread_budget[one worker]` | red | `gov resources` does not exist (`invalid choice: 'resources'`, exit 2, no JSON envelope) |
| S15 | `test_w2_20_budget.py::test_s15_every_program_a_heavy_job_starts_gets_the_slots_thread_budget[four workers]` | red | `gov resources` does not exist (`invalid choice: 'resources'`, exit 2, no JSON envelope) |
| S15 | `test_w2_20_budget.py::test_s15_the_configuration_file_may_set_the_budget` | red | `gov resources` does not exist (`invalid choice: 'resources'`, exit 2, no JSON envelope) |
| S16 | `test_w2_20_measured.py::test_s16_one_slot_holds_a_cpu_hungry_suite_to_its_share_plus_one_within_20_percent_of_the_time` | skipped (`local_only`) | skips unless `GOV_W2_20_MEASURE=1`; the CTO runs it outside the sandbox; on integrate it would fail on `gov resources --slot` |
| S17 | `test_w2_20_budget.py::test_s17_a_heavy_job_and_its_children_are_confined_to_the_slots_share_outside_the_servers_cpus` | red | `gov resources` does not exist (`invalid choice: 'resources'`, exit 2, no JSON envelope) |
| S17 | `test_w2_20_budget.py::test_s17_two_slots_held_at_once_have_disjoint_cpu_sets` | red | `gov resources` does not exist (`invalid choice: 'resources'`, exit 2, no JSON envelope) |
| S18 | `test_w2_20_pools.py::test_s18_a_pool_is_sized_to_the_cpu_set_never_to_the_machines_count[gov.secrets]` | green (guard) | `gov.secrets._workers` already sizes to the CPU set (the emergency patch) |
| S18 | `test_w2_20_pools.py::test_s18_a_pool_is_sized_to_the_cpu_set_never_to_the_machines_count[gov.codeintel]` | red | `gov.codeintel.index` makes `ThreadPoolExecutor()`: 32 wide for a CPU set of 2 |
| S19 | `test_w2_20_launch.py::test_s19_a_launch_is_refused_while_a_reading_is_shut_naming_the_limit_and_its_reading[memory-a lead]` | red | the launcher never consults the gate: `DID NOT RAISE` `GovError`, the stub session starts |
| S19 | `test_w2_20_launch.py::test_s19_a_launch_is_refused_while_a_reading_is_shut_naming_the_limit_and_its_reading[memory-a worker]` | red | the launcher never consults the gate: `DID NOT RAISE` `GovError`, the stub session starts |
| S19 | `test_w2_20_launch.py::test_s19_a_launch_is_refused_while_a_reading_is_shut_naming_the_limit_and_its_reading[working size-a lead]` | red | the launcher never consults the gate: `DID NOT RAISE` `GovError`, the stub session starts |
| S19 | `test_w2_20_launch.py::test_s19_a_launch_is_refused_while_a_reading_is_shut_naming_the_limit_and_its_reading[working size-a worker]` | red | the launcher never consults the gate: `DID NOT RAISE` `GovError`, the stub session starts |
| S19 | `test_w2_20_launch.py::test_s19_a_launch_is_refused_while_a_reading_is_shut_naming_the_limit_and_its_reading[load-a lead]` | red | the launcher never consults the gate: `DID NOT RAISE` `GovError`, the stub session starts |
| S19 | `test_w2_20_launch.py::test_s19_a_launch_is_refused_while_a_reading_is_shut_naming_the_limit_and_its_reading[load-a worker]` | red | the launcher never consults the gate: `DID NOT RAISE` `GovError`, the stub session starts |
| S19 | `test_w2_20_launch.py::test_s19_a_launch_is_refused_while_a_reading_is_shut_naming_the_limit_and_its_reading[cpu-a lead]` | red | the launcher never consults the gate: `DID NOT RAISE` `GovError`, the stub session starts |
| S19 | `test_w2_20_launch.py::test_s19_a_launch_is_refused_while_a_reading_is_shut_naming_the_limit_and_its_reading[cpu-a worker]` | red | the launcher never consults the gate: `DID NOT RAISE` `GovError`, the stub session starts |
| S19 | `test_w2_20_launch.py::test_s19_a_launch_is_refused_while_a_reading_is_shut_naming_the_limit_and_its_reading[disk-a lead]` | red | the launcher never consults the gate: `DID NOT RAISE` `GovError`, the stub session starts |
| S19 | `test_w2_20_launch.py::test_s19_a_launch_is_refused_while_a_reading_is_shut_naming_the_limit_and_its_reading[disk-a worker]` | red | the launcher never consults the gate: `DID NOT RAISE` `GovError`, the stub session starts |
| S19 | `test_w2_20_launch.py::test_s19_a_launch_is_refused_while_a_reading_is_shut_naming_the_limit_and_its_reading[inodes-a lead]` | red | the launcher never consults the gate: `DID NOT RAISE` `GovError`, the stub session starts |
| S19 | `test_w2_20_launch.py::test_s19_a_launch_is_refused_while_a_reading_is_shut_naming_the_limit_and_its_reading[inodes-a worker]` | red | the launcher never consults the gate: `DID NOT RAISE` `GovError`, the stub session starts |
| S19 | `test_w2_20_launch.py::test_s19_a_launch_is_refused_while_a_reading_is_shut_naming_the_limit_and_its_reading[config-a lead]` | red | the launcher never consults the gate: `DID NOT RAISE` `GovError`, the stub session starts |
| S19 | `test_w2_20_launch.py::test_s19_a_launch_is_refused_while_a_reading_is_shut_naming_the_limit_and_its_reading[config-a worker]` | red | the launcher never consults the gate: `DID NOT RAISE` `GovError`, the stub session starts |
| S19 | `test_w2_20_launch.py::test_s19_a_launch_that_declares_a_gpu_need_is_refused_without_the_room[a lead]` | red | `launch()` takes no `gpu_need_mib` (`TypeError`) |
| S19 | `test_w2_20_launch.py::test_s19_a_launch_that_declares_a_gpu_need_is_refused_without_the_room[a worker]` | red | `launch()` takes no `gpu_need_mib` (`TypeError`) |
| S19 | `test_w2_20_launch.py::test_s19_guard_a_launch_starts_while_the_gate_is_open[a lead]` | green (guard) | an open gate starts the session (stub) |
| S19 | `test_w2_20_launch.py::test_s19_guard_a_launch_starts_while_the_gate_is_open[a worker]` | green (guard) | an open gate starts the session (stub) |
| S19 | `test_w2_20_launch.py::test_s19_the_override_starts_it_and_is_written_in_the_launch_log_and_the_output[a lead]` | red | `launch()` takes no `gate_override` (`TypeError`) |
| S19 | `test_w2_20_launch.py::test_s19_the_override_starts_it_and_is_written_in_the_launch_log_and_the_output[a worker]` | red | `launch()` takes no `gate_override` (`TypeError`) |
| S19 | `test_w2_20_launch.py::test_s19_an_override_that_names_no_decision_is_refused` | red | `launch()` takes no `gate_override` (`TypeError`) |
| S19 | `test_w2_20_launch.py::test_s19_gov_launch_takes_the_override_and_the_gpu_need_on_its_command_line` | red | `gov launch` refuses `--gate-override` and `--gpu-need-mib` (argparse exit 2) |
| S20 | `test_w2_20_query_start.py::test_s20_the_start_takes_its_cpus_and_priority_from_the_gate_file` | green (guard) | as today (W2-123's cap) |
| S20 | `test_w2_20_query_start.py::test_s20_the_device_comes_from_the_gate_file[no device: the GPU visible]` | green (guard) | the GPU is not hidden today |
| S20 | `test_w2_20_query_start.py::test_s20_the_device_comes_from_the_gate_file[gpu: the GPU visible, a caller's -1 removed]` | red | the caller's `CUDA_VISIBLE_DEVICES=-1` reaches the server |
| S20 | `test_w2_20_query_start.py::test_s20_the_device_comes_from_the_gate_file[cpu: the GPU hidden]` | red | device `cpu` not read: `CUDA_VISIBLE_DEVICES` unset |
| S20 | `test_w2_20_query_start.py::test_s20_a_malformed_device_shuts_the_start_named[tpu]` | red | the device is not read: the server starts (`started: True`) |
| S20 | `test_w2_20_query_start.py::test_s20_a_malformed_device_shuts_the_start_named[a phrase]` | red | the device is not read: the server starts (`started: True`) |
| S20 | `test_w2_20_query_start.py::test_s20_a_malformed_device_shuts_the_start_named[a number]` | red | the device is not read: the server starts (`started: True`) |
| S20 | `test_w2_20_query_start.py::test_s20_no_thread_budget_variable_is_inherited_by_the_server` | red | the server inherits all eight planted variables |
| S20 | `test_w2_20_query_start.py::test_s20_the_output_is_appended_to_the_servers_own_log` | red | the output goes to `/dev/null`; no log |
| S20 | `test_w2_20_query_start.py::test_s20_each_start_writes_one_line_naming_the_time_the_device_and_the_caller[gpu]` | red | no start log (`0 lines`) |
| S20 | `test_w2_20_query_start.py::test_s20_each_start_writes_one_line_naming_the_time_the_device_and_the_caller[cpu]` | red | no start log (`0 lines`) |
| S21 | `test_w2_20_plan_source.py::test_s21_a_lead_its_stale_ready_list_would_admit_is_refused` | red | the check reads the lead worktree's list: `admitted=True` for PLN-f001 |
| S21 | `test_w2_20_plan_source.py::test_s21_a_lead_its_stale_ticket_would_admit_is_refused_naming_the_current_wait` | red | the check reads the lead worktree's ticket: `admitted=True` for PLN-f002 |
| S21 | `test_w2_20_plan_source.py::test_s21_a_lead_the_main_tree_admits_is_admitted_from_the_lead_worktree` | red | `unknown ticket 'PLN-f004'` (the worktree has no copy) |
| S21 | `test_w2_20_plan_source.py::test_s21_guard_from_the_main_tree_itself_the_check_reads_its_own_tickets_and_list` | green (guard) | W2-136's check from the main tree, kept |
| S21 | `test_w2_20_plan_source.py::test_s21_a_named_ready_list_is_followed_from_the_lead_worktree[absolute]` | red | the tickets come from the worktree: `unknown ticket 'PLN-f004'` |
| S21 | `test_w2_20_plan_source.py::test_s21_a_named_ready_list_is_followed_from_the_lead_worktree[relative to the main tree]` | red | `unknown ticket 'PLN-f004'` (and the relative path read in the worktree) |
| S21 | `test_w2_20_plan_source.py::test_s21_the_launcher_refuses_a_lead_its_stale_copies_would_admit` | red | `DID NOT RAISE`: the lead starts on the stale list |
| S21 | `test_w2_20_plan_source.py::test_s21_the_launcher_starts_a_lead_the_main_tree_admits` | red | `LAUNCH_REFUSED`: `unknown ticket 'PLN-f004'` |
| S21 | `test_w2_20_plan_source.py::test_s21_a_plan_override_is_one_line_in_the_launch_log_and_the_line_on_standard_error` | red | no `launch.log`: the override goes to stderr only |
| S4 | `test_w2_20_config.py::test_s8_init_config_writes_a_dated_sourced_template_with_this_machines_decided_values` | red | `gov resources` does not exist (`invalid choice: 'resources'`) |
| S7 | `test_w2_20_launch.py::test_s19_s7_a_full_set_of_heavy_slots_never_refuses_a_launch[a lead]` | red | `gov resources --slot` does not exist (the holder cannot be planted) |
| S7 | `test_w2_20_launch.py::test_s19_s7_a_full_set_of_heavy_slots_never_refuses_a_launch[a worker]` | red | `gov resources --slot` does not exist |
| S7 | `test_w2_20_remeasure.py::test_s7_s9_the_remeasure_keeps_the_rebuild_peak_from_rebuild_slot_holders_which_hold_no_verification_lock` | red | `gov resources` does not exist (`invalid choice: 'resources'`) |
| S8 | `test_w2_20_config.py::test_s8_init_config_writes_a_dated_sourced_template_with_this_machines_decided_values` | red | `gov resources` does not exist (`invalid choice: 'resources'`) |
| S8 | `test_w2_20_config.py::test_s8_init_config_never_overwrites_an_existing_file` | red | `gov resources` does not exist (`invalid choice: 'resources'`) |
| S9 | `test_w2_20_remeasure.py::test_s7_s9_the_remeasure_keeps_the_rebuild_peak_from_rebuild_slot_holders_which_hold_no_verification_lock` | red | `gov resources` does not exist (`invalid choice: 'resources'`) |
| S19 | `test_w2_20_launch.py::test_s19_s7_a_full_set_of_heavy_slots_never_refuses_a_launch[a lead]` | red | `gov resources --slot` does not exist |
| S19 | `test_w2_20_launch.py::test_s19_s7_a_full_set_of_heavy_slots_never_refuses_a_launch[a worker]` | red | `gov resources --slot` does not exist |
| S19 | `test_w2_20_launch.py::test_s19_the_slots_refuse_a_launch_only_when_their_reading_cannot_be_taken[heavy_slots missing-a lead]` | red | the launcher never consults the gate: `DID NOT RAISE` |
| S19 | `test_w2_20_launch.py::test_s19_the_slots_refuse_a_launch_only_when_their_reading_cannot_be_taken[heavy_slots missing-a worker]` | red | the launcher never consults the gate: `DID NOT RAISE` |
| S19 | `test_w2_20_launch.py::test_s19_the_slots_refuse_a_launch_only_when_their_reading_cannot_be_taken[heavy_slots malformed-a lead]` | red | the launcher never consults the gate: `DID NOT RAISE` |
| S19 | `test_w2_20_launch.py::test_s19_the_slots_refuse_a_launch_only_when_their_reading_cannot_be_taken[heavy_slots malformed-a worker]` | red | the launcher never consults the gate: `DID NOT RAISE` |
| F1 | `test_w2_20_budget.py::test_s15_every_program_a_heavy_job_starts_gets_the_slots_thread_budget[one worker]` | red | `gov resources` does not exist (`invalid choice: 'resources'`, exit 2, no JSON envelope) |
| F1 | `test_w2_20_budget.py::test_s15_every_program_a_heavy_job_starts_gets_the_slots_thread_budget[four workers]` | red | `gov resources` does not exist (`invalid choice: 'resources'`, exit 2, no JSON envelope) |
| F1 | `test_w2_20_budget.py::test_s17_a_heavy_job_and_its_children_are_confined_to_the_slots_share_outside_the_servers_cpus` | red | `gov resources` does not exist (`invalid choice: 'resources'`, exit 2, no JSON envelope) |
| F2 | `test_w2_20_failure.py::test_a_session_entered_from_another_repository_counts_against_this_ones_gate` | red | `gov resources` does not exist (`invalid choice: 'resources'`, exit 2, no JSON envelope) |
| F2 | `test_w2_20_failure.py::test_W2_M244_W2_M188_a_start_while_the_gate_is_shut_is_refused_with_the_reading` | red | `gov resources` does not exist (`invalid choice: 'resources'`, exit 2, no JSON envelope) |
| F2 | `test_w2_20_failure.py::test_W2_M244_the_refusal_without_json_has_the_same_exit_code_and_names_the_reason` | red | `gov resources` does not exist (`invalid choice: 'resources'`, exit 2, no JSON envelope) |
| F2 | `test_w2_20_failure.py::test_W2_M188_a_start_while_the_gate_is_open_goes_ahead` | red | `gov resources` does not exist (`invalid choice: 'resources'`, exit 2, no JSON envelope) |
| F2 | `test_w2_20_gate.py::test_a_reading_that_cannot_be_taken_never_opens_the_gate[memory]` | red | `gov resources` does not exist (`invalid choice: 'resources'`, exit 2, no JSON envelope) |
| F2 | `test_w2_20_gate.py::test_a_reading_that_cannot_be_taken_never_opens_the_gate[load]` | red | `gov resources` does not exist (`invalid choice: 'resources'`, exit 2, no JSON envelope) |
| F2 | `test_w2_20_gate.py::test_a_reading_that_cannot_be_taken_never_opens_the_gate[busy cores]` | red | `gov resources` does not exist (`invalid choice: 'resources'`, exit 2, no JSON envelope) |
| F2 | `test_w2_20_gate.py::test_a_reading_that_cannot_be_taken_never_opens_the_gate[embedding p95]` | red | `gov resources` does not exist (`invalid choice: 'resources'`, exit 2, no JSON envelope) |
| F2 | `test_w2_20_gate.py::test_a_reading_that_cannot_be_taken_never_opens_the_gate[disk]` | red | `gov resources` does not exist (`invalid choice: 'resources'`, exit 2, no JSON envelope) |
| F3 | `test_w2_20_disk.py::test_s4_an_unreadable_disk_is_shut_for_a_close_too` | red | `gov.resources` does not exist |
| F3 | `test_w2_20_disk.py::test_f3_a_start_check_refuses_while_the_disk_is_below_either_floor` | red | `gov resources` does not exist (`invalid choice: 'resources'`, exit 2, no JSON envelope) |
| F4 | `test_w2_20_slots.py::test_f4_no_fixed_ceiling_on_leads_or_sessions` | red | `gov resources` does not exist (`invalid choice: 'resources'`, exit 2, no JSON envelope) |
| F5 | `test_w2_20_config.py::test_f5_the_values_in_force_are_the_files_and_follow_it` | red | `gov resources` does not exist (`invalid choice: 'resources'`, exit 2, no JSON envelope) |
| F5 | `test_w2_20_disk.py::test_s4_the_floors_are_the_configuration_files` | red | `gov.resources` does not exist |
| F5 | `test_w2_20_gate.py::test_with_no_configuration_file_the_gate_is_shut_and_names_it` | red | `gov resources` does not exist (`invalid choice: 'resources'`, exit 2, no JSON envelope) |
| F5 | `test_w2_20_gate.py::test_a_reading_that_cannot_be_taken_never_opens_the_gate[memory]` | red | `gov resources` does not exist (`invalid choice: 'resources'`, exit 2, no JSON envelope) |
| F5 | `test_w2_20_gate.py::test_a_reading_that_cannot_be_taken_never_opens_the_gate[load]` | red | `gov resources` does not exist (`invalid choice: 'resources'`, exit 2, no JSON envelope) |
| F5 | `test_w2_20_gate.py::test_a_reading_that_cannot_be_taken_never_opens_the_gate[busy cores]` | red | `gov resources` does not exist (`invalid choice: 'resources'`, exit 2, no JSON envelope) |
| F5 | `test_w2_20_gate.py::test_a_reading_that_cannot_be_taken_never_opens_the_gate[embedding p95]` | red | `gov resources` does not exist (`invalid choice: 'resources'`, exit 2, no JSON envelope) |
| F5 | `test_w2_20_gate.py::test_a_reading_that_cannot_be_taken_never_opens_the_gate[disk]` | red | `gov resources` does not exist (`invalid choice: 'resources'`, exit 2, no JSON envelope) |
| F6 | `test_w2_20_memory.py::test_f6_a_workers_memory_is_charged_once_not_in_its_leads_tree_and_again_as_its_own_session` | red | `gov resources` does not exist (`invalid choice: 'resources'`, exit 2, no JSON envelope) |

**Count.** KPI lines with tests: 27 of 27 (21 success, 6 failure); S16 by its `local_only` case only. 164 cases in
79 test functions (round 1: 146 in 66); 183 map rows (a case that proves two lines is listed under each).

**Not tested (and why), after round 2:** S4's literal floors are now checked in `--init-config`'s template (P-3);
elsewhere they stay planted (no default may stand, S8). S7's "the rebuild's peak ... counted by the gate like a test
run's" has its measuring half (P-5's case) but no case of the gate's use: a running job's memory is already in
`MemAvailable` and S6 reserves nothing for a run not started, so no reading shows the count apart (package P-7).
S19's "a heavy-job slot" is tested as P-2 settles it (an unreadable `heavy_slots` refuses; a full set does not).
W2-136's F2 entry criterion is now W2-20's line, S21.

## Packages for the orchestrator

**Round 1's P-1 to P-6 are settled** (the CTO, delegated, 2026-11-09; the ticket's "The designer's points settled",
DEC-1097 (8)): P-1 (a), P-2 (a) with (c), P-3 (a), P-4 confirmed, P-5 (a), P-6 confirmed. They stay below as written
in round 1, for the record; the cases follow the settlement (table "Round 2's changes").

**P-7 (round 2). Is `rebuild_peak_bytes` a required value of the file (S8: missing shuts), and how does the gate
count it (S7 "counted by the gate like a test run's")?** Options: (a) required like the other measured values, due
after seven days, and counted as the verification peak is: not reserved before a run starts (S6), so in practice only
recorded; (b) optional until the first re-measure writes it (a gap in S8's "a value missing shuts"); (c) reserved for
a rebuild waiting for its slot (a rule the line does not state). The tests plant it in every file and assert only its
measure, so (a) and (b) both pass them. Recommendation (a), confidence medium; a case for "missing shuts" and for
`due_for_remeasure` once decided (one parameter each).

**P-8 (round 2). The plan override's line (S21).** The F2 line says "a launch log"; the tests use P-1's
`~/.gov-os/machine/launch.log` (one log for every launch override) and ask the line to hold `plan_override`, the
decision id and the ticket. Alternative: a log of the project's (`.gov-runtime/`), which a lead worktree would not
share. Recommendation: the machine-wide log, confidence medium-high. A relative `GOV_PLAN_READY` is read against the
main tree *(choice)*; drop that one row if the dispatcher only ever names an absolute path.

**P-1. The override's form (S19).** "gate_override: <DEC-id> on the launch". Options: (a) a launch option,
`gov launch ... --gate-override DEC-NNN` / `launch(..., gate_override=)`, written to the launch log and stderr (the
tests' choice); (b) a ticket field `gate_override:` as W2-136's `plan_override:` (it would admit every launch of the
ticket while it stands, and a ticket change needs its own decision mark); (c) an environment variable (leaks into the
session and its workers' launches). Recommendation (a), confidence medium: the line says "on the launch", and one
override per launch keeps it recorded once. Cost of changing: the three override cases and the command-line case.
"The plan's output" is read as the launch's own output line (stderr), as W2-136 prints its plan override; `gov plan`
is not in W2-20's paths. **Paths:** `src/gov/launch/launcher.py` and `command.py` are not in W2-20's allowed paths
(only `src/gov/launch/gate*`): the launcher's call of the gate, the keyword and the option need them added (or the
lines made by W2-136's ticket). Recommendation: add both files to W2-20's paths, marked DEC-1088 (5)(b).

**P-2. S19 lists "a heavy-job slot" among the readings that refuse a launch; S7 says sessions take no slot and are
gated only by load, memory and disk.** Options: (a) S7 wins: a full set of slots never refuses a session (the tests'
reading: `test_s7_a_session_takes_no_slot`); (b) S19 wins: a launch is refused while every slot is held; (c) a launch
is refused only while the slot reading cannot be taken (malformed `heavy_slots`, already the `config` reason).
Recommendation (a)/(c), confidence medium-high: DEC-983 is explicit that sessions take no slot; the S19 list reads as
the gate's readings in general. Also S19 lists the GPU for a launch that declares a need: the tests give `launch()`
and `gov launch` a `gpu_need_mib` / `--gpu-need-mib`; drop it if no session ever declares one.

**P-3. Who writes the configuration file.** S8 forbids defaults; S4 names 100 GiB and 10,000,000 "set in the gate's
one configuration file"; nothing creates the file. Options: (a) the engineer ships a dated, sourced template
(e.g. `gov resources --init-config` writing this machine's DEC values, refusing to overwrite); (b) the owner writes it
by an ACT. Recommendation (a), confidence medium; then a case can check the template's values.

**P-4. S16's 20 %.** With the suite confined to a share of the CPUs, a fixed amount of CPU-bound work takes longer by
about machine ÷ share, so "no more than 20 % slower" can hold only for a suite that is not CPU-bound in total
(oversubscription removed) or whose programs are time-bound. The case uses time-bound programs (the 20 % then
measures the slot's overhead). Recommendation: the CTO confirms that reading, or names the planted suite. Confidence
medium.

**P-5. S7's "the rebuild's peak memory is measured with the re-measure (S9) and counted by the gate like a test
run's".** The verification lock is one exclusive lock; a rebuild in its own slot holding it would serialise every
heavy job. Options: (a) the re-measure keeps a third figure, the rebuild peak, from samples of slot holders of kind
`rebuild`; (b) a rebuild is sampled as a verification run (holds the lock), accepting the serialisation; (c) drop the
clause. Recommendation (a), confidence low-medium; no case until decided.

**P-6. S10 against S13.** S10: "a start with no declared need never reads the GPU"; S13: the GPU "read once per
check". The tests: the start check without a need never runs `nvidia-smi`; the reading (`gov resources`) and a start
check with a need read it once. Recommendation: keep that reconciliation, confidence medium-high.

**Interface choices the engineer may challenge** (each costs one support constant or a few asserts to change): the
CPU condition counts `busy + p95(shared) + p95(query) < nproc` (the servers' current use may be counted twice; an
alternative is to add only the p95 above their current use); a GPU process's kind from its command line; the
trip-wire, re-measure and slot as `gov resources` options; the log and start-log paths under `~/.gov-os/machine/`.

## Discoveries

- `gov.check.schema` (line 327) sizes its pool to a fixed `min(8, len(keys))`, not the CPU set (S18 "the product's
  own parallel work"); outside W2-20's paths. A row for its owner.
- **Round 2: W2-136's launcher cases will meet W2-20's gate.** `tests/acceptance/W2-136/test_w2_136_launch_check.py`
  (`launcher_with`, lines 97-142) runs the real `launch` with a temporary `HOME` that has no `gate.json` and no
  planted readings. Once every launch runs the gate (S19), with no file the gate is shut (S8) and those cases
  (`test_s9_the_launcher_starts_a_lead_the_check_admits`, `..._writes_an_override_in_the_launch_log`,
  `..._a_worker_launch_never_consults_the_plan`) would be refused by the gate, not by the plan. A recorded rewrite
  of W2-136's fixture (plant an open gate, or stub it) is needed when W2-20 lands; not this designer's paths.
- **Round 2: W1-32's command-set case fails on `links` and `plan` too**, apart from `resources` (read from its code
  and integrate's `gov --help`, lines 79-82; not run without the port): `gov --help` offers `links` and `plan`,
  which no recorded list names (`RECORDED_GOV_COMMANDS` in W1-07's support), so its "extra" assertion fails on them
  once `resources` exists. A row for whoever records those commands.
- `tests/acceptance/W2-07/w2_07_support.py` (line 90) says W2-07's disk floors are top-level keys of the path map,
  while S4 puts them in the gate's configuration file and gives `gov close` one function to call. Two homes for one
  value; W2-07's or W2-66's call should read `check_disk` (S4) rather than its own keys.
