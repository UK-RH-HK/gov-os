# W2-124 (DAEO-mb2t) closed: merged and closed in one step by the merge queue (DEC-989)

- Commit tested (the lead's final, verified result): 80ee394a89cb; merge a2f28ccf319e; w2/integrate 50e59c1ec87b -> a2f28ccf319e (fast-forward to the tested merge); profile STANDARD
- Queue record: /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/merge-queue/records/a2f28ccf319e.json; log /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/merge-queue/log/20261112-202304-369605
- Batch: W2-124
- Run: scoped, 188 targets; counts {'tests': 5752, 'failures': 1, 'errors': 4, 'skipped': 13}
- Selected: tests/acceptance/W2-124/, tests/unit/accept, tests/unit/adapters, tests/unit/adopt, tests/unit/bridge, tests/unit/brief, tests/unit/check, tests/unit/checkpoint, tests/unit/ci, tests/unit/cli, tests/unit/close/test_evidence.py, tests/unit/close/test_nightly.py, tests/unit/close/test_nightly_cleanup.py, tests/unit/close/test_parallel_runs.py, tests/unit/close/test_run_and_record.py, tests/unit/close/test_select.py, tests/unit/close/test_serial.py, tests/unit/close/test_tool.py, tests/unit/close/test_w2_115_attribution.py, tests/unit/close/test_w2_115_batch.py, tests/unit/close/test_w2_115_close.py, tests/unit/close/test_w2_115_nightly.py, tests/unit/close/test_w2_115_select.py, tests/unit/close/test_w2_115_support.py, tests/unit/close/test_w2_115_verdict.py, tests/unit/close/test_w2_115_verify.py, tests/unit/closure, tests/unit/codeintel, tests/unit/context, tests/unit/decisions, tests/unit/dispatch, tests/unit/doctor, tests/unit/gitenv, tests/unit/guard/test_decide.py::TestAuditor, tests/unit/guard/test_decide.py::TestNonRoleSubagent, tests/unit/guard/test_decide.py::TestDenyOutputFormat, tests/unit/guard/test_decide.py::TestUnparseableBash, tests/unit/guard/test_decide.py::TestHookProcess, tests/unit/guard/test_decide.py::TestRoleSubagentNoSessionRole, tests/unit/guard/test_decide.py::TestRoleSubagentGoverns ...
- Reds caused by the change: none (the queue advances only then); flaky candidates: tests/unit/dispatch/test_peaks.py, tests/unit/dispatch/test_returns.py, tests/unit/dispatch/test_start.py, tests/unit/dispatch/test_status.py
- Traced against: 50e59c1ec87b4be51fb86f6d559a4e2960d01a93 (the head without the batch, once each way, the same failure; 3 rounds for the load-sensitive list's cases (Q-1, DEC-1050))
- Red on the head without the batch too, the same failure, not this change's (investigated by the CTO at once, DEC-968): tests/acceptance/W2-23/test_w2_23_space.py::test_s6_every_kernel_hook_exits_alike_with_a_space_in_the_project_dir
- Acceptance tests' authors (G-1, DEC-1050): 2 commit(s) changing tests/acceptance/, each with Role: independent-test-designer or owner
- Core changed (scoped, not full, DEC-968): src/gov/close/rebuild_gate.py; unplaced: none
- Review: not required (STANDARD)
- gitleaks: off by configuration (DEC-1045): the change was not scanned
- Queue run: 2026-11-12 20:23:04 to 2026-11-12 20:58:57
- Closed: 2026-11-12 20:59:44 GMT, by the orchestrator under DEC-953 items 1 and 5, DEC-989
