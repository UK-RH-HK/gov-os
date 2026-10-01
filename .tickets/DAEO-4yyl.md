---
id: DAEO-4yyl
status: open
deps: [DAEO-drvn, DAEO-uudf]
links: []
created: 2026-09-30T22:49:58Z
type: task
priority: 1
assignee: engineer
external-ref: W1-10
tags: [wave-1, implementation, standard]
wbs_id: W1-10
title: Store and record graph
class: implementation
role: engineer
depends_on:
- W1-07
- W1-08
allowed_paths:
- src/gov/store/**
- src/gov/records/**
- tests/unit/store/**
kpis:
  success:
  - 'Frontmatter of every record and Implements:/Task: trailers load into .gov-runtime/store.db deterministically (same digest twice) [CAP-13.a]'
  - Queries return the exact ACTIVE set, IMPLEMENTS/VALIDATES/SUPERSEDES/DEPENDS_ON edges and dangling references by id [CAP-08.a, CAP-09.b]
  - Full load of a dev tier < 5 s
  - 'The graph stores all eight typed edges: EVIDENCE_FOR, CONSTRAINS, IMPLEMENTS, TESTS, GENERATES, VALIDATES, SUPERSEDES, DEPENDS_ON [CAP-09.a]'
  failure:
  - A record present in git is missing from the graph
  - Graph content depends on file order or time
profile: STANDARD
sources:
- S0a-G-03
- G-20
- DEC-012
- CAP-01
- CAP-08
- CAP-09
- CAP-13
- CAP-29
- CAP-50
est_loc: 260
acceptance_tests:
  path: tests/acceptance/W1-10/
  author: independent-test-designer (MR-3, DEC-069); to be written before implementation
---
# W1-10 Store and record graph

The deterministic frontmatter and commit-trailer graph in the shared SQLite store.
