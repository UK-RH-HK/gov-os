---
id: PROJ-0000
status: open
deps: []
links: []
created: 2026-01-01T00:00:00Z
type: task
priority: 2
assignee: engineer
external-ref: W1-00
tags: []
wbs_id: W1-00
title: Short title of the ticket
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on: []
allowed_paths:
- src/example/**
kpis:
  success:
  - What must be true when the ticket is done [CAP-00.a]
  failure:
  - What must never be true
profile: STANDARD
sources:
- DEC-000
est_loc: 100
acceptance_tests:
  path: tests/acceptance/W1-00/
  author: independent-test-designer; written before implementation
---
# W1-00 Short title of the ticket

One or two sentences on what the ticket delivers.
