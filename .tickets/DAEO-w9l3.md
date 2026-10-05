---
id: DAEO-w9l3
status: closed
deps: [DAEO-topz, DAEO-lc4q]
links: []
created: 2026-09-30T22:49:58Z
type: task
priority: 2
assignee: engineer
external-ref: W1-14
tags: [wave-1, implementation, standard]
wbs_id: W1-14
title: Proposal-to-ticket bridge
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on:
- W1-09
- W1-12
allowed_paths:
- src/gov/tasks/bridge*
- tests/unit/bridge/**
kpis:
  success:
  - Tickets derived from an OpenSpec change tasks.md carry kpis, role, allowed_paths, profile and a back-reference to the change [CAP-31.a]
  - Derived tickets pass the ticket schema and the DAG is acyclic
  failure:
  - A derived ticket lacks KPIs or allowed_paths
  - An implementer ticket allowed_paths covers tests/acceptance/**
profile: STANDARD
sources:
- G-05
- CAP-31
- MR-2
est_loc: 120
acceptance_tests:
  path: tests/acceptance/W1-14/
  author: independent-test-designer (MR-3, DEC-069); to be written before implementation
---
# W1-14 Proposal-to-ticket bridge

Closed specifications generate the work (MR-2).
