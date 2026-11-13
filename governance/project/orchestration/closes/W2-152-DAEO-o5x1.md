# W2-152 (DAEO-o5x1) closed: merged and closed in one step by the merge queue (DEC-989)

- Commit tested (the lead's final, verified result): 2900a31d2681; merge 0a362c042c48; w2/integrate 48ef8cf6603b -> 0a362c042c48 (fast-forward to the tested merge); profile STANDARD
- Queue record: /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/merge-queue/records/0a362c042c48.json; log /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/merge-queue/log/20261112-191509-607093
- Batch: W2-152
- Run: scoped, 120 targets; counts {'tests': 4630, 'failures': 0, 'errors': 4, 'skipped': 8}
- Selected: tests/acceptance/W2-152/, tests/unit/accept, tests/unit/adapters, tests/unit/adopt, tests/unit/bridge, tests/unit/brief, tests/unit/check, tests/unit/checkpoint, tests/unit/ci, tests/unit/cli, tests/unit/close/test_evidence.py, tests/unit/close/test_nightly.py, tests/unit/close/test_nightly_cleanup.py, tests/unit/close/test_parallel_runs.py, tests/unit/close/test_run_and_record.py, tests/unit/close/test_select.py, tests/unit/close/test_serial.py, tests/unit/close/test_tool.py, tests/unit/closure, tests/unit/codeintel, tests/unit/context, tests/unit/decisions, tests/unit/dispatch, tests/unit/doctor, tests/unit/gitenv, tests/unit/guard/test_decide.py::TestAuditor, tests/unit/guard/test_decide.py::TestNonRoleSubagent, tests/unit/guard/test_decide.py::TestDenyOutputFormat, tests/unit/guard/test_decide.py::TestUnparseableBash, tests/unit/guard/test_decide.py::TestHookProcess, tests/unit/guard/test_decide.py::TestRoleSubagentNoSessionRole, tests/unit/guard/test_decide.py::TestRoleSubagentGoverns, tests/unit/guard/test_decide.py::TestExpandToken, tests/unit/guard/test_decide.py::TestFreezeState, tests/unit/guard/test_decide.py::TestUnmarkedFlagRecord, tests/unit/guard/test_heldout.py, tests/unit/guard/test_heldout_limit.py, tests/unit/guard/test_hook_deadline.py, tests/unit/guard/test_reads.py::test_each_route_is_decided_as_policy_2_says, tests/unit/guard/test_reads.py::test_the_search_refusal_names_the_folder_and_how_to_exclude_it ...
- Reds caused by the change: none (the queue advances only then); flaky candidates: tests/unit/dispatch/test_peaks.py, tests/unit/dispatch/test_returns.py, tests/unit/dispatch/test_start.py, tests/unit/dispatch/test_status.py
- Traced against: 48ef8cf6603b57dd8d3506875bd28e07737fb123 (the head without the batch, once each way, the same failure; 3 rounds for the load-sensitive list's cases (Q-1, DEC-1050))
- Red on the head without the batch too, the same failure, not this change's (investigated by the CTO at once, DEC-968): none
- Acceptance tests' authors (G-1, DEC-1050): no commit changes tests/acceptance/
- Core changed (scoped, not full, DEC-968): none; unplaced: none
- Review: not required (STANDARD)
- gitleaks: off by configuration (DEC-1045): the change was not scanned
- Queue run: 2026-11-12 19:15:09 to 2026-11-12 19:26:52
- Closed: 2026-11-12 19:32:59 GMT, by the orchestrator under DEC-953 items 1 and 5, DEC-989
