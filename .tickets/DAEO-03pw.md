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
  - A fresh read-only auditor compares the Wave 1 output with every Contract v4 W1 item, its covers list and the MR clauses, and issues a verdict; contested and owner-level findings reach the owner in chat
    as decision packages, agreed fixes become tickets
  - The audit→repair loop runs to convergence or to three consecutive non-converging iterations, then an escalation package goes to the owner; the orchestrator holds the count and never discloses it to
    the auditor or repair sessions (DEC-096)
  failure:
  - The auditor authored any audited file
  - A W1 contract item has no finding row
profile: FULL
sources:
- DEC-070
- DEC-088
- DEC-092
- DEC-096
- MR-4
- CAP-47
est_loc: 0
acceptance_tests:
  path: tests/acceptance/W1-43/
  author: independent-test-designer (MR-3, DEC-069); to be written before implementation
---
# W1-43 Wave 1 exit audit

Independent wave-exit audit against Contract v4 (DEC-070).
