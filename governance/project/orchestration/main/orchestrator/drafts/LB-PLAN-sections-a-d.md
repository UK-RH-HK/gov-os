# Load-balancing plan, sections a to d (research draft for the CTO, 2026-11-02 11:10 UTC)

Sources are named for each figure. "Estimated" marks a figure I inferred and did not measure. History limits:
both Ollama logs begin at 2026-11-01 21:51 UTC (the servers were restarted then and the logs are not rotated), so
the embedding figures cover about 13 hours. The capacity sampler (`log/capacity/kinds.jsonl`) begins 2026-10-31
14:17. `log/lead-mem.jsonl` begins 2026-10-29 17:02.

## a. Where the embedding work comes from

### a.1 How a rebuild embeds (product code)

- `gov rebuild` runs these stages: record, lexical, secrets, semantic, codeintel and compaction
  (`src/gov/rebuild/command.py:107-198`). Only the semantic stage embeds (`command.py:152-165` →
  `semantic.refresh`).
- The semantic stage embeds only the chunks that have no vector yet (`semantic.py:255-258`), so the size of a
  rebuild depends on what is missing from the tree's `store.db`:
  - **cold** means an empty store or a new clone: about 54,000 chunks;
  - **incremental** means a warm store: only the chunks that changed.
- Chunks are sent 32 per `/api/embed` request (`BATCH = 32`, `semantic.py:50`), one request after another. Each
  request has a 120 s timeout (`TIMEOUT_S`, `semantic.py:51`, `_ask` at `:94`) and is not retried. If one request
  fails, the stage stops and returns `NO_EMBEDDING` (`:263-264`).
- The vectors embedded before the failure are kept. The `return` inside `with connection:` commits them, so the
  next rebuild resumes from there. Evidence: the queue's warm `merged` clone now holds 53,000 vectors for 61,689
  chunks after six failed attempts (read-only count of `~/gov-os-runs/W2-00/merge-queue/warm/merged/.gov-runtime/store.db`).
- `rebuild_slot.sh:22-35` turns "ok but semantic not_recreated" into exit 75.
- **Measured cold stage:**
  - 4,709 s for 54,425 chunks in 1,701 requests (W2-122 evidence, two other rebuilds beside it);
  - 4,087 s for 54,463 chunks (W2-123 evidence, figure 4).
- **Lead cold first rebuilds:** 3,008 to 3,751 s (worktree logs `W2-61h`, `W2-90b`, `W2-91`, `W2-105`:
  `rebuild-*.json` `timing.semantic_s`).
- **Incremental stage:** 1 to 750 s, with a median under 100 s over the 107 lead rebuilds that carry timings (same
  logs).

### a.2 Every source of embedding requests, and which server it uses

| # | Source | Server | What it embeds | Per occurrence |
|---|---|---|---|---|
| 1 | A lead's first rebuild of a new worktree (`LEAD-w2-common.md:35`) | shared 11434 | cold, ~54k chunks | 3,000–4,700 s |
| 2 | The lead's rebuild before the red check or before verification (`LEAD-w2-common.md:106`, step 4 at `:153`) | shared | incremental | 1–750 s |
| 3 | The same again for each further run or round (run 2, run 3, repair) | shared | incremental | as row 2 |
| 4 | Lead measurement clones (base/head rebuilds: W2-13, W2-86, W2-91, W2-108) | shared | cold or warm | up to 1,400 s |
| 5 | `gov check` → retrieval-regression (`retrieve_check.py:56-82`): clones a-dev and b-dev into a temporary folder and runs `semantic.refresh` on each | shared | cold every time: the 150- and 149-file tiers. Chunk count estimated at a few thousand | minutes, estimated |
| 6 | The same check's 52 queries (`dev-queryset.yaml`, 52 `query:` lines) → `retrieve` → `query_vector` | query 11435 | 2 texts per request. The cache sits in the temporary clone, so it is always cold | 52 requests per run |
| 7 | `gov check` → context-reproducibility (`context_check.py:55-58`): `context()` twice per ticket → `retrieve(refresh=False)` → `query_vector` | query | one question per ticket: the first word of the ticket's title (`context/__init__.py:150-169`); 190 tickets in `.tickets/`. The cache is per tree (`.gov-runtime/query-vector-cache.db`) | up to ~190 distinct questions on a cold cache (estimated) |
| 8 | `gov retrieve` by workers and test designers (`LEAD-w2-common.md:30`) | query | the question | 1 request each, cached per tree |
| 9 | Acceptance and unit tests that embed for real (W2-54's green-here and time-limit cases; W2-05's hooked commit runs the retrieval check) | both | rows 5–7 inside tests | not counted |
| 10 | The merge queue's prepare on the merged result (`merge_queue.py:589`, warm clone `merged`) | shared | incremental | 221–689 s healthy; 3,142 s on 11-01 21:56 |
| 11 | The queue's `alt` clone at the baseline (`:634-636`), when a red is not cleared by the nightly's record | shared | the warm clone moved to the baseline commit | 254–1,608 s |
| 12 | The queue's `alt` clone at the head without the batch (`:647-656`), whenever any red is left, owned or cleared | shared | the warm clone moved back to the head | as row 11 |
| 13 | `close_build.py` (still used: `log/close-three-*.out`): a new clone each close (`:284-315`), plus a second clone to trace reds (`:415-432`) | shared | cold | "clone rebuilt in" 717–8,101 s, 12 closes since 10-30 (`log/close-build/*`, `close-three-*.out`) |
| 14 | The integration store refresh (`refresh_integration_store.sh`, twice a day via `store_refresh_daily.sh`, plus by hand). It uses `flock /tmp/gov-os-rebuild.lock`, not a slot | shared | incremental: the A/B worktree that is one refresh behind | not logged per stage |
| 15 | The nightly (`nightly.sh:99-111`): a new clone of the head, rebuilt cold under the old lock | shared | cold | setup 1,016–3,973 s (`log/nightly/status.txt`); 11-02: total 2,233 s, semantic 1,442 s, **not_recreated**, and the night ran on anyway |
| 16 | The dispatcher's health probe (`dispatcher.py:67`, `embed_check_every: 1`, 30 s timeout) | shared | 1 text per pass | 1 request per pass |

### a.3 Counts per ticket and per landing batch, from real records

**Rebuilds in a lead's own worktree** (rows 1–4; worktree logs `.gov-runtime/scratch/lead/log/rebuild*`, counted
by file):

- Across 44 trees: mean 3.0 per tree, range 1–9.
- Recent tickets:
  - W2-04: 8 (`rebuild-1`…`rebuild-8.start`, five runs);
  - W2-104: 7, over two runs. Rebuilds 4, 6 and 7 ended `not_recreated` (`W2-104-A5-run2-dec1020.json`);
  - W2-67: 9;
  - W2-61h: 6, of which rebuild-5 was `not_recreated` after 2,659 s;
  - W2-92: 6 over three runs;
  - W2-96: 5;
  - W2-123: 3 (one cancelled, one cold at 4,087 s, one incremental at 5 s).

**Per landing batch** (rows 10–12, `.gov-runtime/scratch/orchestrator/merge-queue/log/*/prepare-*.txt`):

- One prepare on `merged` per attempt.
- `alt` is rebuilt 0–2 times.
- Overnight 11-01/02, one batch ran six attempts:
  - 21:56: merged ok after 3,142 s. Then the alt baseline build. Then the alt head-without-batch build, which
    failed at 04:32 (`log/land-batch3-20261101-2205.out`).
  - Then five attempts at 04:33, 06:20, 07:56, 08:01 and 09:13. Each failed on the merged prepare. The 06:20 attempt
    failed after 3,342 s. The other four failed after 121–123 s each: the very first request hit the 120 s timeout
    (`log/land-dispatch-20261102-*.out`).

**Per day** (rows 13–15): one cold nightly; up to two integration refreshes; each `close_build.py` close adds 1–2
cold clones.

**Reconciling the owner's "5 to 6 rebuilds per ticket":**

- A typical ticket gets:
  - 3 lead rebuilds (cold first, before red, before verification);
  - +1 to 2 for each further run (most tickets in the logs had 2–5 runs);
  - its share of the batch's 1–3 queue builds (3–5 tickets per batch);
  - plus every retried landing.
- That totals 5–6. W2-04 (8), W2-104 (7) and W2-67 (9) are above it.
- **The cost is dominated by the cold builds**, each 50–80 minutes: the lead's first, every `close_build` clone and
  the nightly. A large share of rebuilds fail and are repeated: 7 of the 13 queue prepares since 11-01 12:08 ended
  `not_recreated`.

**Embedding traffic actually seen** (my parse of `[GIN] … "/api/embed"` lines and runner task lines in
`~/.ollama/serve-11434.log` and `serve-11435.log`):

- **Shared server, 11-01 21:51 to 11-02 11:05:**
  - 16,581 requests: 16,291 returned 200, 285 returned 400 (the client gave up: "cancel task"), 5 returned 499 (load
    aborted);
  - latency of the 200s: p50 1.82 s, p90 4.83 s, p99 71 s, max 119 s;
  - 503k inputs embedded: 244,425 on 11-01 after 21:51 and 258,509 on 11-02 to 11:05. That is about **9 full corpora
    in 13 hours**.
- **Query server:**
  - 2,181 requests: 1,839 returned 200, **342 (16 %) gave up**;
  - latency of the 200s: p50 45.9 s, p90 79 s, max 119 s;
  - each request is a 2-text question, so the latency is queueing on a CPU-only runner.
- **The dispatcher's "hung" flags:** `dispatch/dispatch.log` holds 42 lines containing "hung" between 11-02 04:00
  and 11:00, while the runner's task log shows it working throughout.

## b. Less work: the levers and the counts after them

1. **Seeding every copy from the warm integration store (W2-122, not landed; run 2 started 10:39).**
   - Measured: a seeded first rebuild takes 0.7 s of semantic work with nothing changed and 20.3 s with one file
     changed (10 requests), against 4,709 s cold (W2-122 evidence).
   - **Limit found:** a seed is refused whenever the tree's running `gov` code differs from the base's.
     `code_fingerprint()` hashes every file of the `gov` package, plus gitleaks and the Python and SQLite versions
     (`git show w2/W2-122:src/gov/rebuild/seed.py`, docstring and `code_fingerprint`). The evidence says it plainly:
     "a worktree whose ticket changes `src/gov/**` does not seed".
   - So the lever removes the cold first rebuild only for tickets that leave `src/gov/` alone, and for clones at
     the integration head: the nightly, `close_build`, and the queue's alt at the head.
   - Expected after: the nightly's 1,000–4,000 s setup drops to about 30–60 s (estimated from W2-122's seeded
     totals of 30.8 and 57.7 s). Code tickets still pay one cold build each.
2. **A machine-wide, content-addressed vector cache.** This is my proposal; it does not exist yet.
   - A chunk's vector depends only on the model, its revision and the text sent (`text[:512]`), not on the `gov`
     code.
   - A cache keyed `(model, revision, sha256(text[:512]))` would sit beside the shared stores, in the same way as
     the query cache (`semantic.py:67-77, 134-169`). `_build` would consult it before `_embed` (`semantic.py:258-265`).
   - Then every rebuild anywhere embeds only texts the machine has never embedded. Cold clones and code-changing
     tickets included, it would remove almost all of the 503k inputs per 13 hours seen above (estimated).
   - It would also make vectors more reproducible, because the same text gets the same stored vector. That bears
     on P-W2-123-2.
   - Cost: one product ticket (an estimated 80–150 lines in `semantic.py`, plus a bound and eviction like
     `_cache`).
3. **The baseline read from the nightly's results (DEC-1001 (c)).**
   - It is in force as decided. The register says "the check on the head without the batch stays"
     (`DECISION_REGISTER.md:12547`ff).
   - In code, the queue clears a red from the nightly's record (`merge_queue.py:618-629`). But whenever any red
     remains, owned or cleared (`if self.base and (out["owned"] or out["unowned"])`, `:647`), it rebuilds `alt` at
     the head without the batch (`:654-656`).
   - Overnight the baseline was the red nightly of 10-31 (1f0bb5b3c516; 13 reds). Six reds were cleared by the
     record, and five others still needed the baseline build. Both alt builds then ran, and the second failed:
     "the prepare command failed on the head without the batch".
   - It will keep happening while the last green nightly is old and the head carries known reds.
   - What would remove it:
     - **(i)** a fresh nightly verdict, so the record clears more reds;
     - **(ii)** take the head-without-batch state from the integration store's tree (`W2-00-store`, already
       rebuilt at the head) instead of rebuilding `alt`;
     - **(iii)** seed `alt` from the integration store.
   - Expected after: 0 alt builds in most batches. Only a new red needs the baseline build.
4. **Warm clones in the queue (DEC-1001 (b)).**
   - In force: every attempt logs "warm clone merged reused" (`merge_queue.py:433-466`, `WARM_KEEP` at `:140`).
   - A healthy incremental prepare takes 221–689 s (prepare logs, 11-01 12:08 and 12:34).
   - Weakness: `alt` moves between the baseline (10-31) and the head, so each move re-embeds the difference. A third
     warm clone kept at the baseline would avoid that (estimated). The alt store now holds 41,385 vectors for
     59,378 chunks.
5. **One integration refresh per landing.**
   - Today it runs twice a day plus by hand (`store_refresh_daily.sh`), outside the heavy slots, under the old
     global lock (`refresh_integration_store.sh:16`).
   - Refreshing once after each landing keeps the seed base at most one landing old, which makes lever 1 apply to
     the nightly and to the alt clones.
   - Cost: one incremental build per landing, a few hundred seconds (estimated from the queue's incremental
     prepares). It should go through `rebuild_slot.sh`.
6. **Retire the cold `close_build.py` clones** in favour of the queue, or seed them. This removes 717–8,101 s per
   close.
7. **The retrieval check's dev tiers (row 5)** are embedded cold in a temporary folder on every `gov check`, and
   their 52 queries go cold to the query server. The fix: keep a pre-built store for a-dev and b-dev under the
   workbench, read-only and keyed by tier commit and code, together with its query cache.
8. **Next step: one shared read-only index, with each worktree indexing only its own changes.**
   - Today each tree has its own `.gov-runtime/store.db` (`gov.store.STORE_REL`). Search opens it read-only
     (`semantic._open`, `:224-233`), and `_NEAREST` (`:62-64`) joins `semantic_vector` to `lexical_chunk`.
   - What it would take:
     - **(a)** the base: the integration store's `store.db`, opened read-only (W2-00-store already exists,
       double-buffered);
     - **(b)** an overlay store per tree holding only the chunks of files that differ from the base commit
       (`git diff --name-only base..HEAD` plus untracked indexable files), and a tombstone list for deleted or
       changed paths;
     - **(c)** search runs `_NEAREST` and the lexical query on both stores and merges them, dropping base chunks
       whose path is tombstoned. That touches `semantic.search`/`_status`/`_vectors`, `lexical.search`/`_checked`,
       `fusion.py`, `retrieve.py:125`, and the record store's loader (`store/loader.py`), because the records of
       changed files must also override the base;
     - **(d)** a freshness rule: the overlay is valid against a named base digest. When the base moves, the overlay
       is rebuilt (small).
   - This is a larger change than lever 2, because two stores' answers must equal one store's (the
     context-reproducibility hash).
   - **Lever 2 gives most of the embedding saving at a fraction of the risk.** Lever 8 also saves the lexical,
     secrets and codeintel stages (~60–150 s per rebuild) and the disk.

**Count after levers 1–7, estimated:**

- Per ticket:
  - code-changing tickets: 1 cold build plus incremental ones of seconds to minutes;
  - other tickets: 0 cold builds.
- Per batch: 1 incremental prepare, and alt only for new reds.
- Per day: the nightly seeded.
- With lever 2, even the cold builds embed only the new texts.
- The "5 to 6 rebuilds" may remain in number, but each costs minutes, not an hour.

## c. Faster embedding

**GPU: see the GPU section** (a separate agent is measuring the GPU's throughput, query embedding on the GPU, and the
reranker on the GPU).

The history below is what that section should start from:

- **The shared runner was on the GPU until 04:33 and has been on the CPU since.** All 29 of 29 layers were
  offloaded at the starts at 21:51, 23:56 and 02:36 (`serve-11434.log` line 12 and following, 1,724,901 and
  following, 3,232,541 and following).
- CUDA crashes killed the runner at 23:56:05 and 02:36:44 (`ggml-cuda.cu:108: CUDA error`, "core dumped",
  `serve-11434.log` lines 1,724,865 and 3,232,500).
- At the reload at 04:33:41, only 1,977 MiB of GPU memory was free, with 12,063 MiB "unaccounted" (held by other
  processes). The runner was fitted with **0/29 layers on the GPU**.
- `/api/ps` now reports `size_vram` 1.42 GB of 2.56 GB.
- What holds the GPU memory, likely: the rerankers. `rerank_worker.py:16-17` says "the GPU when there is one". The
  capacity sampler saw up to 15 rerankers at once with 13.7 GB of RSS (`kinds.jsonl`, 11-02), and nvidia-smi now
  lists one `rerank_worker.py` process as the GPU's compute app.

**Throughput by period** (shared runner, my parse of the runner's task lines and the gaps between slot uses):

| Period | Device | Chunks/s (hour's total ÷ 3,600) | Median per chunk | Busy share |
|---|---|---|---|---|
| 11-01 22:00–23:00 | GPU | **44.8** (161,350 chunks) | 19 ms | ~97 % |
| 11-01 23:00 – 11-02 02:00 | GPU | 21.8–32.7 | 21–32 ms | ~86–96 % |
| 11-02 05:00–11:00 | CPU (fallback) | **0.4–1.4** | 122–512 ms (mean 0.54–1.67 s; p90 ~3 s) | ~63–90 % |

On the CPU, a cold stage of 54k chunks would take roughly 11–37 hours (estimated). That explains the
121-second timeouts on every attempt since 04:33.

1. **Batching: what the code does and what larger batches would give.**
   - 32 inputs per request (`semantic.py:50, 259-262`).
   - The runner log shows Ollama 0.35.0 splitting a request into one task per input. They run one at a time through
     the runner's single slot (`launch_slot_` … `release` … "all slots are idle", once per input; runner started
     with `-np 1`). So **a larger batch adds no compute parallelism**. It only saves HTTP round trips, which are
     already small: the first-request load was 8.0 s, and a warm one-text request took 0.03–0.06 s (W2-123 figure 5).
   - Larger batches make each request longer: 32 × 0.5–1.7 s on the CPU is 16–54 s before queueing. That makes the
     120 s timeout more likely, and other clients wait behind the whole batch.
   - The 32-text form is also what is not bit-reproducible (97 of 384 vectors differ, minimum cosine 0.999427;
     P-W2-123-2). Single-text requests were exact on repeat.
   - So the useful changes are the other way:
     - smaller requests (8, or 1) with a per-request timeout and the bounded retry (DEC-1026), at little cost on the
       GPU (estimated);
     - real batching only through a runner that evaluates several sequences in one pass (item 4).
2. **Separating the traffic (who calls which server today).**
   - **Shared 11434** (`OLLAMA_HOST`, default `ollama.DEFAULT_HOST`): every rebuild's semantic stage (rows 1–4 and
     10–15), the retrieval check's dev-tier refreshes (row 5) and the dispatcher's probe (row 16).
   - **Query 11435** (`GOV_QUERY_OLLAMA_HOST`, CPU-only by DEC-798/DEC-975; `semantic.query_vector`, `:172-191`):
     the questions of `gov retrieve`, context-reproducibility and retrieval-regression (rows 6–8).
   - The split by kind is already done. The contention that remains:
     - **(i)** cold rebuilds and incremental ones share one serial runner, so a lead's 30 s incremental build waits
       behind a cold 4,000 s one. A third server just for cold or seeded bulk work, or a priority queue in front
       of the runner, would separate them (estimated);
     - **(ii)** the probe adds one request per pass to the shared queue;
     - **(iii)** both servers are pinned to the same CPUs (item 3).
3. **CPUs for each server.**
   - Both run on CPUs 12–19 at nice 10: `taskset` reads 12-19 for the shared `ollama serve` (pid 414672), its runner
     (pid 216790) and the query server (pid 645918), which has `CUDA_VISIBLE_DEVICES=-1`.
   - The runner reports `n_threads = 10` on 8 permitted CPUs (`serve-11434.log`, `system_info`), so it is
     oversubscribed inside its own set.
   - On the GPU the shared server used 2.1–4.9 cores and never all 8 (W2-123 figure 2). On the CPU it now uses about
     7.5 cores (`dispatch/status.txt` 11:04: "the embedding server 7.54"; capacity sampler p50 7.4 cores on 11-02),
     so it starves the query server on the same CPUs (P-W2-123-3: 54.3 s and 86.8 s per question).
   - Fix (P-W2-123-3 (a)): disjoint CPU sets. For example the shared server keeps 12–19 and the query server gets 2
     CPUs of its own (estimated: a 2-text question takes well under 1 s on 2 idle cores). Also set the runner's
     threads to the size of its set.
4. **Real parallel runners.**
   - Ollama 0.35.0 starts this model with `-np 1` whatever `OLLAMA_NUM_PARALLEL` says (P-W2-123-1, `sched.go:745`).
   - The two routes are:
     - **N `ollama serve` instances on N ports**, with the semantic stage spreading its batches across them. Each
       instance takes 2.2 GiB on the GPU (P-W2-123-1);
     - **`llama-server` started directly** with `-np N` (and continuous batching).
   - The determinism check (S5: single-text requests, float32 byte for byte) refused 3 of 8 overlapping cases in
     W2-123's sweep: 1–4 of 256 vectors differ, minimum cosine 0.9997. The 32-text form already differs at -np 1.
   - So any parallel setting needs the owner to rule first on the tolerance (P-W2-123-2 (b): a cosine floor of
     0.9994) or on single-text requests (P-W2-123-2 (c)). Lever b.2 (the vector cache) shrinks the question:
     vectors computed once are reused, so a small nondeterminism no longer moves between rebuilds.
   - Measured parallel gain: none yet. W2-123's rows differ only by machine load (three at once in total 21.3–40.5
     chunks/s against 23.3–33.7 alone). An instance per GPU slot is estimated to scale until the GPU saturates; the
     GPU section has the figures.

## d. How many agents at once, once b and c are in

**Measured peaks:**

- **Leads** (`dispatch/peaks.json`, computed 11-02 10:26 over 7 days; `lead-mem.jsonl`):
  - a lead's RSS: p95 4,085 MB (18,829 samples), max 9,581 MB;
  - outside verification: p95 2,275 MB (365 samples), max 4,924 MB;
  - inside verification: p95 3,935 MB;
  - one slot run: 1,660 MB (`slot_run_kb`).
- **Daily lead-memory peaks** (`lead-mem.jsonl`): the most leads at once was 7–8 on 10-29 to 11-01, with all leads
  together at most 13.7–14.3 GB. On 11-02 it was 5 leads and 7.0 GB.
- **Kinds** (`peaks.json` `kinds`, p95):
  - test_run 16.8 cores and 3,854 MB;
  - embedding 8.1 cores and 2,920 MB;
  - rebuild with embedding 15.3 cores;
  - rerankers 9,663 MB (all of them together);
  - other 3,948 MB; claude 2,662 MB.
- **Machine load** (`kinds.jsonl`): load1 p50 35/18/21 and p95 78/76/53 on 10-31, 11-01 and 11-02 (20 threads).
  MemAvailable fell to 4.8, 4.3 and 3.8 GB.
- **Fixed limits:**
  - 3 heavy slots × 6 workers (`heavy_slots.conf`);
  - the gate's floor is 3 GiB (`gate-config.json` `floor_kb` 3,145,728);
  - the dispatcher's CPU rule allows slots × K = 3 × 2 = **6 leads** (`dispatcher.py:616`, `config.json` K 2);
  - CPU margin 2 (`:286, :602`).

**What admission does today** (`dispatcher.py:594-657`; `dispatch/status.txt` 11:04):

1. **Real CPU first:** busy cores plus the embedding server's p95 headroom must stay below 20 − 2.
2. **No admission** while any heavy step has run outside a slot for over 5 minutes. At 11:04 this held everything:
   "a heavy step runs outside a slot over 5 min: … gov.retrieval.retrieve_check (… 25 min, W2-61h)". That is `gov
   check`'s retrieval family run without `heavy_slot.sh`, against the brief's rule (`LEAD-w2-common.md:64`).
3. **Leads under 6.**
4. **Memory:**
   - The rule: available memory plus the leads' current memory must reach the floor, plus each running lead at its
     p95 or its own max, plus the newcomer, plus 3 slot runs at 1,660 MB, plus the services' headroom (the
     embedding, codegraph and outside rerankers' p95 above what they hold now).
   - At 11:04: 4 leads running, 17.3 GB available, the gate open.

**Recommended concurrency once b and c are in** (estimated from the figures above):

- **Memory** (24.0 GB):
  - fixed: floor 3.0 + 3 slot runs 5.0 + embedding 2.9 + other and claude about 4–6, which leaves about 7–9 GB for
    leads;
  - at the outside p95 of 2.3 GB that is **3–4 leads**, and at the all-samples p95 of 4.1 GB it is 2;
  - rerankers are the swing factor: up to 13.7 GB RSS at 15 at once. Capping rerankers (one per tree, or one shared
    worker) is the precondition for more than 4 leads.
- **CPU** (20 threads):
  - with the embedder on the GPU (2–5 cores, W2-123) and 3 slots × 6 workers, the test slots alone fill about 18 of
    20;
  - with the embedder on the CPU (7.5–8.1 cores) the machine is oversubscribed at 3 slots. **While the embedder is
    on the CPU, run 2 slots, not 3.**
- **Together:** 3–4 leads (6 is the rule's cap today), plus 1 queue run (it holds a priority slot,
  `heavy_slot.sh:19-23`, DEC-1011), plus at most 1 close. The total of heavy jobs stays at the 3 slots.
- After lever b.2 and the GPU fix, rebuild minutes stop being the queue's bottleneck. The binding limits then become
  memory (leads and rerankers) and the test slots, not embedding.

**Dispatcher changes that would hold it there:**

- **Health probe:**
  - judge the embedder by progress, not by one request's latency: runner tasks completed per minute (the log's
    `launch_slot_` lines or `/proc` CPU of the runner), and queue age;
  - flag HUNG only when no task completes for N minutes;
  - probe less often (`embed_check_every` > 1, the probe on the query server or a 1-text call to `/api/ps`), so the
    probe is not itself queued work.
- **Embedding backlog as an admission input:** refuse a new lead or a cold rebuild while the shared runner's backlog
  exceeds a threshold, or while it reports 0 GPU layers (`/api/ps` `size_vram` against `size`, or the runner log's
  "offloaded 0/29"), and alert in that case. Last night the fallback went unnoticed for 6 hours.
- **Slots follow the embedder's device:** SLOTS = 3 when the embedder is on the GPU, 2 when it is on the CPU.
- **Rerankers:** count them in admission by their GPU memory as well as their RSS. Cap them machine-wide.
- **K = 2 → derived:** the lead cap from memory (3–4), not from slots × K = 6.
- **Steps outside a slot:** keep the refusal, but make the lead-side tools wrap `gov check` families in
  `heavy_slot.sh` automatically, so one lead's mistake does not freeze every admission.

## Open questions I could not settle

1. **What holds 12 GB of GPU memory at 04:33.** The rerankers are likely, but nvidia-smi does not attribute memory
   under WSL ("[N/A]"). This is for the GPU section.
2. **Embedding history before 2026-11-01 21:51.** The Ollama logs were reset at the restart, so daily request
   counts exist for about 13 hours only.
3. **The chunk counts of the a-dev and b-dev tiers per `gov check`,** and how many real-embedding calls the test
   suite makes. I did not measure them; doing so needs runs that load the machine.
4. **Whether a seeded base whose code differs only outside the chunker, embedder and secrets filter could be
   accepted safely.** This is W2-122's fingerprint policy. Lever b.2 sidesteps it.
5. **Whether `llama-server -np N` with batched sequences gives the same vectors within the 0.9994 floor.** It has
   not been measured. It needs the owner's tolerance ruling first (P-W2-123-2).
6. **Why the merged clone needed 3,142 s on 11-01 21:56 despite being warm.** Earlier failed attempts and a moved
   base are likely, but I did not establish the store's state before that run.
