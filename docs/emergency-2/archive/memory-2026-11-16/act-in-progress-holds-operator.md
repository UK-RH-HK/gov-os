---
name: act-in-progress-holds-operator
description: "log/act-in-progress.txt makes the operator agent's G9 hold every ACT; never leave it while an agent ACT is queued"
metadata:
  node_type: memory
  type: feedback
  originSessionId: b40cba91-6c08-4f82-b30e-591a4b93fb70
  modified: 2026-11-11T18:28:20.027Z
---

`.gov-runtime/scratch/orchestrator/log/act-in-progress.txt` (the CTO's commit-freeze note, DEC-1028 item 6) is read by the
operator agent's G9 (`operator_run.py` g9 → `oc.holds`): while it exists, every queued ACT is held ("the CTO's
log/act-in-progress.txt exists"), run after run.

**Why:** on 11-11 ACT-NIGHTLY-RESTART-1 sat held from 17:50 to 18:28 because the CTO had written a freeze note for a
by-hand ACT and appended the queued ACT to it.

**How to apply:** write the file only when you mean to hold the operator (e.g. a re-pin window); for a by-hand ACT keep the
freeze in the checkpoint instead; before queuing a `.req`, check the file is absent. Related: [[merge-task-trailer]],
[[control-paths-by-act]].
