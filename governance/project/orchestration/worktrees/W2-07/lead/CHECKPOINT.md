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

## td-3 (returned DONE, about 19:55)
- Session ab9fa908-2f6a-4cff-990b-7248beef6188, gov launch, sandboxed (check passed), --effort high; twelve fields present.
- Commits 2e888299 (Rewrite-Reason: DEC-868 item 3), 1a6f239a (DEC-868 item 1 (b), KPI 5), 4ceb05ed (KPI 10, W2-M252);
  each Task: DAEO-r9ss, Role: independent-test-designer, Implements: DEC-908, DEC-868, Co-Authored-By. 5 files, +199/-52.
- Its runs: W1-30 512/512, W2-01 88/88, collect 15812/15814 no error. gov retrieve: FACET_UNAVAILABLE (stale). 1 guard read refusal.
- Tripwire 5: this tree head + W1-30 only (allowed). Other trees moved by their own sessions: W2-00-record head, W2-67 head and
  `?? tests/acceptance/W1-27/w2_67_td4_plant.py` and W1-27 folder, W2-69 head, W2-70 head and W1-01 folder.
- Case [6] (no-store reason stem, gov check's 200-character cut): judged not lowered.

## Lead check (check3.sh, at 4ceb05ed): all green
- W1-30 512 p; W2-53 57 p; W2-01 88 p; W2-07 40 p; unit close + telemetry 463 p. gov.__file__ in this worktree.
- CP-DAEO-r9ss-0010 committed as 614817ec (Task: DAEO-r9ss, Implements: engineer, Role: orchestrator).
- Verification: verify3.sh (log/v3-*), started about 20:25, at 614817ec. Rebuild exit 0 (lexical, semantic, codeintel
  recreated); collect 15812/15814 exit 0, no error; gov check exit 0, ok, YELLOW: core-decision-citations (warning,
  DECISION_UNRECORDED for DEC-872/DEC-863 in old commits), openspec-validate (OPENSPEC_ABSENT, not on PATH).
  The parallel run took the lock at 21:59 and was stopped at 94% by the Bash tool's two-hour limit at 22:25 (the load and
  lock waits took 95 min); 2 F seen in its first 6%. No result. Lesson: wait in the foreground, then start each run alone.
- Rerun: parallel3.sh (log/p3-*), queued on the lock at 23:10 behind W2-70's serial run. Then serial3.sh alone.

## Next
1. (done) td-3.
2. Lead check (W1-30, W2-53, W2-01, W2-07, tests/unit/close, each its own process), then verify3.sh (rebuild, collect, gov check,
   parallel and serial under flock with -o tmp_path_retention_policy=failed). Then checkpoint and DONE.
- Loop: held by the lead (not disclosed).

## Refusals (run 3)
- Lead: 0 so far.
