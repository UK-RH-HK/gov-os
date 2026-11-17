---
name: merge-task-trailer
description: "a ticket branch's merge commit carries that ticket's Task id, never only DAEO-sdxk, or the landing check flags it on control paths"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 412a4e37-2f72-42fc-8da2-6310c385f8f1
  modified: 2026-11-10T17:43:03.986Z
---

Merging a ticket's branch into w2/integrate: the merge commit's `Task:` is the merged ticket's id (e.g. `DAEO-t8mp`
for W2-128), not the CTO's `DAEO-sdxk`. `governance/project/operator/landing_check.py` treats a commit whose only Task
is DAEO-sdxk as "outside a ticket", and on a (b)/(O) control path (kernel template, guard, path map…) that is a P1.

**Why:** 2026-11-10, the owner-approved template 1.0.1 merge `6cc09c7ea` carried only DAEO-sdxk and raised a landing
P1 (a trailer slip, not a fault in substance; history not rewritten).

**How to apply:** in every `git merge --no-ff` message, write `Task: <the ticket's DAEO id>`; keep DAEO-sdxk only for
the CTO's own record commits. Related: [[merge-never-staged]].
