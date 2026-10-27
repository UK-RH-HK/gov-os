# Lead checkpoint — DAEO-2azm (W2-74), run 1

- State: td-1 returned DONE (session 1b6a41d0-7eb2-4cb7-a90c-fc545c13419b, twelve fields present, sandboxed). Commits 6d7bee919a9f (retire, Rewrite-Reason DEC-925 item 1, P-I1-2), 66d3f3feb54c (W1-49, DEC-917), 1ebb6f0f96aa (W2-69 rename, DEC-911); trailers checked. Tripwire: this tree only head + W1-01/W1-47/W1-49/W2-69 (allowed); W2-57 tree changed by its own run (head 101285866733 -> 8d34ea94ba5a, sandbox dotfiles, W1-19/W1-30/W2-57 folders), not ours.
- Lead checks (log/checks/summary.txt): W1-01 16p/25s, W1-47 23p, W1-49 30p, W2-69 132p; collection 16588/16590 (2 deselected), keyword_warn 0 hits. gov.__file__ in this worktree.
- Rebuild (log/rebuild.json) ok, all three stores recreated. gov check: all GREEN but core-decision-citations YELLOW (163 historic DECISION_UNRECORDED warnings) and openspec-validate YELLOW (openspec not on PATH in that command). keyword_warn on worktree: 0.
- Parallel run (log/parallel.txt, parallel.xml): exit 0, 16292 passed, 31 skipped, 43m42s (waited ~50 min on W2-57's lock).
- Now: full_run.sh serial (log/serial.*), then pre-close collection gate, gov checkpoint record, commit, return DONE.
- Base head: a42e899b56fb (w2/W2-74), clean at start.
- Decided (DEC-925 item 1): three revisions (retire 6 docs/source cases; W1-49 [not on PATH] gets a gov; rename W2-69 case id). LITE, no review.
- Next: check td-1's return (twelve fields, trailers, tripwire); lead checks script under .gov-runtime/scratch/lead/; rebuild; full run in the close's form under flock with retention option and disk gate; return.
- Loop count: 0 iterations of implementation (test-revision ticket).
