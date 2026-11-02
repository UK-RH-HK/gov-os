# LB-PLAN section c — embedding and reranking on the GPU (measured)

- **Author:** research session (read-only on the repository; no tracked file edited, nothing installed, nothing committed).
- **Date:** 2026-11-02, 11:05 to about 12:05 UTC.
- **Scratch:** `/tmp/tmp.chzdEiVAhl` (scripts in `scripts/`, raw figures in `data/bench.jsonl`, `data/facet.json`,
  `data/rerank-cuda.json`, measure records in `measure-gpu/` and `measure-cpu/`, server logs in `logs/`).
- **Rules kept:** the shared servers (:11434, :11435) were not stopped, restarted, reconfigured or loaded by me; I sent
  them read-only probes only (`/api/ps` on :11434, twice). Every experiment ran on private servers (:11446 Ollama
  on the GPU, :11447 Ollama on the CPU only, :11448 the bundled `llama-server` on the GPU), each stopped at the end.
  Only the visible half of `memory-retrieval` was used.
- **Load:** the 1-minute load was 10.5 to 19 during the GPU throughput runs and **29 to 65** from about 11:16
  onwards (other sessions: up to 7 gitleaks at once, the busy query runner on :11435). Every figure after 11:16 was taken
  on a crowded machine; the CPU figures especially are worse than a quiet machine would give (marked).

## 0. The GPU today

| | |
|---|---|
| GPU | NVIDIA GeForce RTX 5070 Ti, 16,303 MiB (16,302 MiB as llama.cpp reports it) |
| Driver | 610.88 (KMD), nvidia-smi 610.57.01, CUDA UMD 13.3; Ollama's runner uses its bundled `cuda_v13` backend |
| Ollama | 0.35.0, runner `llama-server` (llama.cpp build 161755f29) |
| Reranker env | `~/.local/share/gov-os/reranker-venv/bin/python` → `/usr/bin/python3`; torch 2.14.1+cu130, CUDA available: **yes**; sentence-transformers 6.1.0; model loads as **bfloat16** |
| In use at 11:05 | 2,621 MiB, GPU 1 %: about 1.35 GiB is the shared runner's compute buffer (0 layers on the GPU, see §1), the rest the Windows desktop. WSL's nvidia-smi lists no processes, so per-process use is read from the runners' own logs. |
| In use at 11:20 to 11:45 | 5.0 to 13.4 GiB, swinging with other sessions' rerankers (one `rerank_worker` of `gov-os-worktrees/W2-61h` was resident throughout) |
| At 11:15 | the shared runner was reloaded by the CTO/owner with **29/29 layers on the GPU** (`/api/ps`: `size_vram` = `size` = 2,370,652,077) |

## 1. Why the GPU was idle (plain words)

1. **The shared runner was not on the GPU at all.** From 2026-11-01 23:56 it ran with `offloaded 29/29 layers to
   GPU`. The runner crashed twice with `CUDA error: unknown error` in `cudaMemcpyAsync` (device to host, reading a
   result back) at **02:36:44** and **04:30:57** (`serve-11434.log` lines 3232500 and 3421608; `signal: aborted (core
   dumped)`, every in-flight `/api/embed` got HTTP 400). At the reload at 04:33:41, Ollama's GPU discovery timed out
   ("GPU discovery watchdog timed out … unable to refresh free memory, using old values") and llama.cpp saw only
   **1,977 MiB free of 16,302**. Its fitting step stepped the layers down 29 → 0 and loaded **0/29 layers** to the
   GPU; only a 1,353 MiB compute buffer went there, which is the `size_vram` of about 1.42 GB that `/api/ps` showed.
   The weights (604 MiB) and KV cache (448 MiB) were on the CPU, so the model ran on the CPU while holding GPU memory.
2. **Why the GPU was full at 04:33 and why CUDA failed (the likely cause; inferred, not proven).** The log shows
   12,063 to 12,971 MiB "unaccounted" on the device at the reload, held by other processes. The only other GPU users
   on this machine are the rerankers: `rerank_worker.py` leaves the device to the library ("the GPU when there is
   one"), and the environment's torch has CUDA, so **every search's private reranker loads onto the GPU**. I measured one
   at **2.8 GiB allocated / 3.2 GiB reserved** by torch (bf16, 30 candidates of 512 characters) plus the CUDA
   context: about **3.5 GiB per reranker process** (§5). Four rerankers fill the card; W2-112's ticket counts up to 9
   at once (9.4 GiB at peak) and the CTO counts 12 to 15 today. The kernel log has WSL GPU-paravirtualisation
   allocation failures, `dxgkio_create_allocation: Ioctl failed: -12` (ENOMEM) with `get_user_pages_fast failed`,
   1,440 `dxg` lines in all. (dmesg's clock in WSL cannot be mapped reliably to wall time here, so I cannot tie a dxg
   line to 02:36 or 04:30.) An "unknown error" on a copy, rather than a clean out-of-memory, is how a CUDA context
   on WSL usually fails when the host side of the paravirtualised allocation fails. So the likely cause is GPU memory
   (and host pinned memory) exhausted by many concurrent rerankers on WSL. That is inferred: there is no OOM line
   in the runner's log.
3. **Even on the GPU, Ollama keeps it under half busy.** Ollama 0.35.0 starts this model's runner with `-np 1`
   whatever `OLLAMA_NUM_PARALLEL` says (W2-123 figure 1; confirmed again on my :11446: `OLLAMA_NUM_PARALLEL:1` in
   the default config, `runner.parallel=1` ×4,182 log lines, `-np 1` on the runner's command line). With one slot,
   llama-server takes the inputs of an `/api/embed` request **one after another as separate tasks** (the shared
   log shows one "new prompt … n_ctx_slot = 4096" per chunk). Each forward pass is one chunk of 2 to 500 tokens,
   too small to fill the GPU, and the Go server, tokenisation and per-task bookkeeping keep about 5 CPU cores busy.
   So batching 32 per request (`semantic.BATCH`) saves HTTP round trips but not GPU passes. Timeouts:
   `semantic.TIMEOUT_S` = 120 s per request; the rebuild sends one request at a time (no client concurrency); the
   query side sends one request of two texts `[INSTRUCTION, INSTRUCTION+question]` and refuses a vector unless
   `/api/ps` reports `size_vram == 0` (DEC-798).
4. **On the CPU, the shared rebuild path is very slow.** On my CPU-only server (6 cores, `taskset 6-11`, load 29 to
   36), single-chunk requests took **p50 3.28 s, p95 3.65 s, 0.29 chunks/s** (108 requests, from its own log;
   about 6.9 cores busy). The CTO's 0.4 to 1.4 chunks/s for the shared runner on the CPU since 04:33 is in line with
   this.

## 2. Rebuild embedding on the GPU

512 real chunks, each its first 512 characters (as `_build` sends them), taken read-only from the integration store
`~/gov-os-worktrees/W2-00-store/.gov-runtime/store.db` (50,740 embedded chunks; every ~85th chunk in index order;
19 that contained words like key, token or password were skipped). Client pinned to 2 cores; servers pinned to CPUs
0-5. "GPU %" is nvidia-smi's utilisation sampled every 0.2 s, mean (max); "VRAM" is the card's total during the
run (2,621 MiB before, so my server ≈ total − 2,621); "cores" is the server's and runner's CPU time over the wall time.

### 2a. Ollama with the GPU visible (defaults; `-np 1`; 29/29 layers; 2.37 GB VRAM by `/api/ps`)

| inputs per request | requests at once | chunks/s | request p50 s | request p95 s | GPU % mean (max) | VRAM total MiB | cores |
|---|---|---|---|---|---|---|---|
| 1 | 1 | 47.7 | 0.020 | 0.033 | 36.5 (59) | 5,112 | 5.08 |
| 1 | 2 | 54.2 | 0.036 | 0.053 | 40.3 (66) | 5,112 | 4.91 |
| 1 | 4 | 53.2 | 0.074 | 0.100 | 48.6 (65) | 5,112 | 5.01 |
| 8 | 1 | 54.5 | 0.142 | 0.200 | 50.6 (69) | 5,113 | 5.16 |
| 8 | 2 | 56.7 | 0.272 | 0.363 | 43.3 (71) | 5,113 | 4.92 |
| 8 | 4 | 58.7 | 0.542 | 0.619 | 42.3 (59) | 5,113 | 5.29 |
| **32** | **1** | **61.7** | **0.486** | **0.658** | 48.4 (66) | 5,114 | 5.63 |
| 32 | 2 | 54.8 | 1.132 | 1.424 | 60.8 (70) | 5,114 | 5.03 |
| 32 | 4 | 61.6 | 1.902 | 2.262 | 54.8 (73) | 5,117 | 5.55 |
| 128 | 1 | 53.6 | 2.369 | 2.622 | 55.3 (65) | 5,122 | 5.23 |
| 128 | 2 | 55.7 | 4.000 | 5.189 | 54.5 (67) | 5,121 | 5.06 |
| 128 | 4 | 64.9 | 7.876 | 7.891 | 47.0 (67) | 5,125 | 5.89 |

Cold load to the first vector: 1.83 s. Every setting gives 48 to 65 chunks/s: the one slot is the limit, not the
batch or the client concurrency. `OLLAMA_NUM_PARALLEL` is not honoured for this model (above); I did not repeat W2-123's
sweep of 2/4/8, which found the same.

### 2b. The bundled `llama-server` directly, 8 slots (`-np 8 -c 8192 -ngl 99 -b 2048 -ub 2048`; outside Ollama)

To see what the GPU gives when the one-slot limit is lifted, I ran the same binary Ollama ships
(`~/.local/ollama/lib/ollama/llama-server`, same model blob, its CUDA backend by `GGML_BACKEND_PATH`) with 8 slots.
VRAM ≈ 2.95 GiB.

| inputs per request | requests at once | chunks/s | request p50 s | request p95 s | GPU % mean (max) | cores |
|---|---|---|---|---|---|---|
| 1 | 1 | 17.5 (first run, slots warming; p95 0.168) | 0.040 | 0.168 | 22.2 (55) | 3.52 |
| 1 | 2 | 71.0 | 0.028 | 0.038 | 55.1 (73) | 3.50 |
| 8 | 2 | **87.6** | 0.179 | 0.225 | 64.6 (78) | 3.87 |
| 8 | 4 | 83.6 | 0.372 | 0.485 | 64.5 (79) | 4.07 |
| 32 | 1 | 77.3 | 0.411 | 0.497 | 68.4 (81) | 3.76 |
| 128 | 1 | 76.5 | 1.624 | 1.936 | 67.0 (79) | 3.85 |

(all 12 cells in `data/bench.jsonl`). 8 slots give **+25 to +40 %** over Ollama (77 to 88 against 55 to 62 chunks/s) with
about 1.5 fewer cores. That is not a large gain: the per-chunk overhead stays, and the GPU tops out at about 68 %.
Its vectors are not bit-identical to Ollama's (§3).

### 2c. Against W2-123 and the cold semantic stage

| | chunks/s | semantic stage, 54,463 chunks |
|---|---|---|
| Shared runner on the CPU since 04:33 (CTO's figure) | 0.4 to 1.4 | 11 to 38 hours (estimate) |
| My CPU-only Ollama, 6 cores, load ≈ 35, 1 per request | 0.29 | about 52 hours (estimate; a crowded machine) |
| W2-123, GPU, -np 1, alone, capped (load 20.7) | 32.0 | 28 min (its extrapolation 1,586 s for 50,740) |
| W2-123, real cold rebuild on the shared GPU runner, three rebuilds sharing it | 13.3 | **68.1 min (measured)** |
| CTO, shared runner on the GPU, 11-01 22:00 | 44.8 | 20 min (estimate) |
| **This run, Ollama on the GPU, batch 32, alone (load 14)** | **61.7** | **14.7 min (estimate from 512 chunks)** |
| This run, `llama-server` 8 slots, batch 8 × 2 at once | 87.6 | 10.4 min (estimate; needs a different server than Ollama) |

The estimates are 54,463 ÷ chunks/s from 512 chunks, for one rebuild alone; they are not a measured stage. Three
rebuilds sharing one runner divide it (W2-123: 21 to 29 chunks/s in all under load).

## 3. Determinism and agreement (200 chunks)

Cosine per chunk; "bit-identical" = float32 identical. "stored" = the vectors in W2-00-store, built on 11-01 05:15 by the
shared runner (then on the GPU). CPU chunk vectors: see the end of this section.

| pair | min | mean | bit-identical |
|---|---|---|---|
| stored vs Ollama-GPU, 1 per request | 0.999399 | 0.999883 | 0/200 |
| stored vs Ollama-GPU, 32 per request | 0.999409 | 0.999883 | 0/200 |
| stored vs Ollama-GPU, 128 per request | 0.999430 | 0.999896 | 0/200 |
| Ollama-GPU 1 vs 32 per request | (in `agree` output) | | 0/200 |
| stored vs llama-server-8-slots, 1 per request | 0.999427 | 0.999874 | 10/200 |
| llama-server-8 vs Ollama-GPU (any pair) | 0.998869 | 0.999700 | 0/200 |

Questions (the 20 visible): the GPU query vector against the CPU one (my :11447), cosine **min 0.999349, mean ≈ 0.99965**
(`data/facet.json`). This is the same order of disagreement as W2-123's CPU floor (0.9994) and the stored-vs-fresh
drift: the GPU is not measurably worse than the CPU's own non-reproducibility, but it is never bit-identical.

CPU chunk vectors for the same chunks: CPU_CHUNK_PLACEHOLDER

## 4. Query embedding on the GPU and the search answers (the owner's question)

**Set-up.** A clone of `~/gov-os-worktrees/W2-00-store` at `6ebd7b566af4` in my scratch, with copies of its
`store.db` and `codeintel/` (fresh: the facet checks content hashes). The retriever is the **main tree's code**
(`src/` at w2/integrate, `gov --version` → commit `01f5d8be36ae`) through a scratch wrapper `bin/gov`, which imports
the main tree's `src` first and changes only two things: in the GPU run `semantic._on_cpu` returns True (so the GPU
vector is used rather than refused) and the query-vector cache is off; in the CPU run the cache is on but lives in
my clone (so each question was embedded once on the CPU). (The measure's `gov.__file__` line names the pin's path because
its probe pops `sys.path[0]`; the code that ran is the main tree's.) The query host was set by
`GOV_QUERY_OLLAMA_HOST`: :11446 (GPU, 29/29 layers) and :11447 (CPU only). Reranker: the default private one, on the
GPU, in both runs. Command: `python3 -m gov.retrieval.measure memory-retrieval --root <clone> --sets-root <main tree>
--part visible --gov <scratch>/bin/gov --out <scratch>/measure-{gpu,cpu}`.

**The semantic facet alone** (the same store, each question's top-30 with the GPU and the CPU vector, the facet's own
SQL): top-5 the same set in 20 of 20 questions, the same order in 19 (q18 differs in order); top-30 the same set in 12 and 29 of 30 in 8;
the top-30 order differs in all 20 (near-ties swap).

MEASURE_PLACEHOLDER

## 5. The reranker on the GPU

`Qwen/Qwen3-Reranker-0.6B` at the pinned revision, the reranker environment's own interpreter, `CrossEncoder(device=…)`,
offline; 20 visible questions × 30 candidates (512-character chunks), one `predict` per question, after a warm call.

| device | load s | per query p50 s | p95 s | memory |
|---|---|---|---|---|
| GPU (cuda), bf16 | 1.8 | **0.181** | **0.262** | torch peak allocated 2,829 MiB, reserved 3,198 MiB (+ CUDA context; ≈ 3.5 GiB per process) |
| CPU | RERANK_CPU_PLACEHOLDER | | | |

- **The reranker already runs on the GPU in production** whenever the card has room: the worker leaves the device to
  the library, and the environment's torch has CUDA. So each search's private reranker costs about 3.5 GiB of VRAM for
  as long as its `gov retrieve` process lives.
- **Both models together:** the embedder (Ollama, 29/29 layers: 2.37 GB by `/api/ps`; ≈ 2.5 GiB on the card) plus **one**
  reranker (≈ 3.5 GiB) ≈ **6 GiB**. 16 GiB holds both with about 8 GiB of headroom after the desktop (≈ 1.2 GiB). It
  does **not** hold one embedder plus 12 to 15 private rerankers (≈ 45 to 55 GiB). That is the crash risk in §1.
- **W2-112 (one shared reranker, DAEO-clon)** turns the reranker's GPU use from N × 3.5 GiB into 1 × 3.5 GiB (plus
  activations for a larger batch). Under that plan the GPU holds the embedder and the shared reranker together with room to spare.
  At 0.18 s per query on the GPU, one shared reranker serves about 5 searches a second (estimate, 30 candidates each).

## 6. The GPU's share and the cores it frees

- **Embedding (rebuilds).** On the GPU, one runner gives 55 to 65 chunks/s with about 5 cores busy, which is about **0.09
  core-seconds per chunk**. On the CPU (my measurement, crowded machine) it gave 0.29 chunks/s with about 6.9 cores busy:
  about **24 core-seconds per chunk**, some 260 times more (estimate under load; on a quiet machine the CPU figure would be
  better, but SIZING-1 and W2-123 show the CPU path is never close). So the GPU can take **all** of the rebuild
  embedding; the 8 cores capped for the shared server (12-19) then do about 5 cores of work during a rebuild and are idle otherwise.
- **Question embedding (:11435, CPU only by DEC-798/DEC-975).** Each question costs one CPU request of two texts: about
  3 to 16 s on 6 cores under today's load (my :11447: 3.3 s per text at load 35, about 16 s per request at load 50 to 65).
  On the GPU it is about 0.02 to 0.04 s. Moving it frees the query server's cores and removes the minutes-long waits
  a busy query runner causes (its runner was at 450 % CPU during this run). The cost: the vector is not bit-identical
  to the CPU's (cosine ≥ 0.99935 on the 20 questions); the effect on the answers is in §4.
- **Reranking.** It is already on the GPU when there is room; the risk is not speed but memory: 3.5 GiB per process.
  On the CPU a rerank takes RERANK_CPU_SUMMARY.
- **Total.** With the embedder (2.5 GiB) and one shared reranker (3.5 GiB) on the GPU, the GPU could take essentially
  all embedding and reranking work (estimate: well over 95 % of its compute time today is CPU-side overhead or
  CPU-only work that the GPU does faster). It frees the 8 capped cores of the shared server (about 5 used during a rebuild)
  and the query server's 8 (12-19, shared with it). Some CPU stays busy: about 4 to 5 cores per runner for Ollama's
  per-chunk overhead during a rebuild.

## 7. Recommendations (for the plan; each needs the owner's decision)

1. **Keep the shared embedder on the GPU and watch for it falling off.** A watchdog that alerts when the shared log has
   `offloaded 0/N layers to GPU` or `CUDA error`, or when `/api/ps` shows `0 < size_vram < size` for the shared runner.
   One `/api/ps` read a minute is cheap. Action on alert: unload and reload the model once VRAM is free (`keep_alive: 0`
   then one request), never while a rebuild is mid-stage.
2. **Bound the rerankers' GPU memory before anything else** (the crash risk): W2-112's one shared reranker; until then,
   either cap the private rerankers on the GPU (for example a lock or a count of 2, the rest on the CPU) or pin them to
   the CPU with `CUDA_VISIBLE_DEVICES=-1` in `rerank.py`'s child environment when the card has under ~4 GiB free.
3. **Leave `OLLAMA_NUM_PARALLEL` alone**: it is not honoured for this model in 0.35.0. A bigger gain (+25 to 40 %) would
   need serving the embedder with llama-server's own slots, a different server and a change to the request path
   (`/v1/embeddings`) and to DEC-773's determinism assumptions. Not worth it now; the GPU vs CPU gap (×200) is what matters.
4. **The question embedder on the GPU:** see §4 for whether the answers change; DEC-798's CPU-only rule exists for
   bit-reproducibility, which the GPU does not give (and the CPU only gives for single-text, one-in-flight requests).
5. **Crash risk stays** while many CUDA processes share the card on WSL: plan for the shared runner to crash and reload,
   and make the reload find room (point 2).
