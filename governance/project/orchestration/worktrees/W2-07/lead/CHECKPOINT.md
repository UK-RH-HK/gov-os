# W2-07 lead checkpoint (DAEO-r9ss, run 3): after the merge, before td-3

## State
- Branch w2/W2-07, head 6f152f80 (merge of w2/integrate 488972e4; Task: DAEO-r9ss, Implements: DEC-908, Role: orchestrator,
  Co-Authored-By; tree f2313e4a = git merge-tree). Run 2's head was d2eee219. The first merge attempt used `git merge --trailer`
  (not an option of git merge: exit 129, nothing done); the second, with the trailers in the message, made the merge.
- The merge brought only tickets, the register (DEC-905 to DEC-908), the list, the WBS, the common brief, the prompt, P-W1-01-H.
  W2-70 has not merged its test change: W1-01's history and integration-merge cases stay known reds (DEC-906, DEC-908 item 3).

## Decided (DEC-908)
- td-3 on exactly 14 W1-30 cases: 8 context_failures (DEC-868 item 3); governance_checks x2, r8_commits x2, r13_installed_skills x1
  (DEC-868 item 1 (b), KPI 5); iteration::test_each_refusal_opens_repair_ticket (KPI 10, W2-M252).
- W2-L416: judged not small (the watchdog allows 20 commits after a checkpoint, in gov.checkpoint, outside the ticket's paths; a
  close-only rule needs a new test case and changes every repeated-close case of W1-30): named in the return, for W2-24.

## Next
1. td-3: brief briefs/td-3.md, log log/td-3.json, tripwire-before-5.json, gov launch sandboxed, --effort high.
2. Lead check (W1-30, W2-53, W2-01, W2-07, tests/unit/close, each its own process), then verify3.sh (rebuild, collect, gov check,
   parallel and serial under flock with -o tmp_path_retention_policy=failed). Then checkpoint and DONE.
- Loop: held by the lead (not disclosed).

## Refusals (run 3)
- Lead: 0 so far.
