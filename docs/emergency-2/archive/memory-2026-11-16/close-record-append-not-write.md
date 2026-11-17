---
name: close-record-append-not-write
description: "a reopened ticket already has the merge queue's close record under closes/; append the final close as a new section, never Write over it (11-14)"
metadata:
  node_type: memory
  type: feedback
  originSessionId: acd80751-ac8f-4230-9bae-15c678a54895
  modified: 2026-11-14T23:01:03.428Z
---

On 2026-11-14 I wrote W2-61h's and W2-94's final close records with Write, and that replaced the merge queue's own records at `governance/project/orchestration/closes/<W2>-<id>.md` (tested commit, queue record, run counts). I caught it in `git status`, restored both with `git checkout`, and appended my close instead.

**Why:** the queue's record is evidence (tested commit, counts, traced head). Overwriting it loses the close's audit trail.

**How to apply:** before writing any close record, `ls` the target. If it exists (always so for a ticket the queue closed and the CTO kept open), append a `## Final close (<DEC>)` section. More generally, look at any existing file before a Write. Related: [[merge-never-staged]].
