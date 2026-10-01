---
id: DAEO-5x4l
status: open
deps: [DAEO-t6hf, DAEO-jozo]
links: []
created: 2026-09-30T22:49:58Z
type: task
priority: 1
assignee: engineer
external-ref: W1-21
tags: [wave-1, implementation, full]
wbs_id: W1-21
title: gov retrieve with completeness
class: implementation
role: engineer
depends_on:
- W1-19
- W1-20
allowed_paths:
- src/gov/retrieval/retrieve*
- src/gov/retrieval/bundle*
- tests/unit/retrieve/**
kpis:
  success:
  - Paging with continuation; facets; dedup by chunk hash; authority/current filter drops superseded and must-not-cite records; one rerank over the merged set
  - Every bundle cites by id and sha256 and carries one stopping reason from the fixed list
  - RETR-A-04 and RETR-X-02 dev runs produce multi-batch bundles
  - A child hit is expanded to its parent span only within the bundle budget, and the bundle names each expansion (DEC-091)
  failure:
  - A batch-size limit is reported as completeness
  - A superseded record is cited as current
profile: FULL
sources:
- DEC-080
- DEC-091
- G-19
- S0a-G-06
- CAP-14
- CAP-16
- CAP-18
- CAP-41
- CAP-55
est_loc: 280
acceptance_tests:
  path: tests/acceptance/W1-21/
  author: independent-test-designer (MR-3, DEC-069); to be written before implementation
---
# W1-21 gov retrieve with completeness

The retrieval-completeness engine behind the retrieval skill (DEC-080).
