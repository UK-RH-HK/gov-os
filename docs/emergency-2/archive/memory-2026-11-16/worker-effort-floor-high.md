---
name: worker-effort-floor-high
description: "gov launch refuses engineer and test designer below effort high (launcher.py FLOOR, DEC-1120 (3)); launch workers at high, never medium"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 8b96cab1-13ff-4217-858a-3a2dacc691a6
  modified: 2026-11-15T23:58:27.506Z
---

2026-11-16 ~00:02, W2-174 r2c: I launched en-4 (engineer) and td-4-2 (independent-test-designer) at effort `medium`; `gov launch` refused both: "the CLI arguments carry --effort medium, below the floor 'high' of <role>'s high (DEC-1120 (3))" (src/gov/launch/launcher.py ~line 736, W2-184).

**Why:** W2-184's launcher sets an effort floor `high` per role; even a one-line task cannot launch below it.

**How to apply:** launch every engineer and test designer at `high` (or above; `max` needs `--reason`). The auditor floor is presumably the same; check launcher.py's FLOOR before naming anything lower. Related: [[brief-worker-model-launcher-picks]].
