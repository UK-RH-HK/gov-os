---
id: DAEO-dtv3
status: open
deps: []
links: []
created: 2026-09-30T22:49:58Z
type: task
priority: 1
assignee: orchestrator
external-ref: W1-01
tags: [wave-1, config, lite]
wbs_id: W1-01
title: Interim bootstrap guardrails
class: config
role: orchestrator
depends_on: []
allowed_paths:
- .claude/settings.json
- governance/project/bootstrap.md
kpis:
  success:
  - Implementer sessions deny Edit/Write on tests/acceptance/** and on .env*, *.pem, *.key, config/secrets* (verified by one denied attempt each)
  - The operator diff procedure (git diff --name-only vs allowed_paths at each ticket close) is written and used from the first implementation ticket
  failure:
  - Any implementer commit touching tests/acceptance/** before W1-05 lands
  - An existing docs/source deny rule is lost
profile: LITE
sources:
- DEC-084
- DEC-074 Q9
- CAP-58
- CAP-03
est_loc: 30
acceptance_tests:
  path: tests/acceptance/W1-01/
  author: independent-test-designer (MR-3, DEC-069); to be written before implementation
---
# W1-01 Interim bootstrap guardrails

Settings-level guardrails that hold MR-3 until the guard and containment tickets pass their acceptance tests (DEC-084).

