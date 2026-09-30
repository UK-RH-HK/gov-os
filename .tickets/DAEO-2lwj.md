---
id: DAEO-2lwj
status: open
deps: [DAEO-8qvp, DAEO-topz, DAEO-rrxp, DAEO-fygv]
links: []
created: 2026-09-30T22:49:59Z
type: task
priority: 2
assignee: engineer
external-ref: W1-30
tags: [wave-1, implementation, full]
wbs_id: W1-30
title: gov close
class: implementation
role: engineer
depends_on:
- W1-03
- W1-09
- W1-25
- W1-26
allowed_paths:
- src/gov/close/**
- tests/unit/close/**
kpis:
  success:
  - 'Runs tests/acceptance/<ticket>/ and the regression tests, requires Implements: and Task: trailers, runs the containment check, writes a checkpoint and the close record with skill versions'
  - Counts review rounds and refuses a third round without an owner ADR, proposing DELETE/NARROW/DEFER; a failure opens a dependent repair ticket
  failure:
  - A ticket closes with a failing acceptance test
  - A third review round proceeds silently
profile: FULL
sources:
- S0a-G-12
- DEC-044
- DEC-069
- CAP-13
- CAP-24
- CAP-31
- CAP-38
- CAP-59
est_loc: 150
acceptance_tests:
  path: tests/acceptance/W1-30/
  author: independent-test-designer (MR-3, DEC-069); to be written before implementation
---
# W1-30 gov close

CIT-E closure with the loop budget.

