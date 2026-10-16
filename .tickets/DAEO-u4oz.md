---
id: DAEO-u4oz
status: open
deps: [DAEO-g0ip, DAEO-ym8a]
links: []
created: 2026-10-16T16:35:10Z
type: task
priority: 1
assignee: engineer
external-ref: W2-04
tags: [wave-2, implementation, full]
wbs_id: W2-04
title: gov context bounded and reproducible
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on:
- DAEO-g0ip
- DAEO-ym8a
allowed_paths:
- src/gov/context/**
- src/gov/retrieval/supplementary*
- tests/unit/context/**
kpis:
  success:
  - gov context <ticket> holds the packet ceiling (≈ 6k tokens, Contract envelope) and never drops the ticket's own text [AR-1, CAP-15.d].
  - 'When the mandatory inputs alone exceed the ceiling, it refuses with a named error and a non-zero exit; it never reports ok: true over its budget [AR-1, F-M5].'
  - Each decision in the packet is named by its own hash (from W2-03) [AR-1].
  - Two builds of one ticket's context, on stores rebuilt from one commit, give the same packet hash with or without a live semantic index. Ties in the supplementary block are ordered deterministically
    [AR-9, W2-M294, W2-M239, W2-M330].
  - An unreadable mandatory record blocks the context or is marked not read; it is never shown as read with an empty hash [W2-H034, W2-M215].
  - The supplementary query is built from the ticket's KPIs and title, not the first long word [W2-M126].
  failure:
  - DAEO-03pw's context (814,821 tokens at the audit) refuses or fits; a RETIRED or REJECTED record does not satisfy a mandatory source.
profile: FULL
sources:
- CAP-15.d
est_loc: 220
acceptance_tests:
  path: tests/acceptance/W2-04/
  author: independent-test-designer (MR-3); written before implementation
track: A
closes:
- AR-1
- AR-9 (ORION-gp01)
list_rows:
- W2-H034
- W2-L088
- W2-L180
- W2-L183
- W2-L219
- W2-M126
- W2-M133
- W2-M134
- W2-M215
- W2-M228
- W2-M239
- W2-M294
- W2-M330
---
# W2-04 gov context bounded and reproducible

Card: `docs/plan/WAVE_2_WBS.md` §2 (W2-04), as approved (DEC-729). The list rows it takes in are in `list_rows` and in `docs/plan/WAVE_2_TRIAGE.md`; a row's state is re-checked against the code when the ticket picks it up (DEC-718).

- **Allowed paths:** `src/gov/context/**`, `src/gov/retrieval/supplementary*`, `tests/unit/context/**`.
- **KPIs, success:**
  - `gov context <ticket>` holds the packet ceiling (≈ 6k tokens, Contract envelope) and never drops the ticket's own text [AR-1, CAP-15.d].
  - When the mandatory inputs alone exceed the ceiling, it refuses with a named error and a non-zero exit; it never reports `ok: true` over its budget [AR-1, F-M5].
  - Each decision in the packet is named by its own hash (from W2-03) [AR-1].
  - Two builds of one ticket's context, on stores rebuilt from one commit, give the same packet hash with or without a live semantic index. Ties in the supplementary block are ordered deterministically [AR-9, W2-M294, W2-M239, W2-M330].
  - An unreadable mandatory record blocks the context or is marked not read; it is never shown as read with an empty hash [W2-H034, W2-M215].
  - The supplementary query is built from the ticket's KPIs and title, not the first long word [W2-M126].
- **KPIs, failure:** DAEO-03pw's context (814,821 tokens at the audit) refuses or fits; a RETIRED or REJECTED record does not satisfy a mandatory source.
