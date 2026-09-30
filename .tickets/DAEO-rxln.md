---
id: DAEO-rxln
status: open
deps: [DAEO-4yyl, DAEO-7nne]
links: []
created: 2026-09-30T22:49:58Z
type: task
priority: 1
assignee: engineer
external-ref: W1-17
tags: [wave-1, implementation, standard]
wbs_id: W1-17
title: Lexical index and shared store
class: implementation
role: engineer
depends_on:
- W1-10
- W1-15
allowed_paths:
- src/gov/retrieval/lexical*
- src/gov/retrieval/chunking*
- src/gov/retrieval/store*
- cli/govbridge/**
- tests/unit/retrieval/**
kpis:
  success:
  - Carried FTS5 and chunking ported into src/gov; blob-hash incremental index in the shared store
  - Changed blobs re-index before the next retrieval (2.8 s scale on a-dev); an empty or stale index is reported, never returned as absent
  failure:
  - A retrieval returns pre-edit text as current
  - Rebuild digest differs between two runs
profile: STANDARD
sources:
- G-17
- G-20
- G-21
- CAP-07
- CAP-11
- CAP-17
est_loc: 220
acceptance_tests:
  path: tests/acceptance/W1-17/
  author: independent-test-designer (MR-3, DEC-069); to be written before implementation
---
# W1-17 Lexical index and shared store

Lexical part of R1 in the shared store with zero-result semantics.

