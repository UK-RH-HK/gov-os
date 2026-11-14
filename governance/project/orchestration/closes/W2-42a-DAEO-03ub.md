# W2-42a (DAEO-03ub) closed: merged and closed in one step by the merge queue (DEC-989)

- Commit tested (the lead's final, verified result): cd17d270668f; merge 6a30444e9c92; w2/integrate 235fc1cc6858 -> 6a30444e9c92 (fast-forward to the tested merge); profile FULL
- Queue record: /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/merge-queue/records/6a30444e9c92.json; log /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/merge-queue/log/20261113-235705-395476
- Batch: W2-42a
- Run: scoped, 291 targets; counts {'tests': 7654, 'failures': 0, 'errors': 4, 'skipped': 10}
- Selected: tests/acceptance/W2-42a/, tests/unit/accept, tests/unit/adapters, tests/unit/adopt, tests/unit/bridge, tests/unit/brief, tests/unit/check, tests/unit/checkpoint, tests/unit/ci, tests/unit/cli, tests/unit/close/test_evidence.py, tests/unit/close/test_nightly.py, tests/unit/close/test_nightly_cleanup.py, tests/unit/close/test_parallel_runs.py, tests/unit/close/test_run_and_record.py, tests/unit/close/test_select.py, tests/unit/close/test_serial.py, tests/unit/close/test_serial_eng_w2_154.py, tests/unit/close/test_serial_w2_154_nightly.py, tests/unit/close/test_serial_w2_154_plugin.py, tests/unit/close/test_serial_w2_154_support.py, tests/unit/close/test_tool.py, tests/unit/close/test_w2_115_attribution.py, tests/unit/close/test_w2_115_batch.py, tests/unit/close/test_w2_115_close.py, tests/unit/close/test_w2_115_nightly.py, tests/unit/close/test_w2_115_select.py, tests/unit/close/test_w2_115_support.py, tests/unit/close/test_w2_115_verdict.py, tests/unit/close/test_w2_115_verify.py, tests/unit/close/test_w2_183_context_setting.py, tests/unit/closure, tests/unit/codeintel, tests/unit/context, tests/unit/decisions, tests/unit/dispatch, tests/unit/doctor, tests/unit/gitenv, tests/unit/guard/test_decide.py::TestAuditor, tests/unit/guard/test_decide.py::TestNonRoleSubagent ...
- Reds caused by the change: none (the queue advances only then); flaky candidates: tests/unit/dispatch/test_peaks.py, tests/unit/dispatch/test_returns.py, tests/unit/dispatch/test_start.py, tests/unit/dispatch/test_status.py
- Traced against: 235fc1cc68581dfa30206a051fe0fc89a6c7f618 (the head without the batch, once each way, the same failure; 3 rounds for the load-sensitive list's cases (Q-1, DEC-1050))
- Red on the head without the batch too, the same failure, not this change's (investigated by the CTO at once, DEC-968): none
- Acceptance tests' authors (G-1, DEC-1050): 2 commit(s) changing tests/acceptance/, each with Role: independent-test-designer or owner
- Core changed (scoped, not full, DEC-968): src/gov/guard/bash_writes.py, src/gov/guard/decide.py; unplaced: none
- Review: docs/probes/DAEO-03ub/PR-DAEO-03ub-apos-2.md, docs/probes/DAEO-03ub/PR-DAEO-03ub.md
- gitleaks: off by configuration (DEC-1045): the change was not scanned
- Queue run: 2026-11-13 23:57:05 to 2026-11-14 00:13:03
- Closed: 2026-11-14 00:14:02 GMT, by the orchestrator under DEC-953 items 1 and 5, DEC-989
