---
id: DAEO-zndm
status: open
deps: [DAEO-g0ip, DAEO-1ahb]
links: []
created: 2026-10-16T16:35:12Z
type: task
priority: 2
assignee: engineer
external-ref: W2-44
tags: [wave-2, implementation, full]
wbs_id: W2-44
title: Trailers bound to the launch identity
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on:
- DAEO-g0ip
- DAEO-1ahb
allowed_paths:
- src/gov/close/traceability*
- src/gov/guard/containment*
- tests/unit/close/test_traceability*
- tests/unit/containment/**
kpis:
  success:
  - 'A commit''s Role: and Task: are checked against the launch record of the session that made it (W2-21''s Session: trailer), and a forged role is refused [W2-H019, W2-M156, W2-M222, W2-L078].'
  - A worker's commit is attributed to the worker, not to its waiting lead [W2-M038, W2-L135, W2-M037].
  failure: []
profile: FULL
sources:
- DEC-729
est_loc: 160
acceptance_tests:
  path: tests/acceptance/W2-44/
  author: independent-test-designer (MR-3); written before implementation
track: C
closes:
- W2-H019
list_rows:
- W2-H019
- W2-L073
- W2-L077
- W2-L078
- W2-L087
- W2-L099
- W2-L135
- W2-L163
- W2-L212
- W2-M009
- W2-M020
- W2-M022
- W2-M037
- W2-M038
- W2-M156
- W2-M179
- W2-M222
- W2-M233
- W2-M278
---
# W2-44 Trailers bound to the launch identity

Card: `docs/plan/WAVE_2_WBS.md` §2 (W2-44), as approved (DEC-729). The list rows it takes in are in `list_rows` and in `docs/plan/WAVE_2_TRIAGE.md`; a row's state is re-checked against the code when the ticket picks it up (DEC-718).

- **Allowed paths:** `src/gov/close/traceability*`, `src/gov/guard/containment*`, `tests/unit/close/test_traceability*`, `tests/unit/containment/**`.
- **KPIs:**
  - A commit's `Role:` and `Task:` are checked against the launch record of the session that made it (W2-21's `Session:` trailer), and a forged role is refused [W2-H019, W2-M156, W2-M222, W2-L078].
  - A worker's commit is attributed to the worker, not to its waiting lead [W2-M038, W2-L135, W2-M037].
