# W2-112: one shared reranker for every session

Ticket DAEO-clon (W2-112), profile FULL. Sources: DEC-979 item 4 and P-RERANKER-1 (the design), DEC-374 (an absent
reranker keeps the fused order), DEC-397 and ADR-0002 §2 (the pinned model and environment), DEC-1031 item 2 and
DEC-1032 (the GPU budget), DEC-1033 (no reranker on the CPU; the slot rule), DEC-1034 (the settings, the paths, the
sandbox question).

## 1. Design

### The service (`src/gov/retrieval/rerank_service.py`)
- **One process per user.** Run by the reranker environment's interpreter
  (`~/.local/share/gov-os/reranker-venv/bin/python -I`), offline (`HF_HUB_OFFLINE=1`), with the same pinned
  `MODEL` and `REVISION` as the private worker, and the same model call: it loads the worker's own `load` and
  `scores` from `rerank_worker.py` (by file, never by putting `src/gov/retrieval/` on its path).
- **Socket.** `~/.cache/gov-os/rerank.sock`, bound under `umask 0177` (mode 0600); the folder is set to 0700 by
  every caller. No network port.
- **Start on demand, under a lock.** A search that cannot connect (no socket, or a refused one) tries
  `flock(LOCK_EX|LOCK_NB)` on `~/.cache/gov-os/rerank.lock`. The one that gets it removes a dead service's socket
  and starts the service, handing it the locked file descriptor (`pass_fds`); the service keeps it open for its
  whole life. So while a service lives (loading or serving) nobody can take the lock, and no second service starts:
  two searches starting together start one service, and a stale socket left by a killed service is replaced only
  after the kernel has released the dead process's lock. The service runs in its own session (`start_new_session`)
  so a search's end or a terminal's signal does not end it; its standard output and error go to
  `~/.cache/gov-os/rerank-service.log`.
- **The cold start.** The first search, and every search arriving while the model loads, waits for the socket,
  polling every 50 ms, for at most `START_S` = 60 s (a constant in `rerank.py`). The service binds its socket only
  after its model is loaded, so a socket that accepts is a loaded model. A service that ends during the load is
  seen at once (its exit), and the search falls back. Past 60 s the search falls back; the service keeps loading
  and serves later searches.
- **Requests.** One connection per request: the caller sends one JSON line `[query, [text, …]]` and reads one line,
  `{"scores": […], "device": …}` or `{"error": …, "device": …}`. An answer can never reach another caller: it is
  written on that caller's own connection. Requests are answered one at a time in the order the kernel queues the
  connections (first come, first served; backlog 128). No batching across callers, so every answer is exactly the
  model call a private reranker makes.
- **Cap.** `MAX_TEXTS` = 512 texts per request; more is refused with an error (the caller falls back). The cap is
  not 30: `gov retrieve` reranks its whole gathering, `(rounds + 1) × batch size` candidates (90 at radius 4 with
  the default batch of 10), while `fusion.search` sends at most `RERANK_TOP` = 30. A larger `--batch-size` with a
  deep radius can pass 512; such a search reranks through its private fallback.
- **Time limits.** Connecting and being accepted: `CONNECT_S` = 2 s (DEC-1034 T3). The answer: the request's time
  limit `GOV_RERANK_TIMEOUT_S` (default 30 s), counted from the request, so a request queued behind others is not
  pushed into fallback. The service gives a caller 10 s to send its request once connected.
- **Idle end.** No new connection for `GOV_RERANK_IDLE_S` seconds (default 900, read from the environment of the
  search that started it): it removes its socket, answers what was already queued, writes `END` to its log and
  ends; its lock is released with it.

### The device and the GPU budget (DEC-1032)
- Before the model loads, the service reads the GPU's free memory with the library that will hold it
  (`torch.cuda.mem_get_info()`, injectable as `choose_device(free=…)`).
- **Threshold:** the service's share, 3.5 GiB (the top of DEC-1032's 2.5 to 3.5 GB, as measured for one reranker in
  ACT-RERANK-GPU-SLOTS-1 §1), plus the 2 GiB headroom: **5.5 GiB free or more → the GPU (`cuda`)**; less, or no GPU
  to read (no CUDA, no torch, an error) → **the CPU**, named: the `READY` line in `rerank.log` says
  `device cpu`, every answer carries `"device": "cpu"`, the bundle's `rerank.device` is `cpu`, and an `ALERT` line
  (`the shared reranker runs on the CPU: …`) is written to `~/.cache/gov-os/rerank.log`.
- The embedder is already resident when the reading is taken (it is pinned in the shared Ollama server), so its
  memory is counted as used. Never more than one copy: the single-service lock.

### The stopgap's slots (DEC-1033)
- **The service** is its own script, never `rerank_worker.py` and never run through it, so the interim module
  `gov_reranker_gpu_slot` (loaded by the `.pth` in every Python of the reranker environment) leaves it untouched:
  it takes no slot. Its GPU use is bounded by its own free-memory check and the single-service lock.
- **The private worker** (`rerank_worker.py`) now carries the slot rule itself: before torch or the model loads it
  holds one of the `GOV_RERANK_GPU_SLOTS` (default 2) locks `gov-os-rerank-gpu-<n>.lock` in
  `GOV_RERANK_GPU_LOCK_DIR` (default `/tmp`) for its life, or waits up to `GOV_RERANK_GPU_WAIT_S` (default 20 s)
  and ends named (exit 75, `gov reranker: no GPU slot free within 20 s; this search goes without reranking`, no
  model line). A GPU already hidden (`CUDA_VISIBLE_DEVICES` -1 or empty) ends it named (exit 76). Only
  `GOV_RERANK_ALLOW_CPU=1` (tests and measurements) allows the CPU. While the interim module is installed it has
  already taken a slot in that process (`GOV_RERANK_GPU_SLOT`), and the worker takes nothing more; `rerank.py`
  never passes its own `GOV_RERANK_GPU_SLOT` on to a worker.

### The fallbacks (DEC-374, DEC-1033, DEC-1034 item 4)
`rerank.default_reranker()` returns a scorer that, for each search:
1. asks the service (connecting, starting it if needed, within the bounds above);
2. if the service cannot be reached, started, or answered in time, or answers with an error: a **private
   reranker** (`rerank_worker.py`, through the slot rule above), started once per process as before;
3. if that ends without the model (no slot, the GPU hidden, no snapshot, a library absent): **the fused order is
   kept**, no candidate carries a score (`merge.reranked` false), and the reason is recorded.

A session that cannot create or reach a Unix socket (the launch sandbox gives `EPERM`) fails step 1 at once and
goes to step 2, without an error. Each fallback appends one line to `~/.cache/gov-os/rerank.log`:
`<time>\tFALLBACK\t<why the service did not answer>\t<private | unavailable: <why>>`; a session that cannot write
there still searches. Without a reranker environment at all, nothing is started and nothing is logged (today's
DEC-374 case).

### What the bundle and `gov status` show
- `gov retrieve --json` carries `rerank`: `{"by": "service" | "private" | "unavailable" | "given", "device": …,
  "reason": …}` (`by` `unavailable` with its reason when the order is unranked; `device` `cuda`/`cpu` from the
  service, the worker's torch device for a private reranker). `merge.reranked` is unchanged.
- `gov status` carries `reranker`: `{"fallbacks": n, "cpu_alerts": m, "log": path}`, read from the log by
  `rerank.status()` (`rerank.fallback_count()` gives the count alone; `rerank.last_outcome()` the last rerank of the
  calling thread).

## 2. Builder evidence

`tests/unit/retrieval/test_w2_112_shared_reranker.py` (21 tests, hermetic: a throwaway venv with a stand-in `torch`
and `sentence_transformers` at the environment's path in a temporary HOME; the slot locks in a temporary folder;
every process it starts is marked, ended and checked gone): eight searches starting together start one service;
20 concurrent callers each get their own scores from that one process; the socket 0600 and its folder 0700; ties
keep the given order and the scores equal a private reranker's; the idle end removes the socket; the CPU choice
with too little free GPU memory and with none to read (named, alerted); a killed service replaced by the next
search; a service killed mid-request, one that does not answer in time, a request over the cap, a service that
cannot start (each → private, logged); neither (→ unranked, named); no GPU slot (→ unranked, no model on any
device); a sandbox that refuses the socket (→ private at once); the private worker's slot rule; `gov status`'s
count; the bundle's `rerank` entry through `retrieve`.

## 3. The measurement the lead runs (on the real GPU, after this commit)

All with the real environment, the embedder pinned in the shared Ollama server, and `GOV_RERANK_ALLOW_CPU` unset.
1. **Memory with 10 concurrent searches, before and after.** Before: the commit before this one (each search's
   process starts a private reranker). After: this commit. For each, 10 `gov retrieve "<question>" --json`
   processes started together (questions from `fixtures/evaluation/memory-retrieval/visible/`), sampling every
   0.5 s the RSS of every `rerank_worker.py` and `rerank_service.py` process (`ps -o rss,args`) and the machine's
   used memory (`free -b`); report the peak and the mean, and the count of reranker processes (today: up to 9,
   9.4 GiB at peak, CAPACITY-1).
2. **The GPU's memory under 20 concurrent searches.** `nvidia-smi --query-gpu=memory.used,memory.total
   --format=csv -l 1` and `nvidia-smi --query-compute-apps=pid,used_memory --format=csv` during 20 searches started
   together; expected: the embedder (about 3.5 GB), one service (about 2.5 to 3.5 GB), no private reranker, at
   least 2 GB free; the service's `READY` line says `device cuda`.
3. **The searches' times.** The wall time of each of those searches (first, cold: including the service's load; then
   warm), p50 and p95, before and after.
4. **The same answers.** For each of the 20 visible questions, the bundle's evidence order and every
   `rerank_score` from the service against a private reranker on the same device (the service stopped, or
   `rerank._started(...)` called directly): equal within float rounding (the service makes the same `predict` call;
   both are rounded through JSON as `float`). After W2-61h, the 48.
5. **The fallback count.** `gov status`'s `reranker.fallbacks` before and after the run (expected unchanged on a
   healthy run), and `rerank.log` read for `ALERT` lines (expected none).

## 4. Measured

The figures come from the lead's run on the real GPU after this commit; the lead gives them to the next batch. None
are recorded here by the engineer, who ran no real model and touched no GPU.

## 5. ACT: retiring the stopgap (ACT-RERANK-GPU-SLOTS-1)

For the owner's operator, in a plain terminal, **only after W2-112 has merged** (the private worker then carries the
slot rule itself). It removes two files from your reranker environment under `~/.local/share`; no repository commit.

1. Remove the module and its `.pth`:
   ```
   V=$HOME/.local/share/gov-os/reranker-venv
   SP=$($V/bin/python -I -c "import sysconfig; print(sysconfig.get_paths()['purelib'])")
   rm "$SP/gov-reranker-gpu-slot.pth" "$SP/gov_reranker_gpu_slot.py"
   ```
2. The check:
   ```
   $V/bin/python -I -c "import importlib.util, os; print(importlib.util.find_spec('gov_reranker_gpu_slot'), os.environ.get('GOV_RERANK_GPU_SLOT'), os.environ.get('CUDA_VISIBLE_DEVICES'))"
   ```
   prints `None None None`.
3. The lock files `/tmp/gov-os-rerank-gpu-0.lock` and `/tmp/gov-os-rerank-gpu-1.lock` may be removed once
   `fuser /tmp/gov-os-rerank-gpu-0.lock /tmp/gov-os-rerank-gpu-1.lock` shows no process holds them (they are
   recreated by the next private worker that needs one).
4. **Undo:** the commands of ACT-RERANK-GPU-SLOTS-1 §3, with the module of ACT-RERANK-WAIT-1
   (`governance/project/orchestration/tools/gov_reranker_gpu_slot.py`).

**Why it is safe after this ticket:** the shared service never took a slot (it is not `rerank_worker.py`); the
private worker, the only process the module acted on, now holds the same slot locks (same names, same folder, same
settings `GOV_RERANK_GPU_SLOTS`, `GOV_RERANK_GPU_LOCK_DIR`, `GOV_RERANK_GPU_WAIT_S`, the same 20 s wait, the same
named end with exit 75 and 76, the same `GOV_RERANK_ALLOW_CPU=1` opt-out) before torch or the model loads. With the
module gone the worker takes the slot itself instead of finding `GOV_RERANK_GPU_SLOT` set, so removing it changes
nothing in behaviour.
