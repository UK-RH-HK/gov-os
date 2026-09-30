---
id: DAEO-zsvl
status: open
deps: [DAEO-topz, DAEO-wk2v, DAEO-rrxp]
links: []
created: 2026-09-30T22:49:59Z
type: task
priority: 2
assignee: engineer
external-ref: W1-29
tags: [wave-1, implementation, standard]
wbs_id: W1-29
title: Session hooks
class: implementation
role: engineer
depends_on:
- W1-09
- W1-24
- W1-25
allowed_paths:
- template/governance/kernel/hooks/**
- src/gov/hooks/**
- tests/unit/hooks/**
kpis:
  success:
  - SessionStart injects gov context --brief plus tk ready within the 2.5k-token cap; PreCompact and Stop write checkpoints and respect stop_hook_active
  - SubagentStop enforces the return contract (result, evidence, files changed, checkpoint)
  failure:
  - A Stop hook loops
  - SessionStart injects more than the cap
profile: STANDARD
sources:
- DEC-025
- S0a-G-09
- CAP-15
- CAP-37
est_loc: 150
acceptance_tests:
  path: tests/acceptance/W1-29/
  author: independent-test-designer (MR-3, DEC-069); to be written before implementation
---
# W1-29 Session hooks

SessionStart, PreCompact, Stop and SubagentStop hook scripts.

