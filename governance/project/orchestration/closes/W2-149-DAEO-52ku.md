# W2-149 (DAEO-52ku) closed: by DEC-953's practices after the lift (DEC-1132 (1)); the CTO's delegated decision (DEC-1112 (3), 2026-11-11)

- Head at close: 219307d1d (w2/integrate); W2-149's judged paths and `tests/acceptance/W2-149/` are unchanged since the accept's head `31c8c31eb2a2` (`git diff --stat` empty); profile FULL
- Evidence: `gov accept W2-149` (the pinned judge, pin-797495bdfc70) through `heavy_slot.sh` with `GOV_W2_149_BWRAP=1` (the ticket's bwrap opt-in: "run by the CTO outside the sandbox"; bwrap 0.9.0 starts here), at 31c8c31eb2a2, 2026-11-11 22:03:42-22:08:14 UTC: outcome pass; 206 passed, 0 failed, 3 skipped (the `live` cases, a real claude session, `GOV_W2_149_LIVE=1` not set), as BATCH-PREP's 206/206 with 3 live skipped. Log `.gov-runtime/scratch/orchestrator/log/close-w2-149-r2/`
- The earlier run (21:21, without the opt-in): rc 3, 174 passed, 35 skipped; success-26 failed with both its cases skipped (they are S25/S26's bwrap cases). Not a code change: the opt-in was missing.
- Review and probe it rests on: `docs/probes/DAEO-52ku/PR-DAEO-52ku.md` (committed `17c5d4b3e`): the fresh FULL review of the merged code, 42 lines pass, READY by its verdict block; rows FR-1 to FR-4
- Lines met in part or by reading: none in the acceptance run (every line passes); the three `live` cases sit inside lines that pass on their other cases.
- Rows carried, none blocking: FR-1 to FR-4 (the probe); F37 (the log omits the rule check's word) and F40 (the CTO's one search of the auditor's wall before its first real run, DECIDED-NOT-DONE row 66), which BATCH-PREP §2 kept the ticket in_progress for: follow-ups, not KPI lines (the CTO's delegated decision, DEC-1112 (3)). W2-173 waited on this close.
- Route: `tk close` and this record (DEC-953 items 1 and 5); `gov close` and its gates are lifted here (DEC-953, DEC-1052 Q-8) and return through W2-115 on evidence (DEC-1128 (2), DEC-1132 (1)).
- Closed: 2026-11-11, by the orchestrator (session b2f0511f).
