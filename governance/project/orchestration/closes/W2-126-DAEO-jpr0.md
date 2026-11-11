# W2-126 (DAEO-jpr0) closed: by DEC-953's practices at the lift (DEC-1132 (1))

- Head at close: 060e3cd59 (w2/integrate); profile STANDARD
- Evidence: `gov accept W2-126`: 28 passed, 0 failed, 0 skipped (.gov-runtime/scratch/orchestrator/log/lift-accepts-1/summary.txt (`gov accept` on w2/integrate at 74110bb34, 15:19-15:29 UTC 11-11, through the heavy slot)).
- Lines met in part or by reading: S6 met in part: its per-day 'after' figure needs the shared embedder's log after the cache lands (`docs/changes/W2-126-evidence.md`).
- Route: `tk close` and this record (DEC-953 items 1 and 5); `gov close` and its gates are lifted here (DEC-953, DEC-1052 Q-8) and return through W2-115 on evidence (DEC-1128 (2), DEC-1132 (1))
- Closed: 2026-11-11 15:29:58 UTC, by the orchestrator (session 8ddb8b14)
