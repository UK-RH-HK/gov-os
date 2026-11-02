# W2-123 (DAEO-qzrq) — run 2: the rebuild retries a timed-out embedding request, bounded (DEC-1026, delegated)

**Read this first; it overrides the steps below where they differ.** Your run 1 returned DONE at `9bb92097c811`
(head must show it, tree clean; else return PACKAGES naming it). It was approved to land, but every landing since
04:37 failed the same way: `src/gov/retrieval/semantic.py` gives each embedding request `TIMEOUT_S = 120.0` and no
retry, so one batch queued behind another client on the one-at-a-time shared server ends the semantic stage
`not_recreated` (07:56: `semantic_s` 120.9). Your ticket now holds `semantic.py` and one new KPI line (ticket commit
`4c3f3ecd`, DEC-1026):
> a rebuild's embedding request that times out behind other clients is retried, bounded (at most three tries with a
> growing wait, each under the existing per-request timeout), and the semantic stage still ends `not_recreated`, named,
> after the last failed try: never a partial store reported as built; the tries and waits are stated in the result.
**Steps:** (1) merge `w2/integrate` first (`--no-ff`, `Task: DAEO-qzrq`, `Role: orchestrator`): the ticket file changed
there. (2) In parallel (DEC-959 item 7, DEC-963): a test designer in `~/gov-os-worktrees/W2-123-tests` adds this KPI
line's cases (a stand-in endpoint that times out once, twice, three times; never the real server); a fresh engineer
builds it in `semantic.py` to the spec, never to the tests, with its own unit tests. (3) Merge the tests, `gov accept`
(all lines), the scoped run once in a heavy-job slot, output outside the worktree; no new measure of KPI 3. (4) Return
DONE with the exact head. Keep it small (about 15 lines of product code): this unblocks eight tickets' landing.
P-W2-123-1 to -3 stay with the owner.

---

