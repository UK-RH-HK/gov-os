Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-20/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# W2-20 — the engineer's brief, round 2: build to the stated interface (DAEO-r30l)

You are a fresh engineer for **W2-20** (`.tickets/DAEO-r30l.md`: read it in full, with "The designer's points settled"
P-1 to P-8 and "The engineer's round-1 points"). Round 1 (head `8985180a3` on `w2/W2-20`) built every line but S16 with
129 unit tests green, but `gov accept W2-20` passes **39 of 164**: round 1 could not see the interface the acceptance
cases assume, which the designer wrote in its README for the engineer to build to. The CTO hands you that section
below (the spec, not the tests), and the failure messages of the CTO's run outside the sandbox (results only).

**Your job:**
1. **Bring the product to the interface below** (configuration keys and value form, the reading's and the gate's fields
   and condition names, the slot command and its records, the launch's refusal and override lines, the plan check's
   source, the query start), keeping every KPI line and P-1 to P-8. Where the interface and a KPI line disagree, the
   KPI line wins: say so in your return, with the case's failure message.
2. **The unit tests in your paths that the gate's arrival breaks** (the ticket's round-1 points): plant an open gate in
   the launch fixtures of `tests/unit/launch/test_runs.py`, `test_w1_28.py`, `test_w1_32.py`,
   `test_w2_136_plan_check.py` (fixtures only; keep every expectation); change W2-76's two unit tests
   (`tests/unit/rebuild/test_w2_76_watch.py`, `test_w2_76_lock_override.py`) to each tree's own rebuild lock.
3. Update your own unit tests and `docs/changes/W2-20-evidence.md` to match.

## Where you work
- `/home/usain/gov-os-worktrees/W2-20`, branch `w2/W2-20` (integrate merged in, the ticket's new paths with it). Your
  paths are the ticket's `allowed_paths`.
- **You never read `tests/acceptance/`** (W2-20's, and W1-07, W1-26, W1-32 and W2-136's cases revised for this ticket):
  only `gov accept`'s results and the failure messages below. Every Grep or Glob call that could reach it carries
  `!tests/acceptance/**`; recursive grep `--exclude-dir=acceptance`.
- Many cases wait for a heavy job's record (the slot command, its thread budget and CPU set) and time out at 60 s when
  it never comes: make the slot command's records match the interface first; it unblocks the most cases.

## Verify
- Through `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh`, with
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-20/src` and `-m "not local_only" -k "not real and not green_here and not time_limit"`
  on whole folders: your unit tests; then `python3 -m gov.cli.main accept W2-20 --root /home/usain/gov-os-worktrees/W2-20`
  and `accept W2-136` (counts per line); then `tests/unit/resources tests/unit/launch tests/unit/rebuild
  tests/unit/secrets_check tests/unit/retrieval`, every red named with its cause (the W2-112 socket cases need the
  CTO's run outside the sandbox). `gov accept W2-20` takes about 18 minutes: run it in the background and wait for it.
- **Commit as you go**, each part as it passes, so a session that ends early leaves its work committed.

## Rules
- The hidden-half rule: never open anything under `~/gov-os-eval/`, `~/gov-os-runs/`, or any `hidden`,
  `memory-verdict` or `memory-verdict-2` folder. Never touch the Ollama servers, the reranker service, `~/.local/bin`,
  `~/.ollama`, `~/.gov-os/` or any service; no GPU job.
- DEC-1080: Read and Grep tools; one simple command per Bash call. Search again once (DEC-1092 (1)) if needed.
- Do not merge `w2/integrate`. Never touch `tests/acceptance/**`, `.tickets/` or `.claude/`.
- **Commit** on `w2/W2-20` with
  `--trailer "Task: DAEO-r30l" --trailer "Implements: DEC-1088, DEC-1037, DEC-1097" --trailer "Role: engineer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.
- Before you end, every run you started has finished.

## Return
Your whole return is your session's **final message**, in full (the launcher keeps it; it is the record): the twelve
labelled fields of `EMG-common.md` (sandbox and `ps` checks first), what changed, `gov accept`'s counts per line for
W2-20 and W2-136, the unit and regression counts with every red named, and any place where the interface and a KPI
line disagree.

---

# The interface the acceptance cases assume (the designer's README, as written)

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



---

# The failure messages of the CTO's run outside the sandbox (round 1's head `8985180a3`; results only)

124 of 164 cases fail.

- `test_w2_20_budget::test_s15_every_program_a_heavy_job_starts_gets_the_slots_thread_budget[one worker]`: AssertionError: timed out after 60 s waiting for the record of budget
- `test_w2_20_budget::test_s15_every_program_a_heavy_job_starts_gets_the_slots_thread_budget[four workers]`: AssertionError: timed out after 60 s waiting for the record of budget
- `test_w2_20_budget::test_s15_the_configuration_file_may_set_the_budget`: AssertionError: timed out after 60 s waiting for the record of fixed
- `test_w2_20_budget::test_s17_a_heavy_job_and_its_children_are_confined_to_the_slots_share_outside_the_servers_cpus`: AssertionError: timed out after 60 s waiting for the record of confined
- `test_w2_20_budget::test_s17_two_slots_held_at_once_have_disjoint_cpu_sets`: AssertionError: timed out after 60 s waiting for heavy job left to start its command
- `test_w2_20_config::test_s8_a_value_missing_shuts_the_gate_naming_it[memory_floor_bytes]`: AssertionError: no config reason names memory_floor_bytes: {'open': False, 'reasons': [{'condition': 'config', 'reading': None, 'threshold': None, 'why': 'floor_bytes: missing (an object with its value, date and source is needed)'}, {'condition': 'config', 'reading': None, 'threshold': None, 'why': 'trip_floor_bytes: missing (an object with its value, date and source is needed)'}, {'condition': 'c
- `test_w2_20_config::test_s8_a_value_missing_shuts_the_gate_naming_it[oom_floor_bytes]`: AssertionError: no config reason names oom_floor_bytes: {'open': False, 'reasons': [{'condition': 'config', 'reading': None, 'threshold': None, 'why': 'floor_bytes: missing (an object with its value, date and source is needed)'}, {'condition': 'config', 'reading': None, 'threshold': None, 'why': 'trip_floor_bytes: missing (an object with its value, date and source is needed)'}, {'condition': 'conf
- `test_w2_20_config::test_s8_a_value_missing_shuts_the_gate_naming_it[heavy_slots]`: AssertionError: a reason with an unknown condition: {'condition': 'slots', 'reading': None, 'threshold': None, 'why': 'heavy_slots is not configured'}
- `test_w2_20_config::test_s8_a_value_missing_shuts_the_gate_naming_it[gpu_shares]`: AssertionError: no config reason names gpu_shares: {'open': False, 'reasons': [{'condition': 'config', 'reading': None, 'threshold': None, 'why': 'floor_bytes: missing (an object with its value, date and source is needed)'}, {'condition': 'config', 'reading': None, 'threshold': None, 'why': 'trip_floor_bytes: missing (an object with its value, date and source is needed)'}, {'condition': 'config', 
- `test_w2_20_config::test_s8_a_malformed_value_shuts_the_gate_naming_it[a word for a number]`: AssertionError: no config reason names memory_floor_bytes: {'open': False, 'reasons': [{'condition': 'config', 'reading': None, 'threshold': None, 'why': 'floor_bytes: missing (an object with its value, date and source is needed)'}, {'condition': 'config', 'reading': None, 'threshold': None, 'why': 'trip_floor_bytes: missing (an object with its value, date and source is needed)'}, {'condition': 'c
- `test_w2_20_config::test_s8_a_malformed_value_shuts_the_gate_naming_it[no slot at all]`: AssertionError: a reason with an unknown condition: {'condition': 'slots', 'reading': None, 'threshold': None, 'why': 'heavy_slots is not configured'}
- `test_w2_20_config::test_s8_a_malformed_value_shuts_the_gate_naming_it[a date that is no date]`: AssertionError: no config reason names oom_floor_bytes: {'open': False, 'reasons': [{'condition': 'config', 'reading': None, 'threshold': None, 'why': 'floor_bytes: missing (an object with its value, date and source is needed)'}, {'condition': 'config', 'reading': None, 'threshold': None, 'why': 'trip_floor_bytes: missing (an object with its value, date and source is needed)'}, {'condition': 'conf
- `test_w2_20_config::test_s8_a_malformed_value_shuts_the_gate_naming_it[a bare value, no date or source]`: AssertionError: no config reason names memory_floor_bytes: {'open': False, 'reasons': [{'condition': 'config', 'reading': None, 'threshold': None, 'why': 'floor_bytes: missing (an object with its value, date and source is needed)'}, {'condition': 'config', 'reading': None, 'threshold': None, 'why': 'trip_floor_bytes: missing (an object with its value, date and source is needed)'}, {'condition': 'c
- `test_w2_20_config::test_s8_a_file_that_is_not_json_shuts_the_gate`: AssertionError: a reason with an unknown condition: {'condition': 'slots', 'reading': None, 'threshold': None, 'why': 'heavy_slots is not configured'}
- `test_w2_20_config::test_s8_a_measured_figure_older_than_seven_days_is_named_due_for_re_measure[8 days old is due]`: AssertionError: the reading has no due_for_remeasure list: {'registry': '/tmp/gov-os-emg-cto/t20/pytest-of-usain/pytest-0/test_s8_a_measured_figure_olde0/home/.gov-os/machine', 'kind': 'reading', 'available_memory_bytes': 68719476736, 'load_1m': 0.1, 'load_15m': 0.1, 'nproc': 4, 'busy_cores': 0.03, 'busy_window_s': 0.3, 'cpu_demand_cores': 0.03, 'servers': {}, 'memory': {'have_bytes': None, 'need_
- `test_w2_20_config::test_s8_a_measured_figure_older_than_seven_days_is_named_due_for_re_measure[7 days old is not]`: AssertionError: the reading has no due_for_remeasure list: {'registry': '/tmp/gov-os-emg-cto/t20/pytest-of-usain/pytest-0/test_s8_a_measured_figure_olde1/home/.gov-os/machine', 'kind': 'reading', 'available_memory_bytes': 68719476736, 'load_1m': 0.1, 'load_15m': 0.1, 'nproc': 4, 'busy_cores': 0.04, 'busy_window_s': 0.3, 'cpu_demand_cores': 0.04, 'servers': {}, 'memory': {'have_bytes': None, 'need_
- `test_w2_20_config::test_f5_the_values_in_force_are_the_files_and_follow_it`: AssertionError: {'config': {'condition': 'config', 'reading': None, 'threshold': None, 'why': 'embedding_servers.query.host: a host:po... 'memory': {'condition': 'memory', 'reading': None, 'threshold': None, 'why': 'the memory figures are not configured'}} assert None == (7 * 1073741824)
- `test_w2_20_config::test_s8_init_config_writes_a_dated_sourced_template_with_this_machines_decided_values`: AssertionError: the template has no memory_floor_bytes value: None assert (False)  +  where False = isinstance(None, dict)
- `test_w2_20_cpu::test_s2_the_gate_judges_busy_cores_and_load_each_on_its_own_and_shows_both[busy cores high, load low]`: AssertionError: the reading does not show the busy cores: {'registry': '/tmp/gov-os-emg-cto/t20/pytest-of-usain/pytest-0/test_s2_the_gate_judges_busy_c0/home/.gov-os/machine', 'kind': 'reading', 'available_memory_bytes': 68719476736, 'load_1m': 0.1, 'load_15m': 0.1, 'nproc': 4, 'busy_cores': 0.02, 'busy_window_s': 0.3, 'cpu_demand_cores': 0.02, 'servers': {}, 'memory': {'have_bytes': None, 'need_b
- `test_w2_20_cpu::test_s2_the_gate_judges_busy_cores_and_load_each_on_its_own_and_shows_both[load high, busy cores low]`: AssertionError: the reading does not show the busy cores: {'registry': '/tmp/gov-os-emg-cto/t20/pytest-of-usain/pytest-0/test_s2_the_gate_judges_busy_c1/home/.gov-os/machine', 'kind': 'reading', 'available_memory_bytes': 68719476736, 'load_1m': 9.0, 'load_15m': 9.0, 'nproc': 4, 'busy_cores': 0.04, 'busy_window_s': 0.3, 'cpu_demand_cores': 0.04, 'servers': {}, 'memory': {'have_bytes': None, 'need_b
- `test_w2_20_cpu::test_s2_busy_cores_and_load_within_open_the_gate`: AssertionError: gov resources did not succeed: exit 3 envelope: {'ok': False, 'command': 'resources', 'result': {}, 'session': '', 'error': {'code': 'RESOURCE_GATE_SHUT', 'message': 'the resource gate is shut, no session starts: config: floor_bytes: missing (an object with its value, date and source is needed); config: trip_floor_bytes: missing (an object with its value, date and source is needed)
- `test_w2_20_cpu::test_s12_both_servers_cpu_p95_count_when_a_session_is_admitted[both within]`: AssertionError: the reading does not show both servers' p95: {'registry': '/tmp/gov-os-emg-cto/t20/pytest-of-usain/pytest-0/test_s12_both_servers_cpu_p95_0/home/.gov-os/machine', 'kind': 'reading', 'available_memory_bytes': 68719476736, 'load_1m': 0.1, 'load_15m': 0.1, 'nproc': 4, 'busy_cores': 0.02, 'busy_window_s': 0.3, 'cpu_demand_cores': 0.02, 'servers': {}, 'memory': {'have_bytes': None, 'nee
- `test_w2_20_cpu::test_s12_both_servers_cpu_p95_count_when_a_session_is_admitted[the shared server's p95 tips it]`: AssertionError: the reading does not show both servers' p95: {'registry': '/tmp/gov-os-emg-cto/t20/pytest-of-usain/pytest-0/test_s12_both_servers_cpu_p95_1/home/.gov-os/machine', 'kind': 'reading', 'available_memory_bytes': 68719476736, 'load_1m': 0.1, 'load_15m': 0.1, 'nproc': 4, 'busy_cores': 0.18, 'busy_window_s': 0.3, 'cpu_demand_cores': 0.18, 'servers': {}, 'memory': {'have_bytes': None, 'nee
- `test_w2_20_cpu::test_s12_both_servers_cpu_p95_count_when_a_session_is_admitted[the query server's p95 tips it]`: AssertionError: the reading does not show both servers' p95: {'registry': '/tmp/gov-os-emg-cto/t20/pytest-of-usain/pytest-0/test_s12_both_servers_cpu_p95_2/home/.gov-os/machine', 'kind': 'reading', 'available_memory_bytes': 68719476736, 'load_1m': 0.1, 'load_15m': 0.1, 'nproc': 4, 'busy_cores': 0.18, 'busy_window_s': 0.3, 'cpu_demand_cores': 0.18, 'servers': {}, 'memory': {'have_bytes': None, 'nee
- `test_w2_20_disk::test_s4_the_disk_reading_is_one_function_gov_close_can_call[both at their floors opens]`: AttributeError: module 'gov.resources' has no attribute 'check_disk'
- `test_w2_20_disk::test_s4_the_disk_reading_is_one_function_gov_close_can_call[space below its floor]`: AttributeError: module 'gov.resources' has no attribute 'check_disk'
- `test_w2_20_disk::test_s4_the_disk_reading_is_one_function_gov_close_can_call[inodes below their floor [F3]]`: AttributeError: module 'gov.resources' has no attribute 'check_disk'
- `test_w2_20_disk::test_s4_the_disk_reading_is_one_function_gov_close_can_call[both below]`: AttributeError: module 'gov.resources' has no attribute 'check_disk'
- `test_w2_20_disk::test_s4_the_floors_are_the_configuration_files`: AttributeError: module 'gov.resources' has no attribute 'check_disk'
- `test_w2_20_disk::test_s4_an_unreadable_disk_is_shut_for_a_close_too`: AttributeError: module 'gov.resources' has no attribute 'check_disk'
- `test_w2_20_disk::test_f3_a_start_check_refuses_while_the_disk_is_below_either_floor`: AssertionError: {'config': {'condition': 'config', 'reading': None, 'threshold': None, 'why': 'embedding_servers.query.host: a host:po... 'memory': {'condition': 'memory', 'reading': None, 'threshold': None, 'why': 'the memory figures are not configured'}} assert {'config', 'memory'} == {'inodes'}      Extra items in the left set:   'config'   'memory'   Extra items in the right set:   'inodes'   
- `test_w2_20_failure::test_a_session_entered_from_another_repository_counts_against_this_ones_gate`: AssertionError: the start check refused with an empty registry: exit 3   {"ok": false, "command": "resources", "result": {}, "session": "", "error": {"code": "RESOURCE_GATE_SHUT", "message": "the resource gate is shut, no session starts: config: floor_bytes: missing (an object with its value, date and source is needed); config: trip_floor_bytes: missing (an object with its value, date and source i
- `test_w2_20_failure::test_W2_M244_W2_M188_a_start_while_the_gate_is_shut_is_refused_with_the_reading`: AssertionError: {'config': {'condition': 'config', 'reading': None, 'threshold': None, 'why': 'embedding_servers.query.host: a host:po... 'memory': {'condition': 'memory', 'reading': None, 'threshold': None, 'why': 'the memory figures are not configured'}} assert {'config', 'memory'} == {'memory'}      Extra items in the left set:   'config'   Use -v to get more diff
- `test_w2_20_failure::test_W2_M188_a_start_while_the_gate_is_open_goes_ahead`: AssertionError: gov resources did not succeed: exit 3 envelope: {'ok': False, 'command': 'resources', 'result': {}, 'session': '', 'error': {'code': 'RESOURCE_GATE_SHUT', 'message': 'the resource gate is shut, no session starts: config: floor_bytes: missing (an object with its value, date and source is needed); config: trip_floor_bytes: missing (an object with its value, date and source is needed)
- `test_w2_20_gate::test_the_gate_is_open_when_every_condition_holds`: AssertionError: {'available_memory_bytes': 17179869184, 'busy_cores': 0.02, 'busy_window_s': 0.3, 'cleared': [], ...} assert False is True
- `test_w2_20_gate::test_one_broken_condition_shuts_the_gate_and_is_named_with_its_reading_and_threshold[memory]`: AssertionError: expected the one reason 'memory': [{'condition': 'config', 'reading': None, 'threshold': None, 'why': 'floor_bytes: missing (an object with its value, date and source is needed)'}, {'condition': 'config', 'reading': None, 'threshold': None, 'why': 'trip_floor_bytes: missing (an object with its value, date and source is needed)'}, {'condition': 'config', 'reading': None, 'threshold'
- `test_w2_20_gate::test_one_broken_condition_shuts_the_gate_and_is_named_with_its_reading_and_threshold[load [W2-M262]]`: AssertionError: expected the one reason 'load': [{'condition': 'config', 'reading': None, 'threshold': None, 'why': 'floor_bytes: missing (an object with its value, date and source is needed)'}, {'condition': 'config', 'reading': None, 'threshold': None, 'why': 'trip_floor_bytes: missing (an object with its value, date and source is needed)'}, {'condition': 'config', 'reading': None, 'threshold': 
- `test_w2_20_gate::test_one_broken_condition_shuts_the_gate_and_is_named_with_its_reading_and_threshold[cpu]`: AssertionError: expected the one reason 'cpu': [{'condition': 'config', 'reading': None, 'threshold': None, 'why': 'floor_bytes: missing (an object with its value, date and source is needed)'}, {'condition': 'config', 'reading': None, 'threshold': None, 'why': 'trip_floor_bytes: missing (an object with its value, date and source is needed)'}, {'condition': 'config', 'reading': None, 'threshold': N
- `test_w2_20_gate::test_one_broken_condition_shuts_the_gate_and_is_named_with_its_reading_and_threshold[disk]`: AssertionError: expected the one reason 'disk': [{'condition': 'config', 'reading': None, 'threshold': None, 'why': 'floor_bytes: missing (an object with its value, date and source is needed)'}, {'condition': 'config', 'reading': None, 'threshold': None, 'why': 'trip_floor_bytes: missing (an object with its value, date and source is needed)'}, {'condition': 'config', 'reading': None, 'threshold': 
- `test_w2_20_gate::test_one_broken_condition_shuts_the_gate_and_is_named_with_its_reading_and_threshold[inodes]`: AssertionError: expected the one reason 'inodes': [{'condition': 'config', 'reading': None, 'threshold': None, 'why': 'floor_bytes: missing (an object with its value, date and source is needed)'}, {'condition': 'config', 'reading': None, 'threshold': None, 'why': 'trip_floor_bytes: missing (an object with its value, date and source is needed)'}, {'condition': 'config', 'reading': None, 'threshold'
- `test_w2_20_gate::test_several_broken_conditions_are_all_named`: AssertionError: {'config': {'condition': 'config', 'reading': None, 'threshold': None, 'why': 'embedding_servers.query.host: a host:po... 'memory': {'condition': 'memory', 'reading': None, 'threshold': None, 'why': 'the memory figures are not configured'}} assert {'config', 'load', 'memory'} == {'cpu', 'disk...ad', 'memory'}      Extra items in the left set:   'config'   Extra items in the right s
- `test_w2_20_gate::test_exactly_at_a_threshold[memory]`: AssertionError: memory equal to its floor must open: {'registry': '/tmp/gov-os-emg-cto/t20/pytest-of-usain/pytest-0/test_exactly_at_a_threshold_me0/home/.gov-os/machine', 'kind': 'reading', 'available_memory_bytes': 3221225472, 'load_1m': 0.1, 'load_15m': 0.1, 'nproc': 3, 'busy_cores': 0.01, 'busy_window_s': 0.3, 'cpu_demand_cores': 0.01, 'servers': {}, 'memory': {'have_bytes': None, 'need_bytes':
- `test_w2_20_gate::test_exactly_at_a_threshold[load]`: AssertionError: {'config': {'condition': 'config', 'reading': None, 'threshold': None, 'why': 'embedding_servers.query.host: a host:po... 'memory': {'condition': 'memory', 'reading': None, 'threshold': None, 'why': 'the memory figures are not configured'}} assert {'config', 'load', 'memory'} == {'load'}      Extra items in the left set:   'config'   'memory'   Use -v to get more diff
- `test_w2_20_gate::test_exactly_at_a_threshold[cpu]`: AssertionError: {'config': {'condition': 'config', 'reading': None, 'threshold': None, 'why': 'embedding_servers.query.host: a host:po... 'memory': {'condition': 'memory', 'reading': None, 'threshold': None, 'why': 'the memory figures are not configured'}} assert {'config', 'memory'} == {'cpu'}      Extra items in the left set:   'config'   'memory'   Extra items in the right set:   'cpu'   Use -v
- `test_w2_20_gate::test_exactly_at_a_threshold[disk]`: AssertionError: disk equal to its floor must open: {'registry': '/tmp/gov-os-emg-cto/t20/pytest-of-usain/pytest-0/test_exactly_at_a_threshold_di0/home/.gov-os/machine', 'kind': 'reading', 'available_memory_bytes': 68719476736, 'load_1m': 0.1, 'load_15m': 0.1, 'nproc': 3, 'busy_cores': 0.15, 'busy_window_s': 0.3, 'cpu_demand_cores': 0.15, 'servers': {}, 'memory': {'have_bytes': None, 'need_bytes': 
- `test_w2_20_gate::test_exactly_at_a_threshold[inodes]`: AssertionError: inodes equal to its floor must open: {'registry': '/tmp/gov-os-emg-cto/t20/pytest-of-usain/pytest-0/test_exactly_at_a_threshold_in0/home/.gov-os/machine', 'kind': 'reading', 'available_memory_bytes': 68719476736, 'load_1m': 0.1, 'load_15m': 0.1, 'nproc': 3, 'busy_cores': 0.01, 'busy_window_s': 0.3, 'cpu_demand_cores': 0.01, 'servers': {}, 'memory': {'have_bytes': None, 'need_bytes'
- `test_w2_20_gate::test_with_no_configuration_file_the_gate_is_shut_and_names_it`: AssertionError: a reason with an unknown condition: {'condition': 'slots', 'reading': None, 'threshold': None, 'why': 'heavy_slots is not configured'}
- `test_w2_20_gate::test_a_reading_that_cannot_be_taken_never_opens_the_gate[memory]`: AssertionError: {'config': {'condition': 'config', 'reading': None, 'threshold': None, 'why': 'embedding_servers.query.host: a host:po...ile or directory: '/tmp/gov-os-emg-cto/t20/pytest-of-usain/pytest-0/test_a_reading_that_cannot_be_0/no-such-meminfo'"}} assert {'config', 'memory'} <= {'inodes', 'memory'}      Extra items in the left set:   'config'
- `test_w2_20_gate::test_a_reading_that_cannot_be_taken_never_opens_the_gate[load]`: AssertionError: {'config': {'condition': 'config', 'reading': None, 'threshold': None, 'why': 'embedding_servers.query.host: a host:po... 'memory': {'condition': 'memory', 'reading': None, 'threshold': None, 'why': 'the memory figures are not configured'}} assert {'config', 'load', 'memory'} <= {'inodes', 'load'}      Extra items in the left set:   'config'   'memory'
- `test_w2_20_gate::test_a_reading_that_cannot_be_taken_never_opens_the_gate[busy cores]`: AssertionError: {'config': {'condition': 'config', 'reading': None, 'threshold': None, 'why': 'embedding_servers.query.host: a host:po... 'memory': {'condition': 'memory', 'reading': None, 'threshold': None, 'why': 'the memory figures are not configured'}} assert 'cpu' in {'config': {'condition': 'config', 'reading': None, 'threshold': None, 'why': 'embedding_servers.query.host: a host:po... 'memo
- `test_w2_20_gate::test_a_reading_that_cannot_be_taken_never_opens_the_gate[embedding p95]`: AssertionError: {'config': {'condition': 'config', 'reading': None, 'threshold': None, 'why': 'embedding_servers.query.host: a host:po... 'memory': {'condition': 'memory', 'reading': None, 'threshold': None, 'why': 'the memory figures are not configured'}} assert 'cpu' in {'config': {'condition': 'config', 'reading': None, 'threshold': None, 'why': 'embedding_servers.query.host: a host:po... 'memo
- `test_w2_20_gate::test_a_reading_that_cannot_be_taken_never_opens_the_gate[disk]`: AssertionError: an unreadable disk reading is reported as {'path': '/tmp/gov-os-emg-cto/t20/pytest-of-usain/pytest-0/test_a_reading_that_cannot_be_4/home', 'free_bytes': 886020575232, 'free_inodes': 64604347} assert {'free_bytes': 886020575232, 'free_inodes': 64604347, 'path': '/tmp/gov-os-emg-cto/t20/pytest-of-usain/pytest-0/test_a_reading_that_cannot_be_4/home'} is None  +  where {'free_bytes': 
- `test_w2_20_gpu::test_s10_a_declared_gpu_need_opens_only_with_the_need_plus_the_margin_free_on_one_gpu[free 1101 for a need of 1000 opens]`: AssertionError: gov resources did not succeed: exit 3 envelope: {'ok': False, 'command': 'resources', 'result': {}, 'session': '', 'error': {'code': 'RESOURCE_GATE_SHUT', 'message': 'the resource gate is shut, no session starts: config: floor_bytes: missing (an object with its value, date and source is needed); config: trip_floor_bytes: missing (an object with its value, date and source is needed)
- `test_w2_20_gpu::test_s10_a_declared_gpu_need_opens_only_with_the_need_plus_the_margin_free_on_one_gpu[free 1099 shuts]`: AssertionError: {'config': {'condition': 'config', 'reading': None, 'threshold': None, 'why': 'embedding_servers.query.host: a host:po... 'memory': {'condition': 'memory', 'reading': None, 'threshold': None, 'why': 'the memory figures are not configured'}} assert {'config', 'gpu', 'memory'} == {'gpu'}      Extra items in the left set:   'config'   'memory'   Use -v to get more diff
- `test_w2_20_gpu::test_s10_a_declared_gpu_need_opens_only_with_the_need_plus_the_margin_free_on_one_gpu[the second GPU has room]`: AssertionError: gov resources did not succeed: exit 3 envelope: {'ok': False, 'command': 'resources', 'result': {}, 'session': '', 'error': {'code': 'RESOURCE_GATE_SHUT', 'message': 'the resource gate is shut, no session starts: config: floor_bytes: missing (an object with its value, date and source is needed); config: trip_floor_bytes: missing (an object with its value, date and source is needed)
- `test_w2_20_gpu::test_s10_a_declared_gpu_need_opens_only_with_the_need_plus_the_margin_free_on_one_gpu[room only across two GPUs shuts]`: AssertionError: {'config': {'condition': 'config', 'reading': None, 'threshold': None, 'why': 'embedding_servers.query.host: a host:po... 'memory': {'condition': 'memory', 'reading': None, 'threshold': None, 'why': 'the memory figures are not configured'}} assert {'config', 'gpu', 'memory'} == {'gpu'}      Extra items in the left set:   'config'   'memory'   Use -v to get more diff
- `test_w2_20_gpu::test_s10_no_nvidia_smi_or_no_gpu_shuts_a_start_that_declares_a_need_named[no nvidia-smi]`: AssertionError: {'config': {'condition': 'config', 'reading': None, 'threshold': None, 'why': 'embedding_servers.query.host: a host:po... 'memory': {'condition': 'memory', 'reading': None, 'threshold': None, 'why': 'the memory figures are not configured'}} assert {'config', 'gpu', 'memory'} == {'gpu'}      Extra items in the left set:   'config'   'memory'   Use -v to get more diff
- `test_w2_20_gpu::test_s10_no_nvidia_smi_or_no_gpu_shuts_a_start_that_declares_a_need_named[no GPU]`: AssertionError: {'config': {'condition': 'config', 'reading': None, 'threshold': None, 'why': 'embedding_servers.query.host: a host:po... 'memory': {'condition': 'memory', 'reading': None, 'threshold': None, 'why': 'the memory figures are not configured'}} assert {'config', 'gpu', 'memory'} == {'gpu'}      Extra items in the left set:   'config'   'memory'   Use -v to get more diff
- `test_w2_20_gpu::test_s10_no_nvidia_smi_or_no_gpu_shuts_a_start_that_declares_a_need_named[an unreadable GPU]`: AssertionError: {'config': {'condition': 'config', 'reading': None, 'threshold': None, 'why': 'embedding_servers.query.host: a host:po... 'memory': {'condition': 'memory', 'reading': None, 'threshold': None, 'why': 'the memory figures are not configured'}} assert {'config', 'gpu', 'memory'} == {'gpu'}      Extra items in the left set:   'config'   'memory'   Use -v to get more diff
- `test_w2_20_gpu::test_s10_a_start_with_no_declared_need_never_reads_the_gpu[a GPU planted]`: AssertionError: gov resources did not succeed: exit 3 envelope: {'ok': False, 'command': 'resources', 'result': {}, 'session': '', 'error': {'code': 'RESOURCE_GATE_SHUT', 'message': 'the resource gate is shut, no session starts: config: floor_bytes: missing (an object with its value, date and source is needed); config: trip_floor_bytes: missing (an object with its value, date and source is needed)
- `test_w2_20_gpu::test_s10_a_start_with_no_declared_need_never_reads_the_gpu[no nvidia-smi]`: AssertionError: gov resources did not succeed: exit 3 envelope: {'ok': False, 'command': 'resources', 'result': {}, 'session': '', 'error': {'code': 'RESOURCE_GATE_SHUT', 'message': 'the resource gate is shut, no session starts: config: floor_bytes: missing (an object with its value, date and source is needed); config: trip_floor_bytes: missing (an object with its value, date and source is needed)
- `test_w2_20_gpu::test_s13_the_reading_measures_gpu_memory_utilisation_and_which_processes_hold_it`: AssertionError: the reading has no GPU measure: {'read': True, 'gpus': [{'index': 0, 'used_bytes': 5242880000, 'total_bytes': 8589934592, 'free_bytes': 3347054592, 'utilization': 37.0}], 'holders': [{'pid': 2817840, 'used_bytes': 3145728000, 'kind': 'embedder'}, {'pid': 2817841, 'used_bytes': 1572864000, 'kind': 'reranker'}, {'pid': 2817842, 'used_bytes': 524288000, 'kind': 'other'}], 'holders_why
- `test_w2_20_gpu::test_s13_no_gpu_or_an_unreadable_one_is_named_in_the_answer_never_an_error[no nvidia-smi]`: AssertionError: {'read': False, 'why': 'no nvidia-smi on this machine'} assert (True and None is False)  +  where True = isinstance({'read': False, 'why': 'no nvidia-smi on this machine'}, dict)  +  and   None = <built-in method get of dict object at 0x7186d87e1ec0>('available')  +    where <built-in method get of dict object at 0x7186d87e1ec0> = {'read': False, 'why': 'no nvidia-smi on this machi
- `test_w2_20_gpu::test_s13_no_gpu_or_an_unreadable_one_is_named_in_the_answer_never_an_error[no GPU]`: AssertionError: {'read': False, 'why': 'nvidia-smi exit 6: No devices were found'} assert (True and None is False)  +  where True = isinstance({'read': False, 'why': 'nvidia-smi exit 6: No devices were found'}, dict)  +  and   None = <built-in method get of dict object at 0x7186d87c0ac0>('available')  +    where <built-in method get of dict object at 0x7186d87c0ac0> = {'read': False, 'why': 'nvidi
- `test_w2_20_gpu::test_s13_no_gpu_or_an_unreadable_one_is_named_in_the_answer_never_an_error[an unreadable GPU]`: AssertionError: {'read': False, 'why': "nvidia-smi exit 9: NVIDIA-SMI has failed because it couldn't communicate with the NVIDIA driver."} assert (True and None is False)  +  where True = isinstance({'read': False, 'why': "nvidia-smi exit 9: NVIDIA-SMI has failed because it couldn't communicate with the NVIDIA driver."}, dict)  +  and   None = <built-in method get of dict object at 0x7186d8942e80>
- `test_w2_20_gpu::test_s14_a_job_that_would_push_the_embedder_off_the_gpu_waits_and_the_answer_states_the_room[a reranker within its room]`: AssertionError: gov resources did not succeed: exit 3 envelope: {'ok': False, 'command': 'resources', 'result': {}, 'session': '', 'error': {'code': 'RESOURCE_GATE_SHUT', 'message': 'the resource gate is shut, no session starts: config: floor_bytes: missing (an object with its value, date and source is needed); config: trip_floor_bytes: missing (an object with its value, date and source is needed)
- `test_w2_20_gpu::test_s14_a_job_that_would_push_the_embedder_off_the_gpu_waits_and_the_answer_states_the_room[a reranker that would push the embedder off]`: AssertionError: {'available_memory_bytes': 68719476736, 'busy_cores': 0.02, 'busy_window_s': 0.3, 'cleared': [], ...} assert {'config', 'gpu', 'memory'} == {'gpu'}      Extra items in the left set:   'config'   'memory'   Use -v to get more diff
- `test_w2_20_gpu::test_s14_a_job_that_would_push_the_embedder_off_the_gpu_waits_and_the_answer_states_the_room[other work behind the embedder and the reranker]`: AssertionError: {'available_memory_bytes': 68719476736, 'busy_cores': 0.18, 'busy_window_s': 0.3, 'cleared': [], ...} assert {'config', 'gpu', 'memory'} == {'gpu'}      Extra items in the left set:   'config'   'memory'   Use -v to get more diff
- `test_w2_20_gpu::test_s14_a_job_that_would_push_the_embedder_off_the_gpu_waits_and_the_answer_states_the_room[the embedder already loaded]`: AssertionError: gov resources did not succeed: exit 3 envelope: {'ok': False, 'command': 'resources', 'result': {}, 'session': '', 'error': {'code': 'RESOURCE_GATE_SHUT', 'message': 'the resource gate is shut, no session starts: config: floor_bytes: missing (an object with its value, date and source is needed); config: trip_floor_bytes: missing (an object with its value, date and source is needed)
- `test_w2_20_launch::test_s19_a_launch_is_refused_while_a_reading_is_shut_naming_the_limit_and_its_reading[memory-a lead]`: AssertionError: GovError('gov launch refuses the orchestrator session for ticket \'DAEO-lead1\': the resource gate is shut, no session...is needed; memory cannot be read against the threshold None (the memory figures are not configured) (DEC-1088 (5)(b))') assert 'RESOURCE_GATE_SHUT' == 'LAUNCH_REFUSED'      - LAUNCH_REFUSED   + RESOURCE_GATE_SHUT
- `test_w2_20_launch::test_s19_a_launch_is_refused_while_a_reading_is_shut_naming_the_limit_and_its_reading[memory-a worker]`: AssertionError: GovError('gov launch refuses the engineer session for ticket \'DAEO-wrk01\': the resource gate is shut, no session sta...is needed; memory cannot be read against the threshold None (the memory figures are not configured) (DEC-1088 (5)(b))') assert 'RESOURCE_GATE_SHUT' == 'LAUNCH_REFUSED'      - LAUNCH_REFUSED   + RESOURCE_GATE_SHUT
- `test_w2_20_launch::test_s19_a_launch_is_refused_while_a_reading_is_shut_naming_the_limit_and_its_reading[working size-a lead]`: AssertionError: GovError('gov launch refuses the orchestrator session for ticket \'DAEO-lead1\': the resource gate is shut, no session...is needed; memory cannot be read against the threshold None (the memory figures are not configured) (DEC-1088 (5)(b))') assert 'RESOURCE_GATE_SHUT' == 'LAUNCH_REFUSED'      - LAUNCH_REFUSED   + RESOURCE_GATE_SHUT
- `test_w2_20_launch::test_s19_a_launch_is_refused_while_a_reading_is_shut_naming_the_limit_and_its_reading[working size-a worker]`: AssertionError: GovError('gov launch refuses the engineer session for ticket \'DAEO-wrk01\': the resource gate is shut, no session sta...is needed; memory cannot be read against the threshold None (the memory figures are not configured) (DEC-1088 (5)(b))') assert 'RESOURCE_GATE_SHUT' == 'LAUNCH_REFUSED'      - LAUNCH_REFUSED   + RESOURCE_GATE_SHUT
- `test_w2_20_launch::test_s19_a_launch_is_refused_while_a_reading_is_shut_naming_the_limit_and_its_reading[load-a lead]`: AssertionError: GovError('gov launch refuses the orchestrator session for ticket \'DAEO-lead1\': the resource gate is shut, no session...reshold 4; memory cannot be read against the threshold None (the memory figures are not configured) (DEC-1088 (5)(b))') assert 'RESOURCE_GATE_SHUT' == 'LAUNCH_REFUSED'      - LAUNCH_REFUSED   + RESOURCE_GATE_SHUT
- `test_w2_20_launch::test_s19_a_launch_is_refused_while_a_reading_is_shut_naming_the_limit_and_its_reading[load-a worker]`: AssertionError: GovError('gov launch refuses the engineer session for ticket \'DAEO-wrk01\': the resource gate is shut, no session sta...reshold 4; memory cannot be read against the threshold None (the memory figures are not configured) (DEC-1088 (5)(b))') assert 'RESOURCE_GATE_SHUT' == 'LAUNCH_REFUSED'      - LAUNCH_REFUSED   + RESOURCE_GATE_SHUT
- `test_w2_20_launch::test_s19_a_launch_is_refused_while_a_reading_is_shut_naming_the_limit_and_its_reading[cpu-a lead]`: AssertionError: GovError('gov launch refuses the orchestrator session for ticket \'DAEO-lead1\': the resource gate is shut, no session...is needed; memory cannot be read against the threshold None (the memory figures are not configured) (DEC-1088 (5)(b))') assert 'RESOURCE_GATE_SHUT' == 'LAUNCH_REFUSED'      - LAUNCH_REFUSED   + RESOURCE_GATE_SHUT
- `test_w2_20_launch::test_s19_a_launch_is_refused_while_a_reading_is_shut_naming_the_limit_and_its_reading[cpu-a worker]`: AssertionError: GovError('gov launch refuses the engineer session for ticket \'DAEO-wrk01\': the resource gate is shut, no session sta...is needed; memory cannot be read against the threshold None (the memory figures are not configured) (DEC-1088 (5)(b))') assert 'RESOURCE_GATE_SHUT' == 'LAUNCH_REFUSED'      - LAUNCH_REFUSED   + RESOURCE_GATE_SHUT
- `test_w2_20_launch::test_s19_a_launch_is_refused_while_a_reading_is_shut_naming_the_limit_and_its_reading[disk-a lead]`: AssertionError: GovError('gov launch refuses the orchestrator session for ticket \'DAEO-lead1\': the resource gate is shut, no session...is needed; memory cannot be read against the threshold None (the memory figures are not configured) (DEC-1088 (5)(b))') assert 'RESOURCE_GATE_SHUT' == 'LAUNCH_REFUSED'      - LAUNCH_REFUSED   + RESOURCE_GATE_SHUT
- `test_w2_20_launch::test_s19_a_launch_is_refused_while_a_reading_is_shut_naming_the_limit_and_its_reading[disk-a worker]`: AssertionError: GovError('gov launch refuses the engineer session for ticket \'DAEO-wrk01\': the resource gate is shut, no session sta...is needed; memory cannot be read against the threshold None (the memory figures are not configured) (DEC-1088 (5)(b))') assert 'RESOURCE_GATE_SHUT' == 'LAUNCH_REFUSED'      - LAUNCH_REFUSED   + RESOURCE_GATE_SHUT
- `test_w2_20_launch::test_s19_a_launch_is_refused_while_a_reading_is_shut_naming_the_limit_and_its_reading[inodes-a lead]`: AssertionError: GovError('gov launch refuses the orchestrator session for ticket \'DAEO-lead1\': the resource gate is shut, no session...is needed; memory cannot be read against the threshold None (the memory figures are not configured) (DEC-1088 (5)(b))') assert 'RESOURCE_GATE_SHUT' == 'LAUNCH_REFUSED'      - LAUNCH_REFUSED   + RESOURCE_GATE_SHUT
- `test_w2_20_launch::test_s19_a_launch_is_refused_while_a_reading_is_shut_naming_the_limit_and_its_reading[inodes-a worker]`: AssertionError: GovError('gov launch refuses the engineer session for ticket \'DAEO-wrk01\': the resource gate is shut, no session sta...is needed; memory cannot be read against the threshold None (the memory figures are not configured) (DEC-1088 (5)(b))') assert 'RESOURCE_GATE_SHUT' == 'LAUNCH_REFUSED'      - LAUNCH_REFUSED   + RESOURCE_GATE_SHUT
- `test_w2_20_launch::test_s19_a_launch_is_refused_while_a_reading_is_shut_naming_the_limit_and_its_reading[config-a lead]`: AssertionError: GovError('gov launch refuses the orchestrator session for ticket \'DAEO-lead1\': the resource gate is shut, no session...is needed; memory cannot be read against the threshold None (the memory figures are not configured) (DEC-1088 (5)(b))') assert 'RESOURCE_GATE_SHUT' == 'LAUNCH_REFUSED'      - LAUNCH_REFUSED   + RESOURCE_GATE_SHUT
- `test_w2_20_launch::test_s19_a_launch_is_refused_while_a_reading_is_shut_naming_the_limit_and_its_reading[config-a worker]`: AssertionError: GovError('gov launch refuses the engineer session for ticket \'DAEO-wrk01\': the resource gate is shut, no session sta...is needed; memory cannot be read against the threshold None (the memory figures are not configured) (DEC-1088 (5)(b))') assert 'RESOURCE_GATE_SHUT' == 'LAUNCH_REFUSED'      - LAUNCH_REFUSED   + RESOURCE_GATE_SHUT
- `test_w2_20_launch::test_s19_a_launch_that_declares_a_gpu_need_is_refused_without_the_room[a lead]`: AssertionError: GovError('gov launch refuses the orchestrator session for ticket \'DAEO-lead1\': the resource gate is shut, no session...); gpu cannot be read against the threshold 1048576000 (gpu_margin or gpu_shares is not configured) (DEC-1088 (5)(b))') assert ('RESOURCE_GATE_SHUT' == 'LAUNCH_REFUSED'      - LAUNCH_REFUSED   + RESOURCE_GATE_SHUT)
- `test_w2_20_launch::test_s19_a_launch_that_declares_a_gpu_need_is_refused_without_the_room[a worker]`: AssertionError: GovError('gov launch refuses the engineer session for ticket \'DAEO-wrk01\': the resource gate is shut, no session sta...); gpu cannot be read against the threshold 1048576000 (gpu_margin or gpu_shares is not configured) (DEC-1088 (5)(b))') assert ('RESOURCE_GATE_SHUT' == 'LAUNCH_REFUSED'      - LAUNCH_REFUSED   + RESOURCE_GATE_SHUT)
- `test_w2_20_launch::test_s19_s7_a_full_set_of_heavy_slots_never_refuses_a_launch[a lead]`: AssertionError: timed out after 60 s waiting for heavy job holder to start its command
- `test_w2_20_launch::test_s19_s7_a_full_set_of_heavy_slots_never_refuses_a_launch[a worker]`: AssertionError: timed out after 60 s waiting for heavy job holder to start its command
- `test_w2_20_launch::test_s19_the_slots_refuse_a_launch_only_when_their_reading_cannot_be_taken[heavy_slots missing-a lead]`: AssertionError: GovError('gov launch refuses the orchestrator session for ticket \'DAEO-lead1\': the resource gate is shut, no session...re not configured); slots cannot be read against the threshold None (heavy_slots is not configured) (DEC-1088 (5)(b))') assert 'RESOURCE_GATE_SHUT' == 'LAUNCH_REFUSED'      - LAUNCH_REFUSED   + RESOURCE_GATE_SHUT
- `test_w2_20_launch::test_s19_the_slots_refuse_a_launch_only_when_their_reading_cannot_be_taken[heavy_slots missing-a worker]`: AssertionError: GovError('gov launch refuses the engineer session for ticket \'DAEO-wrk01\': the resource gate is shut, no session sta...re not configured); slots cannot be read against the threshold None (heavy_slots is not configured) (DEC-1088 (5)(b))') assert 'RESOURCE_GATE_SHUT' == 'LAUNCH_REFUSED'      - LAUNCH_REFUSED   + RESOURCE_GATE_SHUT
- `test_w2_20_launch::test_s19_the_slots_refuse_a_launch_only_when_their_reading_cannot_be_taken[heavy_slots malformed-a lead]`: AssertionError: GovError('gov launch refuses the orchestrator session for ticket \'DAEO-lead1\': the resource gate is shut, no session...re not configured); slots cannot be read against the threshold None (heavy_slots is not configured) (DEC-1088 (5)(b))') assert 'RESOURCE_GATE_SHUT' == 'LAUNCH_REFUSED'      - LAUNCH_REFUSED   + RESOURCE_GATE_SHUT
- `test_w2_20_launch::test_s19_the_slots_refuse_a_launch_only_when_their_reading_cannot_be_taken[heavy_slots malformed-a worker]`: AssertionError: GovError('gov launch refuses the engineer session for ticket \'DAEO-wrk01\': the resource gate is shut, no session sta...re not configured); slots cannot be read against the threshold None (heavy_slots is not configured) (DEC-1088 (5)(b))') assert 'RESOURCE_GATE_SHUT' == 'LAUNCH_REFUSED'      - LAUNCH_REFUSED   + RESOURCE_GATE_SHUT
- `test_w2_20_launch::test_s19_guard_a_launch_starts_while_the_gate_is_open[a lead]`: gov.cli.errors.GovError: gov launch refuses the orchestrator session for ticket 'DAEO-lead1': the resource gate is shut, no session starts: config: floor_bytes: missing (an object with its value, date and source is needed); config: trip_floor_bytes: missing (an object with its value, date and source is needed); config: gpu_shares: a non-empty list of {"kind": <name>, "bytes": <integer>} in priorit
- `test_w2_20_launch::test_s19_guard_a_launch_starts_while_the_gate_is_open[a worker]`: gov.cli.errors.GovError: gov launch refuses the engineer session for ticket 'DAEO-wrk01': the resource gate is shut, no session starts: config: floor_bytes: missing (an object with its value, date and source is needed); config: trip_floor_bytes: missing (an object with its value, date and source is needed); config: gpu_shares: a non-empty list of {"kind": <name>, "bytes": <integer>} in priority or
- `test_w2_20_launch::test_s19_the_override_starts_it_and_is_written_in_the_launch_log_and_the_output[a lead]`: AssertionError: the launch log's line does not hold 'gate_override': 2026-11-09T04:30:33+00:00 gov launch: OVERRIDE gate DEC-1234: the orchestrator session for ticket 'DAEO-lead1' in /tmp/gov-os-emg-cto/t20/pytest-of-usain/pytest-0/test_s19_the_override_starts_i0/this-repo starts while the resource gate is shut, no session starts: config: floor_bytes: missing (an object with its value, date and so
- `test_w2_20_launch::test_s19_the_override_starts_it_and_is_written_in_the_launch_log_and_the_output[a worker]`: AssertionError: the launch log's line does not hold 'gate_override': 2026-11-09T04:30:33+00:00 gov launch: OVERRIDE gate DEC-1234: the engineer session for ticket 'DAEO-wrk01' in /tmp/gov-os-emg-cto/t20/pytest-of-usain/pytest-0/test_s19_the_override_starts_i1/this-repo starts while the resource gate is shut, no session starts: config: floor_bytes: missing (an object with its value, date and source
- `test_w2_20_load::test_s5_the_load_rule_is_the_lower_of_the_1_and_15_minute_loads_below_nproc[a short peak opens]`: AssertionError: {'available_memory_bytes': 68719476736, 'busy_cores': 0.03, 'busy_window_s': 0.3, 'cleared': [], ...} assert (False is True)
- `test_w2_20_load::test_s5_the_load_rule_is_the_lower_of_the_1_and_15_minute_loads_below_nproc[a falling load opens]`: AssertionError: {'available_memory_bytes': 68719476736, 'busy_cores': 0.04, 'busy_window_s': 0.3, 'cleared': [], ...} assert (False is True)
- `test_w2_20_load::test_s5_the_load_rule_is_the_lower_of_the_1_and_15_minute_loads_below_nproc[just below nproc opens]`: AssertionError: {'available_memory_bytes': 68719476736, 'busy_cores': 0.02, 'busy_window_s': 0.3, 'cleared': [], ...} assert (False is True)
- `test_w2_20_load::test_s5_the_load_rule_is_the_lower_of_the_1_and_15_minute_loads_below_nproc[both at nproc shuts]`: AssertionError: {'config': {'condition': 'config', 'reading': None, 'threshold': None, 'why': 'embedding_servers.query.host: a host:po... 'memory': {'condition': 'memory', 'reading': None, 'threshold': None, 'why': 'the memory figures are not configured'}} assert {'config', 'load', 'memory'} == {'load'}      Extra items in the left set:   'config'   'memory'   Use -v to get more diff
- `test_w2_20_load::test_s5_the_load_rule_is_the_lower_of_the_1_and_15_minute_loads_below_nproc[both above nproc shuts]`: AssertionError: {'config': {'condition': 'config', 'reading': None, 'threshold': None, 'why': 'embedding_servers.query.host: a host:po... 'memory': {'condition': 'memory', 'reading': None, 'threshold': None, 'why': 'the memory figures are not configured'}} assert {'config', 'load', 'memory'} == {'load'}      Extra items in the left set:   'config'   'memory'   Use -v to get more diff
- `test_w2_20_memory::test_s6_the_running_sessions_live_memory_is_added_to_memavailable`: AssertionError: the session's live memory is not read: {'registry': '/tmp/gov-os-emg-cto/t20/pytest-of-usain/pytest-0/test_s6_the_running_sessions_l0/home/.gov-os/machine', 'kind': 'reading', 'available_memory_bytes': 5234491392, 'load_1m': 0.1, 'load_15m': 0.1, 'nproc': 4, 'busy_cores': 0.04, 'busy_window_s': 0.3, 'cpu_demand_cores': 0.04, 'servers': {}, 'memory': {'have_bytes': None, 'need_bytes
- `test_w2_20_memory::test_s6_each_running_session_and_the_new_one_need_a_working_size[2 running opens]`: AssertionError: gov resources did not succeed: exit 3 envelope: {'ok': False, 'command': 'resources', 'result': {}, 'session': '', 'error': {'code': 'RESOURCE_GATE_SHUT', 'message': 'the resource gate is shut, no session starts: config: floor_bytes: missing (an object with its value, date and source is needed); config: trip_floor_bytes: missing (an object with its value, date and source is needed)
- `test_w2_20_memory::test_s6_each_running_session_and_the_new_one_need_a_working_size[3 running shuts]`: AssertionError: {'config': {'condition': 'config', 'reading': None, 'threshold': None, 'why': 'embedding_servers.query.host: a host:po... 'memory': {'condition': 'memory', 'reading': None, 'threshold': None, 'why': 'the memory figures are not configured'}} assert {'config', 'memory'} == {'memory'}      Extra items in the left set:   'config'   Use -v to get more diff
- `test_w2_20_memory::test_s6_nothing_is_reserved_for_a_run_that_has_not_started`: AssertionError: gov resources did not succeed: exit 3 envelope: {'ok': False, 'command': 'resources', 'result': {}, 'session': '', 'error': {'code': 'RESOURCE_GATE_SHUT', 'message': 'the resource gate is shut, no session starts: config: floor_bytes: missing (an object with its value, date and source is needed); config: trip_floor_bytes: missing (an object with its value, date and source is needed)
- `test_w2_20_memory::test_f6_a_workers_memory_is_charged_once_not_in_its_leads_tree_and_again_as_its_own_session`: AssertionError: the two sessions' live memory is None: the worker's 192 MiB is not counted exactly once assert (False)  +  where False = isinstance(None, int)
- `test_w2_20_plan_source::test_s21_the_launcher_starts_a_lead_the_main_tree_admits`: gov.cli.errors.GovError: gov launch refuses the orchestrator session for ticket 'PLN-f004': the resource gate is shut, no session starts: config: floor_bytes: missing (an object with its value, date and source is needed); config: trip_floor_bytes: missing (an object with its value, date and source is needed); config: gpu_shares: a non-empty list of {"kind": <name>, "bytes": <integer>} in priority 
- `test_w2_20_plan_source::test_s21_a_plan_override_is_one_line_in_the_launch_log_and_the_line_on_standard_error`: gov.cli.errors.GovError: gov launch refuses the orchestrator session for ticket 'PLN-f005': the resource gate is shut, no session starts: config: floor_bytes: missing (an object with its value, date and source is needed); config: trip_floor_bytes: missing (an object with its value, date and source is needed); config: gpu_shares: a non-empty list of {"kind": <name>, "bytes": <integer>} in priority 
- `test_w2_20_query_start::test_s20_the_output_is_appended_to_the_servers_own_log`: AssertionError: timed out after 10 s waiting for the server's output in its log
- `test_w2_20_query_start::test_s20_each_start_writes_one_line_naming_the_time_the_device_and_the_caller[gpu]`: AssertionError: one start, and the start log holds 0 lines: [] assert 0 == 1  +  where 0 = len([])
- `test_w2_20_query_start::test_s20_each_start_writes_one_line_naming_the_time_the_device_and_the_caller[cpu]`: AssertionError: one start, and the start log holds 0 lines: [] assert 0 == 1  +  where 0 = len([])
- `test_w2_20_reading::test_the_reading_reports_memory_load_processors_and_the_registry_folder`: AssertionError: {'available_memory_bytes': 17179869184, 'busy_cores': 0.47, 'busy_window_s': 0.3, 'cleared': [], ...} assert None == 1.25  +  where None = <built-in method get of dict object at 0x7186d84ef1c0>('busy_cores_1m')  +    where <built-in method get of dict object at 0x7186d84ef1c0> = {'available_memory_bytes': 17179869184, 'busy_cores': 0.47, 'busy_window_s': 0.3, 'cleared': [], ...}.ge
- `test_w2_20_reading::test_every_live_session_is_read_with_its_pid_repository_ticket_role_and_live_memory`: AssertionError: a session without its live memory: {'pid': 2821569, 'repository': '/tmp/gov-os-emg-cto/t20/pytest-of-usain/pytest-0/test_every_live_session_is_rea0/this-repo', 'ticket': 'DAEO-lite', 'role': 'engineer', 'started': '2026-11-09T04:30:58+00:00', 'memory_bytes': 10956800} assert False  +  where False = isinstance(None, int)  +    where None = <built-in method get of dict object at 0x71
- `test_w2_20_remeasure::test_s9_samples_note_the_verification_lock_and_the_remeasure_writes_both_figures_with_the_date`: AssertionError: None assert (False)  +  where False = isinstance(None, list)
- `test_w2_20_remeasure::test_s7_s9_the_remeasure_keeps_the_rebuild_peak_from_rebuild_slot_holders_which_hold_no_verification_lock`: AssertionError: timed out after 60 s waiting for heavy job rb to start its command
- `test_w2_20_slots::test_s7_a_heavy_job_waits_for_a_machine_wide_slot[a test run waits for a test run]`: AssertionError: timed out after 60 s waiting for heavy job first to start its command
- `test_w2_20_slots::test_s7_a_heavy_job_waits_for_a_machine_wide_slot[a rebuild waits for a test run]`: AssertionError: timed out after 60 s waiting for heavy job first to start its command
- `test_w2_20_slots::test_s7_a_heavy_job_waits_for_a_machine_wide_slot[a test run waits for a rebuild]`: AssertionError: timed out after 60 s waiting for heavy job first to start its command
- `test_w2_20_slots::test_s7_the_number_of_slots_is_the_configuration_files`: AssertionError: timed out after 60 s waiting for heavy job one to start its command
- `test_w2_20_slots::test_s7_a_rebuild_excludes_only_another_rebuild_of_the_same_tree`: AssertionError: timed out after 60 s waiting for heavy job x1 to start its command
- `test_w2_20_slots::test_s7_a_session_takes_no_slot`: AssertionError: timed out after 60 s waiting for heavy job holder to start its command
- `test_w2_20_slots::test_f4_no_fixed_ceiling_on_leads_or_sessions`: AssertionError: a ceiling on sessions shut the gate: {'open': False, 'reasons': [{'condition': 'config', 'reading': None, 'threshold': None, 'why': 'floor_bytes: missing (an object with its value, date and source is needed)'}, {'condition': 'config', 'reading': None, 'threshold': None, 'why': 'trip_floor_bytes: missing (an object with its value, date and source is needed)'}, {'condition': 'config'
- `test_w2_20_stale::test_W2_M244_W2_M188_W2_M262_a_stale_entry_does_not_count_against_the_gate`: AssertionError: a dead session counted against the gate: {'registry': '/tmp/gov-os-emg-cto/t20/pytest-of-usain/pytest-0/test_W2_M244_W2_M188_W2_M262_a0/home/.gov-os/machine', 'kind': 'reading', 'available_memory_bytes': 12884901888, 'load_1m': 0.1, 'load_15m': 0.1, 'nproc': 4, 'busy_cores': 0.32, 'busy_window_s': 0.4, 'cpu_demand_cores': 0.32, 'servers': {}, 'memory': {'have_bytes': None, 'need_by
- `test_w2_20_tripwire::test_s11_below_the_trip_floor_the_largest_heavy_job_is_stopped_and_nothing_else`: AssertionError: timed out after 60 s waiting for heavy job small-job-A to start its command
- `test_w2_20_tripwire::test_s11_at_or_above_the_trip_floor_nothing_is_stopped`: AssertionError: timed out after 60 s waiting for heavy job small-job-A to start its command
