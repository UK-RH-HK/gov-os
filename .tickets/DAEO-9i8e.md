---
id: DAEO-9i8e
status: in_progress
deps: [DAEO-8nue]
links: []
created: 2026-09-30T22:49:58Z
type: task
priority: 2
assignee: engineer
external-ref: W1-23
tags: [wave-1, implementation, standard]
wbs_id: W1-23
title: Hierarchical synthesis notes
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on:
- W1-22
allowed_paths:
- src/gov/retrieval/synthesis*
- tests/unit/synthesis/**
kpis:
  success:
  - When evidence exceeds the packet budget, notes are derived under .gov-runtime/, cite source ids and hashes, and disclose unresolved evidence [CAP-15.f]
  - A note is invalidated when any cited source hash changes; notes are rebuildable [CAP-15.f]
  failure:
  - A note survives a change to a cited source
  - A note cites a span not in its source
profile: STANDARD
sources:
- DEC-080
- DEC-030
- DEC-036
- CAP-15
est_loc: 100
acceptance_tests:
  path: tests/acceptance/W1-23/
  author: independent-test-designer (MR-3, DEC-069); to be written before implementation
---
# W1-23 Hierarchical synthesis notes

Derived, cited, hash-checked synthesis (DEC-080).
