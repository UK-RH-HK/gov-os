# W2-181 (DAEO-ywb5) closed: merged and closed in one step by the merge queue (DEC-989)

- Commit tested (the lead's final, verified result): 499543a836d3; merge 7651610c4a19; w2/integrate 32d10098b0b7 -> 7651610c4a19 (fast-forward to the tested merge); profile LITE
- Queue record: /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/merge-queue/records/7651610c4a19.json; log /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/merge-queue/log/20261112-231504-076263
- Batch: W2-181
- Run: scoped, 131 targets; counts {'tests': 4890, 'failures': 1, 'errors': 4, 'skipped': 9}
- Selected: tests/acceptance/W2-157/, tests/unit/accept, tests/unit/adapters, tests/unit/adopt, tests/unit/bridge, tests/unit/brief, tests/unit/check, tests/unit/checkpoint, tests/unit/ci, tests/unit/cli, tests/unit/close/test_evidence.py, tests/unit/close/test_nightly.py, tests/unit/close/test_nightly_cleanup.py, tests/unit/close/test_parallel_runs.py, tests/unit/close/test_run_and_record.py, tests/unit/close/test_select.py, tests/unit/close/test_serial.py, tests/unit/close/test_tool.py, tests/unit/close/test_w2_115_attribution.py, tests/unit/close/test_w2_115_batch.py, tests/unit/close/test_w2_115_close.py, tests/unit/close/test_w2_115_nightly.py, tests/unit/close/test_w2_115_select.py, tests/unit/close/test_w2_115_support.py, tests/unit/close/test_w2_115_verdict.py, tests/unit/close/test_w2_115_verify.py, tests/unit/closure, tests/unit/codeintel, tests/unit/context, tests/unit/decisions, tests/unit/dispatch, tests/unit/doctor, tests/unit/gitenv, tests/unit/guard/test_decide.py::TestAuditor, tests/unit/guard/test_decide.py::TestNonRoleSubagent, tests/unit/guard/test_decide.py::TestDenyOutputFormat, tests/unit/guard/test_decide.py::TestUnparseableBash, tests/unit/guard/test_decide.py::TestHookProcess, tests/unit/guard/test_decide.py::TestRoleSubagentNoSessionRole, tests/unit/guard/test_decide.py::TestRoleSubagentGoverns ...
- Reds caused by the change: none (the queue advances only then); flaky candidates: tests/unit/dispatch/test_peaks.py, tests/unit/dispatch/test_returns.py, tests/unit/dispatch/test_start.py, tests/unit/dispatch/test_status.py, tests/unit/orchestration/test_w2_149_indep_launch.py::test_f8_the_schemas_hashes_are_in_the_wall
- Traced against: 32d10098b0b7c53febb00990ecd887697fdd82c5 (the head without the batch, once each way, the same failure; 3 rounds for the load-sensitive list's cases (Q-1, DEC-1050))
- Red on the head without the batch too, the same failure, not this change's (investigated by the CTO at once, DEC-968): none
- Acceptance tests' authors (G-1, DEC-1050): 1 commit(s) changing tests/acceptance/, each with Role: independent-test-designer or owner
- Core changed (scoped, not full, DEC-968): none; unplaced: none
- Review: not required (LITE)
- gitleaks: off by configuration (DEC-1045): the change was not scanned
- Queue run: 2026-11-12 23:15:04 to 2026-11-12 23:28:24
- Closed: 2026-11-12 23:29:02 GMT, by the orchestrator under DEC-953 items 1 and 5, DEC-989
