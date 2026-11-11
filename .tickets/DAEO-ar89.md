---
id: DAEO-ar89
status: open
deps: []
links: [DAEO-zqvn]
created: 2026-11-11T01:07:01Z
type: task
priority: 4
assignee: engineer
external-ref: W2-155
tags: [wave-2, implementation, after-the-lift, performance]
wbs_id: W2-155
title: 'The warm query path profiled against W1-19''s 0.5 s budget; a simple cause fixed, or the evidence and options to the owner within a short time box'
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on: []
allowed_paths:
- src/gov/retrieve/**
- src/gov/retrieval/**
- tests/unit/retrieve/**
- tests/unit/retrieval/**
kpis:
  success:
  - 'S1 A profile of the warm real-model query path (the case of W1-19 and W2-13 that measures warm p95 with the real models) names where the time goes, stage by stage, and which retrieval changes since the budget last held added to it; the profile is kept as an evidence note in the ticket''s folder [DEC-1125 (1)]'
  - 'S2 If a simple cause is found within the time box: it is fixed, and W1-19''s and W2-13''s warm real-model cases pass at 0.5 s p95 on an idle machine, with no other case made red [DEC-1125 (1), W1-19]'
  - 'S3 If no simple cause is found within the time box (2 lead-hours): work stops and the evidence and options go to the owner; the budget is not changed by this ticket [DEC-1125 (1), DEC-105]'
  failure:
  - 'More than the time box spent without stopping and reporting.'
  - 'The 0.5 s budget, the case or its measure changed to make it pass.'
  - 'Any change outside the paths above.'
profile: LITE
sources:
- DEC-1125
- DEC-1123
est_loc: 60
acceptance_tests:
  path: tests/acceptance/W1-19/
  author: 'existing: W1-19''s and W2-13''s warm real-model latency cases (no new acceptance tests; MR-3 holds for any case change)'
track: A
list_rows: []
needs: []
---
# W2-155 The warm query path profiled: W1-19's 0.5 s budget

Filed by the CTO on the owner's decision DEC-1125 (1), 2026-11-11: **after the lift, low priority.**

- **Why:** D-10 run 2 (11-10, head `078e972d5`) measured the warm real-model query p95 at 0.543 s (W1-19) and 0.587 s
  (W2-13) against the 0.5 s budget; both red alone on an idle machine, no `src` change since run 1, the query server
  on the GPU. Earlier D-10 measures on 11-10 read 0.54-0.58 s even at low load. The owner ruled it a named red for the
  re-pin and the lift; the budget stays as written (DECIDED-NOT-DONE row 110).
- **The owner's note for whoever takes it:** profile the warm query path, including the retrieval changes since the
  budget last held, but do not over-spend time on it: the gap is not noticeable and does no harm. If a simple cause is
  found, fix it; if not within a short time box, stop and bring the owner the evidence and options instead.
