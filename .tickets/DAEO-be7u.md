---
id: DAEO-be7u
status: closed
deps: [DAEO-uudf, DAEO-4yyl, DAEO-egm9]
links: []
created: 2026-09-30T22:49:58Z
type: task
priority: 2
assignee: engineer
external-ref: W1-11
tags: [wave-1, implementation, full]
wbs_id: W1-11
title: Decision checker and owner-approval facts
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on:
- W1-08
- W1-10
- W1-34
allowed_paths:
- src/gov/decisions/**
- template/governance/kernel/schemas/madr*
- tests/unit/decisions/**
kpis:
  success:
  - Flags ACTIVE-while-superseded, duplicate or overlapping ids across directories, and supersession cycles on the b-dev fixtures (HZ-B-03, HZ-B-04, HZ-B-06) [CAP-51.a]
  - A change that sets a decision ACTIVE without an owner approval fact from git fails [CAP-01.b, CAP-21.a]
  - Files stay byte-identical
  - 'A declined, revoked or stale gate, or a gate answered for another CIT, does not authorise execution: the checker fails a ticket or change that cites one as its approval [CAP-34.d]'
  failure:
  - Any planted decision hazard is missed
  - The checker rewrites a decision file
profile: FULL
sources:
- G-04
- DEC-074 D2
- DEC-046
- CAP-21
- CAP-51
- CAP-01
- CAP-34
est_loc: 310
acceptance_tests:
  path: tests/acceptance/W1-11/
  author: independent-test-designer (MR-3, DEC-069); to be written before implementation
---
# W1-11 Decision checker and owner-approval facts

D2 checker with the MADR schema and the simplified D-0007 approval rule.
