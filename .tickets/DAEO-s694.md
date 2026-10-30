---
id: DAEO-s694
status: open
deps: [DAEO-g0ip, DAEO-jzvg, DAEO-7rr2]
links: []
created: 2026-10-16T16:35:11Z
type: task
priority: 4
assignee: engineer
external-ref: W2-41
tags: [wave-2, implementation, full, wave-3, deferred]
wbs_id: W2-41
title: Close and escalation integrity
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on:
- DAEO-g0ip
- DAEO-jzvg
- DAEO-7rr2
allowed_paths:
- src/gov/close/**
- src/gov/tasks/external*
- tests/unit/close/**
kpis:
  success:
  - Close refuses task-less changes to test configuration [W2-H022].
  - The commit range is computed by ancestry [W2-H023].
  - Only a decision naming the escalated ticket lifts its escalation [W2-H024].
  - Escalation state is stored where the caller cannot reset it, or a reset is detected [W2-H025].
  - The external-references list is read from a commit and accepts decision ids only [W2-H033].
  - The probe gate judges every commit after the probe that touches the ticket's paths, whatever its task, and refuses a hand-resolved merge that drops probed code [W2-M015, W2-M204, W2-M255, W2-M256, W2-M203,
    W2-M254].
  - A late commit on a closed ticket is caught [W2-M115].
  - The tree and HEAD are re-checked before the record is written [W2-M164].
  failure: []
profile: FULL
sources:
- DEC-729
est_loc: 160
acceptance_tests:
  path: tests/acceptance/W2-41/
  author: independent-test-designer (MR-3); written before implementation
track: C
closes:
- W2-H022 … W2-H025
- W2-H033
list_rows:
- W2-H022
- W2-H023
- W2-H024
- W2-H025
- W2-H033
- W2-L116
- W2-L162
- W2-L190
- W2-L211
- W2-M015
- W2-M053
- W2-M054
- W2-M112
- W2-M114
- W2-M115
- W2-M164
- W2-M203
- W2-M204
- W2-M205
- W2-M208
- W2-M254
- W2-M255
- W2-M256
---
# W2-41 Close and escalation integrity

**Deferred to Wave 3 (DEC-953 item 10b, approved by DEC-954, 2026-10-30).** `gov close` is not a gate here; its high rows go to Wave 3's hardening; W2-81's proof shows whether any bites.

Card: `docs/plan/WAVE_2_WBS.md` §2 (W2-41), as approved (DEC-729). The list rows it takes in are in `list_rows` and in `docs/plan/WAVE_2_TRIAGE.md`; a row's state is re-checked against the code when the ticket picks it up (DEC-718).

- **Allowed paths:** `src/gov/close/**` (except `cache*` and `select*`), `src/gov/tasks/external*`, `tests/unit/close/**`.
- **KPIs:**
  - Close refuses task-less changes to test configuration [W2-H022].
  - The commit range is computed by ancestry [W2-H023].
  - Only a decision naming the escalated ticket lifts its escalation [W2-H024].
  - Escalation state is stored where the caller cannot reset it, or a reset is detected [W2-H025].
  - The external-references list is read from a commit and accepts decision ids only [W2-H033].
  - The probe gate judges every commit after the probe that touches the ticket's paths, whatever its task, and refuses a hand-resolved merge that drops probed code [W2-M015, W2-M204, W2-M255, W2-M256, W2-M203, W2-M254].
  - A late commit on a closed ticket is caught [W2-M115].
  - The tree and HEAD are re-checked before the record is written [W2-M164].
