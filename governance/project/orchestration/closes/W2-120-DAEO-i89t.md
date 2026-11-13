# W2-120 (DAEO-i89t) closed: merged and closed in one step by the merge queue (DEC-989)

- Commit tested (the lead's final, verified result): 1eec1209bd0a; merge 0ab1510bb72f; w2/integrate aa3bfdc19b9d -> 0ab1510bb72f (fast-forward to the tested merge); profile STANDARD
- Queue record: /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/merge-queue/records/0ab1510bb72f.json; log /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/merge-queue/log/20261113-005604-420658
- Batch: W2-120
- Run: scoped, 179 targets; counts {'tests': 5101, 'failures': 0, 'errors': 4, 'skipped': 8}
- Selected: tests/acceptance/W2-120/, tests/unit/accept, tests/unit/adapters, tests/unit/adopt, tests/unit/bridge, tests/unit/brief, tests/unit/check, tests/unit/checkpoint, tests/unit/ci, tests/unit/cli, tests/unit/close/test_evidence.py, tests/unit/close/test_nightly.py, tests/unit/close/test_nightly_cleanup.py, tests/unit/close/test_parallel_runs.py, tests/unit/close/test_run_and_record.py, tests/unit/close/test_select.py, tests/unit/close/test_serial.py, tests/unit/close/test_tool.py, tests/unit/close/test_w2_115_attribution.py, tests/unit/close/test_w2_115_batch.py, tests/unit/close/test_w2_115_close.py, tests/unit/close/test_w2_115_nightly.py, tests/unit/close/test_w2_115_select.py, tests/unit/close/test_w2_115_support.py, tests/unit/close/test_w2_115_verdict.py, tests/unit/close/test_w2_115_verify.py, tests/unit/closure, tests/unit/codeintel, tests/unit/context, tests/unit/decisions, tests/unit/dispatch, tests/unit/doctor, tests/unit/gitenv, tests/unit/guard/test_decide.py::TestAuditor, tests/unit/guard/test_decide.py::TestNonRoleSubagent, tests/unit/guard/test_decide.py::TestDenyOutputFormat, tests/unit/guard/test_decide.py::TestUnparseableBash, tests/unit/guard/test_decide.py::TestHookProcess, tests/unit/guard/test_decide.py::TestRoleSubagentNoSessionRole, tests/unit/guard/test_decide.py::TestRoleSubagentGoverns ...
- Reds caused by the change: none (the queue advances only then); flaky candidates: tests/unit/dispatch/test_peaks.py, tests/unit/dispatch/test_returns.py, tests/unit/dispatch/test_start.py, tests/unit/dispatch/test_status.py
- Traced against: 9ad3bf74290f4c7447b079a002c94b708561f450 (the head without the batch, once each way, the same failure; 3 rounds for the load-sensitive list's cases (Q-1, DEC-1050))
- Red on the head without the batch too, the same failure, not this change's (investigated by the CTO at once, DEC-968): none
- Acceptance tests' authors (G-1, DEC-1050): 2 commit(s) changing tests/acceptance/, each with Role: independent-test-designer or owner
- Core changed (scoped, not full, DEC-968): src/gov/check/skill_validator.py; unplaced: none
- Review: not required (STANDARD)
- gitleaks: off by configuration (DEC-1045): the change was not scanned
- Queue run: 2026-11-13 00:56:04 to 2026-11-13 01:15:56
- Closed: 2026-11-13 01:16:40 GMT, by the orchestrator under DEC-953 items 1 and 5, DEC-989
