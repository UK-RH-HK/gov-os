# W2-92 (DAEO-n0wb) lead checkpoint — end of run 3 (status DONE)

## State (2026-11-02 09:40 UTC)
- Branch w2/W2-92, head 448a835a9dca (checkpoint record CP-DAEO-n0wb-0014). Code head e95eb4ad12ca.
- Run 3 commits: e95eb4ad12ca engineer (eng-9, DEC-1019: no record file cited without a record graph); 448a835a9dca orchestrator (CP-0014). trailer_gate: 20 judged, 0 lacking, 0 bad Implements.
- Tests worktree: none (removed in run 2).

## Results (all outputs /tmp/gov-os-lead-W2-92/log/run3/)
- W1-21 authority file alone, in a slot, at e95eb4ad12ca: 16 passed (the case test_without_a_record_graph_no_superseded_record_is_cited_as_current passes).
- Rebuild (worktree code): exit 0, 08:05:22-08:12:34. gov.__file__ = /home/usain/gov-os-worktrees/W2-92/src/gov/__init__.py.
- select_tests: scoped, core_changed [src/gov/retrieval/retrieve.py], unplaced [], 269 options; serial selected 1.
- Scoped parallel (slot): 4426 passed, 4 failed, 2 skipped, 19 min 58 s. Failures: W2-59 hook-line x4 (red at base in run 1, not this ticket's). Serial: 1 passed.
- gov accept DAEO-n0wb (slot): 7/7 lines, 30 passed.
- gov check (exit 3): RED retrieval-regression (600 s limit passed); YELLOW core-decision-citations (DEC-1006/DEC-1019 unrecorded in this tree), openspec-validate (nothing to validate); context reproducibility GREEN, secrets indexing GREEN.
  - retrieval-regression is environmental: run alone as gov check launches it, it scores hit@5 0.0 (every class 0 %) at the pre-ticket base 7ca16b19df3f (346 s), at run 2's code d72c96fc029c and at this head (605 s); it was GREEN at run 2's code last night (check-2, check-3). Probe: lexical matches whole-question phrases (0 hits by design), so these questions rest on the semantic route; under load near 26 with 5 other retrieve_check processes on the one shared embedder, indexing two tiers took >1500 s once. The change acts only when a store's record graph cannot be read; the check's tiers always load their store.
- collect-only: 19106/19108 collected (2 deselected), no error. keyword_warn: 0.

## No re-measure (DEC-1019 acts only without a record graph; the measure's stores have one).

## Brief gaps (run 3)
- gov accept cannot run W1-21 (DAEO-5x4l): README maps no KPI line (ACCEPT_NO_MAP) | this ticket's part | ~5 min.
- retrieval-regression's sensitivity to the shared embedder's load (and 0 % at base today) | common brief / tool | ~60 min.
- The Bash tool's background limit kills an until-loop waiter moved to the background after 10 min | tool | ~5 min.

## Scratch
- /home/usain/gov-os-runs/W2-92/{base, head, measure, records}: 1.5G, 33,062 inodes (the control; the orchestrator may remove it after the landing).
- /tmp/gov-os-lead-W2-92: 49M, 4,003 inodes (rm needs a prompt).
