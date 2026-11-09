---
id: DAEO-zi7s
status: in_progress
deps: []
links: [DAEO-p3ln]
created: 2026-11-09T01:21:41Z
type: task
priority: 1
assignee: engineer
external-ref: W2-147
tags: [wave-2, implementation, plan, standard]
wbs_id: W2-147
title: 'gov plan breaks a cycle only at a ticket inside it: a ticket outside every cycle keeps all its waits (DEC-1102)'
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on: []
allowed_paths:
- src/gov/plan/**
- tests/unit/plan/test_w2_147*
kpis:
  success:
  - 'S1 A cycle is broken only at a ticket inside it: the ticket whose incoming waits are broken is chosen from the cycle''s strongly connected component, never from a ticket outside it, by the fixed key (priority, then WBS order, then id), and only the waits from inside that component are broken. Verify: a planted cycle (A waits on B, B waits on A) with an outside ticket C that waits on A and sorts first by the key: the break falls on A or B, and C''s wait on A is kept [DEC-1102, DEC-1088 (1)]'
  - 'S2 A ticket outside every cycle keeps all its waits: it is never named broken and comes after every ticket it waits on in the batches. Verify: the planted graph of S1, and the case seen on 2026-11-09 (W2-88 waiting on W2-145 while W2-145 and W2-137 formed a cycle, and W2-27 waiting on W2-88): W2-27''s wait on W2-88 is kept and W2-27 is batched after W2-88 [DEC-1102]'
  - 'S3 The choice is deterministic and named: the same tickets give byte-identical output in any file order, and each break is named in the plan''s output (CYCLE_TIEBREAK) with the ticket chosen and the waits broken. Verify: each planted graph in two shuffled file orders, in the text and --json outputs [DEC-1102, DEC-1088 (1)]'
  - 'S4 The planted graphs, each with its stated outcome: a cycle with an outside waiter (S1); two separate cycles, each broken once inside itself, with no wait between them or to an outside ticket broken; a self-loop (a ticket waiting on itself), broken at that ticket and named; no cycle, where the output is byte-identical to today''s (integrate''s) for the same tickets. Verify: planted ticket stores in a temporary folder, never this repository''s .tickets/ [DEC-1102]'
  failure:
  - 'A wait of a ticket outside every cycle broken, or a ticket outside the cycle chosen as the break.'
  - 'A break chosen differently for the same tickets in another file order, or a break not named in the output.'
  - 'Any change in the output for tickets with no cycle.'
profile: STANDARD
sources:
- DEC-1102
- DEC-1088
- DEC-1099
est_loc: 80
acceptance_tests:
  path: tests/acceptance/W2-147/
  author: independent-test-designer (MR-3), from these KPI lines, before the engineer; planted ticket stores in a temporary folder only
track: B
list_rows: []
needs:
- src/gov/plan/derive.py
waits_on: []
---
# W2-147 gov plan breaks a cycle only at a ticket inside it

The owner's DEC-1102. W2-136 (`DAEO-p3ln`) is merged; a merged ticket's KPIs are not edited (DEC-1088 (6)), so the
defect is its own ticket.

- **The defect:** `src/gov/plan/derive.py`'s `_order` breaks the incoming waits of the first remaining ticket by the
  fixed order even when that ticket is not in the cycle. Seen on 2026-11-09 while applying DEC-1099 (3): with W2-88
  waiting on W2-145 while W2-145 and W2-137 formed a cycle, it broke W2-27's wait on W2-88.
- **Why before the lift:** `gov plan` decides launches from the lift; a plan that silently drops a real wait would
  launch work out of order (DEC-1102's basis).
- **Timing:** tests first (an independent test designer), one review, merged before the lift's re-pin.
- **Est.:** about 80 lines with the engineer's unit tests; half a day with its review.

[DEC-1102]
