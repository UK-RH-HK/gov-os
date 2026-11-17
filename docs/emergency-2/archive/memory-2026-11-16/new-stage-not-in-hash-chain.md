---
name: new-stage-not-in-hash-chain
description: "a new adoption stage inserted into project.STAGES strands every adoption recorded before it (A4-A9, A7/A10 refuse); make it a side record checked by its one consumer"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 410fd16f-43c0-42bb-8516-deef172ca5b2
  modified: 2026-11-16T17:28:16.096Z
---

Inserting a new stage into a hash-chained stage list (gov.adopt.project.STAGES) makes every later stage of an
adoption recorded before the stage existed refuse STAGE_MISSING: the redis copy of W2-88 S25 (gov-os-runs/W2-88/redis)
went red at A9, and lite_gates walks the same list (outside the ticket's paths). It also reddened
test_w2_88_nc1.py:225 (whole-file diff of project.py vs 01ec6d2a7). W2-192 en-1 (11-16) built AS that way on my brief;
en-2 moved it to a side record (chain A0-A2, only A3 requires it).

**Why:** the chain binds each record to the one before by hash; old records cannot gain a link afterwards.

**How to apply:** before briefing a new stage or record into a chain, look at existing adopted repositories
(~/gov-os-runs/*) and every reader of the list; prefer a side record checked by its consumer. See [[lead-brief-plan-ticket-id]].
