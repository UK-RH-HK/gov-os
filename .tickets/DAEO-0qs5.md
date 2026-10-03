---
id: DAEO-0qs5
status: open
deps: [DAEO-ipqy]
links: []
created: 2026-10-03T13:05:33Z
type: task
priority: 2
assignee: orchestrator
external-ref: W1-48
tags: [wave-1, ops, lite]
wbs_id: W1-48
title: Claude Code version pin
class: ops
role: orchestrator
depends_on:
- W1-06
allowed_paths:
- governance/project/tool-registry.yaml
kpis:
  success:
  - Claude Code is recorded in governance/project/tool-registry.yaml pinned at 2.1.285 or later, with install and uninstall commands, date and approving decision; the upgrade is installed by the orchestrator
    through a DEC-083 decision package (DEC-157) [CAP-25.d]
  - The CLI used for headless runs and the VS Code extension's bundled version are the same version, at or above the pin, and the registry record states both [CAP-61.e]
  failure:
  - A headless run uses a CLI below 2.1.285
  - The pin is raised without a recorded owner approval
profile: LITE
sources:
- DEC-153
- DEC-157
- DEC-083
- CAP-25
- CAP-61
est_loc: 10
acceptance_tests:
  path: tests/acceptance/W1-48/
  author: independent-test-designer (MR-3, DEC-069); to be written before implementation
---
# W1-48 Claude Code version pin

DEC-153 ticket 3. The spike saw 2.1.284 on the CLI; the test designer saw 2.1.286. Strict sandbox mode needs 2.1.285 or
later (`spike-sandbox/EVIDENCE.md` §5.5).
