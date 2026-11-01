# P-RERANKER-1: one shared reranker for every session, before the three layers (P1, a new ticket, DEC-974, DEC-979 item 4)

For the owner. A proposal to file one ticket (W2-112), not yet filed.

## 1. Context

- Every `gov retrieve` that reranks starts its own reranker: `gov.retrieval.rerank._started` launches `rerank_worker.py` as a child process from `~/.local/share/gov-os/reranker-venv` (the pinned `Qwen/Qwen3-Reranker-0.6B` at revision `e61197ed…`, ADR-0002 §2, DEC-397). The child loads the model once and lives as long as the process that started it; it answers one line `[query, [text, …]]` with one line of scores.
- If the reranker cannot be loaded (the environment or the snapshot is absent), the search keeps its fused order and no candidate carries a score (DEC-374). The search never fails for want of a reranker.
- Measured on 2026-10-31 (CAPACITY-1 §1): 1 to 9 reranker processes at once, 1.2 GiB each (up to 2.0), 3.5 GiB on average and **9.4 GiB at peak**, of a WSL machine of 24 GiB.

## 2. What happens with the three layers

About 29 sessions (the CTO, about 4 senior engineers, about 8 leads, about 2 workers each), about 10 searching at once: 12 to 18 GiB of rerankers alone, about 31 to 37 GiB in all, which does not fit 24 GiB (CAPACITY-1 §3). With one shared reranker, about 21 GiB, which fits.

## 3. Why it matters

Without it, the three layers either run out of memory (the machine swaps, the out-of-memory killer ends sessions: work lost) or must be held to fewer sessions than the plan needs. The three layers start after ACT 2, so the ticket must land before them.

## 4. The proposal: W2-112, "One reranker serves every session"

**How it serves many sessions at once:**
- **One process per machine:** the same pinned model, revision and environment as today, run as a small service that listens on a local socket in the user's own folder (`~/.cache/gov-os/rerank.sock`, mode 0600; no network port). It is started on demand by the first search that needs it, under a lock so that two searches starting together start one service (as `gov` starts `ollama serve` on demand today), and it ends itself after a set idle time (for example 15 minutes).
- **Many callers, one model:** each search sends its one request (`[query, [text, …]]`, as today) and waits for its own answer. The service queues requests first come, first served; it may score the pairs of several waiting requests in one model call, up to a set number of pairs, and gives each caller its own scores. A request has a cap on its texts (the bundle's candidate limit) and a time limit.
- **The same answers:** the same model, revision and device as a private reranker, so the order and the scores match a private reranker's on the same inputs (within float rounding; ties keep the given order). Measured on the 20 visible questions and, after W2-61h, the 48.
- **Memory:** one model in memory, about 1.2 to 2 GiB, instead of up to 9.4 GiB today and 12 to 18 GiB with the three layers.

**What searches fall back to if it is down** (it cannot start, does not answer within its connect time of about 2 s, or answers with an error):
1. **A private reranker, as today**, for that search's process: the same model, so the same answers, at today's memory cost for that one process. This is the default.
2. **Where a private reranker cannot start either** (a sandboxed worker without the reranker environment, or the machine's memory floor reached): **no rerank**, the fused order kept and the bundle marked `rerank: unavailable` (today's DEC-374 behaviour), so the agent knows the order is unranked.
- A search never fails or hangs because of the service. Each fallback is logged, and `gov status` counts the searches that fell back.

**KPIs (for the test designer):** many sessions at once (for example 20 concurrent searches) are answered by one process, each with its own scores, in order; the answers match a private reranker's; with the service killed mid-run, every search still answers (by fallback 1 or 2) within its time limit; two searches starting together start one service; the socket is the user's alone; memory measured before and after with 10 concurrent searches.

**Profile FULL** (concurrency and a fallback path). **Paths:** `src/gov/retrieval/rerank.py`, `rerank_worker.py` and a new `rerank_service.py`; `tests/unit/retrieval/test_w2_112*`. **Order:** W2-32 holds `src/gov/retrieval/**` (its model pin and swap touch `rerank.py`), so W2-112 starts after W2-32, before ACT 2 and the three layers; it rides on memory's chain without holding it. **Estimate:** about 200 lines, 6 to 8 hours.

**Later, not in this ticket:** the service on the GPU (about 13 GB of its 16 GB free). That frees the memory and CPU further, but needs the same GPU-against-CPU determinism test that W2-15b now carries for the embedder (DEC-975).

## 5. Options

- **(a) File W2-112 as proposed**, after W2-32 and before ACT 2 *(recommended, high confidence)*.
- (b) File it with the GPU from the start: more gain, but its determinism is unmeasured; it waits for W2-15b's GPU-against-CPU result.
- (c) No shared reranker: cap the number of searches at once instead. Cheaper to build, but sessions wait for each other's searches, and the cap would have to stay low (about 4 or 5) to fit the three layers.

## 6. What it blocks, and what waiting costs

It blocks the three layers (they do not fit without it). Waiting costs nothing until W2-32 is done; deciding now lets the test designer write its tests in parallel with W2-32.
