---
id: DAEO-78bn
status: open
deps: [DAEO-emkd]
links: []
created: 2026-09-30T22:49:58Z
type: task
priority: 2
assignee: engineer
external-ref: W1-04
tags: [wave-1, implementation, full]
wbs_id: W1-04
title: Install-approval rule
class: implementation
role: engineer
depends_on:
- W1-02
allowed_paths:
- src/gov/guard/install*
- template/governance/kernel/schemas/tool-registry*
- tests/unit/install/**
kpis:
  success:
  - Install commands (package managers, curl|sh, binary downloads into PATH) from the orchestrator return an ask decision; from any other role they are denied
  - The approval prompt appears even when the harness runs in Auto mode (DEC-083 KPI)
  - The tool-registry schema requires version, sha256, install and uninstall commands, date and approving decision id
  failure:
  - Any install executes without an owner approval in chat
  - sudo is ever allowed to an agent role
  - A matcher result ever allows a command that the harness would otherwise ask about (matching only escalates to ask or deny)
profile: FULL
sources:
- DEC-083
- DEC-040
- CAP-25
est_loc: 60
acceptance_tests:
  path: tests/acceptance/W1-04/
  author: independent-test-designer (MR-3, DEC-069); to be written before implementation
---
# W1-04 Install-approval rule

DEC-040 as amended by DEC-083: orchestrator-only install proposals, owner approval in chat, registry record.
