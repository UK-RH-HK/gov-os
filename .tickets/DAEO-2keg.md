---
id: DAEO-2keg
status: open
deps: [DAEO-g0ip, DAEO-lrre, DAEO-yadm]
links: []
created: 2026-10-16T16:35:11Z
type: task
priority: 4
assignee: engineer
external-ref: W2-35
tags: [wave-2, implementation, standard, wave-3, deferred]
wbs_id: W2-35
title: 'The UX readiness row: approved wireframes, visual checks'
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on:
- DAEO-g0ip
- DAEO-lrre
- DAEO-yadm
allowed_paths:
- src/gov/readiness/ux*
- template/governance/kernel/schemas/readiness*
- tests/unit/readiness/**
kpis:
  success:
  - For a feature with a user interface, the UX row closes only on scenario-derived wireframes or mockups the owner has approved, and its acceptance tests include visual checks against them [CAP-30.g, DEC-104].
    A visual-testing tool is installed under DEC-083 when first needed (queued).
  failure: []
profile: STANDARD
sources:
- CAP-30.g
- DEC-104
- DEC-083
est_loc: 150
acceptance_tests:
  path: tests/acceptance/W2-35/
  author: independent-test-designer (MR-3); written before implementation
track: C
closes:
- CAP-30.g
- DEC-104
list_rows:
- W2-M322
---
# W2-35 The UX readiness row: approved wireframes, visual checks

**Deferred to Wave 3 (DEC-953 item 10b, approved by DEC-954, 2026-10-30).** CAP-30.g moved to Wave 3 (DEC-841).

Card: `docs/plan/WAVE_2_WBS.md` §2 (W2-35), as approved (DEC-729). The list rows it takes in are in `list_rows` and in `docs/plan/WAVE_2_TRIAGE.md`; a row's state is re-checked against the code when the ticket picks it up (DEC-718).

- **Allowed paths:** `src/gov/readiness/ux*`, `template/governance/kernel/schemas/readiness*`, `tests/unit/readiness/**`.
- **KPIs:** for a feature with a user interface, the UX row closes only on scenario-derived wireframes or mockups the owner has approved, and its acceptance tests include visual checks against them [CAP-30.g, DEC-104]. A visual-testing tool is installed under DEC-083 when first needed (queued).
