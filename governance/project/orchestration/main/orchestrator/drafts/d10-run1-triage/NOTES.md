# D-10 run 1 triage notes (session 8ddb8b14, 2026-11-10)

- Run 1: start 18:10:09 UTC, pid 159396, head afad23270a30, 16 workers (nproc 20). Swap already 4.2 GB used at start (free-before.txt).
- Nightly folder: log/nightly/20261110-1810. Clone rebuilt 18:16. Parallel 18:16-18:34: pytest 991 s (16:31):
  9449 passed, 118 failed, 44 errors, 87 skipped. Serial from 18:34.
- Record fix (working tree, commit after exit): "after 18:20" -> "at 18:10:09 UTC" in START-NEXT-SESSION §00 and DECIDED-NOT-DONE row 110.

## Parallel reds, first reading (no re-runs yet)
1. W2-145 s1-s4 (55) and likely W2-112 (~46): "no temporary folder ... short enough for a Unix socket's path (108 bytes):
   set TMPDIR" -> harness/environment (long basetemp under the run's clone). Check W2-112's reason.
2. W2-50 launcher/owner_answers/review_findings/short_round (17): gov launch LAUNCH_NO_TEMPLATE: planted home lacks
   .claude/templates/role-engineer.md -> fixture vs the templates/ACT-CLAUDE-COPIES-3 change.
3. W1-41 migration/path_map/verdict/unknown (16): ADOPT_CODE_GRAPH_UNREADABLE: codebase-memory-mcp [Errno 2] not found
   -> PATH/environment in the test sandbox.
4. Singles to read: W1-01 x2 (DEC-253 merge rule; tests/acceptance trailer), W1-06 digests (deadman standby vs ALERT),
   W1-21, W1-28, W2-04, W2-131/135 unchanged, W2-32 s4, W2-56 endings, W2-61/61h, W2-96, test_cto_safety_nets (5),
   q22/q23 (cited lines drift), lens B Q07/Q14 table.
