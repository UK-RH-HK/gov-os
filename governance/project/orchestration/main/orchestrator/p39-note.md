
## Three scratch files moved out of the runtime folder (2026-10-10; for the exit auditor; DEC-604, DEC-611)

The secrets-indexing check found a string in three files of the orchestrator's scratch folder (DEC-602). The operator moved them, whole, into `~/gov-os-workbench/archive/orchestrator-logs/`; each sha256 matched before the move and matches in the archive. The files were never tracked.

| Original path | Bytes | sha256 | Now at |
|---|---|---|---|
| `.gov-runtime/scratch/orchestrator/briefs/W1-15-A5-head.md` | 3,420 | `01d488c53cc56f1d6f59ee8a4c89d6f80b45e6a3e2df7b089306d1e28ed45d32` | `~/gov-os-workbench/archive/orchestrator-logs/W1-15-A5-head.md` |
| `.gov-runtime/scratch/orchestrator/briefs/W1-15-A5.md` | 9,720 | `a14cf4dba37034fd7c144e4ae5c421ec0192803576f0764b2d0e82f84b706fae` | `~/gov-os-workbench/archive/orchestrator-logs/W1-15-A5.md` |
| `.gov-runtime/scratch/orchestrator/log/W1-16-lead-run1.json` | 13,341 | `a1871c9d539ea34d3d825617629e09bbe92ed83180eaef4ed47ec695f5ec0537` | `~/gov-os-workbench/archive/orchestrator-logs/W1-16-lead-run1.json` |

From DEC-604 on, briefs and logs name a canary or planted secret by its id, never by its value.
