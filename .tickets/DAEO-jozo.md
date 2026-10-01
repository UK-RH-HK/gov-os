---
id: DAEO-jozo
status: open
deps: [DAEO-4yyl, DAEO-lkeb]
links: []
created: 2026-09-30T22:49:58Z
type: task
priority: 2
assignee: engineer
external-ref: W1-20
tags: [wave-1, implementation, standard]
wbs_id: W1-20
title: gov closure
class: implementation
role: engineer
depends_on:
- W1-10
- W1-16
allowed_paths:
- src/gov/closure/**
- tests/unit/closure/**
kpis:
  success:
  - Resolves referenced ids through the record graph and codebase-memory callers/callees to a radius-scaled depth, with no model
  - Byte-identical output on repeated runs; DEPTH_LIMIT_REACHED lists the gaps
  failure:
  - Output differs between runs on the same commit
  - An unresolved id is omitted from the gap list
profile: STANDARD
sources:
- DEC-080
- DEC-033
- S0a-G-03
- CAP-09
- CAP-57
est_loc: 100
acceptance_tests:
  path: tests/acceptance/W1-20/
  author: independent-test-designer (MR-3, DEC-069); to be written before implementation
---
# W1-20 gov closure

Deterministic worklist closure (DEC-080).
