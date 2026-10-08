---
id: DAEO-8goq
status: in_progress
deps: [DAEO-w616, DAEO-9279, DAEO-6mk8]
links: []
created: 2026-09-30T22:49:59Z
type: task
priority: 2
assignee: engineer
external-ref: W1-32
tags: [wave-1, implementation, standard]
wbs_id: W1-32
title: gov status
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on:
- W1-13
- W1-28
- W1-31
allowed_paths:
- src/gov/status/**
- tests/unit/status/**
- src/gov/launch/**
- tests/unit/launch/**
kpis:
  success:
  - gov launch keeps the session's exit code and names the folder on stderr when its temp folder cannot be removed; SIGTERM and SIGHUP end the session and remove the folder as an interrupt does; the exit code after an interrupt is 130 (from W1-28, DEC-392)
  - gov status --json reports ready/blocked/claimed tickets, open decision packages, readiness per specification, governance share, pause state and doctor summary
  - Pause state appears in gov status (moved from W1-28, DEC-364)
  - 'Read-only: git status --porcelain unchanged [CAP-27.a]'
  - The command set stays at the Wave 1 list (no command without a contract item) [CAP-28.a]
  failure:
  - status mutates the repository
  - An open gate is missing from the output
profile: STANDARD
sources:
- S0a-G-01
- CAP-28
- CAP-27
est_loc: 80
acceptance_tests:
  path: tests/acceptance/W1-32/
  author: independent-test-designer (MR-3, DEC-069); to be written before implementation
---
# W1-32 gov status

The human control surface.
