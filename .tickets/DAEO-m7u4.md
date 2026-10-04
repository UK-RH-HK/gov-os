---
id: DAEO-m7u4
status: closed
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
state_class: AUTHORITATIVE
role: orchestrator
depends_on:
- W1-02
- W1-03
- W1-04
allowed_paths:
- .claude/settings.json
- governance/project/bootstrap.md
- governance/project/roster.yaml
- .claude/agents/**
kpis:
  success:
  - The Gov OS repository runs W1-02, W1-03 and W1-04 as live hooks for every later ticket
  - The interim operator diff check is retired and recorded as such
  - A minimal subagent definition for the orchestrator role exists under .claude/agents/, with the subagent type name orchestrator (DEC-119) [CAP-22.a]
  - A minimal subagent definition for the engineer role exists under .claude/agents/, with the subagent type name engineer (DEC-119) [CAP-22.a]
  - A minimal subagent definition for the product-spec role exists under .claude/agents/, with the subagent type name product-spec (DEC-119) [CAP-22.a]
  - A minimal subagent definition for the independent-test-designer role exists under .claude/agents/, with the subagent type name independent-test-designer (DEC-119) [CAP-22.a]
  - A minimal subagent definition for the independent-auditor role exists under .claude/agents/, with the subagent type name independent-auditor (DEC-119) [CAP-22.a]
  failure:
  - A later ticket runs without the guard active
  - The switch-over happens before W1-02..04 acceptance tests pass
profile: LITE
sources:
- DEC-084
- MR-3
- CAP-22
- DEC-119
est_loc: 20
acceptance_tests:
  path: tests/acceptance/W1-05/
  author: independent-test-designer (MR-3, DEC-069); to be written before implementation
---
# W1-05 Dogfood switch-over

Wire the guard, containment and install rule into this repository once their acceptance tests pass (DEC-084).

## Notes

**2026-10-02T21:17:41Z**

Claimed 2026-10-02 before a test design request (DEC-133). The acceptance tests of 7b7d01b and 2cdabc9 predate DEC-142 and DEC-144: they require the PreToolUse hook for Edit, Write, NotebookEdit and Bash only, while a later tool call of any tool by the same actor must reach the hook. Implementation waits for TESTS READY. KPIs unchanged.
