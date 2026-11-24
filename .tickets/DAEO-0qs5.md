---
id: DAEO-0qs5
status: closed
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
state_class: AUTHORITATIVE
role: orchestrator
depends_on:
- DAEO-ipqy
allowed_paths:
- governance/project/tool-registry.yaml
kpis:
  success:
  - Claude Code is recorded in governance/project/tool-registry.yaml pinned at 2.1.285 or later, with install and uninstall commands, date and approving decision; the upgrade is installed by the owner,
    or by the orchestrator under DEC-083, and in both cases recorded with its owner approval (DEC-157, DEC-203, DEC-209) [CAP-25.d]
  - The CLI used for headless runs and the active VS Code extension's bundled version are both at or above the minimum, 2.1.285, and the registry record states both; a difference between them, or from the registry's record,
    is drift that gov doctor reports, not a failure, except that the CLI at the recorded version with another sha256 is a failure (DEC-210, DEC-214) [CAP-61.e]
  - The sandbox prerequisites bubblewrap 0.9.0 and socat 1.8.0.0 are recorded in governance/project/tool-registry.yaml as owner installs, with version, install and uninstall commands, date and approving decision (DEC-141)
  failure:
  - A headless run uses a CLI below 2.1.285
  - bubblewrap or socat is missing from the registry while gov launch depends on it
  - The pin is raised without a recorded owner approval
profile: LITE
sources:
- DEC-153
- DEC-141
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

## Fix: the KPI map of W1-48 in the form `gov accept` reads (F17)

Found 2026-11-22 (fixes-015a): `gov accept W1-48` stopped with `ACCEPT_MAP_UNREADABLE`. Kind: a fix, no new ticket; the ticket
stays closed. The README's map was rewritten in the form `gov accept` reads (`1771c4283`); no test changed. It now reads the map;
lines that still read fail name tests of files retired by TI-6, not found: see the next paragraph.

Left on the base: `success-3` and `failure-2` name `test_w1_48_sandbox_prereqs.py`'s cases (retired, TI-6 `ba3e86bce`), and `success-1`'s one failure is `test_every_node_22_command_of_the_registry_carries_the_path_prefix` (the registry's `rea-agents` install carries the v22.23.5 prefix).
