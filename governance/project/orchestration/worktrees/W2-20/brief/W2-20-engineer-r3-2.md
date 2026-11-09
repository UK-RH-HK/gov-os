Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-20/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# W2-20 — the engineer's brief, round 3: the review's findings and the CTO's rulings (DAEO-r30l)

You are a fresh engineer for **W2-20** (`.tickets/DAEO-r30l.md`). Round 2 and the designer's rounds 4 to 7 are on
`w2/W2-20` (head `c90771b74`): `gov accept W2-20` was 163 passed, 0 failed, S16 skipped, before round 7 (round 7 adds
cases that are red until you build them); W2-136 76/76; W2-112's socket cases 37 passed. The machine's gate file was
rewritten by the owner's operator for round 2's format (ACT-GATE-CONFIG-2), so your session was admitted.

The independent review (round 1) is **NOT READY** on F1. The CTO, as moderator, rules:

- **Fix (blocking):** **F1**: hold one machine-wide lock from the gate check until the session is registered (or
  register a provisional entry inside the same lock before releasing it), so launches that start together are counted
  against each other; a launch that ends before registering leaves no entry. A unit case starting several launches at
  once (stand-in CLI) shows that only those the memory rule admits start.
- **Fix (the CTO's ruling): F2**, the CPU rule counted the embedding servers twice and would shut the gate during store
  rebuilds, refusing honest work. The designer has revised the cases (round 7): build to the interface below, "The
  gate", cpu: `busy_cores_1m + max(0, p95(shared) − now(shared)) + max(0, p95(query) − now(query)) < nproc`, with the
  new reading `embedding_cpu_now` (each server's CPU use over the same last minute; planted through
  `GOV_RESOURCES_EMBEDDING_CPU_NOW`; unreadable is null and shuts on cpu). See "Round 7's changes" below.
- **Fix too (cheap, in scope):** **F4** (a missing or malformed `oom_floor_bytes` is named, as S8 requires, never a
  silently skipped trip-wire); **F6** (an entry whose pid is alive but whose start time differs from the recorded
  `started` is stale and cleared; CPU history from before a restart is discarded at once instead of reading null);
  **F8** (a plan override is logged only once the gate admits the launch).
- **The configuration format is frozen from `28fbcfebf` (the CTO's ruling):** the machine's file was written from it.
  **Do not change any configuration key's name, nesting, value form or meaning** in `src/gov/resources/config.py` or
  anywhere that reads the file; a new case (round 7) pins it. If a fix seems to need a configuration change, stop and
  name it in your return instead.
- **Rows, not this round:** F3 (S16's evidence: the designer has revised the case; the CTO re-runs it), F5, F7, F9, F10.

Add unit cases for each fix; update `docs/changes/W2-20-evidence.md` (F1, F2, F4, F6, F8 and the rows named).

## The review's findings, as written (round 1)

**F1. Concurrent launches all pass the memory check.** `launcher.py:404` and `:390` run the check, then `_run` (`:457`) registers the session after `Popen`, with no lock in between. Several launches that start together each read the same session count, so each counts only itself as the new session. The memory rule then lets in up to k−1 sessions past its limit, at 2.04 GiB each. On this 23.5 GiB machine that limit is about 7–8 sessions.
Ordinary work: yes, because `launch_worker.sh` starts each worker with `setsid … &` and returns at once, and a CTO's parallel tool calls start launches at the same moment. Each check takes at least 0.25 s.
Consequence: fails open. scope: in (S19, S6).

**F2. The CPU rule counts the embedding servers twice.** `gate.py:92` adds busy cores, which already include the servers' current use, to each server's p95. That p95 is kept for a week, and each sample is an average since the previous reading. During store rebuilds the shared server's p95 can sit near 8 cores, so the gate shuts at about 12 busy cores of 20, whenever a rebuild runs. This is the designer's stated interface choice.
Ordinary work: yes, because rebuilds are frequent.
Consequence: other (honest launches falsely refused; the override exists). scope: in (S2, S12).

**F3. S16's evidence used the wrong share.** The case sets `share = affinity // slots`, which is 6. The slot's real CPU set is the 8 CPUs outside the servers' sets divided by 3, so 2 CPUs. Against the real share plus one (3), the recorded 3.13 is over. That figure counts the whole machine, including whatever else ran at the time. The confinement itself holds by construction (`sched_setaffinity`). So the KPI's aim is probably met, but the evidence does not show it.
Ordinary work: no, because this is about evidence, not product behaviour.
Consequence: other. scope: in (S16).

**F4. The trip-wire is silently off when `oom_floor_bytes` is missing or malformed.** `slots.py:366` skips the pass and says nothing. With today's file, every heavy job would run without a trip-wire.
Ordinary work: no, because the ACT required before merge writes the key; after that only a hand edit removes it.
Consequence: fails open. scope: in (S11, S8).

**F5. A listening socket with no readable owner reads as 0 CPU.** `machine.listener` returns None when no readable file descriptor holds the socket, and `embedding_cpu` (`:236`, `:253`) treats that as "not listening", 0.0 cores. A server run by another user would hit this.
Ordinary work: no, because on this machine both servers run as the user.
Consequence: fails open. scope: in (F5).

**F6. After a WSL restart, old state causes false refusals.** `machine.alive` ignores an entry's `started` time, so a reused pid counts as a live session with its working size until that process ends. Also, `cpu-stat.json` history from before the restart makes busy cores read as null ("the counters went back") for up to about a minute.
Ordinary work: yes, because `wsl --shutdown` kills launchers before their cleanup runs.
Consequence: other (fails closed). scope: in (S3, S2).

**F7. Two separate slot pools until the tooling moves.** `heavy_slot.sh` uses `/tmp/gov-os-heavy-slot-i.lock` and the product uses `~/.gov-os/machine/slots/`, so 3+3 heavy jobs can run at once. Neither `gov accept` nor `gov rebuild` takes a slot itself. S17's exclusion of the servers' CPUs leaves 2 CPUs per slot, against 6 today.
Ordinary work: yes, after the merge.
Consequence: other. scope: out (tooling and the decision).

**F8. A plan override is logged before the gate check runs.** `launcher.py:386–390`: if the gate then refuses, `launch.log` holds `OVERRIDE plan_override` for a lead that never started.
Ordinary work: yes.
Consequence: other. scope: in (S21).

**F9. Possible double count of the embedder's GPU share on WSL.** A GPU work kind with no listed process keeps its whole share (`gpu_room`). If WSL's `nvidia-smi` lists no compute processes, or names them so the kind reads as `other`, the embedder's share is held back on top of the free memory it already took. That would wrongly refuse a start that declares a GPU need.
Ordinary work: no, because no launch declares a GPU need today.
Consequence: other. scope: in (S14, S10).

**F10. The re-measure can only raise its figures, and nothing samples on a schedule.** `measure.remeasure` takes the largest of every sample ever kept (`samples.jsonl` is never trimmed). Nothing takes samples on a schedule, so the stale 2.04 GiB working size stays until someone samples by hand. That figure is named as due for re-measure, as S8 asks.
Ordinary work: yes.
Consequence: other. scope: in (S9).

## Verdict per line
- **Fail:** S6 and S19 (F1); S16 (F3, evidence only, does not block).
- **Pass with a non-blocking finding:** S2 and S12 (F2); S3 (F6); S7 (F7, out of scope); S8 and S11 (F4); S9 (F10); S10 and S14 (F9); S21 (F8); the F5 line (F5).
- **Pass, no finding:** S1, S4, S5, S13, S15, S17, S18, S20, F1, F2, F3, F4, F6.


## Where you work
- `/home/usain/gov-os-worktrees/W2-20`, branch `w2/W2-20`; your paths are the ticket's `allowed_paths`.
- **You never read `tests/acceptance/`**: only `gov accept`'s results. Every Grep or Glob call that could reach it
  carries `!tests/acceptance/**`; recursive grep `--exclude-dir=acceptance`.

## Verify
- Through `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh`, with
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-20/src` and `-m "not local_only" -k "not real and not green_here and not time_limit"`:
  your unit tests and `tests/unit/resources tests/unit/launch tests/unit/rebuild tests/unit/secrets_check`; then
  `python3 -m gov.cli.main accept W2-20 --root /home/usain/gov-os-worktrees/W2-20` (about 18 minutes; in the
  background) and `accept W2-136`.

## Rules
- The hidden-half rule: never open anything under `~/gov-os-eval/`, `~/gov-os-runs/`, or any `hidden`,
  `memory-verdict` or `memory-verdict-2` folder. Never touch the Ollama servers, the reranker service, `~/.local/bin`,
  `~/.ollama`, `~/.gov-os/` or any service; no GPU job. Never make a gate reading fail open.
- DEC-1080: Read and Grep tools; one simple command per Bash call. Search again once (DEC-1092 (1)) if needed.
- Do not merge `w2/integrate`. Never touch `tests/acceptance/**`, `.tickets/` or `.claude/`.
- **Commit** on `w2/W2-20` with
  `--trailer "Task: DAEO-r30l" --trailer "Implements: DEC-1088, DEC-1097" --trailer "Role: engineer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.
- Before you end, every run you started has finished.

## Return
Your whole return is your session's **final message** (the launcher keeps it; it is the record): the twelve labelled
fields of `EMG-common.md` (sandbox and `ps` checks first), each finding and what you changed, the new unit cases, the
unit, regression and `gov accept` counts with every red named.


---

# The interface the acceptance cases assume (the designer's README after round 7, as written)

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
| `embedding_cpu_now` | `{"shared": cores, "query": cores}`, the two servers' CPU use over the same last minute as `busy_cores_1m` (the part of the busy cores that is theirs), shown beside their p95, or `null` (round 7). |
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
- **cpu (S2, S12), round 7 (the CTO's ruling under DEC-1097 (8) on review F2):**
  `busy_cores_1m + max(0, p95(shared) − now(shared)) + max(0, p95(query) − now(query)) < nproc`, where `now` is
  `embedding_cpu_now`. The busy cores already hold the servers' current use, so only the part of each server's p95
  above its current use is added: the servers are never counted twice, and a server busier now than its p95 adds
  nothing (it takes nothing away either). Reading: the sum; threshold: nproc. Equal shuts. Busy cores alone shut it
  only at nproc or above: 4.0 busy of 4 with each server's p95 equal to its current use shuts (S2's case); 3.9 opens.
  A store rebuild (12 busy of 20, the shared server using 7.5 of its p95 8.0 now) adds 0.5 and opens; the same p95
  with the servers idle now adds all 8.0 of it. An unreadable `embedding_cpu_now` shuts on `cpu` with `reading`
  `null` (F5). (Rounds 1 to 6 added the whole p95 on top of the busy cores: a false refusal during store rebuilds.)
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
| `GOV_RESOURCES_EMBEDDING_CPU_NOW` | the gate's own sampling of the two servers over the busy cores' last minute | JSON `{"shared": cores, "query": cores}` (round 7) |
| `GOV_RESOURCES_DISK` | `statvfs` of the shared disk | JSON `{"free_bytes": N, "free_inodes": N}` |
| `nvidia-smi` on `PATH` | | read with `--query-gpu=<fields>` and `--query-compute-apps=<fields>`, `--format=csv[,noheader][,nounits]`; fields `memory.total`, `memory.used`, `memory.free`, `utilization.gpu`; `pid`, `process_name`, `used_memory`. Exit 6 with "No devices were found" is no GPU. |

A process's GPU kind is read from its command line *(choice)*: a word whose file name begins with `ollama` is an
`embedder`; `rerank` anywhere a `reranker`; anything else `other`.

### The configuration file: `$HOME/.gov-os/machine/gate.json`

The file `gov.retrieval.ollama` already reads for the servers' cap (`GATE_REL`). Every gate value is an object
`{"value": V, "date": "YYYY-MM-DD", "source": "text"}`; a value without its date or source, or with a date that is
not a date, is malformed. **No default stands in for a missing value** (the old defaults of DEC-742 are gone).

**Frozen from `28fbcfebf` (round 7, the CTO):** W2-20's head when ACT-GATE-CONFIG-2 writes the machine's file. No key
below is renamed, added or given another meaning. `gov resources --init-config` writes exactly this set and nothing
else: the eleven dated values (each exactly `{"value", "date", "source"}`); `thread_budget` only as a dated value
when present (the template may leave it out); `embedding_servers` with `shared` and `query` (and at most a section
`date` and `source`), each server `cpus` (a CPU list text, W2-123's form) and `nice` (0 to 19), optionally
`parallel`, `probe_slow_s`, `probe_hung_s`, its own `date` and `source`, and for `query` `device`. Each server is
dated and sourced on itself or by the section (`test_s8_init_config_writes_exactly_the_frozen_configuration_format`).

| Key | Value | Notes |
|---|---|---|
| `memory_floor_bytes` | integer ≥ 0 | 3 GiB on this machine (DEC-942 item 2) |
| `verification_peak_bytes` | integer ≥ 0 | measured (S9); due after seven days |
| `working_size_bytes` | integer ≥ 0 | measured (S9); due after seven days |
| `rebuild_peak_bytes` | integer ≥ 0 | measured (S9, P-5 (a)); required, dated and sourced like every value (P-7, settled in the ticket) |
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

`test_w2_20_measured.py` runs a planted suite (8 tests, each starting a program that forks one spinning process per
`os.cpu_count()` CPU for 3 s, ignoring its CPU set; `-n 2` when pytest-xdist is there) twice: plainly and through
`gov resources --slot test`, under the real `~/.gov-os/machine/gate.json` (read, never written). It samples busy cores
from `/proc/stat` every 0.2 s and asserts: without the slot the p95 exceeds the share + 1 (else there is no measure);
with it, at most the share + 1; and the slot's run at most 20 % slower. It prints the figures for the evidence. **The
CTO runs it outside the sandbox**, on the real machine, not inside another heavy slot; elsewhere it skips:
`GOV_W2_20_MEASURE=1 PYTHONPATH=<tree>/src python3 -m pytest tests/acceptance/W2-20/test_w2_20_measured.py -m local_only -p no:cacheprovider -s`.
The planted programs spin until a deadline, so the time compares the slot's overhead, not a fixed amount of work
(P-4, confirmed by the CTO 2026-11-09: the 20 % is measured on time-bound programs; the case is unchanged).

**Round 5 (2026-11-09, `Rewrite-Reason: DEC-1097 (8)`).** The CTO's run outside the sandbox (20 CPUs, share 6) failed
the first assert: without the slot the busy cores' p95 was 3.65, not above 7, so there was no measure. The cause was in
the case: `spin.py` spun `os.cpu_count()` Python threads, which the GIL holds to about one core per program, so 8 tests
on 2 workers never loaded more than three or four cores. `spin.py` now forks one process per `os.cpu_count()` CPU, each
spinning until the same deadline, and the parent waits for them (it prints `spin: N processes for N CPUs`, which the
planted suite's capture swallows). The time-bound design (P-4), the sampling and the three assertions are unchanged.

**Round 6 (2026-11-09, `Rewrite-Reason: DEC-1097 (8)`).** The CTO's run outside the sandbox passed (`share 6 of 20 CPUs
(3 slots); busy cores p95 with the slot 3.13, without 20.00`), but the independent review's F3 found it judged against
the wrong share: `affinity // slots` (6), where the slot's real set is the CPUs outside the servers' sets divided by
the slots (8 // 3 = 2 on that machine), and the busy cores counted the whole machine, other sessions included. The
case now (1) takes the share by S17's rule in this README's interface: the case's CPUs (`os.sched_getaffinity`, which
`gov resources` inherits) less every CPU in `embedding_servers.shared.cpus` and `.query.cpus` of the real `gate.json`,
`max(1, len(pool) // heavy_slots)`; (2) checks that the slot really gave its programs that many CPUs (each planted
program writes its CPU set to `seen/<pid>.json` beside it; inside the slot every set must have `share` CPUs); (3)
measures each run net of the machine's background: after a 1 s settle, busy cores are sampled for 3 s with nothing of
the case running, just before each run, and that p95 is subtracted from the run's p95 (the background's median is
printed too). The assertions compare the net figures: without the slot, net above share + 1; with it, net at most
share + 1. The time-bound design (P-4) and the 20 % check are unchanged. It prints four `S16 evidence:` lines: the
share and how it was reached, the CPU sets seen in the slot; the two backgrounds (p95 and median); the gross and net
p95 of each run against share + 1; the two times.

**Round 7 (2026-11-09, `Rewrite-Reason: DEC-1097 (8)`).** The CTO did not accept round 6's background: one sampled just
after the plain run holds that run's tail and flatters the net figure. The background is now sampled **once, before the
plain run**, on a quiet machine (a 2 s settle, then 5 s of samples with nothing of the case running), and its
**median** is subtracted from both runs' p95 (net = gross p95 − the background's median). An unsampled 2 s settle
separates the plain run from the slot's run. The second `S16 evidence:` line now gives the one background's median and
p95 and its sample count; the third each run's gross and net p95 against share + 1. The real share (S17's rule), the
CPU-set check, the time-bound design (P-4) and the 20 % check are unchanged. **On a quiet machine** is the CTO's run
condition: the case does not judge quietness itself; a busy background shows in the printed median and p95.


## Round 7's changes (2026-11-09)

The CTO's rulings before the engineer's round 3. Item 1's commits carry `Rewrite-Reason: the CTO's ruling under
DEC-1097 (8), a false refusal (review F2)`; item 3's `Rewrite-Reason: DEC-1097 (8)`; item 2's new case none.

| Ruling | Case | Change | Commit |
|---|---|---|---|
| 1, F2 | support (`w2_20_support.py`) | the servers' current use as a planted reading, `GOV_RESOURCES_EMBEDDING_CPU_NOW` (`set_readings(embedding_now=...)`), idle (0.0, 0.0) by default, so a case that plants only the p95 keeps its sum; no case changes what it asserts | `e5aafd01d` |
| 1, F2 | `test_w2_20_cpu.py::test_s2_the_gate_judges_busy_cores_and_load_each_on_its_own_and_shows_both` | the servers busy now at their p95 (0.25 each, inside the busy cores): the cpu reading is the busy cores alone, 4.0 of 4, asserted | `7919608ec` |
| 1, F2 | `test_w2_20_cpu.py::test_s12_both_servers_cpu_p95_count_when_a_session_is_admitted` | the servers idle now: their whole p95 is headroom and counts (same sums); the reading shows `embedding_cpu_now` beside the p95 | `e8d18604a` |
| 1, F2 | `test_w2_20_cpu.py::test_s12_only_the_part_of_each_servers_p95_above_its_current_use_is_added` (new, 3 cases) | 20 CPUs: a store rebuild (busy 12, shared p95 8.0 using 7.5 now) opens; the same p95 idle now shuts at equal (20.0); a server busier now than its p95 subtracts nothing, equal shuts (20.0) | `4f86a75db` |
| 1, F2 | `test_w2_20_cpu.py::test_s12_f5_the_servers_current_use_unreadable_shuts_on_cpu` (new) | the new reading fails closed: `null`, shut on `cpu`, `reading` `null` | `ee04552af` |
| 1, F2 | `test_w2_20_gate.py::test_exactly_at_a_threshold[cpu]` | equal by the new rule: 2.25 + (1.0 − 0.5) + (0.25 − 0.0) = 3.0 of 3 shuts (counted twice it reads 3.5) | `ecd13afd4` |
| 2 | `test_w2_20_config.py::test_s8_init_config_writes_exactly_the_frozen_configuration_format` (new) | `--init-config` under a planted HOME writes exactly "The configuration file"'s key set, value form and nesting, and nothing else | `a197aed6f` |
| 3 | `test_w2_20_measured.py::test_s16_one_slot_holds_a_cpu_hungry_suite_to_its_share_plus_one_within_20_percent_of_the_time` | one background, before the plain run; its median nets both runs; gross, net, median and p95 printed | `fe6fe8ac0` |

Unchanged, and still right under the new rule because the servers are idle now in them (the support's default): the
cpu cases of `test_one_broken_condition_shuts_the_gate_and_is_named_with_its_reading_and_threshold[cpu]` (3.5 + 0.25 +
0.25 = 4.0), `test_several_broken_conditions_are_all_named` (9 + 0.5 + 0.5 = 10.0) and
`test_w2_20_launch.py`'s `cpu` rows (4.0).

Run on this branch (no product; integrate's code), round 2's command with an empty `HOME` (and `PYTHONUSERBASE` at
the user site, so pytest is found): **159 failed, 9 passed, 1 deselected** (169 cases): round 4's 154 red plus the five
new cases, all red because the product is missing (`gov resources`: `invalid choice: 'resources'`, exit 2, no JSON
envelope); the nine greens are the same guards; the deselected one is S16 (`local_only`), which collects and skips
without `GOV_W2_20_MEASURE=1`.

