---
name: no-deferral
description: "Owner standing rule 11-14: do now all that can be done now; only an owner wait (until asleep) or a ticket dependency holds work"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 6ff2ee7c-f234-443c-8484-b5e93fc3d159
  modified: 2026-11-14T13:43:40.571Z
---

Stop deferring. Do now everything that can be done now: nothing waits for the next morning, the next digest or a later batch; a defect spotted is fixed in the same flow. Only two things hold work: an item waiting on the owner (until the owner says they are asleep, DEC-1156 (8)) or a dependency between tickets. Whenever something waits on the owner, tell them at once as a full package with its line, and keep everything else moving.

**Why:** the owner's message 2026-11-14 ~13:50 (to be recorded in DEC-1180); deferred items (q02's run path, DIF lines) had slipped.

**How to apply:** at each wake, list what is doable now and do it; never write "after the digest/tomorrow" for work with no owner wait or ticket dependency. Related: [[night-bring-lead-stoppers]], [[dec-1157-no-holds]].
