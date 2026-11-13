# W2-155 (DAEO-ar89): the warm real-model query path profiled against W1-19's 0.5 s budget

Lead, run 1, 2026-11-12 23:49 to 00:05 GMT, head `0ea583eb6` (w2/integrate merged). No source change.

## Method
- The measured call, as W1-19's timed pass and W2-13's real-model case make it: `fusion.search(root, q, limit=None, refresh=False)` on a fresh clone of each dev tier (`a-dev`, `b-dev`, W1-19's `clone_tier`), the index built by `semantic.refresh`, the three warm-up questions, then each of the 52 dev queries once, in one process.
- Each stage timed by wrapping its module attribute (`perf_counter`), plus cProfile over the timed queries; every rerank request's text count, longest pair, padded size and round trip recorded.
- Through `heavy_slot.sh` (slot waited for), `TMPDIR=/tmp/w2-155-prof`, `HF_HUB_OFFLINE=1`. The live shared reranker (pid 32310, the pinned install `pin-797495bdfc70`, `cuda:0`) and the live query embedder: none started, none restarted.
- Machine load (1-min load average) during the runs: 8.2 to 11.3 out of 20 CPUs: **not idle**. The scripts are `profile_warm.py` and `bench_service.py`, kept beside this note.

## Where the time goes (run 235507; 52 queries; whole chunks as the code reads them)
| stage | mean s | p95 s | calls per query |
|---|---|---|---|
| lexical route (`lexical.search`: freshness `_checked` x2 with 2 `git` calls, BM25 `_ranked`) | 0.004 | 0.006 | 1 |
| semantic route (`semantic.search`: `_status` 0.003, `_ready` + `ensure_query_available` 0.001, `query_vector` 0.006 (vector cache), the sqlite-vec query) | 0.011 | 0.017 | 1 |
| RRF fusion and `_records` (one read-only sqlite connection) | 0.001 | 0.001 | 1 |
| **rerank: the shared service's round trips** | **0.332** | **0.525** | 1 (1.88 requests) |
| **total** | **0.348** | **0.538** | |
- Everything except the rerank: p95 0.021 s. **The rerank is 95 % of the time**; cProfile puts 17.9 s of 18.8 s in the socket's `recv_into`, waiting for the service.
- A first run (fresh clones, run 235032) gave p95 0.564 s, mean 0.362 s: the same split.

## The live service's time by request shape (5 requests each, median ms)
| texts x characters | 1 x 10 | 1 x 600 | 16 x 600 | 30 x 600 | 33 x 600 | 15 x 1300 | 18 x 1300 | 30 x 1300 |
|---|---|---|---|---|---|---|---|---|
| ms | 85 (min 62) | 92 | 125 | 146 | 212 | 141 | 156 | 255 |
- **A fixed cost of about 60-85 ms per model forward**, whatever its size: a request of one 10-character text takes 62-85 ms, and 33 texts (two of `CrossEncoder.predict`'s batches of 32) take about 65 ms more than 30. So each extra request a search sends costs about 60-85 ms before any scoring.
- Note: the 30 x 1300 shape (39,000 padded characters) is above the client's 24,000 bound; five such requests were sent to the live service (no error, no fallback).

## The retrieval changes since the budget last held (W1-19's close, 2026-10-06: p95 0.317 s)
| change | what it does to the warm query | time it adds (measured here) |
|---|---|---|
| **W2-32 S7 (DEC-1067 (f), 2026-11-04):** the reranker reads the whole chunk (`RERANK_LIMIT_CHARS` 500 -> 24,000) under the padded request bound (`MAX_REQUEST_CHARS` 24,000 = count x longest pair) | 46 of 52 queries now send **2 requests** (1.88 a query, 15.9 texts each) instead of 1 of 30; longer texts | **+0.098 s mean, +0.177 s p95**: the same run with the read at 500 characters (probe-only patch) gives p95 **0.361 s**, mean 0.250 s, 1.0 request a query |
| W2-112 (DEC-1068, re-pin window 4): the service empties the GPU cache after every request | the next request's allocations made afresh; estimated "a few ms", never measured (memory: not found) | part of the 60-85 ms fixed cost a request; not separable without a service copy on the GPU (not run) |
| W2-112 / DEC-982, W2-145: one shared service over a Unix socket, no private reranker | connect + JSON | < 0.001 s |
| W2-137 (DEC-1090 (2)): request cap 16 -> 64 texts | fewer requests (helps) | 0 (the char bound now binds, not the count) |
| DEC-773 / DEC-782 / DEC-798, W2-32 S10: the query embedder on the GPU, the query-vector cache | `query_vector` | 0.006 s mean (0.012 p95) |
| W2-108, W2-138 (dcda27011): freshness keyed per process, the store's commit in results | `lexical._checked` twice, 2 `git` calls | 0.005 s mean |
| W2-13 (DEC-725): the ranked BM25 lexical route | `_ranked` | 0.001 s mean |

## Conclusion: no simple cause within the ticket's authority
The cause is identified: the second reranker request per query that W2-32 S7's whole-chunk read creates under the 24,000-character padded bound, at a fixed 60-85 ms per model forward on the live service. Every remedy either changes the results (scores or order) or changes a decided bound or a decided service behaviour, and a service-side change reaches the live service only at the next re-pin. The Interface forbids a result change; DEC-1067 (f) and DEC-1068 are decided. So no fix is made; the budget and the cases are unchanged (DEC-105).

## Options for the owner (DEC-105: apply now, defer or re-baseline)
1. **Raise the padded request bound so a search's 30 candidates go in one request** (e.g. `MAX_REQUEST_CHARS` 24,000 -> 48,000; changes DEC-1067 (f), CTO's GPU bound). Same scores (one batch instead of two). Estimated p95 about 0.45 s (from the measured per-request fit; not measured end to end). Cost: about 1 engineer-hour + a GPU window to read the per-request peak (the service releases after each request since window 4); a larger padded peak per request. Live at the next re-pin only for the bound (client side, so live as soon as the pin moves). **Recommended, confidence medium.**
2. **Measure the release's cost (DEC-1068), then release only above a reserved threshold** (e.g. reserved > model + 2 GB). Cost: one GPU window with a service copy, then about 1 hour; memory still bounded. Saves an unknown share of the 60-85 ms per request. Live at the re-pin.
3. **A shorter reranker read** (e.g. 2,000 characters; 500 measured p95 0.361 s). Changes scores and order: needs the hit@5/MRR re-measure (DEC-1125 (2)'s audit); reverses part of W2-32 S7's quality decision.
4. **Half precision (bf16) in the service.** Faster forwards; scores change slightly (order on near ties); hit@5 re-measure; live at the re-pin; about 2 hours + a GPU window.
5. **Re-baseline the budget** (e.g. 0.6 s p95), or **defer** (keep it a named red; the owner's note: the gap is not noticeable and does no harm). No cost now.

## Run 2 (2026-11-13 00:35-01:51 GMT): option 1 applied, measured slower, reverted
- **GPU reading (DEC-1159 (2), 00:37, GPU 0 %, the only request in rerank.log):** one request of 2 pairs x 24,000 (48,000 padded, the bound's worst case): peak 9,639 MiB from 8,255 (+1,384 MiB), back to 8,255 after; budget 14,255 (16,303 - 2,048): within. `gpu-reading-2x24000.json`, `.smi.csv`.
- **The change** (eng-1, 49f5ec46f): `MAX_REQUEST_CHARS` 48,000, the pair read kept at 24,000 (`MAX_PAIR_CHARS`, `fusion.RERANK_LIMIT_CHARS`), so results were unchanged; unit cases green.
- **W1-19's and W2-13's warm real-model cases on 49f5ec46f** (through heavy_slot.sh, 01:33-01:46, load 4-16, not idle): W1-19 p95 **0.757 s** (52), W2-13 p95 **0.843 s** (52): both red, worse than 0.543/0.587; W1-19's 2.5 GB rerank case passed. `latency-013043/`.
- **A/B, same clones, alternating, one heavy slot, 01:48-01:50 (load 11-15):**

| bound | round | p95 s | mean s | requests | median request s | padded / real chars |
|---|---|---|---|---|---|---|
| 48,000 | 1 | 0.790 | 0.460 | 52 | | |
| 24,000 | 1 | 0.571 | 0.378 | 98 | | |
| 48,000 | 2 | 0.757 | 0.465 | 52 | 0.355 | 3.03 |
| 24,000 | 2 | 0.554 | 0.353 | 98 | 0.161 | 2.15 |

- **Cause:** the real candidates differ in length (30 texts ~11,400 characters, longest ~1,270). One request pads all 30 to the longest; the 24,000 grouping (longest first) puts the short ones in a second, short request. The forward's cost follows the padded size, which outweighs the ~70 ms fixed cost a request saves. Run 1's bench used equal-length texts and missed it: option 1's premise (faster, about 0.45 s) is disproved.
- **Done:** 49f5ec46f reverted (8da607e3d); the branch's code equals w2/integrate's; the budget and the cases untouched (DEC-105).

## Options for the owner (run 2)
A. **Option 5: keep the warm p95 a named red; close W2-155 on this evidence** (no cost; the owner's note: not noticeable). **Recommended, confidence high.**
B. **Length-aware grouping in the client:** split a search's candidates where the padding saved exceeds a request's fixed cost (e.g. three requests by length band). Same scores. Not measured; at best about 0.05 s off the mean; about 1-2 engineer-hours + an A/B; a new ticket.
C. **Length-sorted batches inside the service** (the model pads per internal batch): service change, live only at the next re-pin; same scores; about 2 hours + a GPU window.
D. Run 1's options 2 (release threshold), 3 (shorter read: changes scores), 4 (bf16: changes scores) stand as they were.
