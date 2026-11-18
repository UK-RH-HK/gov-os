# W1-04 — Install-approval rule: acceptance tests

Written by the Independent Test Designer (MR-3, DEC-069) from the KPIs of ticket `DAEO-78bn` (W1-04), the Contract v4
items it cites (CAP-25.a, CAP-25.b) and the owner's answers DEC-120, DEC-121 and DEC-127.

**Retired with the guard (EMERGENCY-2 6.1, DAEO-gr7t).** The install rule lived in the PreToolUse guard, which is retired:
every case that put an install command, `sudo` or a permission mode through the guard
(`test_w1_04_install_rule.py`, `test_w1_04_sudo.py`, `test_w1_04_only_escalates.py`, `test_w1_04_auto_mode.py`,
`test_w1_04_probe_findings.py`) is deleted. What stays is the tool-registry schema (success 3): the schema is still in the
kernel template. `w1_04_support.py` stays as the fixture project and ticket form other suites use (W2-110's
`w2_110_support.py`, through W2-113); its guard half is retired.

## Run

```sh
python3 -m pytest tests/acceptance/W1-04 -q
```

Standard library and `pytest` only. No network, no dev tiers, no `local_only` tests.

## KPI map

| KPI line | tests | expected red reason |
|---|---|---|
| success-1: install commands from the orchestrator return an ask decision, from any other role a denial [CAP-25.b] | retired with the guard, EMERGENCY-2 6.1, DAEO-gr7t | none: no test |
| success-2: the approval prompt appears even in Auto mode [CAP-25.b] | retired with the guard, EMERGENCY-2 6.1, DAEO-gr7t | none: no test |
| success-3: the tool-registry schema requires version, sha256, install and uninstall commands, date and approving decision id [CAP-25.a] | `test_w1_04_registry_schema.py` | the schema file is missing or lets a registry without one of the six facts through |
| failure-1: any install executes without an owner approval in chat | retired with the guard, EMERGENCY-2 6.1, DAEO-gr7t | none: no test |
| failure-2: sudo is ever allowed to an agent role | retired with the guard, EMERGENCY-2 6.1, DAEO-gr7t | none: no test |
| failure-3: a matcher result ever allows a command the harness would otherwise ask about | retired with the guard, EMERGENCY-2 6.1, DAEO-gr7t | none: no test |
