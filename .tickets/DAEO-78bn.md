---
id: DAEO-78bn
status: closed
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
state_class: AUTHORITATIVE
role: engineer
depends_on:
- W1-02
allowed_paths:
- src/gov/guard/install*
- template/governance/kernel/hooks/pretooluse*
- template/governance/kernel/schemas/tool-registry*
- tests/unit/install/**
kpis:
  success:
  - Install commands (package managers, curl|sh, binary downloads into PATH) from the orchestrator return an ask decision; from any other role they are denied [CAP-25.b]
  - The approval prompt appears even when the harness runs in Auto mode (DEC-083 KPI) [CAP-25.b]
  - The tool-registry schema requires version, sha256, install and uninstall commands, date and approving decision id [CAP-25.a]
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

## Notes

**2026-10-02T18:20:34Z**

Reopened 2026-10-02 as a repair for three defects shown by the acceptance tests added in 17ef3ae (probe findings, DEC-136): uv with an option before the subcommand, pip2 and python2.7 -m pip, wget -qO FILE into a PATH directory. KPIs unchanged.

**2026-10-03T13:06:19Z**

S2 (2026-10-03): no KPI change. Under DEC-152 and DEC-161 the OS sandbox backs this rule's misses in launched worker sessions (write wall and network wall); in the orchestrator's own session the rule and the settings ask rules stand alone. Worker roles never install system-wide (DEC-157).

**2026-10-03T13:41:57Z**

S2 repair 2026-10-03 (DEC-163). W1-46 adds a minimal research role that may install inside its own experiment folder only; the sandbox's write fence denies a system-wide install. Install commands stay denied for every other worker role. KPIs and status unchanged.

**2026-10-03T14:16:48Z**

S2 round-2 repair (2026-10-03): no KPI change. DEC-172 withdraws the settings ask rules for installs and downloads; W1-47 removes them from the committed .claude/settings.json. From then this rule decides install commands alone, in the orchestrator's own session too; in launched worker sessions the sandbox backs it.
