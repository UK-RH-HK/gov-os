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
  - Reports every row open for the profile (FULL for spines) and rejects N/A_WITH_REASON with an empty reason [CAP-30.a, CAP-53.a]
  - Blocks OpenSpec apply/archive and ticket READY while required rows are open
  - Output is identical on repeated runs
  - Lists every required open row with its linked gap ticket id, or UNLINKED (DEC-089) [CAP-30.b]
  - Closing a spine, STANDARD or FULL feature specification creates an audit ticket for a fresh Independent Auditor naming the milestone (DEC-088) [CAP-47.d]
  failure:
  - A spec with a required MISSING row is reported closed
  - A defaulted N/A passes
  - A spine, STANDARD or FULL specification closes without an audit ticket
profile: FULL
sources:
- G-08
- DEC-085
- DEC-088
- DEC-089
- CAP-30
- MR-1
- MR-2
- MR-4
- CAP-47
- CAP-53
est_loc: 170
acceptance_tests:
  path: tests/acceptance/W1-13/
  author: independent-test-designer (MR-3, DEC-069); to be written before implementation
---
# W1-13 gov readiness

The readiness checker that closes specifications and gates work.
