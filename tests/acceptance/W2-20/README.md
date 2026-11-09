# W2-20 — Machine-wide resource gate: acceptance tests

Written by the independent test designer (MR-3) from the KPI lines of ticket `DAEO-r30l` (W2-20, STANDARD) as they
stand on 2026-11-09, and the decisions they cite. **Revision round of 2026-11-09 (DEC-1097 (8)):** W2-20 was built on
2026-10-17 to its first KPI lines; its ticket has since gained and changed many lines. The 10-17 cases were brought
from `w2/W2-20` unchanged (commit `fa2abff4d`), then each old case whose line changed was revised or removed in its
own commit (`Rewrite-Reason: DEC-1097 (8)`), and every new line got new cases. No implementation was read: only the
ticket, the decisions, and today's `w2/integrate` code outside W2-20's own work (the launcher, W2-136's plan check,
`gov.retrieval.ollama`, the pools of `gov.secrets` and `gov.codeintel`) and the interim wrapper `~/.local/bin/ollama`
(read, never run).

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
| `gov resources --check [--gpu-need-mib N] [--gpu-kind embedder\|reranker\|other] [--json]` | **The start check** for one new session (or a job that declares a GPU need). Without `--gpu-need-mib` it never runs `nvidia-smi` (S10). `--gpu-kind` defaults to `other`. | 0 and `ok: true` (the reading as `result`) when open; when shut, `ok: false`, `error.code` `RESOURCE_GATE_SHUT`, the reading in `error.details`, an exit code other than 0 and 2 (the same without `--json`, and the text names the broken condition) |
| `gov resources --register PID --ticket ID --session-role ROLE` | Enters a session in the machine-wide registry (its pid, repository, ticket, role). `--heavy` is no longer part of the interface (no weights, DEC-983). | 0, `ok: true` |
| `gov resources --slot test\|rebuild [--tree T] [--workers N] -- CMD...` | **A heavy job.** Waits for one of the configured machine-wide slots (a rebuild also for its tree's lock, `--tree` default the root), then runs `CMD` confined to the slot's CPU set with the slot's thread budget, and gives the slot back when `CMD` ends. *(choice)* | `CMD`'s exit code; `CMD`'s output passes through |
| `gov resources --sample [--json]` | Takes one sample of every live session's process-tree memory, noting whether a verification run holds the lock. Result `samples`: `[{pid, tree_memory_bytes, verification}]`. *(choice)* | 0 |
| `gov resources --remeasure [--json]` | Writes `verification_peak_bytes` (largest sample) and `working_size_bytes` (largest sample outside verification) into the configuration file, dated today, with a source; result `{"old": {both keys}, "new": {both keys}}`. *(choice)* | 0 |
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
  shuts. *(choice: how the servers' p95 is counted)*
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
  command line `gov launch <role> <ticket> [--gate-override DEC-NNN] [--gpu-need-mib N] [-- ...]` *(choice; package
  P-1)*.
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
