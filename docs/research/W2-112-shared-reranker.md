# W2-112: one shared reranker for every session

Ticket DAEO-clon (W2-112), profile FULL. Sources: DEC-979 item 4 and P-RERANKER-1 (the design), DEC-374 (an absent
reranker keeps the fused order), DEC-397 and ADR-0002 §2 (the pinned model and environment), DEC-1031 item 2 and
DEC-1032 (the GPU budget), DEC-1033 (no reranker on the CPU; the slot rule), DEC-1034 (the settings, the paths, the
sandbox question), DEC-1036 (T5 (b): no service below its GPU share; T6 (b): the service holds a GPU slot).

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

### The GPU slot, then the GPU share (DEC-1032, DEC-1036 T5 and T6)
The service starts in this order, before torch's free-memory reading and before the model loads:
1. **A GPU slot (T6 (b)).** It takes one of the two slots the private rerankers use (the same locks
   `gov-os-rerank-gpu-<n>.lock` in `GOV_RERANK_GPU_LOCK_DIR`, the same `GOV_RERANK_GPU_SLOTS`, the same wait
   `GOV_RERANK_GPU_WAIT_S`, default 20 s, through the worker's own `take_slot`) and holds it for its life. So at most
   one private reranker runs beside it: the embedder (about 3.5 GB), the service and one private reranker (about
   3.5 GiB each), about 10.5 GB of the card's 16, with DEC-1032's 2 GB headroom kept. Without a slot within the
   wait it ends named (exit 75; exit 76 when the GPU is hidden, whatever `GOV_RERANK_ALLOW_CPU` says).
2. **Its share of the GPU's memory (T5 (b)).** Holding the slot, it reads the GPU's free memory with the library
   that will hold it (`torch.cuda.mem_get_info()`, injectable as `gpu_short(free=…)`). **Threshold:** the share,
   3.5 GiB (the top of DEC-1032's 2.5 to 3.5 GB, as measured for one reranker in ACT-RERANK-GPU-SLOTS-1 §1), plus
   the 2 GiB headroom: **5.5 GiB free or more → it loads on the GPU**; less, or no GPU to read (no CUDA, no torch,
   an error) → **it does not start** (exit 77). The embedder is already resident when the reading is taken, so its
   memory is counted as used.

**No reranker on the CPU anywhere (DEC-1033):** the service has no CPU path. Each refusal is a `REFUSED` line in
`~/.cache/gov-os/rerank.log` (`the shared reranker does not start: <reason>`), counted by `gov status`
(`reranker.service_refusals`); the search that started it names the reason in its bundle (`rerank.reason`: `the
service ended before it listened (no GPU slot freed within its wait | the GPU is hidden from it | the GPU has too
little free memory for its share)`) and falls back: to a private reranker, which waits for a slot in turn, else the
order is kept, unranked and named. Searches that were waiting for that service do not start another one (it would
meet the same refusal): they fall back at once. Never more than one copy on the GPU: the single-service lock.

**The cold start's bound still holds:** the starting search waits at most `START_S` = 60 s in all; the slot wait
(20 s by default) comes first, so a service without a slot ends within it and the search falls back well inside
the bound; with a slot, the reading is immediate and the load has the rest.

### The stopgap's slots (DEC-1033, DEC-1036 T6)
- **The service** is its own script, never `rerank_worker.py` and never run through it, so the interim module
  `gov_reranker_gpu_slot` (loaded by the `.pth` in every Python of the reranker environment) leaves it untouched;
  **it takes a slot itself** with the same rule (above). This reverses the first design's "the service takes no
  slot" (DEC-1036 T6 (b)). `rerank.py` never passes its own `GOV_RERANK_GPU_SLOT` on to it.
- **The private worker** (`rerank_worker.py`) now carries the slot rule itself: before torch or the model loads it
  holds one of the `GOV_RERANK_GPU_SLOTS` (default 2) locks `gov-os-rerank-gpu-<n>.lock` in
  `GOV_RERANK_GPU_LOCK_DIR` (default `/tmp`) for its life, or waits up to `GOV_RERANK_GPU_WAIT_S` (default 20 s)
  and ends named (exit 75, `gov reranker: no GPU slot free within 20 s; this search goes without reranking`, no
  model line). A GPU already hidden (`CUDA_VISIBLE_DEVICES` -1 or empty) ends it named (exit 76); so does a
  machine where torch sees no GPU at all (exit 78, checked after the slot and before the model loads). Only
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
  "reason": …}` (`by` `unavailable` with its reason when the order is unranked; `device` the torch device the model
  sits on, `cuda:0` for the service; `reason` why the service did not answer, when it fell back).
  `merge.reranked` is unchanged.
- `gov status` carries `reranker`: `{"fallbacks": n, "service_refusals": m, "log": path}`, read from the log by
  `rerank.status()` (`rerank.fallback_count()` gives the count alone; `rerank.last_outcome()` the last rerank of the
  calling thread).

## 2. Builder evidence

`tests/unit/retrieval/test_w2_112_shared_reranker.py` (26 tests, hermetic: a throwaway venv with a stand-in `torch`
and `sentence_transformers` at the environment's path in a temporary HOME; the slot locks in a temporary folder;
every process it starts is marked, ended and checked gone): eight searches starting together start one service;
20 concurrent callers each get their own scores from that one process; the socket 0600 and its folder 0700; ties
keep the given order and the scores equal a private reranker's; the idle end removes the socket; the service holds
one GPU slot for its life and frees it when it dies; it waits for a slot; without one it ends named, the searches
waiting for it start no other and go on unranked, and no model loads on any device; below its GPU share, with no
GPU to read, or with the GPU hidden (also with `GOV_RERANK_ALLOW_CPU=1`), it does not start (REFUSED, named) and
the search falls back; a killed service replaced by the next search; a service killed mid-request, one that does
not answer in time, a request over the cap, a service that cannot load (each → private, logged); neither
(→ unranked, named); with no GPU at all, neither the service nor the private worker loads a model (→ unranked,
named); SIGTERM removes the service's socket; a sandbox that refuses the socket (→ private at once); the private
worker's slot rule and its named end without a GPU (exit 78); `gov status`'s counts; the bundle's `rerank` entry
through `retrieve`.

## 3. The measurement, as the lead ran it

On the real machine (one RTX 5070 Ti, 16,303 MiB), with the real reranker environment, on commit `775c58eda031`,
2026-11-02 14:11 UTC, `GOV_RERANK_ALLOW_CPU` unset. **The shared Ollama servers were never asked:** no `gov retrieve`
search was sent. Each measured "search" is a process that reranks one visible question's candidates through
`gov.retrieval.rerank.rerank()`. The candidates are the lexical route's first 30 chunks for that question's text, in
the form a search gives the reranker (`[path: …]` and the first 500 characters). The questions are the 20 of
`fixtures/evaluation/memory-retrieval/visible/` (`q01` to `q20`); Q12 has 7 candidates, the others 30. A sampler read
`nvidia-smi`'s `memory.used`, the RSS of every reranker process and `free -b` every 0.25 s.
1. **Cold:** one search, which starts the service and waits for its model to load.
2. **20 concurrent searches, warm:** the 20 questions started together against the loaded service.
3. **10 concurrent searches, warm:** 10 of the questions started together.
4. **Before (a private reranker per search):** one private reranker (`rerank_worker.py`) started directly, its load
   time, its time per question, its RSS and its GPU memory.
5. **The same answers:** for each of the 20 questions, the service's scores against one private reranker's on the
   same device.
6. **The stop:** the service stopped with SIGTERM; the GPU's memory, the processes left, and `gov status`'s reranker
   part read afterwards.

## 4. Measured

The lead's run, by the method above (the engineer ran no real model and touched no GPU).

- **Before the run:** the GPU held 3,171 MiB of 16,303 MiB (the embedder, pinned in the shared Ollama server); RAM
  used 6.32 GiB; no GPU slot held.
- **Cold (one search, which started the service and loaded the model):** 7.56 s wall; the service answered on
  `cuda:0`.
- **20 concurrent searches, warm:** all 20 answered by the one service process on `cuda:0`, none fell back. Wall
  p50 2.32 s, p95 3.82 s, max 4.01 s (the whole phase 4.12 s). GPU memory used at peak 6,429 MiB: the embedder and
  the service, the service's one copy about 3.26 GB, 9.9 GB free. The service's RSS 1.68 GiB; one reranker process
  of this tree.
- **10 concurrent searches, warm:** all 10 answered by the service on `cuda:0`. Wall p50 1.09 s, p95 2.13 s. GPU
  peak 6,428 MiB. The service's RSS 1.69 GiB (its peak over the cold and warm phases: 1.79 GiB).
- **Before (a private reranker per search):** one private reranker started directly took 4.18 s to load on
  `cuda:0`, 0.20 s per question (p50), about 1.7 GiB RSS and about 3.3 GB of GPU memory (GPU peak 9,694 MiB with the
  service and one private reranker). With 10 searches at once that was up to 10 such processes; CAPACITY-1
  measured 9 at once, 9.4 GiB at peak. Under the emergency interim (DEC-1033) at most two run on the GPU and the
  others go unranked after 20 s. **After: one process, 1.7 to 1.8 GiB, whatever the number of searches.**
- **The same answers:** for each of the 20 questions, the service's scores against one private reranker's on the
  same device (`cuda:0`): the order identical in 20 of 20, the largest score difference 0.
- **The stop:** the service ended on SIGTERM; the GPU's memory came back to 3,163 MiB (released); no reranker
  process of this tree was left. `gov status`'s reranker part afterwards: 0 fallbacks, 0 service refusals.
- **A note:** on `775c58eda031`, SIGTERM left the service's socket file (it was removed only on the idle end); a later
  search then started a new service over the stale socket. Since the next commit, the service removes its socket
  on SIGTERM too (a signal handler; builder test `test_a_service_stopped_with_sigterm_removes_its_socket`).
- **After W2-61h:** the 48 questions, not yet measured.

## 5. ACT: retiring the stopgap (ACT-RERANK-GPU-SLOTS-1)

For the owner's operator, in a plain terminal. It removes two files from your reranker environment under
`~/.local/share`; no repository commit. **W2-112's merge is not enough.** Only a `rerank_worker.py` of W2-112 or later
carries the slot rule itself; every older one (the installed, pinned `gov` until it is re-pinned, and any checkout,
clone or worktree whose branch predates W2-112) relies on the module alone and, without it, loads its model on the GPU
beside the two held slots: a third copy, the crash state DEC-1031 records. Until the precondition below holds, **the
module stays**: beside W2-112's worker it is harmless (it has already taken the slot in that process, and the worker
then takes nothing more).

**Precondition (both checks must pass):**
1. The installed `gov` carries the worker's own slot rule (in practice after a re-pin of `~/.local/bin/gov` to a
   release that carries W2-112's worker). This prints the worker's path and a count of `1` or more; `0` means it is older:
   ```
   P=$(dirname "$(readlink -f "$HOME/.local/bin/gov")")
   F=$("$P/python" -I -c "import importlib.util as u; print(u.find_spec('gov.retrieval.rerank_worker').origin)")
   echo "$F"; grep -c 'def take_slot' "$F"
   ```
   (On 2026-11-02 at 19:3x the live pin `pin-a7182f6c`, the emergency re-pin, printed `0`: it does not yet.)
2. No tree on the machine runs an older worker: the main checkout, the merge queue's clone, every worktree, any
   other copy or installed environment. This lists every `rerank_worker.py` under your home and `/tmp` that lacks
   the rule; it must print nothing:
   ```
   find "$HOME" /tmp -path '*/gov/retrieval/rerank_worker.py' 2>/dev/null | while read -r f; do grep -q 'def take_slot' "$f" || echo "OLD $f"; done
   ```
   Each `OLD` line is a tree to bring up to date (its branch merged with a main that holds W2-112) or remove first.

**Then, and only then:**
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
3. **Undo:** the commands of ACT-RERANK-GPU-SLOTS-1 §3, with the module of ACT-RERANK-WAIT-1
   (`governance/project/orchestration/tools/gov_reranker_gpu_slot.py`).

**Never remove the slot lock files** `/tmp/gov-os-rerank-gpu-0.lock` and `/tmp/gov-os-rerank-gpu-1.lock` (nor any
`gov-os-rerank-gpu-<n>.lock` in `GOV_RERANK_GPU_LOCK_DIR`), whether or not a process holds them. They are empty and
must stay. A slot is a lock on that file's inode: removing a file a reranker holds lets the next reranker create a new
file at the same name and lock it, so it loads beside the holder (the review saw three rerankers on two slots); and
`fuser` cannot rule that out, since a reranker may take the lock just after it looks.

**Why it is safe once the precondition holds:** the module never acted on the shared service (it is not
`rerank_worker.py`), which takes its slot with its own code (DEC-1036 T6). The private worker, the only process the
module acted on, then carries in every tree that can start one the same slot rule (the same lock files in the same
folder, the same settings `GOV_RERANK_GPU_SLOTS`, `GOV_RERANK_GPU_LOCK_DIR`, `GOV_RERANK_GPU_WAIT_S`, the same 20 s
wait, the same named end with exit 75 and 76, the same `GOV_RERANK_ALLOW_CPU=1` opt-out) before torch or the model
loads. With the module gone such a worker takes the slot itself instead of finding `GOV_RERANK_GPU_SLOT` set, so
removing it changes nothing in behaviour. Before the precondition holds that is false: an older worker, without the
module, takes no slot at all. Rerankers already running when the module is removed keep the slot they took (their lock
stays open for their life).
