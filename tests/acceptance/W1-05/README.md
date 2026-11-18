# W1-05 — Dogfood switch-over: acceptance tests

Written by the Independent Test Designer (MR-3, DEC-069) from the KPIs of ticket `DAEO-m7u4` (W1-05) as updated under
DEC-119, and from DEC-084, DEC-113, DEC-117 and DEC-118.

**Retired with the guard (EMERGENCY-2 6.1, DAEO-gr7t).** The live hooks, the guard's decisions on a subagent type and
the containment check are retired: `test_w1_05_live_hooks.py` (every case: the PreToolUse and PostToolUse wiring, the
guard's write, read, install and sudo decisions, the 100 ms p95, the containment restore) and, in
`test_w1_05_role_subagents.py`, the two cases that put a subagent type through the guard
(`test_the_live_guard_takes_the_definition_s_type_name_as_the_role`,
`test_the_engineer_subagent_can_work_on_an_engineer_ticket`) are deleted. What stays is the record that the diff check
is retired and the five subagent definitions.

## Run

```sh
python3 -m pytest tests/acceptance/W1-05 -q
```

Standard library and `pytest` only. No network, no dev tiers, no `local_only` tests. The tests read
`governance/project/bootstrap.md` and `.claude/agents/`.

## KPI map

| KPI line | tests | expected red reason |
|---|---|---|
| success-1: The Gov OS repository runs W1-02, W1-03 and W1-04 as live hooks for every later ticket | retired with the guard, EMERGENCY-2 6.1, DAEO-gr7t | none: no test |
| success-2: The interim operator diff check is retired and recorded as such | `test_w1_05_switch_over_record.py::test_the_operator_diff_check_is_recorded_as_retired` | `bootstrap.md` nowhere says the diff check is retired |
| success-3 to 7: A minimal subagent definition for each of the orchestrator, engineer, product-spec, independent-test-designer and independent-auditor roles exists under `.claude/agents/`, with that subagent type name (DEC-119) | `test_w1_05_role_subagents.py::test_a_subagent_definition_exists_for_the_role` | `.claude/agents/` does not exist |
| failure-1: A later ticket runs without the guard active | retired with the guard, EMERGENCY-2 6.1, DAEO-gr7t | none: no test |
| failure-2: The switch-over happens before W1-02..04 acceptance tests pass | retired (DEC-899), and with the guard | none: no test |
