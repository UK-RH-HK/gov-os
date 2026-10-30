---
id: DAEO-w19l
status: open
deps: [DAEO-g0ip, DAEO-yadm]
links: []
created: 2026-10-16T16:35:11Z
type: task
priority: 4
assignee: engineer
external-ref: W2-36
tags: [wave-2, implementation, standard, wave-3, deferred]
wbs_id: W2-36
title: gov discover
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on:
- DAEO-g0ip
- DAEO-yadm
allowed_paths:
- src/gov/discover/**
- tests/unit/discover/**
kpis:
  success:
  - gov discover <question or feature> opens a discovery ticket, runs the discovery skill (readiness gaps, owner questions), and schedules research and experiment tasks whose evidence records back the answer.
    The same request in plain language works the same way [CAP-32.d, DEC-166, W2-M284].
  failure: []
profile: STANDARD
sources:
- CAP-32.d
- DEC-166
est_loc: 160
acceptance_tests:
  path: tests/acceptance/W2-36/
  author: independent-test-designer (MR-3); written before implementation
track: C
closes:
- CAP-32.d
- DEC-166
list_rows:
- W2-M284
---
# W2-36 gov discover

**Deferred to Wave 3 (DEC-953 item 10b, approved by DEC-954, 2026-10-30).** CAP-32.d moved to Wave 3 (DEC-841).

Card: `docs/plan/WAVE_2_WBS.md` §2 (W2-36), as approved (DEC-729). The list rows it takes in are in `list_rows` and in `docs/plan/WAVE_2_TRIAGE.md`; a row's state is re-checked against the code when the ticket picks it up (DEC-718).

- **Allowed paths:** `src/gov/discover/**` (new), `tests/unit/discover/**`.
- **KPIs:** `gov discover <question or feature>` opens a discovery ticket, runs the discovery skill (readiness gaps, owner questions), and schedules research and experiment tasks whose evidence records back the answer. The same request in plain language works the same way [CAP-32.d, DEC-166, W2-M284].
