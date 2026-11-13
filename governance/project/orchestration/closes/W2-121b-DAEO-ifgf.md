# W2-121b (DAEO-ifgf) closed: merged and closed in one step by the merge queue (DEC-989)

- Commit tested (the lead's final, verified result): 6e10493a5f8e; merge c8f4e393327e; w2/integrate 84cc42343ffb -> c8f4e393327e (fast-forward to the tested merge); profile FULL
- Queue record: /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/merge-queue/records/c8f4e393327e.json; log /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/merge-queue/log/20261112-235305-079328
- Batch: W2-121b
- Run: scoped, 136 targets; counts {'tests': 5381, 'failures': 1, 'errors': 4, 'skipped': 23}
- Selected: tests/acceptance/W2-121b/, tests/unit/accept, tests/unit/adapters, tests/unit/adopt, tests/unit/bridge, tests/unit/brief, tests/unit/check, tests/unit/checkpoint, tests/unit/ci, tests/unit/cli, tests/unit/close/test_evidence.py, tests/unit/close/test_nightly.py, tests/unit/close/test_nightly_cleanup.py, tests/unit/close/test_parallel_runs.py, tests/unit/close/test_run_and_record.py, tests/unit/close/test_select.py, tests/unit/close/test_serial.py, tests/unit/close/test_tool.py, tests/unit/close/test_w2_115_attribution.py, tests/unit/close/test_w2_115_batch.py, tests/unit/close/test_w2_115_close.py, tests/unit/close/test_w2_115_nightly.py, tests/unit/close/test_w2_115_select.py, tests/unit/close/test_w2_115_support.py, tests/unit/close/test_w2_115_verdict.py, tests/unit/close/test_w2_115_verify.py, tests/unit/closure, tests/unit/codeintel, tests/unit/context, tests/unit/decisions, tests/unit/dispatch, tests/unit/doctor, tests/unit/gitenv, tests/unit/guard/test_decide.py::TestAuditor, tests/unit/guard/test_decide.py::TestNonRoleSubagent, tests/unit/guard/test_decide.py::TestDenyOutputFormat, tests/unit/guard/test_decide.py::TestUnparseableBash, tests/unit/guard/test_decide.py::TestHookProcess, tests/unit/guard/test_decide.py::TestRoleSubagentNoSessionRole, tests/unit/guard/test_decide.py::TestRoleSubagentGoverns ...
- Reds caused by the change: none (the queue advances only then); flaky candidates: tests/unit/dispatch/test_peaks.py, tests/unit/dispatch/test_returns.py, tests/unit/dispatch/test_start.py, tests/unit/dispatch/test_status.py, tests/acceptance/W2-121/test_s1_lock_off_status.py::test_s1_two_ticks_started_together_run_one_pass
- Traced against: 84cc42343ffb66e19f039d5718c68fb3434014c2 (the head without the batch, once each way, the same failure; 3 rounds for the load-sensitive list's cases (Q-1, DEC-1050))
- Red on the head without the batch too, the same failure, not this change's (investigated by the CTO at once, DEC-968): none
- Acceptance tests' authors (G-1, DEC-1050): 3 commit(s) changing tests/acceptance/, each with Role: independent-test-designer or owner
- Core changed (scoped, not full, DEC-968): none; unplaced: none
- Review: docs/probes/DAEO-ifgf/PR-DAEO-ifgf.md
- gitleaks: off by configuration (DEC-1045): the change was not scanned
- Queue run: 2026-11-12 23:53:05 to 2026-11-13 00:11:28
- Closed: 2026-11-13 00:16:49 GMT, by the orchestrator under DEC-953 items 1 and 5, DEC-989
