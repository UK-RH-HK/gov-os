# W2-94 (DAEO-g87r) closed: merged and closed in one step by the merge queue (DEC-989)

- Commit tested (the lead's final, verified result): 4480c451c955; merge 36423324c84f; w2/integrate a8e1eb27bd1b -> 36423324c84f (fast-forward to the tested merge); profile STANDARD
- Queue record: /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/merge-queue/records/36423324c84f.json; log /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/merge-queue/log/20261114-184110-154659
- Batch: W2-94
- Run: scoped, 149 targets; counts {'tests': 7260, 'failures': 3, 'errors': 4, 'skipped': 45}
- Selected: tests/acceptance/W2-94/, tests/unit/accept, tests/unit/adapters, tests/unit/adopt, tests/unit/bridge, tests/unit/brief, tests/unit/check, tests/unit/checkpoint, tests/unit/ci, tests/unit/cli, tests/unit/close/test_evidence.py, tests/unit/close/test_nightly.py, tests/unit/close/test_nightly_cleanup.py, tests/unit/close/test_parallel_runs.py, tests/unit/close/test_run_and_record.py, tests/unit/close/test_select.py, tests/unit/close/test_serial.py, tests/unit/close/test_serial_eng_w2_154.py, tests/unit/close/test_serial_w2_154_nightly.py, tests/unit/close/test_serial_w2_154_plugin.py, tests/unit/close/test_serial_w2_154_support.py, tests/unit/close/test_tool.py, tests/unit/close/test_w2_115_attribution.py, tests/unit/close/test_w2_115_batch.py, tests/unit/close/test_w2_115_close.py, tests/unit/close/test_w2_115_nightly.py, tests/unit/close/test_w2_115_select.py, tests/unit/close/test_w2_115_support.py, tests/unit/close/test_w2_115_verdict.py, tests/unit/close/test_w2_115_verify.py, tests/unit/close/test_w2_183_context_setting.py, tests/unit/closure, tests/unit/codeintel, tests/unit/context, tests/unit/decisions, tests/unit/dispatch, tests/unit/doctor, tests/unit/gitenv, tests/unit/guard/test_decide.py::TestAuditor, tests/unit/guard/test_decide.py::TestNonRoleSubagent ...
- Reds caused by the change: none (the queue advances only then); flaky candidates: tests/unit/dispatch/test_peaks.py, tests/unit/dispatch/test_returns.py, tests/unit/dispatch/test_start.py, tests/unit/dispatch/test_status.py, tests/acceptance/W2-94/test_w2_94_fix_flow.py::test_s9_on_delivery_the_counts_carry_the_fix_and_no_content[corrected-extra0], tests/acceptance/W2-94/test_w2_94_fix_flow.py::test_s9_a_result_of_a_wrong_form_is_20_nothing_delivered_and_the_action_null[by_kind absent], tests/unit/retrieval/test_w2_112_shared_reranker.py::test_the_running_service_writes_one_memory_line_per_request
- Traced against: a8e1eb27bd1ba1c471a5c8588802d09b94fbb4aa (the head without the batch, once each way, the same failure; 3 rounds for the load-sensitive list's cases (Q-1, DEC-1050))
- Red on the head without the batch too, the same failure, not this change's (investigated by the CTO at once, DEC-968): none
- Acceptance tests' authors (G-1, DEC-1050): 1 commit(s) changing tests/acceptance/, each with Role: independent-test-designer or owner
- Core changed (scoped, not full, DEC-968): none; unplaced: none
- Review: not required (STANDARD)
- gitleaks: off by configuration (DEC-1045): the change was not scanned
- Queue run: 2026-11-14 18:41:10 to 2026-11-14 19:00:20
- Closed: 2026-11-14 19:01:17 GMT, by the orchestrator under DEC-953 items 1 and 5, DEC-989

## Final close (DEC-1184 (6)): kept open after the land, closed on the owner's operator's result

- Merged into w2/integrate by the merge queue: the one-question fix flow (16:18, 0b43625da) and S13's counts-schema `fix` key (36423324c, fdf397527), kept open at 61793c613 for the q02 run
- Reviews: `docs/probes/DAEO-g87r/PR-DAEO-g87r-fix.md` (P1-P8 rows, pass), `PR-DAEO-g87r-s13b.md` and the path case's narrow check (4480c451c, pass at 900035fdd51c, no findings)
- q02's writer variant version 2 (sha256 7aa6d88c, DEC-1182 (5)) installed at aa1fa659f (on w2/integrate, not yet pushed)
- The owner's operator's run (2026-11-14): step 2's approved line, as the CTO's command gave it, lacked the kind `writer` (the cause was the CTO's command, DEC-1184 (6)); the operator corrected it to `brief writer <path>`, set the mode back to 400 and relaunched: run `20261114T222836Z-examin-r2` delivered, fix q02 `corrected`, `check_gold` 20 of 20 hold
- No launched session read the hidden half; counts only reached the CTO (DEC-820 (d))
- Closed: 2026-11-14, by the orchestrator under DEC-953 items 1 and 5, DEC-1132 (1), DEC-1182 (5), DEC-1184 (6)
