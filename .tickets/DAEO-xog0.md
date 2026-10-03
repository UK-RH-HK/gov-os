---
id: DAEO-xog0
status: open
deps: [DAEO-m7u4]
links: []
created: 2026-09-30T22:49:59Z
type: task
priority: 2
assignee: product-spec
external-ref: W1-33
tags: [wave-1, role-definition, standard]
wbs_id: W1-33
title: Wave 1 role definitions
class: role-definition
role: product-spec
depends_on:
- W1-05
allowed_paths:
- template/governance/kernel/roles/**
- governance/project/roster.yaml
- .claude/agents/**
kpis:
  success:
  - Five roles (orchestrator, product/spec, independent test designer, engineer, independent auditor) each with purpose, allowed-path pattern, tools, model tier, authority level and handoff format [CAP-22.a]
  - Only the test designer pattern includes tests/acceptance/**; the auditor is read-only; only the orchestrator may install, and only after owner approval in chat (DEC-083)
  - 'Each role maps the Framework §32 permission classes: WRITE_REPO_SCOPED via allowed_paths; PACKAGE_INSTALL/SYSTEM_INSTALL per DEC-083; SECRET_READ denied; network, database, cloud, CI-trigger and deploy
    classes denied unless granted [CAP-58.b]'
  - The generated definitions replace the minimal definitions W1-05 placed under .claude/agents/ (DEC-119, DEC-154); the orchestrator definition states its write scope, anywhere in the repository except
    tests/acceptance/** (DEC-156) [CAP-22.a]
  - The generated definitions leave the minimal research role of W1-46 in place where it exists; W1-33 does not redefine it (DEC-163)
  failure:
  - A role lacks any required field
  - An implementer role pattern covers tests/acceptance/**
profile: STANDARD
sources:
- DEC-066
- DEC-083
- MR-5
- CAP-47
- CAP-22
- CAP-58
- MR-3
- MR-4
- DEC-119
- DEC-154
- DEC-156
- DEC-163
est_loc: 300
acceptance_tests:
  path: tests/acceptance/W1-33/
  author: independent-test-designer (MR-3, DEC-069); to be written before implementation
---
# W1-33 Wave 1 role definitions

The virtual software company, Wave 1 roster.
