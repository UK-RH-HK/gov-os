# W2-123 evidence: KPI 3, the embedding server's parallel requests and CPU cap, measured

The implementer's evidence for W2-123's KPI 3 (DEC-996 item 3 A; DEC-1014, DEC-1017). Every figure below is the
ticket lead's measure, taken in its own session on 2026-11-01/02 and recorded in
`.gov-runtime/scratch/lead/measure/FIGURES.md` with its raw records beside it in that folder. Each figure names its
record. No figure was added, and none is rounded beyond one decimal (the determinism cosines are quoted as recorded).

## 1. What was measured, how and where

- **The machine:** 20 logical CPUs, an RTX 5070 Ti with 16 GiB, WSL2. Other leads, closes and tests ran throughout:
  the 1-minute load average at the end of each phase was 20.7 to 48.5 (`sweep-1.jsonl`, field `load1`).
- **The server measured:** a private instance on 127.0.0.1:11444, never the shared servers (127.0.0.1:11434 and
  :11435) except where a figure below says it is the shared server's own rebuild. It ran the same binary
  (`/home/usain/.local/ollama/bin/ollama`, Ollama 0.35.0) and the same model (`qwen3-embedding:0.6b`, on the GPU) as
  `ollama serve`, with `OLLAMA_NUM_PARALLEL` set to the case's value.
- **The cap, applied as the ticket's start applies it:** the CPU set (`sched_setaffinity`) and the niceness are set
  inside the started process before it runs `ollama serve`, so the runner it starts inherits them. Capped = CPUs
  12-19 at nice 10 (ACT-OLLAMA-CAP-1's cap); uncapped = CPUs 0-19 at nice 0. Script `measure.py` (mode `sweep`,
  function `by_hand`), records `sweep-1.jsonl`, 2026-11-01 23:01 to 23:25 UTC. Each case's record shows the started
  server's and runner's CPU set and niceness as read from `/proc` (field `started`).
- **A rebuild's semantic stage, replayed:** the stage's own requests (`semantic.BATCH` = 32 chunks per request, each
  chunk its first 512 characters, one request after the other), sent through `gov.retrieval.semantic`'s own
  `_embed`, over 1,024 chunks of the integration store (`~/gov-os-worktrees/W2-00-store`, 50,740 embedded chunks).
  Every vector was compared with the stored one. "Alone" is one replay; "three at once" is three replays of
  different 1,024-chunk slices started together.
- **The semantic stage in seconds** is the corpus (50,740 chunks) divided by the chunks per second of one rebuild
  (for "three at once", the slowest of the three). It is an extrapolation from 1,024 chunks, stated as such; the
  cold rebuild of figure 4 is the measured stage.
- **Cores busy:** the server's and its runner's CPU time over the phase's wall time. **GPU %:** nvidia-smi's
  utilisation, sampled each second.
- **The determinism check of each case:** S5's form (each text in a request of its own, `parallel` requests in
  flight at once, float32 byte for byte) on 256 chunks spread over the corpus, against references made at -np 1 with
  one request in flight. It ran once per case, so "alone" and "three at once" of one case share it.
- **The code measured:** the request form is `src/gov/retrieval/semantic.py` as last changed at `ee5056be590a`
  (this ticket does not change it). The sweep's start used `measure.py`'s own copy of the start's cap (the two calls
  above), because it ran from 23:01 while this ticket's first code commit, `e404e268f3fb`, was committed at 23:13.
  The ticket's own `ensure_available` was used in the run of figure 2 (2026-11-02 00:05, branch head
  `986a77619a32`, whose `ollama.py` is that of `3dabcdaca633`).

## 2. The 16 measured cases (`sweep-1.jsonl`)

| parallel | cap | alone or three at once | chunks per second (one rebuild) | chunks per second (all) | semantic stage s (extrapolated) | server cores busy | GPU % | runner started with | determinism check (256) | load |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | capped | alone | 32.0 | 32.0 | 1585.6 | 3.61 | 62.0 | -np 1 | accepted (0 differ) | 20.7 |
| 1 | capped | three at once | 8.6 | 25.8 | 5900.0 | 2.63 | 37.8 | -np 1 | accepted (0 differ) | 48.5 |
| 1 | uncapped | alone | 31.3 | 31.3 | 1621.1 | 4.40 | 57.2 | -np 1 | accepted (0 differ) | 42.1 |
| 1 | uncapped | three at once | 12.5 | 37.4 | 4059.2 | 4.49 | 52.3 | -np 1 | accepted (0 differ) | 38.0 |
| 2 | capped | alone | 25.0 | 25.0 | 2029.6 | 3.05 | 52.9 | -np 1 | accepted (0 differ) | 37.7 |
| 2 | capped | three at once | 7.1 | 21.3 | 7146.5 | 2.20 | 35.2 | -np 1 | accepted (0 differ) | 40.5 |
| 2 | uncapped | alone | 30.2 | 30.2 | 1680.1 | 4.15 | 51.7 | -np 1 | refused (1 differs) | 39.4 |
| 2 | uncapped | three at once | 11.4 | 34.3 | 4450.9 | 3.92 | 46.4 | -np 1 | refused (1 differs) | 38.3 |
| 4 | capped | alone | 16.9 | 16.9 | 3002.4 | 2.10 | 38.1 | -np 1 | accepted (0 differ) | 39.8 |
| 4 | capped | three at once | 7.4 | 22.2 | 6856.8 | 2.30 | 38.1 | -np 1 | accepted (0 differ) | 34.7 |
| 4 | uncapped | alone | 33.7 | 33.7 | 1505.6 | 4.74 | 60.3 | -np 1 | refused (1 differs) | 30.4 |
| 4 | uncapped | three at once | 13.5 | 40.5 | 3758.5 | 4.93 | 57.3 | -np 1 | refused (1 differs) | 28.7 |
| 8 | capped | alone | 24.2 | 24.2 | 2096.7 | 2.95 | 49.8 | -np 1 | refused (4 differ) | 27.5 |
| 8 | capped | three at once | 9.7 | 29.0 | 5230.9 | 3.01 | 47.1 | -np 1 | refused (4 differ) | 32.7 |
| 8 | uncapped | alone | 23.3 | 23.3 | 2177.7 | 2.99 | 38.5 | -np 1 | accepted (0 differ) | 46.0 |
| 8 | uncapped | three at once | 9.8 | 29.5 | 5177.6 | 3.21 | 36.8 | -np 1 | accepted (0 differ) | 42.8 |

"parallel" is the `OLLAMA_NUM_PARALLEL` the server was started with; "runner started with" is what its runner
(`llama-server`) was really given, read from its command line.

## 3. Further figures

1. **What the runner was really started with** (`np_check-2314.log`, script `np_check.py`). In every case above the
   runner was started with `-np 1`, whatever `OLLAMA_NUM_PARALLEL` said. Ollama's own log confirms it: on a private
   server on :11446 with `OLLAMA_NUM_PARALLEL=4` and `OLLAMA_DEBUG=1`, its "server config" line shows
   `OLLAMA_NUM_PARALLEL:4`, and the runner is set up with `runner.parallel=1` (sched.go:745) and `-np 1`. Ollama
   0.35.0 serves this embedding model one request at a time.
2. **The cap and the niceness apart** (`sweep-1.jsonl`; `measure2-failed-0024.log`). In all 16 cases the server and
   its runner used 2.10 to 4.93 cores, below the 8 CPUs of the cap; the GPU was 35 to 62 % busy. Under three rebuilds
   at once on a loaded machine, the capped server (8 CPUs at nice 10) gave 21.3 to 29.0 chunks per second in all, the
   uncapped one 29.5 to 40.5. Measuring the CPU set and the niceness apart was tried (2026-11-02 00:05, through the
   ticket's own start reading the gate's file) and could not be done: the GPU's memory was full (15.0 of 16.3 GiB,
   held outside the Gov OS), the private runner fell back to the CPU and its first warm request after a restart
   failed. That run did show the ticket's own start applying the cap: the server (pid 2071762) and its runner (pid
   2073121) both ran on CPUs 12-19 at nice 10, started by `ensure_available` from the gate file
   `{"embedding_servers": {"shared": {"parallel": 1, "cpus": "12-19", "nice": 10}}}`.
3. **The determinism matrix** (`det_matrix-2242.jsonl`, script `det_matrix.py`, 384 chunks, CPUs 12-19 at nice 10,
   2026-11-01 22:42):
   - single-text requests, one in flight: the same vectors on repeat at -np 1 (0 of 384 differ), and the same at a
     setting of 2, 4 and 8 with one in flight (0 of 384 against -np 1);
   - single-text requests with 2, 4 and 8 in flight: 0, 1 and 3 of 384 differ (smallest cosine 0.9997);
   - the rebuild's own request form (32 texts per request), the same request repeated at -np 1: 97 of 384 differ
     (smallest cosine 0.999427, largest element difference 0.0077); the stored vectors differ from fresh ones in 158
     of 384 (41 %); and in the sweep 308 to 405 of every 1,024 replayed chunks differed from the stored ones.
4. **A cold rebuild's semantic stage on the shared server** (`rebuild-2-record.json`, a copy of that rebuild's
   `.gov-runtime/rebuild/record.json`; log `.gov-runtime/scratch/lead/log/rebuild-2.log`). The lead's rebuild of this
   ticket's worktree on 127.0.0.1:11434, capped by ACT-OLLAMA-CAP-1 (CPUs 12-19, nice 10, -np 1, on the GPU), started
   2026-11-01 23:56:13 UTC: the semantic stage took **4,087.0 s (68.1 minutes) for 54,463 chunks, 13.3 chunks per
   second**; the whole rebuild 4,183.3 s (record 14.5, lexical 27.5, secrets 17.3, code graph 50.7, compaction 3.5).
   `gov rebuild` flagged it slow (over 1,800 s). Other trees' rebuilds used the same one-at-a-time server meanwhile
   and the load was 17 to 48, so this is the "three at once, capped" situation of the table (extrapolated 5,231 to
   7,146 s for 50,740 chunks), on real work. SIZING-1 measured 12 to 25 minutes for this stage on a quieter machine.
5. **The probe's times** (`np_check-2314.log`; `det_matrix-2242.jsonl`). A cold model load to the first vector took
   8.0 s (server up at 23:14:32.28, runner set up at 23:14:40.27); a warm one-text request took 0.03 to 0.06 s under
   load (384 single requests in 10.0 to 15.1 s).
6. **The ticket's probe on the real servers, once each** (2026-11-02 01:07, the lead, during the rebuild of figure 4):
   the shared server `healthy` in 1.6 s; the CPU-only query server `slow`, 54.3 s for one text (CPU-only at nice 10 on
   a loaded machine, its model likely loaded cold). Both answered; nothing was stopped or started.

## 4. The setting chosen

Chosen setting: parallel requests 1 for both servers and the CPU cap of 8 logical CPUs at nice 10 (the highest-numbered 8 the caller may use: 12-19 here). Why: Ollama 0.35.0 starts this model's runner with `-np 1` whatever the setting (figure 1), so no other value changes anything but the risk of overlapping requests, which the determinism check refused in 3 of 8 cases; and the 8-CPU cap is not the limit: the server never used more than 4.93 of its 8 CPUs, with the GPU 35 to 62 % busy (figure 2). The cost measured under contention is the niceness, which is the owner's chosen policy (ACT-OLLAMA-CAP-1), not the CPU set; the cap is therefore kept, not raised.

The defaults in `src/gov/retrieval/ollama.py` follow it, all unchanged in value, each constant's comment now naming
this file and its figure:

| constant | value | source |
|---|---|---|
| `DEFAULT_PARALLEL` | 1 (shared), 1 (query) | §4 and figure 1 |
| `DEFAULT_CPU_COUNT` | 8 | figure 2 |
| `DEFAULT_NICE` | 10 | ACT-OLLAMA-CAP-1 and -2, and figure 2 |
| `DEFAULT_PROBE_SLOW_S` | 10 s | figure 5: above a cold model load of 8.0 s |
| `DEFAULT_PROBE_HUNG_S` | 120 s | `semantic.TIMEOUT_S`, where a rebuild's own request gives up |

A repository's own figures go in the gate's configuration file (W2-20); the code holds no CPU number or port of this
machine.

## 5. What this means, and what it does not show

What it means:

- **Parallel requests do not exist for this server today.** Through Ollama 0.35.0's own setting, the embedding
  model's runner answers one request at a time, whatever the setting says. The differences between rows of one cap
  are the machine's changing load, not the setting. So the speed-up DEC-1014 hoped for cannot come from
  `OLLAMA_NUM_PARALLEL` with this Ollama version and model.
- **The 8-CPU cap is not the limit.** The server never used more than 4.93 of its 8 CPUs, and the GPU was never more
  than 62 % busy. Raising the cap would not make it faster.
- **The lower priority costs speed when the machine is busy.** With three rebuilds at once, the capped server gave
  about a quarter to a third fewer chunks per second than the uncapped one. That is the niceness yielding to test
  runs, which is what ACT-OLLAMA-CAP-1 asked for.
- **A busy shared server makes a rebuild's semantic stage slow.** The real cold rebuild took 68.1 minutes for this
  stage, against 12 to 25 minutes in SIZING-1 on a quieter machine, because other rebuilds shared the
  one-at-a-time server.
- **Overlapping requests now and then change a vector**, so a parallel setting above 1 would carry a risk with no
  gain; the ticket's determinism check refuses it.

What it does not show:

- **It does not show the CPU set and the niceness apart.** That run failed (the GPU's memory was held outside the
  Gov OS), so the share of the cost due to nice 10 alone, as against the 8-CPU set alone, is inferred from the cores
  busy, not measured.
- **The semantic stage in seconds in the table is extrapolated** from 1,024 chunks per rebuild; only figure 4 is a
  full stage, and it ran once, on a busy machine.
- **The machine's load moved from 20.7 to 48.5 during the sweep**, and each case ran once; small differences between
  rows are within that noise and rank nothing.
- **The rebuild itself is not reproducible bit for bit, even at -np 1.** With 32 texts per request, the same request
  repeated gives slightly different vectors (97 of 384, smallest cosine 0.999427), and 308 to 405 of every 1,024
  replayed chunks differed from the stored ones. The determinism check here compares single-text requests; it does
  not make the batched rebuild reproducible.
- **It does not show other Ollama versions or models.** A version that honours the parallel setting for embedding
  models would need its own measure before any default above 1 is chosen.
