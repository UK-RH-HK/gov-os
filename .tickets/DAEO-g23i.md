---
id: DAEO-g23i
status: open
deps: [DAEO-g0ip, DAEO-6n5k, DAEO-s694, DAEO-xxgp]
links: []
created: 2026-10-16T16:35:11Z
type: task
priority: 2
assignee: engineer
external-ref: W2-38
tags: [wave-2, implementation, full]
wbs_id: W2-38
title: Profile from impact; impact-selected tests at close
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on:
- DAEO-g0ip
- DAEO-6n5k
- DAEO-s694
- DAEO-xxgp
allowed_paths:
- src/gov/impact/profile*
- src/gov/close/select*
- tests/unit/impact/**
- tests/unit/close/test_select*
kpis:
  success:
  - An R0 change runs only the LITE checks, and an R3 change raises the FULL gate and readiness rows, with the profile computed by gov impact [CAP-53.b].
  - A close runs the tests gov impact names, on top of W2-66's path-scoped selection (W2-48's cache was withdrawn, DEC-880). The full suite runs at milestones and in CI [W2-H043, W2-M240, W2-M241, W2-M163].
  failure:
  - A change whose impact misses a test that would fail is caught by the milestone run and recorded as a learning event.
profile: FULL
sources:
- CAP-53.b
est_loc: 150
acceptance_tests:
  path: tests/acceptance/W2-38/
  author: independent-test-designer (MR-3); written before implementation
track: C
closes:
- CAP-53.b
- W2-H043
list_rows:
- W2-H043
- W2-M163
- W2-M240
- W2-M241
---
# W2-38 Profile from impact; impact-selected tests at close

Card: `docs/plan/WAVE_2_WBS.md` §2 (W2-38), as approved (DEC-729). The list rows it takes in are in `list_rows` and in `docs/plan/WAVE_2_TRIAGE.md`; a row's state is re-checked against the code when the ticket picks it up (DEC-718).

- **Allowed paths:** `src/gov/impact/profile*`, `src/gov/close/select*`, `tests/unit/impact/**`, `tests/unit/close/test_select*`.
- **KPIs:**
  - An R0 change runs only the LITE checks, and an R3 change raises the FULL gate and readiness rows, with the profile computed by `gov impact` [CAP-53.b].
  - A close runs the tests `gov impact` names, on top of W2-66's path-scoped selection (W2-48's cache was withdrawn, DEC-880). The full suite runs at milestones and in CI [W2-H043, W2-M240, W2-M241, W2-M163].
- **Failure:** a change whose impact misses a test that would fail is caught by the milestone run and recorded as a learning event.
