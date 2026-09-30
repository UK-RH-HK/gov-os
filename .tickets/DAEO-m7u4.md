---
id: DAEO-m7u4
status: open
deps: [DAEO-emkd, DAEO-8qvp, DAEO-78bn]
links: []
created: 2026-09-30T22:49:58Z
type: task
priority: 1
assignee: orchestrator
external-ref: W1-05
tags: [wave-1, config, lite]
wbs_id: W1-05
title: Dogfood switch-over
class: config
role: orchestrator
depends_on:
- W1-02
- W1-03
- W1-04
allowed_paths:
- .claude/settings.json
- governance/project/bootstrap.md
- governance/project/roster.yaml
kpis:
  success:
  - The Gov OS repository runs W1-02, W1-03 and W1-04 as live hooks for every later ticket
  - The interim operator diff check is retired and recorded as such
  failure:
  - A later ticket runs without the guard active
  - The switch-over happens before W1-02..04 acceptance tests pass
profile: LITE
sources:
- DEC-084
- MR-3
est_loc: 20
acceptance_tests:
  path: tests/acceptance/W1-05/
  author: independent-test-designer (MR-3, DEC-069); to be written before implementation
---
# W1-05 Dogfood switch-over

Wire the guard, containment and install rule into this repository once their acceptance tests pass (DEC-084).

