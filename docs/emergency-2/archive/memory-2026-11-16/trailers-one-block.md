---
name: trailers-one-block
description: "Task:/Role:/Decided-by: and the Co-Authored-By/Claude-Session lines go in ONE final paragraph — a blank line between them hides Task and Role from git"
metadata:
  node_type: memory
  type: feedback
  originSessionId: f3886235-4854-4c91-9cf3-1a1dd009cb50
  modified: 2026-11-13T20:09:23.040Z
---

In every commit message, `Task:`, `Role:`, `Implements:`, `Decided-by:`, `Rewrite-Reason:` AND the attribution lines (`Co-Authored-By:`, `Claude-Session:`) must form one paragraph at the end, with no blank line between them.

**Why:** git reads trailers only from the last paragraph. On 2026-11-13 evening I put a blank line before `Co-Authored-By:`, so 11 commits had no parsed `Task:`/`Role:`. The landing check (`governance/project/operator/landing_check.py`) then read the W2-37 hand merge (72c6def88, a kernel path) as "outside a ticket" and raised a P1 to the owner. Traceability tools that read trailers miss those commits too. History can't be amended (DEC-412).

**How to apply:** before every `git commit -m`, check that the message's last paragraph holds every trailer. After committing, `git log -1 --format='%(trailers:key=Task,valueonly)'` must print the ticket. Related: [[merge-task-trailer]].
