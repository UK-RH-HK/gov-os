---
name: class-trailer-every-commit
description: "from 2026-11-16 (provisional rubric, DEC-1208/1209) every commit carries `Class: Q|L|S|F` in its trailer block; decision records and report commits are Q unless they touch a protected area"
metadata:
  node_type: memory
  type: feedback
  originSessionId: acd80751-ac8f-4230-9bae-15c678a54895
  modified: 2026-11-16T17:39:14.777Z
---

The provisional rubric (governance/project/orchestration/packages/PROVISIONAL-RUBRIC.md) says the class is written in every commit (`Class: Q|L|S|F`) or its ticket. The rubric research found that 0 of 8 commits after 17:19 on 11-16 carried it, mine included.

**Why:** I adopted the rubric in text but not in my own commit habit.

**How to apply:** put `Class: <Q|L|S|F>` in the one trailer block of every commit, next to Task/Role ([[trailers-one-block]]). Report and checkpoint commits are Q. A decision record is Q, since the register entry itself is the owner's. Path cases on a ticket take that ticket's class. Anything touching a protected area (guard, acceptance tests, memory, close, data, kernel) is F.
