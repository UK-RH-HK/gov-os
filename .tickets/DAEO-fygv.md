---
id: DAEO-fygv
status: open
deps: [DAEO-topz, DAEO-be7u, DAEO-w616]
links: []
created: 2026-09-30T22:49:59Z
type: task
priority: 2
assignee: engineer
external-ref: W1-26
tags: [wave-1, implementation, full]
wbs_id: W1-26
title: gov check G0-G2
class: implementation
role: engineer
depends_on:
- W1-09
- W1-11
- W1-13
allowed_paths:
- src/gov/check/**
- tests/unit/check/**
kpis:
  success:
  - Runs schema, id grammar, orphans, path map, adapter drift, openspec validate --strict, decision checker, readiness, ticket DAG acyclicity and field completeness, and the rule that no implementer allowed_paths
    covers tests/acceptance/**
  - Every policy key maps to a check or is declared informational (D-0003); each family is reported RED/YELLOW/GREEN
  failure:
  - A planted defect of any listed family passes
  - The scope of a check is a hand-maintained list
profile: FULL
sources:
- S0a-G-02
- DEC-041
- DEC-046
- CAP-38
- MR-2
- MR-3
est_loc: 200
acceptance_tests:
  path: tests/acceptance/W1-26/
  author: independent-test-designer (MR-3, DEC-069); to be written before implementation
---
# W1-26 gov check G0-G2

Deterministic governance checks, derived from the repository.

