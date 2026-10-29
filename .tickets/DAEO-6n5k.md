---
id: DAEO-6n5k
status: in_progress
deps: [DAEO-g0ip, DAEO-ym8a]
links: []
created: 2026-10-16T16:35:11Z
type: task
priority: 2
assignee: engineer
external-ref: W2-37
tags: [wave-2, implementation, full]
wbs_id: W2-37
title: gov impact
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on:
- DAEO-g0ip
- DAEO-ym8a
allowed_paths:
- src/gov/impact/**
- src/gov/closure/**
- tests/unit/impact/**
kpis:
  success:
  - A decision change raises a CIT-P that lists the affected specifications, decisions, tickets, tests and code from both graphs, with a radius [CAP-33.b, W2-M285].
  - After apply or archive, the CIT-E record matches the proposal or lists the differences [W2-L319].
  - '"What''s the impact of X?" in plain language runs gov impact [CAP-33.g, DEC-167].'
  - It also takes the S0b2 glue G-16 (id mapping) and G-24 (deletable-class join).
  failure: []
profile: FULL
sources:
- CAP-33.b
- CAP-33.g
- DEC-167
est_loc: 280
acceptance_tests:
  path: tests/acceptance/W2-37/
  author: independent-test-designer (MR-3); written before implementation
track: C
closes:
- CAP-33.b
- CAP-33.g
- DEC-167
list_rows:
- W2-L319
- W2-M056
- W2-M150
- W2-M285
- W2-M320
---
# W2-37 gov impact

Card: `docs/plan/WAVE_2_WBS.md` §2 (W2-37), as approved (DEC-729). The list rows it takes in are in `list_rows` and in `docs/plan/WAVE_2_TRIAGE.md`; a row's state is re-checked against the code when the ticket picks it up (DEC-718).

- **Allowed paths:** `src/gov/impact/**` (new), `src/gov/closure/**` (read API only), `tests/unit/impact/**`.
- **KPIs:**
  - A decision change raises a CIT-P that lists the affected specifications, decisions, tickets, tests and code from both graphs, with a radius [CAP-33.b, W2-M285].
  - After apply or archive, the CIT-E record matches the proposal or lists the differences [W2-L319].
  - "What's the impact of X?" in plain language runs `gov impact` [CAP-33.g, DEC-167].
  - It also takes the S0b2 glue G-16 (id mapping) and G-24 (deletable-class join).
