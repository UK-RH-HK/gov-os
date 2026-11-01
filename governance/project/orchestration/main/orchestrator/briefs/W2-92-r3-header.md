# W2-92 (DAEO-n0wb) — run 3 after P-W2-92-5 (DEC-1019, delegated)

**Read this first; it overrides the steps below where they differ.** Your run 2 returned PACKAGES at `ac960862cfe7`;
`git rev-parse --short=12 HEAD` must show it and `git status --short` nothing, or stop and return PACKAGES naming it.
The CTO decided P-W2-92-5 as you recommended:
- **P-W2-92-5 (a) (DEC-1019):** keep P-1's soft read, and when the record graph cannot be read, cite no evidence from a
  record file and say so in the closure facet, so a superseded or must-not-cite record is never cited as current
  (DEC-423). W1-21's `test_without_a_record_graph_no_superseded_record_is_cited_as_current` and your f3 must both
  pass; W1-21's test is not touched. If (a) cannot pass both, return PACKAGES with (b) costed; do not apply (b) alone.
- Then follow your own checkpoint's "Run 3": one engineer batch in `retrieve.py` (scope as in DEC-1006), the rebuild
  (`bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/rebuild_slot.sh <tree>`),
  `gov check`, the scoped run once, `gov accept`; no re-measure (say so in the return); return DONE with the exact head.
- **Every heavy step in a slot:** the acceptance suite and the scoped run go through `verify_lock.sh` (heavy-job
  slots, DEC-983); in run 2 one acceptance run with 4 workers ran outside a slot (the dispatcher flags it). Keep suite
  output outside the worktree before any rebuild (your discovery 4).
- You are memory's critical path: W2-13 waits for your landing.

---

