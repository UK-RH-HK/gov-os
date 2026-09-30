---
id: DAEO-topz
status: open
deps: [DAEO-drvn, DAEO-uudf]
links: []
created: 2026-09-30T22:49:58Z
type: task
priority: 2
assignee: engineer
external-ref: W1-09
tags: [wave-1, implementation, full]
wbs_id: W1-09
title: Ticket vendoring, claims and READY rule
class: implementation
role: engineer
depends_on:
- W1-07
- W1-08
allowed_paths:
- template/governance/kernel/bin/tk
- src/gov/tasks/**
- tests/unit/tasks/**
kpis:
  success:
  - tk v0.3.2 is vendored with sha256 408f2c11... verified by gov doctor
  - A second claim on a held ticket fails with the holder named (O_EXCL lock in .tickets/.claims/)
  - The ready queue excludes tickets that are claimed, whose acceptance tests directory is missing, or whose specification is not closed
  failure:
  - Two agents hold the same claim
  - A ticket without tests/acceptance/<id>/ appears as READY
profile: FULL
sources:
- G-03
- DEC-074
- DEC-069
- CAP-23
- CAP-31
- CAP-53
- MR-2
- MR-3
est_loc: 80
acceptance_tests:
  path: tests/acceptance/W1-09/
  author: independent-test-designer (MR-3, DEC-069); to be written before implementation
---
# W1-09 Ticket vendoring, claims and READY rule

Vendored ticket script plus the claim convention and the READY filter (DEC-069, MR-2).

