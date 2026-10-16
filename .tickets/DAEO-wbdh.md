---
id: DAEO-wbdh
status: open
deps: [DAEO-g0ip, DAEO-r9ss]
links: []
created: 2026-10-16T16:35:11Z
type: task
priority: 2
assignee: engineer
external-ref: W2-31
tags: [wave-2, implementation, full]
wbs_id: W2-31
title: Budget gates
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on:
- DAEO-g0ip
- DAEO-r9ss
allowed_paths:
- src/gov/budget/**
- src/gov/close/budget*
- src/gov/hooks/budget*
- tests/unit/budget/**
kpis:
  success:
  - A ticket declares a token budget with executable thresholds [CAP-04.a].
  - A run that exceeds it stops at the next gov close or hook boundary and raises a decision package, and the breach is recorded in the ticket [CAP-04.d].
  failure:
  - A breach that passes silently.
profile: FULL
sources:
- CAP-04.a
- CAP-04.d
est_loc: 200
acceptance_tests:
  path: tests/acceptance/W2-31/
  author: independent-test-designer (MR-3); written before implementation
track: C
closes:
- CAP-04.a
- CAP-04.d
list_rows: []
---
# W2-31 Budget gates

Card: `docs/plan/WAVE_2_WBS.md` §2 (W2-31), as approved (DEC-729). The list rows it takes in are in `list_rows` and in `docs/plan/WAVE_2_TRIAGE.md`; a row's state is re-checked against the code when the ticket picks it up (DEC-718).

- **Allowed paths:** `src/gov/budget/**` (new), `src/gov/close/budget*`, `src/gov/hooks/budget*`, `tests/unit/budget/**`.
- **KPIs:**
  - A ticket declares a token budget with executable thresholds [CAP-04.a].
  - A run that exceeds it stops at the next `gov close` or hook boundary and raises a decision package, and the breach is recorded in the ticket [CAP-04.d].
- **Failure:** a breach that passes silently.
