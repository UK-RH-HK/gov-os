---
id: DAEO-rrxp
status: open
deps: [DAEO-drvn, DAEO-uudf]
links: []
created: 2026-09-30T22:49:59Z
type: task
priority: 2
assignee: engineer
external-ref: W1-25
tags: [wave-1, implementation, standard]
wbs_id: W1-25
title: gov checkpoint
class: implementation
role: engineer
depends_on:
- W1-07
- W1-08
allowed_paths:
- src/gov/checkpoint/**
- tests/unit/checkpoint/**
kpis:
  success:
  - A checkpoint conforming to the carried schema is written at every ticket transition, compaction and stop
  - A fresh session resumes the ticket at the recorded next step from the checkpoint alone
  failure:
  - A ticket transition leaves no checkpoint
  - A checkpoint references an input by id without its hash
profile: STANDARD
sources:
- S0a-G-09
- CAP-13
- CAP-22
- CAP-37
est_loc: 150
acceptance_tests:
  path: tests/acceptance/W1-25/
  author: independent-test-designer (MR-3, DEC-069); to be written before implementation
---
# W1-25 gov checkpoint

Structured checkpoints in the repository.

