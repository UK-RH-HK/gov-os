---
id: DAEO-wudw
status: open
deps: [DAEO-g0ip, DAEO-u4oz]
links: []
created: 2026-10-16T16:35:11Z
type: task
priority: 4
assignee: engineer
external-ref: W2-39
tags: [wave-2, implementation, standard, wave-3, deferred]
wbs_id: W2-39
title: Model and provider switch reconstructs the same inputs
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on:
- DAEO-g0ip
- DAEO-u4oz
allowed_paths:
- src/gov/context/**
- src/gov/checkpoint/**
- tests/unit/context/**
- tests/unit/checkpoint/**
kpis:
  success:
  - A ticket's context, checkpoint resume and handoff record, built for two different models, give the same input hash [CAP-37.e].
  failure: []
profile: STANDARD
sources:
- CAP-37.e
est_loc: 80
acceptance_tests:
  path: tests/acceptance/W2-39/
  author: independent-test-designer (MR-3); written before implementation
track: C
closes:
- CAP-37.e
list_rows:
- W2-L035
- W2-L043
- W2-L113
- W2-M060
- W2-M062
- W2-M136
- W2-M137
- W2-M213
---
# W2-39 Model and provider switch reconstructs the same inputs

**Deferred to Wave 3 (DEC-953 item 10b, approved by DEC-954, 2026-10-30).** CAP-37.e moved to Wave 3 (DEC-841).

Card: `docs/plan/WAVE_2_WBS.md` §2 (W2-39), as approved (DEC-729). The list rows it takes in are in `list_rows` and in `docs/plan/WAVE_2_TRIAGE.md`; a row's state is re-checked against the code when the ticket picks it up (DEC-718).

- **Allowed paths:** `src/gov/context/**` (the model-independence part), `src/gov/checkpoint/**` (resume inputs only), `tests/unit/context/**`, `tests/unit/checkpoint/**`.
- **KPIs:** a ticket's context, checkpoint resume and handoff record, built for two different models, give the same input hash [CAP-37.e].
