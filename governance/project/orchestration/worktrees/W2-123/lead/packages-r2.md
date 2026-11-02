# W2-123 run 2: package P-W2-123-4 (does not block this ticket's landing)

## P-W2-123-4: a rebuild's embedding request that fails without timing out (transient) is not retried

1. **Context.** DEC-1026 gave W2-123 one KPI line: a *timed-out* embedding request is retried, at most three tries with
   a growing wait. Run 2 built exactly that (181bb54c0050), and the lead's interface spec (R1) kept every other failure
   as before: no retry, the stage ends `not_recreated` with the bare `NO_EMBEDDING`.
2. **What happened.** The lead's verification rebuild of this worktree (2026-11-02 10:39-11:12 UTC, this branch's code,
   three rebuilds at once on the shared server: W2-04's, this one and a third) embedded for 1,896.5 s and then ended
   `semantic: not_recreated` with the bare `Ollama did not embed with qwen3-embedding:0.6b`. A time-out would have
   given the retry's own reason, so the failing request was *not* a time-out: an HTTP error, a dropped connection, or
   an answer without a vector for each text (the shared server's log goes to /dev/null, so which one is unknown). The
   shared server (pid 414672, up since 2026-11-01 22:46) was never restarted, and no restart record exists. The same
   batch, sent once by the lead minutes later, answered in 2.6 s with 32/32 finite vectors, and the next rebuild
   (incremental) ended `recreated` (semantic 144.7 s). So the failure was transient and did not depend on the content.
3. **Why it matters.** The batch's landing rebuild runs while other clients use the one-at-a-time shared server. Run
   2 removes the failure seen at 07:56 (a time-out at 120 s), but a transient non-timeout failure ends the semantic
   stage the same way and would fail a landing again. The stage still fails closed (named, never a partial store
   reported as built), so this is lost time, not a hole.
4. **Options.**
   - (a) **Land run 2 as it is, and record a Wave 3 row** for the non-timeout failures. Cost: none now. Risk: a landing
     may fail again on a transient error, though less often than on the time-outs.
   - (b) **A run 3 of about 3 product lines:** also retry, within the same three tries and waits, an HTTP 5xx answer
     and a connection reset or remote close (`http.client.RemoteDisconnected`, `ConnectionResetError`) on a chunk batch.
     A 4xx, a non-JSON answer and a missing vector are still not retried. This changes the KPI line ("times out" becomes
     "times out or fails transiently"), which is P2 under DEC-957 (CTO). Cost: about one hour (test designer and
     engineer in parallel, gov accept, the scoped run). Risk: low; it fails closed the same way.
   - (c) **Keep the shared server's log** (stderr to a file instead of /dev/null in `ensure_available`, in this
     ticket's paths) so the next failure is named. Cost: about 2 lines. It does not prevent the failure.
5. **Recommendation.** (a) now, so the eight tickets land, with (b) and (c) together as one follow-up (a new ticket
   or W2-123 run 3, DEC-974: for the owner or the CTO to file). Confidence medium: one failure seen, its exact kind
   unknown.
6. **What it blocks.** Nothing in this ticket. Waiting risks another failed landing, which the landing's own retry of
   the rebuild (an incremental rebuild embeds only what is missing) recovers in minutes, as the lead's second rebuild did.

## P-W2-123-5: the DEC-1032 line (the query server's start no longer hides the GPU), asked at 12:4x by the CTO

1. **Context.** The CTO added a success line to the ticket on w2/integrate (b0156a41): `ensure_query_available` stops
   hiding the GPU; W2-54's `test_w2_54_cpu_embedder.py` is revised with `Rewrite-Reason: DEC-1032`. The CTO's message
   said to return PACKAGES if it doesn't fit run 2; the retry stays the priority.
2. **What I found.** `src/gov/retrieval/semantic.py` (w2/integrate, lines 117-188, this ticket's path and W2-126's
   too) uses a question's vector only when the query server's `/api/ps` reports the model wholly on the CPU
   (`size_vram == 0`); otherwise `NOT_ON_CPU` and no semantic hit. With the query server on the GPU (the owner's
   ACT-QUERY-GPU-1, or the code's own start once the line is built), every question not already in the vector cache
   loses the semantic facet on every tree. The new line alone doesn't change that gate. Run 1's own acceptance tests
   (the query server's hidden GPU, KPI success-7 "the query server CPU-only") would need revising with it.
   At 12:5x the live query server (pid 645918) was still on the CPU.
3. **Why it matters.** Built as written, the line silently switches off semantic retrieval for new questions. Built
   with the gate change, it is a spec change (what replaces DEC-798's single-vector-on-CPU guarantee) touching
   W2-126's file.
4. **Options.** (a) Land run 2 now; the DEC-1032 line plus the `_on_cpu` gate as one follow-up (W2-123 run 3 or
   folded into W2-126), the ACT held until it lands. Cost: about one round later; no delay to the eight landings.
   (b) Stretch run 2: merge w2/integrate again, a test designer (W2-54 rewrite, run 1's GPU-hidden cases, new
   cases), an engineer (ollama.py, and semantic.py's gate if decided), a new scoped run. Cost: at least 1.5-2 h on
   the frozen, slow machine, plus a spec decision on the gate first. (c) Build only the start's change now, gate
   untouched. Not recommended: it fails quietly (no semantic hits).
5. **Recommendation.** (a), confidence high. Sent to the CTO by message at the time.
6. **What it blocks.** Nothing in run 2. Note: w2/integrate's ticket file has success-8 with no mapped test, which
   the close's per-line accept may report.

Runs 1's packages P-W2-123-1 to -3 stay with the owner (packages.md).
