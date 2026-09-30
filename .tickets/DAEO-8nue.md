---
id: DAEO-8nue
status: open
deps: [DAEO-5x4l]
links: []
created: 2026-09-30T22:49:58Z
type: task
priority: 2
assignee: engineer
external-ref: W1-22
tags: [wave-1, implementation, full]
wbs_id: W1-22
title: Evidence validator and zero-result canaries
class: implementation
role: engineer
depends_on:
- W1-21
allowed_paths:
- src/gov/retrieval/validate*
- src/gov/retrieval/canary*
- template/governance/kernel/canaries/**
- tests/unit/validate/**
kpis:
  success:
  - The validator rejects a bundle without a stopping reason, with an unresolvable citation, a stale hash or a quoted span absent from its source
  - Each index has canaries run after reindex and in doctor; a canary miss sets FACET_UNAVAILABLE
  failure:
  - A bundle with an unresolvable citation passes
  - An empty index answers NOT_FOUND as absence
profile: FULL
sources:
- DEC-080
- DEC-036
- DEC-037
- CAP-17
- CAP-55
est_loc: 120
acceptance_tests:
  path: tests/acceptance/W1-22/
  author: independent-test-designer (MR-3, DEC-069); to be written before implementation
---
# W1-22 Evidence validator and zero-result canaries

Citation validator and canaries (moved to W1 by DEC-080).

