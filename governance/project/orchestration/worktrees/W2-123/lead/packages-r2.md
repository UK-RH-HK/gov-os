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

Runs 1's packages P-W2-123-1 to -3 stay with the owner (packages.md).
