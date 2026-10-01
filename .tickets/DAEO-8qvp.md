---
id: DAEO-8qvp
status: open
deps: [DAEO-emkd]
links: []
created: 2026-09-30T22:49:58Z
type: task
priority: 1
assignee: engineer
external-ref: W1-03
tags: [wave-1, implementation, full]
wbs_id: W1-03
title: Post-command containment check
class: implementation
role: engineer
depends_on:
- W1-02
allowed_paths:
- src/gov/guard/containment*
- template/governance/kernel/hooks/posttooluse*
- tests/unit/containment/**
kpis:
  success:
  - After every Bash call and at gov close, git status --porcelain is compared with allowed_paths; a change outside them is reported to the agent and recorded as a containment finding [CAP-58.a]
  - Changes under tests/acceptance/** by a non-test-designer role are restored from HEAD and the breach is recorded
  - All nine Bash write forms from S0b2 I-06 are caught
  failure:
  - Any out-of-scope change survives without a finding
  - A legitimate in-scope change is reverted
profile: FULL
sources:
- G-02
- DEC-076
- CAP-58
- MR-3
est_loc: 100
acceptance_tests:
  path: tests/acceptance/W1-03/
  author: independent-test-designer (MR-3, DEC-069); to be written before implementation
---
# W1-03 Post-command containment check

Second line of defence for Bash writes the guard cannot parse (G-02, moved to W1 by DEC-076).
