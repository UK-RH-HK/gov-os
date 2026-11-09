---
name: retrieval
description: Method for running gov retrieve — facet retrieval in disposable subagents with validated bundle return
version: "1.0.0"
---

# Retrieval

A method for gathering evidence with `gov retrieve`. The guard and the role file decide what the caller may read and write (CAP-24.b); this skill is the method only.

## How retrieval works

1. **Invoke `gov retrieve`.** Pass the query, the ticket id (`--ticket`), any record or symbol ids to close over (`--id`), and the impact radius (`--radius 0..4`). The radius scales the follow-up rounds (DEC-035, CAP-16).

2. **Facets run in disposable subagents.** Each retrieval facet (lexical, semantic, closure) runs inside a disposable subagent whose context is thrown away when the facet finishes (DEC-032). Only the validated, cited bundle returns to the caller. Intermediate retrieval batches stay in the subagent and never appear in the main context (CAP-56).

3. **Merge, dedup and rerank.** The facet results are fused by reciprocal-rank fusion, deduplicated by chunk hash, and reranked in one pass over the merged set. The bundle names the routes and the expansions (CAP-16).

4. **Stopping reasons.** Every bundle carries exactly one stopping reason from the fixed list: `CLOSURE_COMPLETE`, `SATURATED`, `DEPTH_LIMIT_REACHED`, `BUDGET_EXHAUSTED_WITH_GAPS`, `FACET_UNAVAILABLE` or `UNRESOLVED_IDS`. A batch-size limit is never reported as completeness (DEC-034).

5. **Validate the bundle.** Before using evidence, check that the bundle has a stopping reason, that each citation has an `id` and `sha256`, and that no citation references a superseded record (CAP-16, DEC-032).

6. **Handle continuation.** If the bundle carries a continuation token and the stopping reason is not `CLOSURE_COMPLETE` or `SATURATED`, pass the token back with `--continue` to gather more evidence within the spend budget.

## Key constraints

- **Disposable subagent context.** The facet subagents are throwaway: their internal state, partial results and scratch work do not leak to the implementing context. The caller receives only the final bundle (DEC-032, CAP-56).
- **Radius-scaled rounds.** The spend budget scales with the radius; it is separate from the packet ceiling (CAP-16).
- **Failure and lesson records ahead.** When a ticket is given, failure and lesson records in its scope come ahead in the evidence list (CAP-14).
- **Authority filter.** Superseded, deprecated, rejected and withdrawn records are never cited as current (CAP-51).
