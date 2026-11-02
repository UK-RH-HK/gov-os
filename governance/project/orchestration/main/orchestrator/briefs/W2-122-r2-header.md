# W2-122 (DAEO-blwa) — run 2: the seeding lands without KPI 5 (DEC-1027 C, the owner's decision)

**Read this first; it overrides the steps below where they differ.** Your run 1 returned PACKAGES at `bd50a9581893`
(head must show it, tree clean; else return PACKAGES naming it). The owner decided P-W2-122-K5 (c): KPI 5 (a rebuild
without its semantic store fails) moves to its own ticket, W2-124 (`DAEO-mb2t`), with the owner's rule that adoption
never fails for a missing embedder; your ticket file no longer holds it (`42dad22d`). So:
1. Merge `w2/integrate` first (`--no-ff`, `Task: DAEO-blwa`, `Role: orchestrator`): the ticket file changed there.
2. In parallel: a test designer in `~/gov-os-worktrees/W2-122-tests` retires your 4 K5 cases (and their README map
   lines) with `Rewrite-Reason: DEC-1027 C`, nothing else lowered; a fresh engineer takes the K5 behaviour out of your
   change (`REBUILD_FAILED` with `store: semantic`), so a rebuild without its semantic store answers as it did at your
   base. The seed itself is untouched. P-W2-122-TD-2, -FP and -IF stand as you read them; P-W2-122-CG's follow-up is
   parked (no new ticket now).
3. `gov accept` (all remaining lines), then the scoped run once in a heavy-job slot, output outside the worktree. The
   100 earlier cases should be green again; name any that are not.
4. Return DONE with the exact head. It lands with the waiting batch.

---

