# W2-04 (DAEO-u4oz) — resume after P-W2-04-2 and P-W2-04-3 (DEC-1005, delegated)

**Read this first; it overrides the steps below where they differ.** The CTO decided:
- **P-W2-04-2 (A):** keep the semantic-free lexical block. One fresh test-design batch (a tests worktree, effort
  xhigh) revises, in this ticket, W2-54's 17 cases and W1-41's 2 as your package lists them (dropped_order's hook to
  what the packet shows, TK-W254-BIG's budget, the over-ceiling case expecting `CONTEXT_OVER_CEILING`; the
  cpu_embedder, query_cache and query_vector steps to `gov retrieve`; W1-41's equality without `ticket_text` and its
  key set with the three new keys), and this ticket's own 4 cases with P-1 re-read, each file's commit carrying
  `Rewrite-Reason: W2-04's KPIs 2 and 4 (CAP-15.d, DEC-860), DEC-1005`, no expectation lowered. In parallel, the
  engineer adds the packet key `supplementary_batches` (one batch is one of the context's own lookups).
- **P-W2-04-3 (b):** a dependency ticket counts by its front matter (id, status, title, KPI lines), as CAP-15.b asks;
  the engineer, about 20 lines, in the same batch.
- Your P3 calls stand. The needed tickets you named (W2-M133's provenance `inputs_hash`, W2-M126's measured hit rate,
  a multi-word lexical search with one freshness check, the authority lift in the supplementary block) go to the owner
  as P1s from the CTO (DEC-974): do nothing for them.
- Then: merge the tests while no worker runs, `gov accept` once, the rebuild
  (`bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/rebuild_slot.sh <tree>`,
  DEC-1001), the scoped run once, `gov check`, the review (independent-auditor, effort max), the probe record on a
  pass; return DONE with the exact head. W2-54's sandboxed_worker red on the base is not yours (W2-90b's).

---

