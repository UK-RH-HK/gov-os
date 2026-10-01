---
id: DAEO-zsvl
status: open
deps: [DAEO-topz, DAEO-wk2v, DAEO-rrxp]
links: []
created: 2026-09-30T22:49:59Z
type: task
priority: 1
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
  - SessionStart injects gov context --brief plus tk ready within the 2.5k-token cap; PreCompact and Stop write checkpoints and respect stop_hook_active [CAP-15.g, CAP-37.b]
  - SubagentStop enforces the 12-field return contract of Framework §61 (task, status, work_completed, files_changed, evidence, tests, discoveries, risks, lessons, proposed_decisions, unresolved, recommended_next_action)
    [CAP-37.d]
  - A checkpoint is written when the session's context utilisation passes the configured threshold, not only at PreCompact [CAP-37.c]
  failure:
  - A Stop hook loops
  - SessionStart injects more than the cap
  - A handoff or ticket close proceeds while the latest checkpoint is stale for its policy (watchdog, Contract v3 N3)
profile: STANDARD
sources:
- DEC-025
- S0a-G-09
- CAP-15
- CAP-37
est_loc: 180
acceptance_tests:
  path: tests/acceptance/W1-29/
  author: independent-test-designer (MR-3, DEC-069); to be written before implementation
---
# W1-29 Session hooks

SessionStart, PreCompact, Stop and SubagentStop hook scripts.
