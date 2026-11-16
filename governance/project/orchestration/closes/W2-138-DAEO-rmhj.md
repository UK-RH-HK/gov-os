# W2-138 (DAEO-rmhj) closed: build-phase close (DEC-953)

- Merges: 02ccb9543c96; tested on w2/integrate head 7dcd9a408f60; profile STANDARD
- Its own selection: scoped
- Run: scoped (255 targets)
- Selected: tests/acceptance/W2-138/, tests/unit/accept, tests/unit/adapters, tests/unit/adopt, tests/unit/bridge, tests/unit/brief, tests/unit/check, tests/unit/checkpoint, tests/unit/ci, tests/unit/cli, tests/unit/close/test_evidence.py, tests/unit/close/test_nightly.py, tests/unit/close/test_nightly_cleanup.py, tests/unit/close/test_parallel_runs.py, tests/unit/close/test_run_and_record.py, tests/unit/close/test_select.py, tests/unit/close/test_serial.py, tests/unit/close/test_serial_eng_w2_154.py, tests/unit/close/test_serial_w2_154_nightly.py, tests/unit/close/test_serial_w2_154_plugin.py, tests/unit/close/test_serial_w2_154_support.py, tests/unit/close/test_tool.py, tests/unit/close/test_w2_115_attribution.py, tests/unit/close/test_w2_115_batch.py, tests/unit/close/test_w2_115_close.py, tests/unit/close/test_w2_115_nightly.py, tests/unit/close/test_w2_115_select.py, tests/unit/close/test_w2_115_support.py, tests/unit/close/test_w2_115_verdict.py, tests/unit/close/test_w2_115_verify.py, tests/unit/close/test_w2_183_context_setting.py, tests/unit/closure, tests/unit/codeintel, tests/unit/context, tests/unit/decisions, tests/unit/dispatch, tests/unit/doctor, tests/unit/gitenv, tests/unit/guard/test_decide.py::TestAuditor, tests/unit/guard/test_decide.py::TestNonRoleSubagent ...
- Parallel: {'exit': 1, 's': 1058, 'tests': 8967, 'failures': 1, 'errors': 0, 'skipped': 13}
- Serial: {'exit': 0, 's': 35, 'entries': 3, 'tests': 3, 'failures': 0, 'errors': 0, 'skipped': 0}
- Reds caused by the change: none; flaky candidates: tests/unit/orchestration/test_w2_149_indep_launch.py::test_f1_the_reported_and_the_drawn_id_count_each_entry_once
- Red without the change too, not this change's, investigated by the CTO at once (DEC-968): none
- Core changed (scoped, not full, DEC-968): src/gov/cli/main.py, src/gov/retrieval/retrieve.py; unplaced: none
- Review: not required (STANDARD)
- gitleaks: off by configuration (DEC-1045): the merge's change was not scanned
- Times: rebuild 265 s, tests 1093 s, wall 1365 s
- Closed: 2026-11-16 06:45:18 GMT, by the orchestrator under DEC-953 items 1 and 5
