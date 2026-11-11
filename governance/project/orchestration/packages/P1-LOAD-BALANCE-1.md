# P1-LOAD-BALANCE-1 — one load-balancing plan for this machine (DEC-1028 item 5, DEC-1031 item 1)

For the owner, before decision A. The machine: 20 threads, 24 GB for WSL, one GPU (NVIDIA GeForce RTX 5070 Ti,
16,303 MiB). Written from the history (the servers' logs since 2026-11-01 21:51, the capacity sampler since 10-31,
the leads' memory since 10-29), confirmed by one live hour (10:57 to 11:57) and last night's GPU crashes. The GPU
agent's measured figures (batching and parallel on the GPU, query embedding on the GPU against the memory measure,
the reranker on the GPU) are added as section c.2 when they come; the determinism test runs now (DEC-1031 item 1).
Sections a to d in full: `drafts/LB-PLAN-sections-a-d.md` (every figure with its source); e: `drafts/LB-PLAN-section-e.md`.

## The problem in one paragraph
Three things meet on one machine: **too much embedding work** (about 503,000 texts embedded in 13 hours, nine full
copies of the corpus, because every new tree, clone and close rebuilds cold and every failed attempt repeats it), **a
slow embedder** (one request at a time; on the GPU 22 to 45 chunks/s, on the CPU 0.4 to 1.4), and **too many
memory-hungry agents** (up to 12 private rerankers holding 8 to 14 GB of RAM, more than all the leads). Last night
the three compounded: the rerankers filled the GPU, CUDA crashed three times (23:54, 02:36, 04:30), the embedder
reloaded on the CPU at 04:34, and every landing for seven hours died on its first 120 s request.

## The target architecture (the owner's, DEC-1031 item 1)
1. **One shared embedding service on the GPU, for indexing and queries,** batched and parallel where the vectors stay
   within the agreed tolerance. Today: the shared server is on the GPU again (29/29 layers since 11:15, pinned since
   12:05); the query server is still CPU-only (DEC-798), pending the determinism test now running.
2. **One shared reranker on the GPU** (W2-112), in place of one private reranker per session.
3. **A GPU memory budget:** the embedder first, the shared reranker second, nothing may push the embedder off.
   | Holder | Budget | Today |
   |---|---|---|
   | The embedding model (one runner, pinned) | 3.5 GB (model 2.4 GB plus its buffers) | 2.4 to 3.5 GB, pinned at 12:05 |
   | A second embedding runner, only if real parallelism is adopted (c.4) | 3.5 GB | none |
   | The shared reranker (W2-112) | 2.5 GB (estimated; the GPU agent measures it) | none; private rerankers hidden from the GPU by ACT-RERANK-CPU-1 |
   | Headroom for CUDA itself and the desktop | at least 2 GB | |
   | Everything else (private test servers, measurement runs) | none on the GPU by default | |
   That totals 9.5 to 11.5 GB of 16 GB, with room to spare.
4. **The CPU only as an alerted fallback:** a load with 0 layers on the GPU, or a CUDA crash, is an alert at once
   (the dispatcher's GPU watch, v4.5, live since 11:47), never a silent seven hours.

## a. The work today (in full: section a of the draft)
- **Per ticket:** about 3 rebuilds in the lead's own tree (the first one cold, 3,000 to 4,700 s), 1 to 2 more per
  further run, a share of the batch's 1 to 3 queue builds, and every retried landing: **5 to 6, up to 9** (W2-04 8,
  W2-104 7, W2-67 9). **The cold ones cost the time:** the lead's first, every `close_build.py` clone (717 to 8,101 s),
  the nightly's (1,016 to 3,973 s).
- **Per batch:** one prepare on the warm merged clone (221 to 689 s healthy), plus 0 to 2 `alt` builds whenever any
  red remains (the queue's check on the head without the batch).
- **Queries:** every `gov check` embeds the retrieval check's two dev tiers cold in a temporary folder and sends 52
  questions cold to the query server; context reproducibility asks up to about 190 more.

## b. Less work: the levers, in order of saving (in full: section b)
1. **A machine-wide vector cache keyed by the text** (model, revision, hash of the text): a chunk is embedded once on
   the machine, whatever tree or code asks. It removes almost all of the 503,000 texts a day, cold clones and
   code-changing tickets included. A new product ticket (about 80 to 150 lines in `semantic.py`). **New, yours.**
2. **W2-122's seeding** (decided, DEC-1027 C; landing with its run 2): a seeded first rebuild costs 20 s, not
   4,700 s. Its limit: a tree whose `gov` code differs from the base's is refused the seed, so code tickets still pay
   one cold build until lever 1 exists.
3. **The queue's `alt` builds avoided:** the head without the batch taken from the integration store (already rebuilt
   at the head), not rebuilt; a fresh nightly baseline clears more reds from its record. My tools, today.
4. **One integration-store refresh per landing** (through a heavy slot), so every seed is at most one landing old. My
   tools, today.
5. **`close_build.py`'s cold clones retired or seeded.** My tools, with the queue.
6. **The retrieval check's dev tiers pre-built once** (a read-only store per tier commit, with its query cache), not
   cold on every `gov check`. A product line for W2-121 or the check's ticket.
7. **Next: one shared read-only index with each worktree indexing only its own changes** (an overlay store per tree
   on the integration store). Larger than lever 1; lever 1 gives most of the saving at a fraction of the risk.
**After 1 to 5:** code tickets 1 cold build each (seconds of embedding with lever 1), other tickets none; each batch
one incremental prepare; the nightly seeded (setup about 1 minute).

## c. Faster embedding (in full: section c; the GPU's figures follow in c.2)
1. **The GPU is the lever, and it is idle because of how it is fed and who holds it.** On the GPU the shared runner
   did 44.8 chunks/s (11-01 22:00); on the CPU 0.4 to 1.4. Ollama 0.35.0 runs this model one input at a time (`-np 1`),
   so a request of 32 texts is 32 serial steps: the GPU waits on the step overhead, not on compute. That is why it
   reads 1 to 14 % even when it works.
2. **The GPU's measured figures** (the GPU agent, private servers on their own ports, the shared ones untouched;
   in full: `drafts/LB-PLAN-gpu.md`):
   | Setting | Chunks/s | p95 per request | VRAM | GPU % | CPU cores |
   |---|---|---|---|---|---|
   | Ollama on the GPU, 1 text a request | 47.7 | 0.03 s | about 2.5 GiB | 37 | 5.1 |
   | **Ollama on the GPU, 32 texts a request (the rebuild's form)** | **61.7** | 0.66 s | about 2.5 GiB | 48 | 5.6 |
   | Ollama on the GPU, 128 texts, 4 at once | 64.9 | 7.9 s | about 2.5 GiB | 47 | 5.9 |
   | **llama-server, 8 slots, 8 texts, 2 at once** | **87.6** | 0.23 s | about 2.95 GiB | 65 | 3.9 |
   | Ollama on the CPU only, 6 cores (load about 35) | 0.29 | 3.65 s | 0 | — | 6.9 |
   | **The reranker on the GPU, 30 candidates a query** | 0.18 s p50 a query | 0.26 s | **about 3.5 GiB a process** | — | — |
   | The reranker on the CPU, 4 cores under load | over 100 s a query (did not finish in 400 s) | | 0 | | 4 |
   - A full cold semantic stage (54,463 chunks) would take about **15 minutes** with Ollama on the GPU and about **10**
     with llama-server's slots (estimates, one rebuild alone), against 68 minutes measured for W2-123's real rebuild
     with others sharing the runner, and 11 to 37 hours on the CPU.
   - **Query embedding on the GPU (the determinism test, DEC-1031 item 1), the standing memory measure, visible half,
     the same store:** GPU hit@5 11/20, full evidence 11/20, in the bundle 15/20; CPU hit@5 10/20, full evidence 11/20,
     bundle 15/20. The only difference (Q13, rank 1 against 7) repeats on the CPU vector itself across runs: the
     pipeline's run-to-run variation, not the device. The first-call top 5 is identical in 18 of 20 questions (Q17
     swaps items 4 and 5). **No answer's pass or fail changes because of the device.** The vectors are not
     bit-identical (W2-123 found the CPU embedder itself is not), so moving the query embedder needs DEC-798 and
     DEC-975 amended for that.
   - **GPU memory:** the embedder plus one reranker need about 6 GiB; 16 GiB holds them with about 8 to spare.
     Twelve to fifteen private rerankers would need 45 to 55 GiB: that is what crashed it. **The GPU could take
     essentially all embedding and reranking work,** freeing the shared server's capped cores and all the query
     server's CPU work.
   - **The crashes:** `CUDA error: unknown error` in `cudaMemcpyAsync` at 02:36 and 04:30; the WSL kernel log holds
     1,440 GPU allocation failures (`dxg`, ENOMEM). Inferred cause: GPU memory exhausted by the rerankers (no
     out-of-memory line in the runner's own log).
3. **Batching** gives no compute parallelism at `-np 1`; it only saves round trips. Smaller requests with the bounded
   retry (DEC-1026, W2-123 run 2) fail less and let other clients in between.
4. **Real parallel runners:** several Ollama instances (2.2 GiB each on the GPU), or `llama-server -np N`. They change
   the vectors slightly (W2-123: 1 to 4 of 256 differ, cosine floor 0.9997); they need the tolerance decision
   (P-W2-123-2) first. Lever b.1 shrinks that question: a cached vector is reused, so small differences no longer
   move between rebuilds.
5. **Separate the CPUs:** today both servers are pinned to CPUs 12 to 19, so a rebuild's batch slows every question
   (P-W2-123-3). Until the query embedding moves to the GPU, give the query server CPUs of its own (2 suffice for a
   2-text question, estimated); set the runner's threads to its CPU set (it reports 10 threads on 8 CPUs).

## d. How many agents at once (in full: section d)
- **Memory decides, and the rerankers are the swing:** fixed costs (floor 3 GB, 3 heavy-slot runs 5 GB, the
  embedder's RAM 2.9 GB, other sessions 4 to 6 GB) leave 7 to 9 GB for leads: **3 to 4 leads** at their measured p95
  (2.3 GB outside verification, 4.1 GB with it). With the private rerankers gone (W2-112's shared one on the GPU)
  about 8 GB more is free: **5 to 6 leads.**
- **CPU:** with the embedder on the GPU (2 to 5 cores), 3 heavy slots of 6 workers fill about 18 of 20 threads; with
  it on the CPU (7.5 to 8 cores), 2 slots, not 3.
- **Together:** 3 to 4 leads now (5 to 6 after W2-112), 1 queue run (its priority slot), at most 1 close; the heavy
  jobs within the 3 slots.
- **How the dispatcher keeps it there:**
  - judge the embedder by its progress (tasks done per minute), not one request's latency: no more false "hung"
    flags (42 between 04:00 and 11:00 today);
  - the embedding backlog and the GPU layers as admission inputs: no new lead or cold rebuild while the backlog is
    over its threshold or the embedder is off the GPU;
  - slots follow the embedder's device (3 on the GPU, 2 on the CPU);
  - the lead cap from memory, not slots x 2;
  - the rerankers counted (and capped) by their memory.

## e. Measured (in full: `drafts/LB-PLAN-section-e.md`)
- **Shared server:** 11-02 to 11:05: 8,826 requests, p95 45 s, 290 errors (on the CPU since 04:34). The live hour,
  after the 11:15 reload: 690 requests, p50 1.4 s, p95 4.9 s.
- **Query server:** 11-02 to 11:05: 1,897 requests, p50 53 s, p95 120 s, 328 errors. The live hour: 133, p50 19 s,
  p95 40 s (still on the CPU, sharing the CPUs).
- **Rerankers:** up to 12 at once, 11.4 GB p95, 13.7 GB max (11-02); 8.4 GB in the live hour; 0.07 cores.
- **The machine:** busy cores p50 12 of 20, p95 18.5; leads at once mean 1.9, max 5 (11-02); memory available
  down to 3.4 GB.
- **Who uses the servers:** a lead's `gov check` (its retrieval checks) and its rebuilds are the bulk of both (in the
  live hour W2-61h 241 connection samples, W2-04 90, W2-123 126, W2-122 74), then the dispatcher's probe (35) and the
  merge queue (20).

## f. The recommendation, in order of impact, with its targets and checks
| # | Step | Who | Target | How it is checked |
|---|---|---|---|---|
| 1 | **The embedder on the GPU and kept there:** reloaded (DEC-1029), pinned (12:05), watched (v4.5), at most two rerankers on the GPU (ACT-RERANK-GPU-SLOTS-1, which replaces ACT-RERANK-CPU-1: a reranker on the CPU takes over 100 s a query) | done; the ACT with your operator | 29/29 layers at all times; 0 CUDA crashes a day; the GPU under 11 GB | the dispatcher's `GPU:` line; `gpu-alert` items; the morning log scan |
| 2 | **The bounded retry** (DEC-1026, W2-123 run 2, running) | W2-123 | no rebuild lost to a timed-out request | `server_log_scan.py`: failed embeds; the queue's prepares |
| 3 | **The query embedding on the GPU:** the determinism test passed (no answer changes; the vectors not bit-identical, as on the CPU): amend DEC-798 and DEC-975 and move the query server to the GPU (an ACT: its `CUDA_VISIBLE_DEVICES=-1` removed, its model pinned within the embedder's budget) | yours: the amendment and the ACT | a question answered in under 1 s at p95 (today 19 to 53 s median) | the query server's latency in the log scan; the next memory measure beside this one |
| 4 | **The vector cache by text** (b.1) | a new product ticket: yours | under one corpus (about 54,000 texts) embedded a day, against nine in 13 hours | the runner's task count a day |
| 5 | **Seeding everywhere:** W2-122 lands; the integration store refreshed per landing; the nightly, the queue's clones and the closes seeded; `alt` taken from the integration store | W2-122 (landing); my tools, today | cold builds: 1 per code ticket, 0 otherwise; the nightly's setup about 1 minute | rebuild records (`semantic_s`); the nightly's setup line |
| 6 | **The shared reranker on the GPU** (W2-112), within its budget | W2-112 (filed) | the rerankers' RAM under 2.5 GB in all, against 8 to 14 GB | the capacity sampler's reranker line |
| 7 | **The dispatcher by progress and by memory** (d): progress-based health, backlog and GPU layers in admission, slots by device, the lead cap from memory | my tools, today; W2-121's lines (SMART-WORK-6) | no false "hung" flag; busy cores within 14 to 18 of 20 for at least 80 % of working hours while work waits | the dispatcher's log; W2-121's band report |
| 8 | **Real parallel runners** only after the tolerance decision (P-W2-123-2) and only if 1 to 7 do not meet the targets | later, yours | — | — |

**Decisions for you in this plan:** (i) ACT-RERANK-GPU-SLOTS-1 now (the GPU is at the pre-crash state); (ii) step 3:
amend DEC-798 and DEC-975 so the query embedding moves to the GPU (the determinism test passed), and its ACT;
(iii) step 4's new ticket (the vector cache); (iv) W2-112 (the shared reranker) moved up, before EXAMIN's copy;
(v) the GPU budget above as the default for W2-20's GPU share (SMART-WORK-6 line 2). Steps 1, 2, 5 and 7 are mine
or already decided. Step 8's llama-server slots measured 87.6 chunks/s against Ollama's 61.7: a 40 % gain, kept for
later.
