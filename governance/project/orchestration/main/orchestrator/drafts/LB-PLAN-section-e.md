## e. Measured: the embedding servers and the rerankers, from the history (the live hour confirms it)

**Sources:** the servers' own logs (`/home/usain/.ollama/serve-11434.log`, `serve-11435.log`, since their restart at
21:51 on 2026-11-01: every `/api/embed` request with its latency and status); the capacity sampler
(`log/capacity/kinds.jsonl`, 2,513 samples since 2026-10-31 14:17, per kind of process: count, cores, memory); the
leads' memory sampler (`log/lead-mem.jsonl`, 5,025 samples since 2026-10-29); the dispatcher's peaks
(`dispatch/peaks.json`, seven days); `nvidia-smi`; the servers' environment and CPU affinity (`/proc`).

### The two embedding servers
| | shared (11434) | query (11435) |
|---|---|---|
| Started | 2026-11-01 21:51 (after the hang) | same night |
| CPUs | affinity 12-19, nice 10 | affinity **12-19 too**, nice 10 |
| GPU | allowed; **29/29 layers on the GPU until CUDA crashed at 02:36 and 04:31; reloaded at 04:33 with 1.9 GiB free: 0/29 layers, on the CPU since** (the 1.42 GB `size_vram` is buffers, not layers) | switched off (`CUDA_VISIBLE_DEVICES=-1`, DEC-798) |
| Requests, 11-01 from 21:51 | 7,771; p50 1.5 s, p95 3.1 s, max 67 s; 3 errors | 284; p50 28 s, p95 71 s; 14 errors |
| Requests, 11-02 to 11:05 | 8,826; p50 2.1 s, **p95 45 s**, max 120 s; **290 errors**; 766 over 30 s | 1,897; **p50 53 s, p95 120 s**; **328 errors**; 1,551 over 30 s |
| Summed request time, 11-02 | 19.4 h in 11 h (requests queue behind one another) | 31.9 h in 11 h |

- **The night's root cause:** on the GPU the shared runner embedded about 44.8 chunks/s (11-01 22:00); on the CPU since
  04:33, 0.4 to 1.4 chunks/s (about 30 to 100 times slower). Every landing attempt since 04:37 died on its first
  120 s request (`serve-11434.log` lines 3232500, 3421608: `CUDA error: unknown error`; 3421861: free 1.9 GiB;
  3422346: `offloaded 0/29 layers to GPU`).
- **One request at a time** (W2-123: Ollama runs this model at `-np 1`, whatever it is told): every client queues
  behind the one being served; the summed time above twice the wall time is the queue.
- **The two servers share the same 8 CPUs** (12-19): a rebuild's batch on the shared server slows every query on the
  query server, and the reverse.
- **A query embedding should take well under a second;** today its median is 53 s and its p95 hits the 120 s limit:
  `gov check`'s retrieval checks, `gov retrieve` and the memory measure all wait on it. W2-92's lead found the
  retrieval regression at hit@5 0 % "at the pre-ticket base too" for this reason.
- **The dispatcher's health probe** times out at 30 s; with p95 at 45 s on the shared server it flagged "hung" about
  15 times on 11-02 while the server was busy, holding lead starts each time.
- **Errors:** 290 + 328 on 11-02 are timeouts at 120 s (the client's `TIMEOUT_S`) or the probe's 30 s; six landing
  attempts ended `semantic not_recreated` on them.

### The rerankers (Qwen3-Reranker-0.6B, one process per searching session, on the CPU)
| day | processes at once, p95 | memory, p95 / max |
|---|---|---|
| 10-31 | 6 | 6.7 / 9.4 GB |
| 11-01 | 9 | 7.5 / 10.4 GB |
| 11-02 | 12 | **11.4 / 13.7 GB** |
- The seven-day peaks (`dispatch/peaks.json`): the rerankers' memory p95 9.9 GB, max 14.3 GB, against 24 GB for the
  whole of WSL. They use little CPU (p95 1.4 cores) but hold the most memory of any kind of process: more than the
  test runs (p95 about 3-5 GB) or all Claude sessions together (p95 1.5-3.2 GB). This is what keeps the gate's
  memory check shut while the CPUs idle.

### The machine
| day | busy cores p50 / p95 (of 20) | leads at once, mean / max | memory available, min |
|---|---|---|---|
| 10-31 | 17.1 / 19.4 | 4.5 / 8 | 3.6 GB |
| 11-01 | 11.6 / 18.9 | 3.6 / 8 | 4.3 GB |
| 11-02 | 12.3 / 18.5 | 1.9 / 5 | 3.4 GB |
- The embedding servers' CPU: p95 8.0 to 9.2 cores (their cap is 8).
- **The GPU:** NVIDIA GeForce RTX 5070 Ti, 16,303 MiB; about 2.6 GB in use (the shared server's partial load);
  utilisation about 1 % in the samples taken (13 % mean over a 30 s test at 10:56). Nearly all of it is idle.

### The live hour (10:57 to 11:57) confirms this
[to be filled from `log/lb/hour-20261102.summary.json`]
