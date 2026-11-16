# W2-111 (DAEO-qvff) closed: merged and closed in one step by the merge queue (DEC-989)

- Commit tested (the lead's final, verified result): c3cf424d60f9; merge 15cdf69db712; w2/integrate 13a3d62b9e01 -> 15cdf69db712 (fast-forward to the tested merge); profile FULL
- Queue record: /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/merge-queue/records/15cdf69db712.json; log /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/merge-queue/log/20261116-024003-561661
- Batch: W2-111
- Run: scoped, 311 targets; counts {'tests': 9852, 'failures': 0, 'errors': 4, 'skipped': 10}
- Selected: tests/acceptance/W2-111/, tests/unit/accept, tests/unit/adapters, tests/unit/adopt, tests/unit/bridge, tests/unit/brief, tests/unit/check, tests/unit/checkpoint, tests/unit/ci, tests/unit/cli, tests/unit/close/test_evidence.py, tests/unit/close/test_nightly.py, tests/unit/close/test_nightly_cleanup.py, tests/unit/close/test_parallel_runs.py, tests/unit/close/test_run_and_record.py, tests/unit/close/test_select.py, tests/unit/close/test_serial.py, tests/unit/close/test_serial_eng_w2_154.py, tests/unit/close/test_serial_w2_154_nightly.py, tests/unit/close/test_serial_w2_154_plugin.py, tests/unit/close/test_serial_w2_154_support.py, tests/unit/close/test_tool.py, tests/unit/close/test_w2_115_attribution.py, tests/unit/close/test_w2_115_batch.py, tests/unit/close/test_w2_115_close.py, tests/unit/close/test_w2_115_nightly.py, tests/unit/close/test_w2_115_select.py, tests/unit/close/test_w2_115_support.py, tests/unit/close/test_w2_115_verdict.py, tests/unit/close/test_w2_115_verify.py, tests/unit/close/test_w2_183_context_setting.py, tests/unit/closure, tests/unit/codeintel, tests/unit/context, tests/unit/decisions, tests/unit/dispatch, tests/unit/doctor, tests/unit/gitenv, tests/unit/guard/test_decide.py::TestAuditor, tests/unit/guard/test_decide.py::TestNonRoleSubagent ...
- Reds caused by the change: none (the queue advances only then); flaky candidates: tests/unit/dispatch/test_peaks.py, tests/unit/dispatch/test_returns.py, tests/unit/dispatch/test_start.py, tests/unit/dispatch/test_status.py
- Traced against: 13a3d62b9e012aec4744702426dbce407a93d228 (the head without the batch, once each way, the same failure; 3 rounds for the load-sensitive list's cases (Q-1, DEC-1050))
- Red on the head without the batch too, the same failure, not this change's (investigated by the CTO at once, DEC-968): none
- Acceptance tests' authors (G-1, DEC-1050): 5 commit(s) changing tests/acceptance/, each with Role: independent-test-designer or owner
- Core changed (scoped, not full, DEC-968): src/gov/guard/heldout.py, src/gov/guard/reads.py; unplaced: none
- Review: docs/probes/DAEO-qvff/PR-DAEO-qvff-r4c.md, docs/probes/DAEO-qvff/PR-DAEO-qvff-r5.md, docs/probes/DAEO-qvff/PR-DAEO-qvff-r5b.md
- gitleaks: off by configuration (DEC-1045): the change was not scanned
- Queue run: 2026-11-16 02:40:03 to 2026-11-16 03:04:18
- Closed: 2026-11-16 03:05:00 GMT, by the orchestrator under DEC-953 items 1 and 5, DEC-989
