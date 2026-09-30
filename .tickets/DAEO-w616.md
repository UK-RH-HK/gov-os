---
id: DAEO-w616
status: open
deps: [DAEO-topz, DAEO-lc4q]
links: []
created: 2026-09-30T22:49:58Z
type: task
priority: 2
assignee: engineer
external-ref: W1-13
tags: [wave-1, implementation, full]
wbs_id: W1-13
title: gov readiness
class: implementation
role: engineer
depends_on:
- W1-09
- W1-12
allowed_paths:
- src/gov/readiness/**
- tests/unit/readiness/**
kpis:
  success:
  - Reports every row open for the profile (FULL for spines) and rejects N/A_WITH_REASON with an empty reason
  - Blocks OpenSpec apply/archive and ticket READY while required rows are open
  - Output is identical on repeated runs
  failure:
  - A spec with a required MISSING row is reported closed
  - A defaulted N/A passes
profile: FULL
sources:
- G-08
- DEC-085
- CAP-30
- MR-1
- MR-2
est_loc: 150
acceptance_tests:
  path: tests/acceptance/W1-13/
  author: independent-test-designer (MR-3, DEC-069); to be written before implementation
---
# W1-13 gov readiness

The readiness checker that closes specifications and gates work.

