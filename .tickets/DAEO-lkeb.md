---
id: DAEO-lkeb
status: open
deps: [DAEO-7nne]
links: []
created: 2026-09-30T22:49:58Z
type: task
priority: 2
assignee: engineer
external-ref: W1-16
tags: [wave-1, implementation, full]
wbs_id: W1-16
title: codebase-memory wrapper
class: implementation
role: engineer
depends_on:
- W1-15
allowed_paths:
- src/gov/codeintel/**
- tests/unit/codeintel/**
kpis:
  success:
  - The index lives in a per-repository home under .gov-runtime/; list_projects in one repository shows only its own project
  - A secret-exclusion test proves no planted secret enters the codebase-memory index
  failure:
  - An index file of this repository exists outside .gov-runtime/ after a run
  - A planted secret is found in the code graph
profile: FULL
sources:
- G-06
- DEC-074 Q10
- DEC-076
- CAP-12
est_loc: 50
acceptance_tests:
  path: tests/acceptance/W1-16/
  author: independent-test-designer (MR-3, DEC-069); to be written before implementation
---
# W1-16 codebase-memory wrapper

Per-repository home and secret exclusion for codebase-memory-mcp 0.11.0 (DEC-076).

