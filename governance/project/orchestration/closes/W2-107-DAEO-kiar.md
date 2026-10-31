# W2-107 (DAEO-kiar) closed: build-phase close (DEC-953)

- Merges: fab23f52931c,73736f4b8440; tested on w2/integrate head fab23f52931c; profile FULL
- Its own selection: scoped
- Run: scoped (42 targets)
- Selected: tests/acceptance/W2-107/, tests/unit, tests/acceptance/W1-30/, tests/acceptance/W1-15/, tests/acceptance/W1-41/, tests/acceptance/W2-71/, tests/acceptance/W2-50/, tests/acceptance/W1-16/, tests/acceptance/W2-69/, tests/acceptance/W2-76/, tests/acceptance/W1-27/, tests/acceptance/W1-26/, tests/acceptance/W1-40/, tests/acceptance/W1-28/test_w1_28_fixture_copies.py, tests/acceptance/W1-07/test_w1_07_envelope.py, tests/acceptance/W1-07/test_w1_07_read_act.py, tests/acceptance/W1-07/test_w1_07_registry.py, tests/acceptance/W1-06/test_w1_06_approvals.py, tests/acceptance/W1-08/test_w1_08_path_map.py, tests/acceptance/W1-27/test_w1_27_path_compliance.py, tests/acceptance/W1-27/test_w1_27_path_compliance_r2.py, tests/acceptance/W2-54/test_w2_54_green_here.py, tests/acceptance/W1-33/test_w1_33_agent_definitions.py, tests/acceptance/W1-49/test_w1_49_threshold.py, tests/acceptance/W1-01/test_w1_01_history.py::test_implementer_commits_stay_inside_allowed_paths, tests/acceptance/W1-48/, tests/acceptance/W1-26/test_w1_26_probe_records.py, tests/acceptance/W1-42/, tests/acceptance/W1-30/test_w1_30_r11_declared_here.py, tests/acceptance/W1-10/test_w1_10_register.py::test_every_heading_of_this_repositorys_register_is_one_record_and_none_fails, tests/acceptance/W1-10/test_w1_10_completeness.py::test_every_committed_ticket_and_adr_of_this_repository_is_in_the_graph, tests/acceptance/W2-02/test_w2_02_green_here.py, tests/acceptance/W1-08/test_w1_08_ticket.py, tests/acceptance/W1-08/test_w1_08_probe.py, tests/acceptance/W1-06/test_w1_06_install_approvals.py, tests/acceptance/W1-07/test_w1_07_config.py, tests/acceptance/W1-07/test_w1_07_config_details.py, tests/acceptance/W1-27/test_w1_27_doctor.py, tests/acceptance/W1-27/test_w1_27_doctor_r5.py, tests/acceptance/W1-27/test_w1_27_doctor_r6.py ...
- Parallel: {'exit': 1, 's': 2456, 'tests': 6615, 'failures': 2, 'errors': 0, 'skipped': 2}
- Serial: {'exit': 0, 's': 565, 'entries': 37, 'tests': 71, 'failures': 0, 'errors': 0, 'skipped': 0}
- Reds caused by the change: none; flaky candidates: tests/acceptance/W2-50/test_w2_50_secrets_scan_scale.py::test_a_large_store_among_many_small_files_is_decided_by_gov_check
- Red without the change too, not this change's, investigated by the CTO at once (DEC-968): tests/acceptance/W1-28/test_w1_28_fixture_copies.py::test_every_whole_tree_copy_is_made_by_a_fixture_the_check_runs
- Core changed (scoped, not full, DEC-968): none; unplaced: none
- Review: ['docs/probes/DAEO-kiar/PR-DAEO-kiar-rev3.md', 'docs/probes/DAEO-kiar/PR-DAEO-kiar.md']
- gitleaks on the merge's change: clean
- Times: rebuild 717 s, tests 3021 s, wall 4914 s
- Closed: 2026-10-31 21:49:38 GMT, by the orchestrator under DEC-953 items 1 and 5
