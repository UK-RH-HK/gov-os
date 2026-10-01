---
id: DAEO-wk2v
status: open
deps: [DAEO-4yyl, DAEO-5x4l]
links: []
created: 2026-09-30T22:49:59Z
type: task
priority: 1
assignee: engineer
external-ref: W1-24
tags: [wave-1, implementation, full]
wbs_id: W1-24
title: gov context
class: implementation
role: engineer
depends_on:
- W1-10
- W1-21
allowed_paths:
- src/gov/context/**
- tests/unit/context/**
kpis:
  success:
  - The packet holds every mandatory input by id and sha256, the authority block first, stays under the ceiling (default ~6k tokens) and carries its hash
  - --brief delivers a file path plus a summary <= 2.5k tokens
  failure:
  - A mandatory input is missing from the packet
  - A lower-precedence record appears in the authority block
profile: FULL
sources:
- S0a-G-07
- DEC-003
- DEC-004
- CAP-01
- CAP-15
est_loc: 300
acceptance_tests:
  path: tests/acceptance/W1-24/
  author: independent-test-designer (MR-3, DEC-069); to be written before implementation
---
# W1-24 gov context

Compiled, budgeted, hashed context packets.
