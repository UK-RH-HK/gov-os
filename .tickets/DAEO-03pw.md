---
id: DAEO-03pw
status: open
deps: [DAEO-gjjf]
links: []
created: 2026-09-30T22:49:59Z
type: task
priority: 1
assignee: independent-auditor
external-ref: W1-43
tags: [wave-1, audit, full]
wbs_id: W1-43
title: Wave 1 exit audit
class: audit
role: independent-auditor
depends_on:
- W1-42
allowed_paths:
- docs/audit/wave-1/**
kpis:
  success:
  - A fresh read-only auditor compares the Wave 1 output with Contract v4 W1 items and MR clauses and issues a verdict with findings as tickets
  - At most two audit->repair rounds
  failure:
  - The auditor authored any audited file
  - A W1 contract item has no finding row
profile: FULL
sources:
- DEC-070
- MR-4
- CAP-47
est_loc: 0
acceptance_tests:
  path: tests/acceptance/W1-43/
  author: independent-test-designer (MR-3, DEC-069); to be written before implementation
---
# W1-43 Wave 1 exit audit

Independent wave-exit audit against Contract v4 (DEC-070).

