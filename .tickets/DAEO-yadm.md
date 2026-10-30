---
id: DAEO-yadm
status: open
deps: [DAEO-g0ip, DAEO-ym8a]
links: []
created: 2026-10-16T16:35:11Z
type: task
priority: 4
assignee: engineer
external-ref: W2-34
tags: [wave-2, implementation, standard, wave-3, deferred]
wbs_id: W2-34
title: gov readiness --generate
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on:
- DAEO-g0ip
- DAEO-ym8a
allowed_paths:
- src/gov/readiness/**
- src/gov/tasks/**
- template/governance/kernel/templates/openspec/**
- tests/unit/readiness/**
- tests/unit/bridge/**
kpis:
  success:
  - gov readiness --generate creates one linked gap ticket per required open row, with its dependencies [CAP-30.c, MR-2, W2-M283].
  - A MISSING required row keeps production tickets out of READY [W2-M274].
  - The delivered tasks.md template is accepted by the bridge [W2-H051].
  - A direct openspec archive or a hand-set status does not bypass readiness [W2-H015].
  - The bridge checks the role against the roster [W2-M082].
  failure: []
profile: STANDARD
sources:
- CAP-30.c
- MR-2
est_loc: 180
acceptance_tests:
  path: tests/acceptance/W2-34/
  author: independent-test-designer (MR-3); written before implementation
track: C
closes:
- CAP-30.c
- MR-2
list_rows:
- W2-H015
- W2-H051
- W2-L053
- W2-L164
- W2-L245
- W2-L246
- W2-L247
- W2-M050
- W2-M052
- W2-M074
- W2-M075
- W2-M076
- W2-M077
- W2-M078
- W2-M079
- W2-M080
- W2-M081
- W2-M082
- W2-M083
- W2-M207
- W2-M274
- W2-M283
- W2-M302
- W2-M303
- W2-M305
---
# W2-34 gov readiness --generate

**Deferred to Wave 3 (DEC-953 item 10b, approved by DEC-954, 2026-10-30).** CAP-30.c moved to Wave 3 (DEC-841).

Card: `docs/plan/WAVE_2_WBS.md` §2 (W2-34), as approved (DEC-729). The list rows it takes in are in `list_rows` and in `docs/plan/WAVE_2_TRIAGE.md`; a row's state is re-checked against the code when the ticket picks it up (DEC-718).

- **Allowed paths:** `src/gov/readiness/**`, `src/gov/tasks/**`, `template/governance/kernel/templates/openspec/**`, `tests/unit/readiness/**`, `tests/unit/bridge/**`.
- **KPIs:**
  - `gov readiness --generate` creates one linked gap ticket per required open row, with its dependencies [CAP-30.c, MR-2, W2-M283].
  - A MISSING required row keeps production tickets out of READY [W2-M274].
  - The delivered `tasks.md` template is accepted by the bridge [W2-H051].
  - A direct `openspec archive` or a hand-set status does not bypass readiness [W2-H015].
  - The bridge checks the role against the roster [W2-M082].
