# W2-66c (DAEO-btcs) closed: merged and closed in one step by the merge queue (DEC-989)

- Commit tested (the lead's final, verified result): 400991361362; merge e452af6b1717; w2/integrate 31c8c31eb2a2 -> e452af6b1717 (fast-forward to the tested merge); profile LITE
- Queue record: /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/merge-queue/records/e452af6b1717.json; log /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/merge-queue/log/20261111-215803-001286
- Batch: W2-05, W2-66c
- Run: scoped, 122 targets; counts {'tests': 4033, 'failures': 0, 'errors': 0, 'skipped': 8}
- Selected: tests/acceptance/W2-05/, tests/unit/accept, tests/unit/adapters, tests/unit/adopt, tests/unit/bridge, tests/unit/brief, tests/unit/check, tests/unit/checkpoint, tests/unit/ci, tests/unit/cli, tests/unit/close/test_evidence.py, tests/unit/close/test_nightly.py, tests/unit/close/test_nightly_cleanup.py, tests/unit/close/test_parallel_runs.py, tests/unit/close/test_run_and_record.py, tests/unit/close/test_select.py, tests/unit/close/test_serial.py, tests/unit/close/test_tool.py, tests/unit/closure, tests/unit/codeintel, tests/unit/context, tests/unit/decisions, tests/unit/doctor, tests/unit/gitenv, tests/unit/guard/test_decide.py::TestAuditor, tests/unit/guard/test_decide.py::TestNonRoleSubagent, tests/unit/guard/test_decide.py::TestDenyOutputFormat, tests/unit/guard/test_decide.py::TestUnparseableBash, tests/unit/guard/test_decide.py::TestHookProcess, tests/unit/guard/test_decide.py::TestRoleSubagentNoSessionRole, tests/unit/guard/test_decide.py::TestRoleSubagentGoverns, tests/unit/guard/test_decide.py::TestExpandToken, tests/unit/guard/test_decide.py::TestFreezeState, tests/unit/guard/test_decide.py::TestUnmarkedFlagRecord, tests/unit/guard/test_heldout.py, tests/unit/guard/test_heldout_limit.py, tests/unit/guard/test_hook_deadline.py, tests/unit/guard/test_reads.py::test_each_route_is_decided_as_policy_2_says, tests/unit/guard/test_reads.py::test_the_search_refusal_names_the_folder_and_how_to_exclude_it, tests/unit/guard/test_reads.py::test_a_subagent_is_refused_its_session_s_and_its_type_s_parts ...
- Reds caused by the change: none (the queue advances only then); flaky candidates: none
- Traced against: 31c8c31eb2a2ae17890ca1bb3e07d2520c04ddce (the head without the batch, once each way, the same failure; 3 rounds for the load-sensitive list's cases (Q-1, DEC-1050))
- Red on the head without the batch too, the same failure, not this change's (investigated by the CTO at once, DEC-968): none
- Acceptance tests' authors (G-1, DEC-1050): 1 commit(s) changing tests/acceptance/, each with Role: independent-test-designer or owner
- Core changed (scoped, not full, DEC-968): none; unplaced: none
- Review: not required (LITE)
- gitleaks: off by configuration (DEC-1045): the change was not scanned
- Queue run: 2026-11-11 21:58:02 to 2026-11-11 22:10:58
- Closed: 2026-11-11 22:11:31 GMT, by the orchestrator under DEC-953 items 1 and 5, DEC-989
