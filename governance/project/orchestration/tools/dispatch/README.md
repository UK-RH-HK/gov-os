# The dispatcher (owner, 2026-11-01; DEC-1008 item 5, DEC-1010 items 6 and 7; v4.6: DEC-1032)

A plain program (Python 3 standard library, git, bash; no AI) that keeps the machine full and the work moving without
any Claude session remembering to watch. **Its code is here, committed; its state is in
`.gov-runtime/scratch/orchestrator/dispatch/`** (`DISPATCH_STATE` moves it, for the tests only). The owner's crontab
runs one pass a minute: `run_tick.sh` (here) → `dispatcher.py tick` (here), reading and writing the state folder.

## One pass
1. **The truth:** running leads from the processes (the launch form's identity marker
   `GOV_ROLE":"orchestrator","GOV_TICKET` and a lead worktree as the working folder), waiting launchers and starts
   under 10 minutes old (counted as leads), load, **real busy cores** (from `/proc/stat` deltas since the last pass:
   user + nice + system + irq + softirq + steal; iowait is not busy) and the embedding server's own cores, memory, the
   disk gate, the heavy-job slots held, the merge queue (its `run.lock`, or an interpreter running `land.py`), a close
   running, the main tree (clean, on `w2/integrate`), heavy steps running outside a slot. Every external command has
   a 60 s limit; a timeout is a failed check.
2. **Returns:** every finished lead log not in `log/returns-seen.txt` becomes an inbox item; a start that never ran
   (5 minutes, no process, no return) becomes one, once.
3. **Start:** nothing starts while the shared embedding server's last known state (`embed-health.json`, from the
   previous pass's check, 4d) is HUNG, FAILING or NOT RUNNING: every ready entry waits with "embedding server hung: starts held
   (DEC-1015)". Landings and closes are not held; they fail their own rebuild check instead. Otherwise,
   at most one lead a pass, 120 s apart, the first `ready.txt` entry passing every check (a lead log name;
   not running or launching; not already started for that log; no return yet; no unread inbox item for it; the claim
   `in_progress` on `w2/integrate` and in its worktree; no tracked change there; the brief without `@@`) **and admitted
   with room on every resource (DEC-1032), each from measured peaks; each refusal names the resource that is short**:
   - **real CPU, first and for every admission (the `gate_check` fallback included):** busy cores + the embedding
     server's CPU p95 above what it uses now < nproc − `cpu_margin` (2), over the interval since the last pass (at
     most 3 minutes); a first pass, or a sample older than 3 minutes, records the sample and refuses ("measuring"); a
     dry pass records nothing; an unreadable `/proc/stat` refuses (`real CPU: ...`);
   - **GPU memory, for every admission too:** the GPU's free memory (the last pass's read, 4f, at most
     `gpu_state_max_age_s` 300 old) ≥ the newcomer's expected GPU need + `gpu_headroom_mib` (2048). A lead's expected
     need is one reranker's share (`reranker_gpu_mib`, 3584: a reranker on the GPU, measured about 3.5 GiB) while a
     GPU reranker slot is free (fewer of the `rerank_gpu_slots` (2) lock files `rerank_gpu_glob`
     `/tmp/gov-os-rerank-gpu-*.lock` held than slots: its reranker would take it), else 0 (`GPU memory: N MiB free <
     M MiB (...)`). A GPU not read recently (no nvidia-smi, an old read) is not judged and says so: an absent reading
     is not a shortage, and the GPU watch alerts on its own;
   - **the lead cap from memory (replacing slots × `K`, which is no longer used):** `lead_cap = floor(room / a lead's
     p95)`, room = free memory + the leads' current trees − the floor − the slot runs − the services' headroom (the
     same parts as the memory rule below); running and launching leads + the newcomer ≤ the cap (`memory: lead cap
     N (...)`);
   - **memory** (`memory_rule: slots`, the default): free memory + the leads' current trees ≥ the floor + each running
     or launching lead at the larger of the lead p95 outside verification and its own outside maximum + the newcomer
     likewise + the slot runs + the shared services' headroom (the embedding server and the code-graph daemon at their
     p95 above what they hold; the rerankers outside every lead tree at their kind's p95 above what they hold, while a
     queue or close runs or such a reranker exists) (`memory: available + leads' ...`); `memory_rule: literal` counts
     each lead at its all-sample p95 instead. **The rerankers are counted:** one inside a lead's tree is in that
     lead's current memory and its peak; one outside is in the headroom; the reason names how many there are and
     their RSS now. **The reservation for the rerankers outside the leads (review of v4.6, F4; DEC-1033: at most
     `rerank_gpu_slots` (2) rerankers, on the GPU, the rest end)** is at most that number × one reranker's measured
     peak (the largest RSS of any reranker process in the dispatcher's own samples, one a reranker a pass, in
     `reranker-peak.json`, since `reranker_era_from` "2026-11-02 13:00"), and never above the rerankers' p95; until
     the samples number `reranker_min_samples` (30) **and** span `reranker_min_span_s` (86400: a day, round 2 G2) it
     is the rerankers' 7-day p95 as before. The `Balance:` line
     shows it (`reserve 4.4 GB: 2 x the 2240 MB peak (n samples since ...)`);
   - **the slot runs by device:** the heavy slots reckoned with follow where the shared embedder runs, from its latest
     load line (4f): all layers on the GPU, `slots_gpu` (3); none or only part, `slots_cpu` (2); no load seen yet,
     `heavy_slots.conf`'s number; never fewer than the slots held now. `heavy_slots.conf` itself (which
     `heavy_slot.sh` reads) is not changed: the target is the dispatcher's, in its status and admission only;
   - never while a heavy step has run outside a slot for over 5 minutes (a finding);
   - with `peaks.json` missing, over 7 days old, or under 120 minutes of history outside verification: `gate_check`'s
     verdict (fail closed to the old rule). The status shows `gate_check`'s verdict either way, for comparison.
   It launches with `launch_now.sh` (here): the owner's launch form copied verbatim from
   `tools/launch_when_gate_opens.sh`, without its wait on `gate_check` (admission is the dispatcher's), keeping the
   disk gate.
4. **Land:** `land.txt` claimed by an atomic rename, every line in one `tools/land.py` call, only when the queue is
   free, no close runs and the main tree is clean and on `w2/integrate`; the outcome to `land-done.txt` and the inbox.
   **A close holds a landing only when it conflicts (DEC-1014 item 1):** a running `close_build.py` closing one of the
   landing's tickets (its arguments' W2 ids), or one committing its records (only `.tickets/` or `closes/` files
   modified in the main tree: one pass); any other close does not. `land.py`'s own close commit retries up to 3
   times while another commit holds `index.lock`.
   **The nightly's hold (DEC-1018 item 1):** the nightly (cron 04:00) starts only after 5 quiet minutes with a clean
   main tree and an unchanged `w2/integrate`, and gives up at its latest start; a landing run takes about 45 minutes.
   So from `nightly_hold_from` (config, "03:15", local time) no landing is claimed until the nightly has started:
   `NIGHTLY-RUNNING` in the orchestrator folder newer than today's hold start, or a line for today in
   `log/nightly/status.txt` (written only from 08:00 by `nightly_check.sh`, or after a reboot, so in practice the marker is
   what releases it; a night that gives up, or exits early and removes its marker, stays held until the end). The hold
   always ends at `nightly_hold_until` ("05:30").
   Status: `land: held for the nightly (DEC-1018) until it starts`. A landing already in flight is finalised as usual,
   never stopped; starts and the inbox are not held. The dispatcher's own writes stay in its state folder under
   `.gov-runtime/` (ignored by git), so they never make the main tree unclean.
4b. **The CTO's watchers, as passes (DEC-1014 item 3), each finding one inbox item, once:** a lead's new commit not on
   `w2/integrate` whose subject marks a key result (baseline, measure, figures, hit@5, findings report, probe record,
   research record, PACKAGE; `interim-seen.txt`, keyed by the commit's patch-id, else its subject and tree, so a
   rebased commit is not reported again; a worktree seen the first time is marked silently); a new line of
   `log/guard-refusals.jsonl` with no `verdict` or `judgement` yet (`guard-offset.txt`, written only when the file
   grows; a file shorter than the offset is re-baselined to its end with no items); the nightly's status line for
   today (`nightly-seen.txt`). Their items carry their own label (`Interim:`, `Guard:`, `Nightly:`), never `W2:`, so
   they hold no lead's start. No inbox item overwrites another.
4c. **The guard harvest** (`tools/guard_refusals.py`, at most every 10 minutes): after the start and land decisions,
   detached (`dispatcher.py harvest` in its own session), one at a time under `guard-harvest.lock`, limited to
   `guard_harvest_timeout_s` (300). Its result is `guard-harvest.json`, shown in the status; a non-zero exit or a
   timeout is one of the pass's failures until a harvest succeeds.
4d. **The embedding servers' health, by progress (DEC-1015 item 2; DEC-1032):** every pass, after the decisions,
   each server (`shared` on port 11434, `query` on 11435: `embed_ports`; its log from `gpu_logs`) is judged by its
   runner's progress, not by one request's latency (a slow request under load is not a hang: 42 false "hung" flags on
   11-02). Its log is read on from a saved offset (the first read starts at its end; truncated or rotated: from 0; at
   most `gpu_log_read_max_mb` a pass): tasks done (llama-server's `slot release: ... stop processing`, one per input)
   and requests done (`[GIN] ... | <status> | ... POST "/api/embed"`), each as a rate a minute. **Progress is a task
   done or a 2xx request** (review of v4.6, F2). **A server failure is a 5xx request or a runner task's failure**
   (llama.cpp's `send_error: task id = N, error: ...`); a 4xx (400 a bad input, 404 a wrong model, 499 the client
   gave up) is the client's: neither progress nor a failure (round 2, G1). One `ss -Htnia` call (`embed_ss`, limit
   10 s) gives what waits on each port: a client socket (ESTAB, its peer the server's port) that has sent and had no
   answer since (bytes sent, and no byte received or its last send newer than its last receive; an idle keep-alive
   connection, or one that has sent nothing, does not wait: F3). The states: **BUSY** while there is progress;
   **IDLE** when nothing waits; **WAITING** when requests wait and have not yet waited `embed_stall_s` without
   progress; **HUNG** only when requests have waited `embed_stall_s` (180) with no progress during that wait: the
   stall clock starts when the wait starts (the oldest waiting request's send, or the first pass that saw a request
   waiting), or at the last progress if later, never at an earlier task (F1: a first request after an idle spell is
   not HUNG); **FAILING** when `embed_fail_after` (3) server failures in a row with no 2xx since (F2: an item like
   HUNG's, and starts held). FAILING clears itself (G1): on the first 2xx; after `embed_fail_clear_s` (300) with no
   new failure; or when the test request answers (sent while the shared server is FAILING, at most every
   `embed_check_every` passes); **NOT RUNNING** when nothing has
   listened on its port for `embed_hung_after` (3) passes (NOT LISTENING before that). BUSY, IDLE and WAITING raise
   nothing and hold nothing; HUNG, FAILING and NOT RUNNING are incidents. **The fallback:** when the shared server's
   log is unreadable (or its connections are
   unreadable and no task has completed for `embed_stall_s`), DEC-1015's test request decides, at most every
   `embed_check_every` passes (5) (`POST /api/embed`, `embed_model` `qwen3-embedding:0.6b`, a fixed short text,
   limit `embed_timeout_s` 30, never through a proxy, the server's own keep-alive left alone): `embed_hung_after` (3)
   failures, timeouts or refused connections in a row make an incident: HUNG, or NOT RUNNING when the last check was
   refused. An incident writes one `Server:` item and a `server:` line in `inbox-stale.txt`, once per incident; the
   shared server's holds starts (step 3); the query server's is its own item (`...-server-query-hung.txt`) and
   `server query:` line, and holds no start. Each clears when the server progresses again or idles (or answers). A
   restart (the shared server) runs only when
   `embed_restart_cmd` is set in `config.json` (default none: alert only), the incident has lasted `embed_restart_after_s`
   (900) with no answer in that window, and no restart ran in the last `embed_restart_min_gap_s` (1800); each restart
   is logged and itemised. State: `embed-health.json` (`servers`: each server's offset, rates, waiting, state;
   `how`: progress or probe). Status: `embedding server: shared BUSY 1290 tasks/min (1 waiting, the oldest 0.4 s);
   query IDLE 0 tasks/min`, or by the test request `healthy (0.05 s) | HUNG since ... | NOT RUNNING since ... |
   failing (n in a row)`.
4e. **The heavy-slot holders' progress (DEC-1015 item 2):** each holder of `/tmp/gov-os-heavy-slot-*.lock` (from
   `/proc/locks`; a waiter is not a holder) has its process tree's CPU time (utime + stime) compared with the last
   sample (`slot-progress.json`, keyed by pid and start time). Not grown for `slot_idle_s` (900): IDLE, one `Slot:`
   item naming the slot, the pid, the command, the tree (cwd) and the idle time, and a `slot N pid P:` line, once per
   holder; it clears when the CPU grows or the holder ends. A holder is never killed; while the server is HUNG the item
   says the holder is likely waiting on it. Status: `heavy slot holders: slot N pid P (command) idle M min`.
4f. **The GPU (DEC-1030):** every `gpu_check_every` passes (1), one read of the GPU by `gpu_smi`
   (`/usr/lib/wsl/lib/nvidia-smi`, limit `gpu_smi_timeout_s` 10): its memory and utilisation
   (`--query-gpu=name,memory.used,memory.total,utilization.gpu`), then its holders
   (`--query-compute-apps=pid,process_name,used_memory`; a `[N/A]` memory, as on WSL, keeps the pid). nvidia-smi takes
   one `--query-*` switch a call, so a read is two short calls, the second only when the first answered. Each holder
   is classified from `/proc` by its command line and parents: `embedder shared` (an ollama or llama-server under the
   `ollama serve` with no `OLLAMA_HOST` or `127.0.0.1:11434`), `embedder query` (`127.0.0.1:11435`), `embedder other`
   (any other, e.g. a private test server), `reranker` (a command line holding `rerank`), `other`. A missing or failing
   nvidia-smi is the status line `GPU: unreadable (why)`, never a failure of the pass.
   Each server's log (`gpu_logs`: `shared` `/home/usain/.ollama/serve-11434.log`, `query` `.../serve-11435.log`) is
   read on from its saved byte offset (`gpu-health.json`): the first read takes only the last `gpu_log_baseline_mb`
   (32) and alerts on no old error; an offset past the end or a new inode (truncated, rotated) reads from 0; at most
   `gpu_log_read_max_mb` (64) a pass; a partial last line waits. The latest `load_tensors: offloaded X/Y layers to
   GPU` is kept per server. `gpu_expected` (`shared` true, `query` false: CPU-only by design, DEC-798) says where 0
   layers is an alert (set `gpu_expected: {"query": true}` in `config.json` once the query server runs on the GPU).
   **At once, once per incident**, one `<stamp>-gpu-alert.txt` item (`log:`, `GPU: <kinds>`,
   `status:`, the matching lines, the GPU's state, layers and holders at that moment) and a `gpu:` line in
   `inbox-stale.txt`, for a new `CUDA error` / `out of memory` / `cudaMalloc failed` line (errors more than
   `gpu_alert_gap_s`, default 0: every pass with new error lines alerts, DEC-1030) or a load with 0 layers, **or only
   part of them (0 < X < Y, DEC-1032: the rest runs on the CPU)**, where the GPU is expected (`GPU: 0 layers (shared)`,
   `GPU: partial 20/29 layers (shared)`; the incident lasts until a load with all its layers on the GPU; a short load
   already current at the first read alerts too).
   Status: `GPU: RTX 5070 Ti 9.7/15.9 GB, 24 %; holders: embedder shared (0), reranker (1); layers: shared 29/29,
   query cpu-only by design` and the last alert of the last 24 hours. On WSL nvidia-smi lists the reranker but not the
   llama-server (measured 2026-11-02): the embedder's GPU use shows in its layers.
5. **Status:** `status.json`, `status.txt` (`TICK FAILED` first when part of a pass failed). **One `Balance:` line
   (DEC-1032)**: the real busy CPU against its band (`cpu_band`, 14-18 of 20: below, within, above), memory available
   and the floor, the GPU used/total and free with the headroom, the embedders' layers and nvidia-smi's holders by
   kind, the embedders' states with their tasks a minute, the heavy slots by device, the lead cap from memory (its
   room and a lead's p95), the rerankers (how many, their RSS, the GPU slots held by their lock files); its record is
   `balance` in `status.json`.
6. **Escalation:** `inbox-stale.txt`, one line per cause, each written once per stall: `sentinel: ...` (first) while
   the sentinel is expected (`sentinel-expected` in the state folder) and its watch has written nothing parseable to
   `log/deadman.log` for 2 hours (DEC-1014 item 2: also one inbox item per silence; a malformed line falls back to
   the newest parseable one, none reads "unreadable"); `server: ...` while the shared embedding server is HUNG or NOT
   RUNNING, `server query: ...` likewise for the query server (4d); `gpu: ...` while the last GPU alert's item is
   unread or a 0-layer or partial-load incident holds (4f);
   `slot N pid P: ...` while a slot holder is IDLE (4e); `inbox: ...` while an inbox item is unread 30 minutes. The
   sentinel pushes it, keyed on its first 150 characters, so the short lines come first.

`peaks.json` (state folder) is refreshed at most hourly from `log/capacity/kinds.jsonl` and `log/lead-mem.jsonl`
(7 days). `config.json` (state folder) holds `cpu_margin`, `memory_rule`, `min_outside_samples` and the rest; every
key has its default in the code (`K` is kept for the record but no longer used).

## The Gov Load Balancer (owner, DEC-1039 (1b); DEC-1037 (4), DEC-1038 (4))
The arithmetic is `balancer.py` beside the dispatcher (pure functions, tested alone in `tests/unit/orchestration/
test_balancer.py`); the dispatcher reads the machine, the processes and the samples and calls it.

**The GPU rule.** The GPU's dedicated memory never spills into shared memory and never runs out into a CUDA crash:
the dedicated memory used (nvidia-smi) plus the running jobs' forecast stays at most total minus `gpu_headroom_mib`,
and the shared GPU memory in use stays under `gpu_shared_floor_mib`. The embedders come first, the rerankers second
(at most `rerank_gpu_slots` of them, the rest end, DEC-1033), even when that holds leads to two or three. Every pass
checks both: (1) **the budget**: this pass's nvidia-smi `memory.used` plus each running job's current-phase GPU peak
above what it holds (`GPU rule:` line; above it: one `gpu-alert` item at once, `GPU: GPU budget`, once per incident);
(2) **no spill**: WSL's shared GPU memory, read only through the Windows counters `\GPU Adapter Memory(*)\Dedicated
Usage` and `...\Shared Usage` (`powershell.exe -NoProfile -Command Get-Counter ...`, about 2 s, limit
`gpu_shared_timeout_s` 10; the adapter with the most dedicated memory in use is the card: a virtual display adapter has
none). A reading above `gpu_shared_floor_mib` (1/16 of the card: 1,019 MiB here; the desktop alone holds about 580 MiB,
measured 2026-11-02 19:40) is one `gpu-alert` item at once (`GPU: GPU spill`), once per incident (it ends on a reading
under the floor); an unreadable counter is a status line, never a failure. Both feed the quiet waiter like every
`gpu-alert`. T3 (below) makes a lasting budget breach an incident too.

**The phases of each kind of work, and how a running job's phase is found** (`find_jobs`, `tree_phase`). A job is a
lead (the launch form's marker in a lead worktree), a landing (`land.py`), a close (`close_build.py`), the nightly
(`nightly.sh`, `nightly_cron.sh`), each with its whole process tree; then each rebuild (`gov rebuild`, `-m
gov.cli.main rebuild`) and each heavy-slot run (its `flock ... gov-os-heavy-slot-N.lock`, or a heavy pytest outside a
slot) under none of them. A `heavy_slot.sh` or `rebuild_slot.sh` still waiting for its slot runs nothing and is no job
(its flock, once it has the slot, is). Its phase is read from what its tree runs, in this order: **a rebuild**
(`rebuild.embedding` while the shared embedder makes progress or has requests waiting, by the last pass's 4d state;
else `rebuild.lexical`); **a test run** (a heavy pytest or a heavy-slot lock in the tree: `test`); then, for a lead, **a
review** (a reviewer's session, `GOV_ROLE` independent-auditor / reviewer / independent-test-designer, in its tree:
`review`), **a retrieval** (`gov retrieve`, `gov check`, a retrieval module, a reranker: `retrieval`), **its start**
(its first `lead_start_s`, 600 s: `start`), else **building** (`build`); for the others `other`. A landing or a close
is `rebuild.*`, then `test`; a rebuild `rebuild.*`; a slot run `test`; the nightly `rebuild.*`, `test`. Each job's
measures this pass: its tree's cores, its RSS and the GPU reranker slots its tree holds (the `rerank_gpu_glob` lock
holders). **A process's cores** (review F1, F7): its utime + stime **with its reaped children's** (cutime + cstime, as
`kind_sampler.py` counts them: a test's short-lived programs) since the last pass (`jobs-prev.json`, which keeps each
process's CPU and parent); a process seen in the last pass and gone now was reaped, its whole CPU moved into its
parent's cutime this interval, so its last-seen CPU is taken off the delta of its nearest ancestor still running (only
its last interval counts, not its lifetime again); a process new since the last pass counts from 0; with no usable last
sample (a first or dry pass), its lifetime's average. A process, and a job, at most the machine's CPUs. `Jobs by phase:`
in the status.

**Each phase's measured peak on every resource** (`phase_peaks`, `phase-peaks.json`, refreshed every
`phase_refresh_s` 600 from the balance rows of the last `phase_window_h` 72): CPU cores busy, RAM, GPU memory and GPU
use, per kind and phase (`lead.retrieval`, `slot.test`, `landing.rebuild.embedding`, ...): a p95 once the phase has
`phase_min_samples` (30), before that the larger of today's figure (the floor) and the second-largest sample (one
sample alone never sets a peak for the window: review F1). GPU memory: a retrieval or review holds one reranker's
share, measured as (GPU used - the embedders' share) / the GPU slots held by reranker processes (a tool holding slots
beside the shared service, DEC-1043 item 2, holds no GPU memory), the embedders' share as the GPU used while no
reranker runs (each a p95; below 30 samples the largest, the safe side for pricing; floors 3,584 and 5,734 MiB). GPU use: the
pass's utilisation while the job is the only GPU-heavy one. RAM, while a phase's own samples are few, comes from the
7-day history the memory rule uses (`peaks.json`: a lead's p95 outside verification, 2.1 GB today; inside it 4.1 GB; a
slot run 1.9 GB; a rebuild 0.5 GB). Today's floors (2026-11-02):
| Phase | CPU cores | RAM | GPU memory | GPU use | Heavy | Source |
|---|---|---|---|---|---|---|
| start, retrieval, review | 2.0 | 2.1 GB | one reranker, 3.5 GiB | 10 % | GPU | LB-PLAN-gpu section 5; lead-mem p95 outside verification |
| build | 1.0 | 2.1 GB | 0 | 0 | none | kinds.jsonl `claude` p95 |
| test (a slot run) | 5.9 | 1.9 GB (a lead's tree 4.1 GB) | 0 | 0 | CPU | kinds.jsonl `test_run` per run p95 11-02; peaks.json `slot_run_kb` |
| rebuild.lexical | 2.5 | 0.5 GB | 0 | 0 | CPU | kinds.jsonl `rebuild` p95 11-02 |
| rebuild.embedding | 6.0 | 0.5 GB | 0 (the embedder is resident) | 65 % | GPU | LB-PLAN-gpu section 2a: 5.6 cores, 48-65 % |
| other | 1.0 | 0.5 GB | 0 | 0 | none | |

**The forecast before admission** (`forecast`). A start is admitted only if, for every resource, the running jobs'
current-phase peaks plus the newcomer's worst-phase peak stay within capacity: **CPU** busy cores + each job's peak
above what it uses now + the newcomer's ≤ the top of `cpu_band`; **RAM** available - each job's peak above its RSS now -
the newcomer's ≥ the floor; **GPU memory** used + each job's peak above what it holds + the newcomer's ≤ total -
`gpu_headroom_mib`, the rerankers' part at most the free GPU reranker slots' share. A lead's own admission covers the
phases it enters with no other gate (start, retrieval, building, review; and its entry's `first=<phase>` when given):
its test runs and rebuilds are admitted when they take their slot. The forecast applies after the rules of step 3
(`forecast_admission`, default true; false: shown, not applied), and the admission line names **the binding resource**
either way (`forecast admits (binding GPU: GPU memory 12.6 of 13.9 GB ...)`, `forecast refuses (GPU binding): ...`).
The `Forecast:` line gives the verdict for a lead, a slot grant and a rebuild; `forecast.json` (state) holds them for
`heavy_slot.sh` and `rebuild_slot.sh` to consult (a proposal: neither reads it yet, and `heavy_slot.sh` is another
engineer's).

**Pairing** (`pair`). When several starts are possible in a pass, the one whose heavy resource is the idler goes first:
the CPU's load is its forecast cores against the band's top, the GPU's the larger of its memory against its budget and
the running phases' GPU use. A lead starts GPU-heavy (its retrieval); a ready entry may name another first phase,
`<W2> <ticket> <brief> <log> first=test` (a lead resuming with its tests ready: CPU-heavy). So a GPU-heavy start goes
beside running test slots and a CPU-heavy one while the GPU embeds; equals keep the list's order. The others wait
`paired: ...` (still one start a pass).

**Limits from the machine** (`derive_limits`, DEC-1037 (4)). Detected each pass: logical CPUs (the affinity set),
physical cores (`/proc/cpuinfo`), RAM (MemTotal), the GPU's model and memory (the last nvidia-smi read; `machine.json`).
Every limit is a ratio of it, each giving today's number on this machine (20 CPUs, 24 GB, 16,303 MiB):
| Limit | Rule | Here |
|---|---|---|
| `cpu_band` | 0.70-0.90 of the CPUs | 14-18 |
| `cpu_margin` | 0.10 of the CPUs | 2 |
| heavy slots x workers | slots 0.15 of the CPUs; workers 0.90 of the CPUs / slots | 3 x 6 (heavy_slots.conf: shown beside, the owner's file) |
| `slots_gpu` / `slots_cpu` | the heavy slots / 2/3 of them | 3 / 2 |
| `gpu_headroom_mib` | 0.1256 of the GPU's memory | 2,048 |
| `rerank_gpu_slots` (proposed) | (GPU memory - the embedders' measured share - headroom) / one reranker's measured peak, at least 1 with a GPU | 2 |
| `gpu_shared_floor_mib` | 1/16 of the GPU's memory | 1,019 |
(32 CPUs, 64 GB, 24 GB GPU: 22-29, 3, 5 x 5, 5/3, 3,085, 4; 8 CPUs, 16 GB, no GPU: 6-7, 1, 1 x 7, 1/1, 0, 0.) An
explicit number in `config.json` still wins (the owner's override) and the `Limits:` line says so (`config.json
overrides: cpu_band [12, 16] (derived [14, 18])`). A GPU not read yet uses today's GPU figures. A machine change (CPUs,
cores, RAM by the half GB, the GPU) is one `Machine:` inbox item with the new limits. `limits.json` (state) holds them;
`gov_reranker_gpu_slot.py` reads its lock count from it when `GOV_RERANK_GPU_SLOTS` is unset (installing that copy is
the owner's ACT). **The reranker GPU slots are priced with exactly the count the installed hook enforces** (review
F2; EMG-lb2): the derived (or explicit) number is only the proposal written to `limits.json`; the forecast, the GPU
check and the rerankers' RAM reserve use the hook's count, neither fewer (a newcomer's reranker unpriced: fails open)
nor more (2026-11-02 23:01 and 23:04: a proposal of 3 to 5 left slots "free" while the hook's 2 were both held, and
the running jobs' reranker peaks were added on top of memory nvidia-smi already counted: two false GPU budget alerts)
(`hook_slots`: the installed copy that reads `limits.json` enforces the number there, 1 to 64, else 2; today's copy
its `GOV_RERANK_GPU_SLOTS` default, 2; no hook installed: 64, every newcomer's reranker priced). Every held slot counts as used, a slot held by the CTO's tool
beside the shared service (DEC-1043 item 2) too: a newcomer is priced a reranker only while a slot is free. The
`Limits:` line: `reranker GPU slots 2 priced (the installed hook's own default: 2; proposed 1)`. The servers' CPU sets
stay owner ACTs.

**The standing targets and their incidents** (DEC-1038 (4)). Each pass appends one row to `log/capacity/balance.jsonl`
(the readings, the jobs and phases, the targets, the forecast; renamed to `balance-<stamp>.jsonl` past
`balance_max_mb` 20, the newest 30 kept by `nightly/rotate.sh`). Targets, judged each pass: **T1** busy cores within
the band (above it, or below it while work waits refused by admission or a landing waits, is a breach); **T2** memory
available above the floor; **T3** GPU used at most total minus headroom; **T4** no timed-out embedding (a `[GIN]` line
with 499 or 5xx, or a time at or over `embed_client_timeout_s` 120, in either server's log since the last pass; and the
give-ups in `embed_retry_log`, W2-123's retry log, when configured); **T5** no cold rebuild (`tools/rebuild_counts.py`'s
rule on `log/seed.jsonl`'s new rebuild rows: a seed not used, or a semantic stage of `cold_rebuild_s` 1500 s or more);
**outside-slot** the "heavy steps outside a slot" finding. A breach lasting more than 15 minutes (`breach_open_s`; T1-T3
and outside-slot), or any T4/T5 event, opens **one incident**: one inbox item `incident-<target>-<HHMM>` (label
`Incident:`, it holds no lead) and the record `log/incidents/<date>-<HHMM>-<target>.md` (the readings, the running jobs
and their phases, the top processes by CPU and by memory grouped by tree and session, the events, and empty **Cause**
and **Fix** for the CTO). None again while it lasts (more events are added to the record); it closes when the target
has held for 15 minutes (`breach_close_s`), and the record says when. State: `targets.json`. Status: `Targets:` with
the incidents open. `tools/targets_report.py [--since] [--hours 07:30-02:00]` (scratch tools) gives the morning
package's shares (T1 at least 80 %; T2, T3 and outside-slot 100 %; T4, T5 zero events), the incidents with their causes
and the worst hour.

## The state folder
`ready.txt` and `land.txt` (the CTO's), `started.txt`, `land-done.txt`, `land-inflight.*`, `never-ran.txt`, `inbox/`
(the CTO moves read items to `inbox/read/`), `status.*`, `peaks.json`, `config.json`, `cpu_prev.json`, `gpu-health.json`,
`dispatch.log`, `tick.lock`, `loop.lock`, `loop.pid`, `OFF` (while present, every pass does nothing); the balancer's
`jobs-prev.json`, `phase-peaks.json`, `forecast.json`, `limits.json`, `machine.json`, `targets.json`.

## Running it
- The owner's crontab line (ACT): `* * * * * /usr/bin/bash /home/usain/Dynamic-Agentic-Engineering-OS/governance/project/orchestration/tools/dispatch/run_tick.sh`
- Without cron: `setsid -f bash /home/usain/Dynamic-Agentic-Engineering-OS/governance/project/orchestration/tools/dispatch/loop.sh`.
- Stop: `touch .gov-runtime/scratch/orchestrator/dispatch/OFF`. A dry pass: `bash run_tick.sh --dry`.
- Tests: `python3 -m pytest -q tests/unit/orchestration/test_dispatcher.py tests/unit/orchestration/test_balancer.py`
  (through the gate, `heavy_slot.sh`).
