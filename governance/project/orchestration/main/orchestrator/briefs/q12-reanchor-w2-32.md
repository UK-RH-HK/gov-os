# Re-anchor the visible question q12 at W2-32's round 2 (DEC-1069 (6), DEC-1070 (14); RUBRIC.md R6, R10)

You are an independent test designer for the CTO, independent of the retrieval work. You change one file of the
memory measure's visible half, and only as the rubric allows.

**Why:** the CTO's measure clone at `w2/W2-32` `9446d322` (W2-32's S11 round 2: the continuation token now carries
the pool's order, with new refusals) stops at its anchor check: `repin_gold.py` reports
`UNRESOLVED q12.yaml entry 1`. q12's gold source is in `src/gov/retrieval/retrieve.py`, which round 2 changed.

**Read:** `docs/research/memory-measure-audit/RUBRIC.md` (version 2) sections 1 and 2 (R1, R6, R7, R10, R11 above all);
`fixtures/evaluation/memory-retrieval/visible/q12.yaml`; and the code at the branch's head, in the worktree
`/home/usain/gov-os-worktrees/W2-32` (read only; `src/gov/retrieval/retrieve.py`, `pool.py`). Never read any run or
measure output, the hidden questions, or the research records about misses.

**Do:**
1. Find where the fact q12 asks now lives at that head.
2. If the same fact holds and only moved or was split: re-anchor (same fact, new span: `heading` one whole line found
   once, `lines` as the rubric says), with the reason in the commit.
3. If the fact itself changed (for example, the refusals q12's gold answer lists now include new cases): re-label by
   R1 so the gold answer and its sources hold at the head, keep the old file as
   `fixtures/evaluation/memory-retrieval/retired/q12-pre-w2-32-r2.yaml`, and say so. Never change the question's text.
   If the question no longer has one clear answer, stop and say so (R3, R11); do not rewrite it.
4. Check: `python3 /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/d4b/repin_gold.py
   /home/usain/gov-os-worktrees/W2-32-tests/fixtures/evaluation/memory-retrieval/visible /home/usain/gov-os-worktrees/W2-32`
   prints `unresolved: 0`.

**Where:** the worktree `/home/usain/gov-os-worktrees/W2-32-tests` (branch `w2/W2-32-tests`). Commit only
`fixtures/evaluation/memory-retrieval/visible/q12.yaml` (and the retired copy if any), with `Task: DAEO-0pyc`,
`Implements: DEC-1069`, `Role: independent-test-designer`, `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
Never merge, push, amend or rebase.

**Return:** status, re-anchor or re-label and why in general terms, the check's line, the commit. Est.: 20 minutes.
