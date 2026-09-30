---
id: DAEO-xw3k
status: open
deps: [DAEO-78bn, DAEO-lkeb, DAEO-rxln, DAEO-8nue]
links: []
created: 2026-09-30T22:49:59Z
type: task
priority: 2
assignee: engineer
external-ref: W1-27
tags: [wave-1, implementation, standard]
wbs_id: W1-27
title: gov doctor and gov rebuild
class: implementation
role: engineer
depends_on:
- W1-04
- W1-16
- W1-17
- W1-22
allowed_paths:
- src/gov/doctor/**
- src/gov/rebuild/**
- tests/unit/doctor/**
kpis:
  success:
  - doctor reports pinned vs found tool versions, hooks wired, path map with zero unclassified paths, index freshness, canaries, framework.lock MATCH/DRIFT, per-repository isolation; non-zero on any failure
  - rebuild recreates every derived store; two rebuilds give the same digest; a fresh clone plus doctor plus rebuild works
  failure:
  - doctor passes with a tool at the wrong version
  - rebuild needs anything not in git
profile: STANDARD
sources:
- S0a-G-04
- DEC-083
- CAP-02
- CAP-06
- CAP-07
- CAP-20
- CAP-25
- CAP-46
- CAP-48
- CAP-54
est_loc: 200
acceptance_tests:
  path: tests/acceptance/W1-27/
  author: independent-test-designer (MR-3, DEC-069); to be written before implementation
---
# W1-27 gov doctor and gov rebuild

Installation health (MR-4) and the rebuild guarantee.

