---
id: CL-DAEO-ebmh
type: close
status: ACTIVE
state_class: AUTHORITATIVE
task: DAEO-ebmh
created: '2026-10-29T14:06:17Z'
outputs:
- .tickets/DAEO-ebmh.md
- docs/checkpoints/DAEO-ebmh/CP-DAEO-ebmh-0002.md
- docs/checkpoints/DAEO-ebmh/CP-DAEO-ebmh-0003.md
- docs/plan/WAVE_2_WBS.md
- tests/acceptance/W2-54/README.md
- tests/acceptance/W2-54/conftest.py
- tests/acceptance/W2-54/test_w2_54_green_here.py
- tests/acceptance/W2-54/w2_54_support.py
- docs/close/DAEO-ebmh/CL-DAEO-ebmh.md
- docs/checkpoints/DAEO-ebmh/CP-DAEO-ebmh-0004.md
packet_hash: 5de4ed3730328407949fa6ba70aeebbc95ec30e4e1c13fd5ae04023361a5dd6c
inputs:
- id: DAEO-ebmh
  hash: sha256:641c150dfbed81cfda41d46041967f60da192788f61eb88aa5ed24cb736931c0
- id: DEC-937
  hash: sha256:83e1d7fa22d7bde5c8912f1212666493a6bd895950c4e429870e4e0aa22aba79
- id: DEC-936
  hash: sha256:83e1d7fa22d7bde5c8912f1212666493a6bd895950c4e429870e4e0aa22aba79
- id: DEC-889
  hash: sha256:83e1d7fa22d7bde5c8912f1212666493a6bd895950c4e429870e4e0aa22aba79
- id: DEC-906
  hash: sha256:83e1d7fa22d7bde5c8912f1212666493a6bd895950c4e429870e4e0aa22aba79
- id: DEC-866
  hash: sha256:83e1d7fa22d7bde5c8912f1212666493a6bd895950c4e429870e4e0aa22aba79
requirements_implemented:
- DEC-868
- DEC-937
decisions_applied:
- DEC-937
- DEC-936
- DEC-889
- DEC-906
- DEC-866
tests_produced:
- tests/acceptance/W2-54/test_w2_54_green_here.py
tests_run:
  passed: 16643
  failed: 0
  errors: 0
  skipped: 32
test_runs:
- run: acceptance
  form: parallel
  seconds: 210.68
  passed: 99
  failed: 0
  errors: 0
  skipped: 0
  workers: auto
  distribution: load
- run: regression
  form: parallel
  seconds: 2544.68
  passed: 16440
  failed: 0
  errors: 0
  skipped: 32
  workers: auto
  distribution: load
- run: regression
  form: serial-afterwards
  seconds: 696.26
  passed: 104
  failed: 0
  errors: 0
  skipped: 0
  cases:
  - tests/acceptance/W1-02/test_w1_02_guard_hook.py::test_decision_p95_is_under_100_ms
  - tests/acceptance/W1-05/test_w1_05_live_hooks.py::test_a_call_waits_under_100_ms_p95_for_the_hook
  - tests/acceptance/W2-57/test_w2_57_designer_read_p95.py
  - tests/acceptance/W1-07/test_w1_07_help.py::test_help_answers_in_under_300_ms
  - tests/acceptance/W1-10/test_w1_10_dev_tier.py::test_a_full_load_of_a_dev_tier_takes_less_than_5_seconds
  - tests/acceptance/W1-17/test_w1_17_dev_tier.py::test_one_changed_file_is_re_indexed_by_the_next_retrieval_within_the_bound
  - tests/acceptance/W1-18/test_w1_18_deadline.py::test_a_daemon_that_never_becomes_healthy_is_given_up_at_the_deadline
  - tests/acceptance/W1-18/test_w1_18_deadline.py::test_an_endpoint_that_accepts_and_never_answers_does_not_hang_the_call
  - tests/acceptance/W1-15/test_w1_15_parallel_scan.py::test_the_check_ends_within_the_bound_on_the_stand_in_runtime_folder
  - tests/acceptance/W1-09/test_w1_09_claims.py::test_claims_raced_from_separate_processes_give_exactly_one_holder
  - tests/acceptance/W1-09/test_w1_09_review.py::test_releases_and_claims_raced_from_separate_processes_never_remove_another_holders_claim
  - tests/acceptance/W1-20/test_w1_20_code.py
  - tests/acceptance/W2-69/test_w2_69_deleted_text_after_rebuild.py::test_the_code_graph_store_holds_no_deleted_word_and_no_free_page_after_a_rebuild
  - tests/acceptance/W2-69/test_w2_69_review_rebuild_root_and_held_store.py::test_a_rebuild_given_the_project_relatively_returns_its_result_and_compacts_every_store
  - tests/acceptance/W1-16/test_w1_16_builtin_allowlist_and_daemon_secrets.py::test_no_planted_secret_stands_in_the_daemon_directory_after_an_index_run
  - tests/acceptance/W1-16/test_w1_16_code_answers.py::test_a_renamed_symbol_is_answered_under_its_new_name_only
  - tests/acceptance/W1-16/test_w1_16_code_answers.py::test_callers_and_impact_are_answered_in_every_language
  - tests/acceptance/W1-16/test_w1_16_code_answers.py::test_callers_and_impact_hit_at_five_is_at_least_sixty_percent
  - tests/acceptance/W1-16/test_w1_16_code_answers.py::test_dead_code_names_the_unreferenced_functions_and_no_live_one
  - tests/acceptance/W1-16/test_w1_16_code_answers.py::test_definitions_name_every_file_that_defines_the_symbol
  - tests/acceptance/W1-16/test_w1_16_code_answers.py::test_references_name_every_file_with_a_call_site
  - tests/acceptance/W1-16/test_w1_16_daemon_dir_and_names.py::test_a_directory_given_by_the_callers_environment_is_not_used
  - tests/acceptance/W1-16/test_w1_16_daemon_dir_and_names.py::test_a_path_name_that_holds_a_secret_is_told_from_an_ordinary_one
  - tests/acceptance/W1-16/test_w1_16_daemon_dir_and_names.py::test_a_run_does_not_use_the_tools_shared_default
  - tests/acceptance/W1-16/test_w1_16_daemon_dir_and_names.py::test_a_socket_path_in_the_daemon_directory_fits_in_a_socket_address
  - tests/acceptance/W1-16/test_w1_16_daemon_dir_and_names.py::test_an_allowlist_of_the_project_does_not_shelter_a_path_name
  - tests/acceptance/W1-16/test_w1_16_daemon_dir_and_names.py::test_each_repository_has_a_daemon_directory_of_its_own
  - tests/acceptance/W1-16/test_w1_16_daemon_dir_and_names.py::test_the_daemon_directory_is_outside_the_repository
  - tests/acceptance/W1-16/test_w1_16_daemon_dir_and_names.py::test_the_tool_alone_keeps_its_daemon_files_in_one_shared_default
  - tests/acceptance/W1-16/test_w1_16_home.py::test_a_repository_answers_only_from_its_own_code
  - tests/acceptance/W1-16/test_w1_16_home.py::test_indexing_again_keeps_one_project
  - tests/acceptance/W1-16/test_w1_16_home.py::test_list_projects_in_one_repository_shows_only_its_own_project
  - tests/acceptance/W1-16/test_w1_16_home.py::test_no_index_file_exists_outside_gov_runtime_after_a_run
  - tests/acceptance/W1-16/test_w1_16_home.py::test_the_home_is_under_the_repositorys_gov_runtime
  - tests/acceptance/W1-16/test_w1_16_home.py::test_the_tools_default_home_is_not_used
  - tests/acceptance/W1-16/test_w1_16_home.py::test_this_repository_is_not_indexed_by_the_run
  - tests/acceptance/W1-16/test_w1_16_home.py::test_two_repositories_have_two_homes
  - tests/acceptance/W1-16/test_w1_16_one_daemon.py
  - tests/acceptance/W1-16/test_w1_16_paths_and_roots.py::test_a_directory_that_is_no_git_repository_is_refused_and_nothing_is_deleted
  - tests/acceptance/W1-16/test_w1_16_paths_and_roots.py::test_a_file_under_a_secret_path_is_not_in_the_code_graph
  - tests/acceptance/W1-16/test_w1_16_paths_and_roots.py::test_a_gov_runtime_that_links_outside_the_repository_is_refused
  - tests/acceptance/W1-16/test_w1_16_paths_and_roots.py::test_a_sub_folder_of_a_repository_is_refused_and_nothing_is_created
  - tests/acceptance/W1-16/test_w1_16_paths_and_roots.py::test_no_secret_of_a_path_name_stands_under_gov_runtime
  - tests/acceptance/W1-16/test_w1_16_paths_and_roots.py::test_the_secrets_indexing_check_of_w1_15_stays_green_with_secret_path_names
  - tests/acceptance/W1-16/test_w1_16_secret_exclusion.py
  - tests/acceptance/W1-16/test_w1_16_token_rule.py::test_a_file_whose_only_match_is_an_ordinary_identifier_reaches_the_index
  - tests/acceptance/W1-16/test_w1_16_token_rule.py::test_a_file_with_a_token_shaped_string_stays_out_of_the_index
  - tests/acceptance/W1-16/test_w1_16_ui_off.py
evidence:
  scope: full
  why_full:
  - reason: SHARED_CORE
    paths:
    - governance/project/path-map.yaml
    - src/gov/close/batch.py
    - src/gov/close/command.py
    - src/gov/close/fingerprint.py
    - src/gov/close/gates.py
    - src/gov/close/repo.py
    - src/gov/close/serial.py
    - src/gov/store/loader.py
  - reason: UNPLACED
    paths:
    - governance/project/briefs/LEAD-w2-common.md
    - governance/project/orchestration/nightly/disk_gate.sh
    - governance/project/orchestration/nightly/nightly.sh
    - governance/project/orchestration/nightly/nightly_alone.py
    - governance/project/orchestration/nightly/nightly_check.sh
    - governance/project/orchestration/nightly/nightly_cron.sh
    - governance/project/orchestration/nightly/nightly_estimate.py
    - governance/project/orchestration/nightly/ping_gate.sh
    - governance/project/orchestration/nightly/rotate.sh
    - governance/project/orchestration/nightly/test_nightly.sh
    - governance/project/prompts/w2-orchestrator.md
  base: 00b371a09163e86f20a086c1e6664073902c4173
  head: 2f2fb03e5076e21ab00a352f86108fafe0bd27e9
  tree: 2f99f86b63abb09aa34132af36612e109eb4dd9b
  changed:
  - .tickets/DAEO-2azm.md
  - .tickets/DAEO-2gc7.md
  - .tickets/DAEO-c1uz.md
  - .tickets/DAEO-e82f.md
  - .tickets/DAEO-e8f0.md
  - .tickets/DAEO-ebmh.md
  - .tickets/DAEO-kh9l.md
  - .tickets/DAEO-pr0y.md
  - .tickets/DAEO-qty6.md
  - .tickets/DAEO-rmbe.md
  - .tickets/DAEO-ye2a.md
  - docs/DECISION_REGISTER.md
  - docs/changes/W2-57-CIT-E.md
  - docs/checkpoints/DAEO-2azm/CP-DAEO-2azm-0003.md
  - docs/checkpoints/DAEO-2azm/CP-DAEO-2azm-0004.md
  - docs/checkpoints/DAEO-2gc7/CP-DAEO-2gc7-0011.md
  - docs/checkpoints/DAEO-5j8b/CP-DAEO-5j8b-0020.md
  - docs/checkpoints/DAEO-c1uz/CP-DAEO-c1uz-0019.md
  - docs/checkpoints/DAEO-cy5o/CP-DAEO-cy5o-0004.md
  - docs/checkpoints/DAEO-cy5o/CP-DAEO-cy5o-0009.md
  - docs/checkpoints/DAEO-cy5o/CP-DAEO-cy5o-0012.md
  - docs/checkpoints/DAEO-e82f/CP-DAEO-e82f-0010.md
  - docs/checkpoints/DAEO-e82f/CP-DAEO-e82f-0011.md
  - docs/checkpoints/DAEO-ebmh/CP-DAEO-ebmh-0002.md
  - docs/checkpoints/DAEO-ebmh/CP-DAEO-ebmh-0003.md
  - docs/checkpoints/DAEO-kh9l/CP-DAEO-kh9l-0018.md
  - docs/checkpoints/DAEO-kh9l/CP-DAEO-kh9l-0019.md
  - docs/checkpoints/DAEO-qty6/CP-DAEO-qty6-0003.md
  - docs/checkpoints/DAEO-qty6/CP-DAEO-qty6-0004.md
  - docs/checkpoints/DAEO-r9ss/CP-DAEO-r9ss-0014.md
  - docs/checkpoints/DAEO-r9ss/CP-DAEO-r9ss-0015.md
  - docs/checkpoints/DAEO-r9ss/CP-DAEO-r9ss-0017.md
  - docs/checkpoints/DAEO-rmbe/CP-DAEO-rmbe-0009.md
  - docs/checkpoints/DAEO-rmbe/CP-DAEO-rmbe-0010.md
  - docs/checkpoints/DAEO-ye2a/CP-DAEO-ye2a-0011.md
  - docs/checkpoints/DAEO-ye2a/CP-DAEO-ye2a-0012.md
  - docs/close/DAEO-2azm/CL-DAEO-2azm.md
  - docs/close/DAEO-c1uz/CL-DAEO-c1uz.md
  - docs/close/DAEO-e82f/CL-DAEO-e82f.md
  - docs/close/DAEO-kh9l/CL-DAEO-kh9l.md
  - docs/close/DAEO-qty6/CL-DAEO-qty6.md
  - docs/close/DAEO-rmbe/CL-DAEO-rmbe.md
  - docs/close/DAEO-ye2a/CL-DAEO-ye2a.md
  - docs/plan/WAVE_2_LIST.md
  - docs/plan/WAVE_2_WBS.md
  - docs/probes/DAEO-2gc7/PR-DAEO-2gc7.md
  - docs/probes/DAEO-cy5o/PR-DAEO-cy5o-reprobe-1.md
  - docs/probes/DAEO-cy5o/PR-DAEO-cy5o-review-2.md
  - docs/probes/DAEO-cy5o/PR-DAEO-cy5o.md
  - docs/research/W2-68-batched-close.md
  - governance/project/briefs/LEAD-w2-common.md
  - governance/project/orchestration/nightly/README.md
  - governance/project/orchestration/nightly/disk_gate.sh
  - governance/project/orchestration/nightly/nightly.sh
  - governance/project/orchestration/nightly/nightly_alone.py
  - governance/project/orchestration/nightly/nightly_check.sh
  - governance/project/orchestration/nightly/nightly_cron.sh
  - governance/project/orchestration/nightly/nightly_estimate.py
  - governance/project/orchestration/nightly/ping_gate.sh
  - governance/project/orchestration/nightly/rotate.sh
  - governance/project/orchestration/nightly/test_nightly.sh
  - governance/project/orchestration/packages/ACT-NIGHTLY-1.md
  - governance/project/orchestration/packages/ACT-REPIN-2.md
  - governance/project/orchestration/packages/ACT-W2-57-LS-1.md
  - governance/project/orchestration/packages/P-REPIN-2.md
  - governance/project/orchestration/packages/P1-MORNING-2026-10-29.md
  - governance/project/path-map.yaml
  - governance/project/prompts/w2-orchestrator.md
  - governance/project/tool-registry.yaml
  - src/gov/adapters/portability.py
  - src/gov/close/batch.py
  - src/gov/close/command.py
  - src/gov/close/fingerprint.py
  - src/gov/close/gates.py
  - src/gov/close/repo.py
  - src/gov/close/serial.py
  - src/gov/doctor/command.py
  - src/gov/store/__init__.py
  - src/gov/store/loader.py
  - tests/acceptance/W1-02/README.md
  - tests/acceptance/W1-02/test_w1_02_multiedit.py
  - tests/acceptance/W1-02/test_w1_02_path_limit_time.py
  - tests/acceptance/W1-02/w1_02_limit_support.py
  - tests/acceptance/W1-02/w1_02_round_support.py
  - tests/acceptance/W1-02/w1_02_support.py
  - tests/acceptance/W1-07/README.md
  - tests/acceptance/W1-07/test_w1_07_envelope.py
  - tests/acceptance/W1-07/w1_07_support.py
  - tests/acceptance/W1-19/test_w1_19_real_models.py
  - tests/acceptance/W1-30/README.md
  - tests/acceptance/W1-30/test_w1_30_r11_declared_here.py
  - tests/acceptance/W1-30/test_w1_30_r13_probe_findings.py
  - tests/acceptance/W1-30/test_w1_30_r15_policy_pairs.py
  - tests/acceptance/W1-33/w1_33_support.py
  - tests/acceptance/W1-38/README.md
  - tests/acceptance/W1-38/conftest.py
  - tests/acceptance/W1-38/test_w1_38_heldout_step.py
  - tests/acceptance/W1-38/test_w1_38_rulesync.py
  - tests/acceptance/W1-38/w1_38_support.py
  - tests/acceptance/W1-46/README.md
  - tests/acceptance/W1-46/test_w1_46_live_sessions.py
  - tests/acceptance/W1-50/test_w1_50_freeze_launcher.py
  - tests/acceptance/W1-50/test_w1_50_freeze_live_pause.py
  - tests/acceptance/W1-50/w1_50_freeze_README.md
  - tests/acceptance/W2-07/README.md
  - tests/acceptance/W2-07/test_w2_07_decision_records.py
  - tests/acceptance/W2-07/w2_07_support.py
  - tests/acceptance/W2-54/README.md
  - tests/acceptance/W2-54/conftest.py
  - tests/acceptance/W2-54/test_w2_54_green_here.py
  - tests/acceptance/W2-54/w2_54_support.py
  - tests/acceptance/W2-57/README.md
  - tests/acceptance/W2-57/conftest.py
  - tests/acceptance/W2-57/test_w2_57_designer_read_p95.py
  - tests/acceptance/W2-57/test_w2_57_doctor_claude_code_unread.py
  - tests/acceptance/W2-57/test_w2_57_doctor_probes.py
  - tests/acceptance/W2-57/test_w2_57_nightly_route.py
  - tests/acceptance/W2-57/test_w2_57_rulesync_probe.py
  - tests/acceptance/W2-57/test_w2_57_serial_list.py
  - tests/acceptance/W2-57/w2_57_list_support.py
  - tests/acceptance/W2-57/w2_57_support.py
  - tests/acceptance/W2-68/README.md
  - tests/acceptance/W2-68/test_w2_68_batch.py
  - tests/acceptance/W2-68/test_w2_68_fingerprints.py
  - tests/acceptance/W2-68/test_w2_68_red_batch.py
  - tests/acceptance/W2-68/test_w2_68_reuse.py
  - tests/acceptance/W2-68/w2_68_support.py
  - tests/acceptance/serial-only.txt
  - tests/unit/adapters/test_portability.py
  - tests/unit/close/test_batch_refresh.py
  - tests/unit/close/test_batch_reuse.py
  - tests/unit/close/test_fingerprint.py
  - tests/unit/close/test_serial.py
  - tests/unit/close/test_w2_07_decision_records.py
  - tests/unit/store/test_fingerprint_store.py
  selected:
  - target: tests/acceptance/W2-54/
    why:
    - reason: OWN
  - target: tests
    why:
    - reason: FULL
  left_out: []
  skips:
  - test: tests/acceptance/W1-01/test_w1_01_history.py::test_interim_rule_stays_in_force_once_introduced[acceptance-tests]
    reason: 'W1-05 is closed: the interim guardrail is retired (DEC-084)'
  - test: tests/acceptance/W1-01/test_w1_01_history.py::test_interim_rule_stays_in_force_once_introduced[installs]
    reason: 'W1-05 is closed: the interim guardrail is retired (DEC-084)'
  - test: tests/acceptance/W1-01/test_w1_01_history.py::test_no_install_is_recorded_before_w1_05
    reason: 'W1-05 is closed: the interim guardrail is retired (DEC-084)'
  - test: tests/acceptance/W1-01/test_w1_01_settings_deny.py::test_implementer_write_to_acceptance_tests_is_denied[Edit]
    reason: 'W1-05 is closed: the interim guardrail is retired (DEC-084)'
  - test: tests/acceptance/W1-01/test_w1_01_settings_deny.py::test_implementer_write_to_acceptance_tests_is_denied[Write]
    reason: 'W1-05 is closed: the interim guardrail is retired (DEC-084)'
  - test: tests/acceptance/W1-01/test_w1_01_settings_deny.py::test_acceptance_test_deny_covers_every_depth[Edit]
    reason: 'W1-05 is closed: the interim guardrail is retired (DEC-084)'
  - test: tests/acceptance/W1-01/test_w1_01_settings_deny.py::test_acceptance_test_deny_covers_every_depth[Write]
    reason: 'W1-05 is closed: the interim guardrail is retired (DEC-084)'
  - test: tests/acceptance/W1-01/test_w1_01_settings_deny.py::test_install_command_is_denied[pip]
    reason: 'W1-05 is closed: the interim guardrail is retired (DEC-084)'
  - test: tests/acceptance/W1-01/test_w1_01_settings_deny.py::test_install_command_is_denied[pip3]
    reason: 'W1-05 is closed: the interim guardrail is retired (DEC-084)'
  - test: tests/acceptance/W1-01/test_w1_01_settings_deny.py::test_install_command_is_denied[python-m-pip]
    reason: 'W1-05 is closed: the interim guardrail is retired (DEC-084)'
  - test: tests/acceptance/W1-01/test_w1_01_settings_deny.py::test_install_command_is_denied[python3-m-pip]
    reason: 'W1-05 is closed: the interim guardrail is retired (DEC-084)'
  - test: tests/acceptance/W1-01/test_w1_01_settings_deny.py::test_install_command_is_denied[uv-pip]
    reason: 'W1-05 is closed: the interim guardrail is retired (DEC-084)'
  - test: tests/acceptance/W1-01/test_w1_01_settings_deny.py::test_install_command_is_denied[uv-tool]
    reason: 'W1-05 is closed: the interim guardrail is retired (DEC-084)'
  - test: tests/acceptance/W1-01/test_w1_01_settings_deny.py::test_install_command_is_denied[npm-bare]
    reason: 'W1-05 is closed: the interim guardrail is retired (DEC-084)'
  - test: tests/acceptance/W1-01/test_w1_01_settings_deny.py::test_install_command_is_denied[npm]
    reason: 'W1-05 is closed: the interim guardrail is retired (DEC-084)'
  - test: tests/acceptance/W1-01/test_w1_01_settings_deny.py::test_install_command_is_denied[npm-global]
    reason: 'W1-05 is closed: the interim guardrail is retired (DEC-084)'
  - test: tests/acceptance/W1-01/test_w1_01_settings_deny.py::test_install_command_is_denied[cargo]
    reason: 'W1-05 is closed: the interim guardrail is retired (DEC-084)'
  - test: tests/acceptance/W1-01/test_w1_01_settings_deny.py::test_install_command_is_denied[apt]
    reason: 'W1-05 is closed: the interim guardrail is retired (DEC-084)'
  - test: tests/acceptance/W1-01/test_w1_01_settings_deny.py::test_install_command_is_denied[apt-get]
    reason: 'W1-05 is closed: the interim guardrail is retired (DEC-084)'
  - test: tests/acceptance/W1-01/test_w1_01_settings_deny.py::test_install_command_is_denied[compound]
    reason: 'W1-05 is closed: the interim guardrail is retired (DEC-084)'
  - test: tests/acceptance/W1-01/test_w1_01_settings_deny.py::test_pipe_to_shell_and_sudo_are_denied[curl-pipe-sh]
    reason: 'W1-05 is closed: the interim guardrail is retired (DEC-084)'
  - test: tests/acceptance/W1-01/test_w1_01_settings_deny.py::test_pipe_to_shell_and_sudo_are_denied[curl-pipe-bash]
    reason: 'W1-05 is closed: the interim guardrail is retired (DEC-084)'
  - test: tests/acceptance/W1-01/test_w1_01_settings_deny.py::test_pipe_to_shell_and_sudo_are_denied[wget-pipe-sh]
    reason: 'W1-05 is closed: the interim guardrail is retired (DEC-084)'
  - test: tests/acceptance/W1-01/test_w1_01_settings_deny.py::test_pipe_to_shell_and_sudo_are_denied[wget-pipe-bash]
    reason: 'W1-05 is closed: the interim guardrail is retired (DEC-084)'
  - test: tests/acceptance/W1-01/test_w1_01_settings_deny.py::test_pipe_to_shell_and_sudo_are_denied[sudo-package-manager]
    reason: 'W1-05 is closed: the interim guardrail is retired (DEC-084)'
  - test: tests/acceptance/W1-01/test_w1_01_settings_deny.py::test_pipe_to_shell_and_sudo_are_denied[sudo-make-install]
    reason: 'W1-05 is closed: the interim guardrail is retired (DEC-084)'
  - test: tests/acceptance/W1-01/test_w1_01_settings_deny.py::test_pipe_to_shell_and_sudo_are_denied[curl-pipe-sudo-sh]
    reason: 'W1-05 is closed: the interim guardrail is retired (DEC-084)'
  - test: tests/acceptance/W1-01/test_w1_01_settings_deny.py::test_guardrails_leave_ordinary_implementer_work_alone
    reason: 'W1-05 is closed: the interim guardrail is retired (DEC-084)'
  - test: tests/acceptance/W1-26/test_w1_26_command.py::test_exit_0_when_all_checks_green
    reason: the full project does not pass gov check yet
  - test: tests/acceptance/W1-03/test_w1_03_probe_findings.py::test_a_check_that_cannot_run_is_reported_and_recorded_with_the_call_s_own_fields[the-gov-package-is-missing]
    reason: this interpreter finds a `gov` package without PYTHONPATH
  - test: tests/acceptance/W2-66/test_w2_66_live_test_map.py::test_the_path_map_s_test_inputs_are_in_the_test_map
    reason: the path map no longer holds test_inputs (the orchestrator's edit is done)
  - test: tests/unit/retrieval/test_lexical.py::test_the_chunking_is_the_carried_one
    reason: 'could not import ''govbridge.core.chunking'': No module named ''govbridge.core.chunking'''
  skip_count: 32
  failures: []
  junit_xml:
  - .gov-runtime/close/DAEO-ebmh/20261029T130208796709Z/01-acceptance-parallel.xml
  - .gov-runtime/close/DAEO-ebmh/20261029T130208796709Z/02-regression-parallel.xml
  - .gov-runtime/close/DAEO-ebmh/20261029T130208796709Z/03-regression-serial-afterwards.xml
  per_test_timeout: 900
  distribution: load
  tmp_path_retention_policy: failed
deviations: not measured
skill_versions:
- name: adopt
  version: 1.0.0
- name: audit
  version: 1.1.0
- name: change
  version: 1.0.0
- name: checkpoint
  version: 1.1.0
- name: discovery
  version: 1.0.0
- name: orchestration
  version: 1.0.0
- name: planning
  version: 1.0.0
- name: retrieval
  version: 1.0.0
- name: test-design
  version: 1.0.0
- name: systematic-debugging
  version: no version
- name: test-driven-development
  version: no version
- name: verification-before-completion
  version: no version
commits:
- commit: f13701be088f5e6f5a00e128b94c02541d987c65
  role: orchestrator
  model: Claude Opus 5.5 <noreply@anthropic.com>
- commit: 3eef001d08dd757c7a9d8a8f0a81d6303185a563
  role: orchestrator
  model: Claude Opus 5.5 <noreply@anthropic.com>
- commit: 12957c13186d3be9d7f312b63f4296ba4f7575bc
  role: independent-test-designer
  model: Claude Opus 5.5 <noreply@anthropic.com>
- commit: e7f90cd32bbddd094a34143899ad3385cd341407
  role: orchestrator
  model: Claude Opus 5.5 <noreply@anthropic.com>
- commit: b52e3a9615c16bca878ed3a11a460558ec84b93b
  role: orchestrator
  model: Claude Opus 5.5 <noreply@anthropic.com>
- commit: 2f2fb03e5076e21ab00a352f86108fafe0bd27e9
  role: orchestrator
  model: Claude Opus 5.5 <noreply@anthropic.com>
check_commit: 2f2fb03e5076e21ab00a352f86108fafe0bd27e9
governance_checks:
  families:
    schema/invariants:
      status: GREEN
      family: schema/invariants
      check_count: 1
    graph integrity:
      status: GREEN
      family: graph integrity
      check_count: 1
    index freshness:
      status: GREEN
      family: index freshness
      check_count: 1
    retrieval regression:
      status: GREEN
      family: retrieval regression
      check_count: 1
    authority/role limits:
      status: YELLOW
      family: authority/role limits
      check_count: 2
    mutation scope:
      status: GREEN
      family: mutation scope
      check_count: 1
    path-map compliance:
      status: GREEN
      family: path-map compliance
      check_count: 1
    context reproducibility:
      status: GREEN
      family: context reproducibility
      check_count: 1
    concurrency/claims:
      status: GREEN
      family: concurrency/claims
      check_count: 1
    adapter/model portability:
      status: GREEN
      family: adapter/model portability
      check_count: 1
    skill regression:
      status: GREEN
      family: skill regression
      check_count: 4
    command-contract consistency:
      status: GREEN
      family: command-contract consistency
      check_count: 1
    secrets indexing:
      status: GREEN
      family: secrets indexing
      check_count: 1
    recovery/rebuild:
      status: GREEN
      family: recovery/rebuild
      check_count: 1
    fresh-agent reconstruction:
      status: GREEN
      family: fresh-agent reconstruction
      check_count: 1
    product traceability:
      status: YELLOW
      family: product traceability
      check_count: 3
    audit reproducibility:
      status: GREEN
      family: audit reproducibility
      check_count: 1
  checks:
  - id: adapter-portability
    family: adapter/model portability
    severity: hard-block
    status: GREEN
    findings: []
    provenance:
      commit: 2f2fb03e5076e21ab00a352f86108fafe0bd27e9
      check_version: 1.0.0
      inputs_hash: fbf7d6ef99447dd0
  - id: audit-reproducibility
    family: audit reproducibility
    severity: hard-block
    status: GREEN
    findings: []
    provenance:
      commit: 2f2fb03e5076e21ab00a352f86108fafe0bd27e9
      check_version: 1.0.0
      inputs_hash: 334a9f58f1e74648
  - id: context-reproducibility
    family: context-reproducibility
    severity: hard-block
    status: GREEN
    findings: []
    provenance:
      commit: 2f2fb03e5076e21ab00a352f86108fafe0bd27e9
      check_version: 1.0.0
      inputs_hash: dc078a4194549323
  - id: core-authority
    family: authority/role limits
    severity: hard-block
    status: GREEN
    findings: []
    provenance:
      commit: 2f2fb03e5076e21ab00a352f86108fafe0bd27e9
      check_version: 1.0.0
      inputs_hash: fae1077522d4e8a9
  - id: core-claims
    family: concurrency/claims
    severity: hard-block
    status: GREEN
    findings: []
    provenance:
      commit: 2f2fb03e5076e21ab00a352f86108fafe0bd27e9
      check_version: 1.0.0
      inputs_hash: 251e8bc309da2153
  - id: core-commands
    family: command-contract consistency
    severity: warning
    status: GREEN
    findings: []
    provenance:
      commit: 2f2fb03e5076e21ab00a352f86108fafe0bd27e9
      check_version: 1.0.0
      inputs_hash: 38f570eed7324cf9
  - id: core-decision-citations
    family: authority/role limits
    severity: warning
    status: YELLOW
    findings:
    - code: DECISION_UNRECORDED
      commit: f13701be088f5e6f5a00e128b94c02541d987c65
      decision: DEC-937
      message: commit f13701be088f cites DEC-937, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: 6a4696eb461c1da2649fb1443551e58fd395ed01
      decision: DEC-921
      message: commit 6a4696eb461c cites DEC-921, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: e48a601dd6a4ad32e21cd42672c67b5d6ca6bbd4
      decision: DEC-877
      message: commit e48a601dd6a4 cites DEC-877, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: 666f56d1c2ff7bd1e653c3f792c2d3454048525a
      decision: DEC-872
      message: commit 666f56d1c2ff cites DEC-872, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: d4096ddeb3751a95895bba381749edd60ced49c9
      decision: DEC-863
      message: commit d4096ddeb375 cites DEC-863, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: 7c2930f7284202e50684b83d1c1cf28f6716f9aa
      decision: DEC-837
      message: commit 7c2930f72842 cites DEC-837, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: ead078ed5e44091eca022f8c4d8a2a601fcf0759
      decision: DEC-837
      message: commit ead078ed5e44 cites DEC-837, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: 198738e027c7361a3e00aa06c303bf6d5e83941b
      decision: DEC-861
      message: commit 198738e027c7 cites DEC-861, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: 3501362f857d373662a6fb4c58f69e1083f8249a
      decision: DEC-859
      message: commit 3501362f857d cites DEC-859, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: 3501362f857d373662a6fb4c58f69e1083f8249a
      decision: DEC-860
      message: commit 3501362f857d cites DEC-860, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: 7d8e49d84aff7f448f6f9fc09630f78f44fb3aa9
      decision: DEC-837
      message: commit 7d8e49d84aff cites DEC-837, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: 87cad875cd1f8f5ca1ffec709cf1519c0e039b8b
      decision: DEC-837
      message: commit 87cad875cd1f cites DEC-837, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: 0243701f6d5af29914f19fc0f27c32405d48de59
      decision: DEC-856
      message: commit 0243701f6d5a cites DEC-856, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: 0243701f6d5af29914f19fc0f27c32405d48de59
      decision: DEC-858
      message: commit 0243701f6d5a cites DEC-858, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: 926066e50b144e398dba6e4dc26da1d55b054902
      decision: DEC-853
      message: commit 926066e50b14 cites DEC-853, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: 926066e50b144e398dba6e4dc26da1d55b054902
      decision: DEC-855
      message: commit 926066e50b14 cites DEC-855, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: c5100159b368ec9a5c8f9dc7496e189c3e850228
      decision: DEC-854
      message: commit c5100159b368 cites DEC-854, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: ce03cb6da7d59123e8c46bc971a19236789be941
      decision: DEC-837
      message: commit ce03cb6da7d5 cites DEC-837, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: a57985219b9a781113a3c43e7bd07eddfe12d31c
      decision: DEC-831
      message: commit a57985219b9a cites DEC-831, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: a57985219b9a781113a3c43e7bd07eddfe12d31c
      decision: DEC-852
      message: commit a57985219b9a cites DEC-852, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: 226ec4583d5c3a047dc09c45d245174dfdec9008
      decision: DEC-801
      message: commit 226ec4583d5c cites DEC-801, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: 7661402c041b048d637977ef4c3be5f11a729aa3
      decision: DEC-811
      message: commit 7661402c041b cites DEC-811, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: a0cb797e6314bda62c38f25141931ac319e2a58f
      decision: DEC-773
      message: commit a0cb797e6314 cites DEC-773, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: a0cb797e6314bda62c38f25141931ac319e2a58f
      decision: DEC-811
      message: commit a0cb797e6314 cites DEC-811, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: 7504971410e99d08bfccdc8cd20ae1ee3af59684
      decision: DEC-773
      message: commit 7504971410e9 cites DEC-773, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: 7504971410e99d08bfccdc8cd20ae1ee3af59684
      decision: DEC-802
      message: commit 7504971410e9 cites DEC-802, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: 7504971410e99d08bfccdc8cd20ae1ee3af59684
      decision: DEC-811
      message: commit 7504971410e9 cites DEC-811, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: 4662871af23b3dcbbf7b8c89fc6adb454db6202c
      decision: DEC-773
      message: commit 4662871af23b cites DEC-773, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: 4662871af23b3dcbbf7b8c89fc6adb454db6202c
      decision: DEC-811
      message: commit 4662871af23b cites DEC-811, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: c53022d78ec6019d2883bc39f0b362ad087813d1
      decision: DEC-773
      message: commit c53022d78ec6 cites DEC-773, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: c53022d78ec6019d2883bc39f0b362ad087813d1
      decision: DEC-798
      message: commit c53022d78ec6 cites DEC-798, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: a4801649a41ba51f76c32bbf5dc409fbd3c97b67
      decision: DEC-773
      message: commit a4801649a41b cites DEC-773, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: a4801649a41ba51f76c32bbf5dc409fbd3c97b67
      decision: DEC-798
      message: commit a4801649a41b cites DEC-798, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: a93d5f7202b31fa37a6daaf564a54428f73a5c9a
      decision: DEC-773
      message: commit a93d5f7202b3 cites DEC-773, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: a93d5f7202b31fa37a6daaf564a54428f73a5c9a
      decision: DEC-798
      message: commit a93d5f7202b3 cites DEC-798, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: cd363a8ee88869023c164913909d03f0b6733be1
      decision: DEC-773
      message: commit cd363a8ee888 cites DEC-773, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: cd363a8ee88869023c164913909d03f0b6733be1
      decision: DEC-798
      message: commit cd363a8ee888 cites DEC-798, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: 986353ccca580074f899587b6d8f91dd559e3cb9
      decision: DEC-773
      message: commit 986353ccca58 cites DEC-773, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: 986353ccca580074f899587b6d8f91dd559e3cb9
      decision: DEC-798
      message: commit 986353ccca58 cites DEC-798, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: 0914d8f8fda603b1d6cf8449a23a855ef7144a21
      decision: DEC-773
      message: commit 0914d8f8fda6 cites DEC-773, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: 0121e48580652c85c31c3e7c5e1c53474d59376e
      decision: DEC-786
      message: commit 0121e4858065 cites DEC-786, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: 08c63a7ae8f2e2ca35a668e8d171b88e1a9d3502
      decision: DEC-782
      message: commit 08c63a7ae8f2 cites DEC-782, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: b33ef9b394a03bdf46fb232f52f94a4562054ed7
      decision: DEC-782
      message: commit b33ef9b394a0 cites DEC-782, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: 77bf7cc78402c63b4bfa028bc22fd7c1812b579c
      decision: DEC-782
      message: commit 77bf7cc78402 cites DEC-782, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: 5f038b47a111c7a72ca07c79a0a870ddbf99eb04
      decision: DEC-773
      message: commit 5f038b47a111 cites DEC-773, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: 5f038b47a111c7a72ca07c79a0a870ddbf99eb04
      decision: DEC-784
      message: commit 5f038b47a111 cites DEC-784, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: b23e1b64c4f88b0925bf26f9d3db105c62638ba6
      decision: DEC-773
      message: commit b23e1b64c4f8 cites DEC-773, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: b23e1b64c4f88b0925bf26f9d3db105c62638ba6
      decision: DEC-782
      message: commit b23e1b64c4f8 cites DEC-782, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: 1f45dc10b02f067e828c6c9128ee4f07b45bfd3e
      decision: DEC-773
      message: commit 1f45dc10b02f cites DEC-773, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: 0affa1623e1fc04f5a34c7aecb5f14b2a81ab08d
      decision: DEC-779
      message: commit 0affa1623e1f cites DEC-779, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: 3bee9a50851a215fe6083095c0a9692574ec22c6
      decision: DEC-773
      message: commit 3bee9a50851a cites DEC-773, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: fc9e6a2ad67df3e9536e5236e957bc95930c3def
      decision: DEC-774
      message: commit fc9e6a2ad67d cites DEC-774, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: fc9e6a2ad67df3e9536e5236e957bc95930c3def
      decision: DEC-778
      message: commit fc9e6a2ad67d cites DEC-778, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: fc9e6a2ad67df3e9536e5236e957bc95930c3def
      decision: DEC-779
      message: commit fc9e6a2ad67d cites DEC-779, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: 6f9bc03a77c76e696829790635f934c10460efdb
      decision: DEC-774
      message: commit 6f9bc03a77c7 cites DEC-774, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: 6f9bc03a77c76e696829790635f934c10460efdb
      decision: DEC-778
      message: commit 6f9bc03a77c7 cites DEC-778, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: 1c80aa9731de889673e1dc6e15bab9b7d6c1b40c
      decision: DEC-774
      message: commit 1c80aa9731de cites DEC-774, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: 1c80aa9731de889673e1dc6e15bab9b7d6c1b40c
      decision: DEC-778
      message: commit 1c80aa9731de cites DEC-778, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: e8255c8a29f914ccb583a4a2e56f93227cd0750c
      decision: DEC-773
      message: commit e8255c8a29f9 cites DEC-773, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: 397a80de1470d5d7b99489527f37500ac272dd88
      decision: DEC-778
      message: commit 397a80de1470 cites DEC-778, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: 2956f9e7386f288b3cf02c2033593af4aef886f5
      decision: DEC-774
      message: commit 2956f9e7386f cites DEC-774, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: 2d60cdd3b8773ac6803d004afb16b10e85652a92
      decision: DEC-764
      message: commit 2d60cdd3b877 cites DEC-764, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: 2d60cdd3b8773ac6803d004afb16b10e85652a92
      decision: DEC-765
      message: commit 2d60cdd3b877 cites DEC-765, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: 3787cc795d7f5822ca291d20bab6e81f00e54b56
      decision: DEC-764
      message: commit 3787cc795d7f cites DEC-764, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: 3787cc795d7f5822ca291d20bab6e81f00e54b56
      decision: DEC-765
      message: commit 3787cc795d7f cites DEC-765, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: 83756def50742181e8ecee389d51ffdcc5891534
      decision: DEC-764
      message: commit 83756def5074 cites DEC-764, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: 83756def50742181e8ecee389d51ffdcc5891534
      decision: DEC-765
      message: commit 83756def5074 cites DEC-765, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: 41aa00c09dd3cdaf135ee8e17cc23ba8ce545464
      decision: DEC-764
      message: commit 41aa00c09dd3 cites DEC-764, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: 41aa00c09dd3cdaf135ee8e17cc23ba8ce545464
      decision: DEC-765
      message: commit 41aa00c09dd3 cites DEC-765, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: 8a310cb2d5111ca7c64386b75e9970c2555b189f
      decision: DEC-758
      message: commit 8a310cb2d511 cites DEC-758, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: d5334c0fe5f1e0a35c6f136af555b9d606291b69
      decision: DEC-758
      message: commit d5334c0fe5f1 cites DEC-758, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: 83b0f2f493789ef0e2b1c134cc47c7fa83822f08
      decision: DEC-758
      message: commit 83b0f2f49378 cites DEC-758, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: ef7c18354c8a5eabbb20cd5e85af5fc387b9c063
      decision: DEC-758
      message: commit ef7c18354c8a cites DEC-758, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: 8a304166610b0416b7a22b8b3c32f11b9237d4c6
      decision: DEC-757
      message: commit 8a304166610b cites DEC-757, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: b247d77009cd2521ededec513eda991a28aee30b
      decision: DEC-762
      message: commit b247d77009cd cites DEC-762, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: fb694fe39c7f8339f0f2c4a9f6fdc76b7a88b100
      decision: DEC-757
      message: commit fb694fe39c7f cites DEC-757, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: 49e4aca090f5c25a70c3bdff2ab14dee7e13a22b
      decision: DEC-757
      message: commit 49e4aca090f5 cites DEC-757, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: a10a9eb35098d91d4a588a5a8c33b0451b53b181
      decision: DEC-757
      message: commit a10a9eb35098 cites DEC-757, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: f082bc6899d2ca2ba2d7feed4be21b4f5cebc4c0
      decision: DEC-757
      message: commit f082bc6899d2 cites DEC-757, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: f15ac648c087df99673bc979690dae8b4b282bcc
      decision: DEC-757
      message: commit f15ac648c087 cites DEC-757, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: 14657729e991d333a4c5f66504d60c2ae4913e6a
      decision: DEC-757
      message: commit 14657729e991 cites DEC-757, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: fa3554e8c98e3f539d77fa3ed9c4d491ed332938
      decision: DEC-757
      message: commit fa3554e8c98e cites DEC-757, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: 5b4b703f98b0246ae80cbb0ccb5dc3adbd158567
      decision: DEC-757
      message: commit 5b4b703f98b0 cites DEC-757, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: 19a4e9fd20b9562c24b1824076c67403fb323db5
      decision: DEC-752
      message: commit 19a4e9fd20b9 cites DEC-752, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: d5abd7867fc8e286aef512de1b1939901ce7a4ce
      decision: DEC-752
      message: commit d5abd7867fc8 cites DEC-752, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: 6d5ad6d0e2977359c08fdc38775d0ea76c26a02f
      decision: DEC-751
      message: commit 6d5ad6d0e297 cites DEC-751, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: 645ecbdf4891faa3949b8e94d9982c621a367a07
      decision: DEC-755
      message: commit 645ecbdf4891 cites DEC-755, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: 3022c2df7b794c170ebae4c723db351ed9b7e5df
      decision: DEC-750
      message: commit 3022c2df7b79 cites DEC-750, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: 3022c2df7b794c170ebae4c723db351ed9b7e5df
      decision: DEC-754
      message: commit 3022c2df7b79 cites DEC-754, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: 184cd3ef47c67d0a04a95d7e9987065732e9a3b8
      decision: DEC-754
      message: commit 184cd3ef47c6 cites DEC-754, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: 8a3c27e9396d43f30ea99d39bbb5d3e5f55eb560
      decision: DEC-751
      message: commit 8a3c27e9396d cites DEC-751, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: df5f1e5001936fd1be3eeaaaf4a15550c30b5a2a
      decision: DEC-751
      message: commit df5f1e500193 cites DEC-751, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: a2bc5e35d22f15a125c86728e1015ac485fdd91b
      decision: DEC-754
      message: commit a2bc5e35d22f cites DEC-754, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: fbc6da0afce2fd9a05b524828f4ed7ea3c6eeca7
      decision: DEC-754
      message: commit fbc6da0afce2 cites DEC-754, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: 15943bd0b02f23966a9f5122b8e9c9a04d9fcc09
      decision: DEC-754
      message: commit 15943bd0b02f cites DEC-754, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: cb49fe973f309f722d1583eb1a7e70b92771314c
      decision: DEC-754
      message: commit cb49fe973f30 cites DEC-754, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: 2cf78313a094877e5c6f398dbe85f4f5445cc146
      decision: DEC-754
      message: commit 2cf78313a094 cites DEC-754, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: f7159e399bea9d69f4f5bae8c96f5e251c5bd3e3
      decision: DEC-754
      message: commit f7159e399bea cites DEC-754, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: ee30c9de09b9fe3944eab40ddec270d72c22e903
      decision: DEC-750
      message: commit ee30c9de09b9 cites DEC-750, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: ee30c9de09b9fe3944eab40ddec270d72c22e903
      decision: DEC-754
      message: commit ee30c9de09b9 cites DEC-754, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: a678e5b2fa8cc2dfe597a9376d4bb4c53737a2eb
      decision: DEC-750
      message: commit a678e5b2fa8c cites DEC-750, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: a678e5b2fa8cc2dfe597a9376d4bb4c53737a2eb
      decision: DEC-754
      message: commit a678e5b2fa8c cites DEC-754, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: e5d1c52862fd6e28d8e8b88d685de45f2c54549b
      decision: DEC-750
      message: commit e5d1c52862fd cites DEC-750, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: f3d4b6f0dc3d6509b36ea8213e49b244c3737663
      decision: DEC-752
      message: commit f3d4b6f0dc3d cites DEC-752, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: f3d4b6f0dc3d6509b36ea8213e49b244c3737663
      decision: DEC-753
      message: commit f3d4b6f0dc3d cites DEC-753, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: 131e2e2d87ada60327b8ad5bad1a7d4c69add9f8
      decision: DEC-752
      message: commit 131e2e2d87ad cites DEC-752, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: 3df9d3963a514551a30d02b56600ff08c1aebe70
      decision: DEC-751
      message: commit 3df9d3963a51 cites DEC-751, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: e58081beb1b14160fb246d6c793eab50fb809864
      decision: DEC-751
      message: commit e58081beb1b1 cites DEC-751, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: b283af775cf9eb6c6ca1011a4c997969d95a65b9
      decision: DEC-750
      message: commit b283af775cf9 cites DEC-750, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: c00c003f73f2691ec91bf14d769e6a083102ff6f
      decision: DEC-750
      message: commit c00c003f73f2 cites DEC-750, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: 40dbe546584714200c846e4fa996103230974a8d
      decision: DEC-750
      message: commit 40dbe5465847 cites DEC-750, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: 728b657ca3d6b518cfa4a4046639542f3e3233fb
      decision: DEC-749
      message: commit 728b657ca3d6 cites DEC-749, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: c7827891fc317c8a8f9a6f0ae8ac92decccf9a75
      decision: DEC-746
      message: commit c7827891fc31 cites DEC-746, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: 993a3f7e5d16e78acb5eb56afe39d0f1c33eb1ac
      decision: DEC-739
      message: commit 993a3f7e5d16 cites DEC-739, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: 887c288c5bad71cd1c402f2c8eec23e5302e3eaf
      decision: DEC-743
      message: commit 887c288c5bad cites DEC-743, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: a5ef3c690695fed2f9e57c2c803714fd6c79fa9f
      decision: DEC-743
      message: commit a5ef3c690695 cites DEC-743, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: 5bc27b7ce0228314dae18293b784524ca00934a6
      decision: DEC-747
      message: commit 5bc27b7ce022 cites DEC-747, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: 17ed8106976d44b2dc25c6d35387ee0450336075
      decision: DEC-746
      message: commit 17ed8106976d cites DEC-746, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: a814cd3b8d7cdcb5dd5b9fa97e31dfc849cc4598
      decision: DEC-739
      message: commit a814cd3b8d7c cites DEC-739, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: 27af72938bef9207e014e7652b721b0330674c80
      decision: DEC-745
      message: commit 27af72938bef cites DEC-745, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: d977009909a18e8f0642a55c0790b4009d23c100
      decision: DEC-745
      message: commit d977009909a1 cites DEC-745, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: 61ca9c1aa62bb4ad7a6e5bfb180e622187658fec
      decision: DEC-737
      message: commit 61ca9c1aa62b cites DEC-737, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: 61ca9c1aa62bb4ad7a6e5bfb180e622187658fec
      decision: DEC-744
      message: commit 61ca9c1aa62b cites DEC-744, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: 92f04d6457d810272510598285d00ddd83794bea
      decision: DEC-739
      message: commit 92f04d6457d8 cites DEC-739, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: bfb5647381fd818be93a8ffcb034e64523437ef2
      decision: DEC-743
      message: commit bfb5647381fd cites DEC-743, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: 00fe09b6fc5cde672103c5ea4788e5d70dd6eef1
      decision: DEC-742
      message: commit 00fe09b6fc5c cites DEC-742, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: ed88d81147ee0b46dbae2ef21edf257903872699
      decision: DEC-741
      message: commit ed88d81147ee cites DEC-741, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: 1586b5ccb2697eb78b03b72f7e37cc714494a18f
      decision: DEC-743
      message: commit 1586b5ccb269 cites DEC-743, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: 630d1fd2b22a1f0c9f31bc42e3c23708fc10ea1e
      decision: DEC-743
      message: commit 630d1fd2b22a cites DEC-743, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: 34680ffe88ebb9007d425ca854f8c3674452bc53
      decision: DEC-738
      message: commit 34680ffe88eb cites DEC-738, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: d7c5f5f2a609b0b5d76a43b4a47d3caa719ebb21
      decision: DEC-741
      message: commit d7c5f5f2a609 cites DEC-741, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: 1d5449eb647807e0a20b7862f82bb19194de447a
      decision: DEC-741
      message: commit 1d5449eb6478 cites DEC-741, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: 1d5449eb647807e0a20b7862f82bb19194de447a
      decision: DEC-744
      message: commit 1d5449eb6478 cites DEC-744, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: 2077cb57ea024351ac6ed5c9dd32417ea5dca2a1
      decision: DEC-743
      message: commit 2077cb57ea02 cites DEC-743, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: d09e8c1b46ae0a3c72fbda549aa6cd6ad218c2de
      decision: DEC-738
      message: commit d09e8c1b46ae cites DEC-738, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: d09e8c1b46ae0a3c72fbda549aa6cd6ad218c2de
      decision: DEC-739
      message: commit d09e8c1b46ae cites DEC-739, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: 7de0e524b07c6ced2215b8c26dfec1a27cd609c4
      decision: DEC-741
      message: commit 7de0e524b07c cites DEC-741, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: 048e19bbdc42453be0f02d9890792f7dc17c95fc
      decision: DEC-744
      message: commit 048e19bbdc42 cites DEC-744, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: a02e3485b85e01ab8e77417e6a00334b2b8ae6bf
      decision: DEC-737
      message: commit a02e3485b85e cites DEC-737, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: 689bd17e1a41e3ec59d3c85ea45cb6250f999907
      decision: DEC-737
      message: commit 689bd17e1a41 cites DEC-737, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: 0e817fe14302035b9e3aee66030f427847a638d6
      decision: DEC-737
      message: commit 0e817fe14302 cites DEC-737, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: eefea284aa6a5ff14aad05cd24a9555a9a80c88b
      decision: DEC-737
      message: commit eefea284aa6a cites DEC-737, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: 6e7e17f519f4e61fa1c922d0f2924fcf64277805
      decision: DEC-736
      message: commit 6e7e17f519f4 cites DEC-736, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: abd86ef5679f43f29d8ef70480c77a86d9ae2c7a
      decision: DEC-736
      message: commit abd86ef5679f cites DEC-736, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: be0e7a8f5d848a5b5cc6de599f9bfe753f2664a5
      decision: DEC-736
      message: commit be0e7a8f5d84 cites DEC-736, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: 7ebe54892c9dd13d5be4485dd476e7eaf99ef23b
      decision: DEC-734
      message: commit 7ebe54892c9d cites DEC-734, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: 7217bfa992556290b37be7eabed5c67ebe8caed9
      decision: DEC-710
      message: commit 7217bfa99255 cites DEC-710, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: 5eb3b0129d8a094651eb03b48435e6bf19700e8a
      decision: ADR-012
      message: commit 5eb3b0129d8a cites ADR-012, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: c579c932f73033ca42c381f4c4468ae77ce1cd88
      decision: DEC-675
      message: commit c579c932f730 cites DEC-675, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: 6ce6e8eb29568087978ff030c246bd2029250002
      decision: DEC-675
      message: commit 6ce6e8eb2956 cites DEC-675, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: abcb3095d267d88c93d19115e9c06ba0fd9fad6f
      decision: DEC-594
      message: commit abcb3095d267 cites DEC-594, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: a1c03c5b76cfdb31f7c5076fcc71a758cc8d4083
      decision: DEC-480
      message: commit a1c03c5b76cf cites DEC-480, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: be2e8c142ec2cc2b0eccaa6a8335b799ed493895
      decision: DEC-480
      message: commit be2e8c142ec2 cites DEC-480, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: 5505ba57e163427559c47fddc9a8f0e441df1fa7
      decision: DEC-476
      message: commit 5505ba57e163 cites DEC-476, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: 5505ba57e163427559c47fddc9a8f0e441df1fa7
      decision: DEC-480
      message: commit 5505ba57e163 cites DEC-480, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: 4b84321d595f0772fc72ce463b2c252acafc6490
      decision: DEC-480
      message: commit 4b84321d595f cites DEC-480, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: fd7ad4f0561aeb8f8d85a32b87926d947f5e77b6
      decision: DEC-476
      message: commit fd7ad4f0561a cites DEC-476, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: 569bdcd3a728ec597d04d9968112b801d21725ca
      decision: DEC-471
      message: commit 569bdcd3a728 cites DEC-471, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: 7439c6d004853cdaa434a7c1e56a478008c2de0b
      decision: DEC-470
      message: commit 7439c6d00485 cites DEC-470, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: 495cff52caba357724ab5e6933dd49442d57a0ed
      decision: DEC-470
      message: commit 495cff52caba cites DEC-470, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: d2c2d6ff1a1e4c3c052dd63505f61f74a6475da5
      decision: DEC-468
      message: commit d2c2d6ff1a1e cites DEC-468, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: e0b438501e856ee65078fe4c8eaa9af1bd7ed8ce
      decision: DEC-468
      message: commit e0b438501e85 cites DEC-468, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: af6fe34ec733fd676f37e194754e21373ad92ebd
      decision: DEC-453
      message: commit af6fe34ec733 cites DEC-453, which its tree does not record
    - code: DECISION_UNRECORDED
      commit: af6fe34ec733fd676f37e194754e21373ad92ebd
      decision: DEC-454
      message: commit af6fe34ec733 cites DEC-454, which its tree does not record
    provenance:
      commit: 2f2fb03e5076e21ab00a352f86108fafe0bd27e9
      check_version: 1.0.0
      inputs_hash: df323178c284465d
  - id: core-graph
    family: graph integrity
    severity: hard-block
    status: GREEN
    findings: []
    provenance:
      commit: 2f2fb03e5076e21ab00a352f86108fafe0bd27e9
      check_version: 1.0.0
      inputs_hash: 1c67056cfb9e0071
  - id: core-mutation
    family: mutation scope
    severity: hard-block
    status: GREEN
    findings: []
    provenance:
      commit: 2f2fb03e5076e21ab00a352f86108fafe0bd27e9
      check_version: 1.0.0
      inputs_hash: 5828b366c691169d
  - id: core-pathmap
    family: path-map compliance
    severity: hard-block
    status: GREEN
    findings: []
    provenance:
      commit: 2f2fb03e5076e21ab00a352f86108fafe0bd27e9
      check_version: 1.0.0
      inputs_hash: dccd211911f03c2d
  - id: core-schema
    family: schema/invariants
    severity: hard-block
    status: GREEN
    findings: []
    provenance:
      commit: 2f2fb03e5076e21ab00a352f86108fafe0bd27e9
      check_version: 1.0.0
      inputs_hash: 55a12d6d001979e1
  - id: fresh-agent-reconstruction
    family: fresh-agent-reconstruction
    severity: hard-block
    status: GREEN
    findings: []
    provenance:
      commit: 2f2fb03e5076e21ab00a352f86108fafe0bd27e9
      check_version: 1.0.0
      inputs_hash: 504ce80c00503f72
  - id: index-freshness
    family: index-freshness
    severity: hard-block
    status: GREEN
    findings: []
    provenance:
      commit: 2f2fb03e5076e21ab00a352f86108fafe0bd27e9
      check_version: 1.0.0
      inputs_hash: 5921bc22ce77c269
  - id: product-traceability-trailers
    family: product traceability
    severity: hard-block
    status: GREEN
    findings: []
    provenance:
      commit: 2f2fb03e5076e21ab00a352f86108fafe0bd27e9
      check_version: 1.0.0
      inputs_hash: 2d15226e1fd12595
  - id: recovery-rebuild
    family: recovery/rebuild
    severity: hard-block
    status: GREEN
    findings: []
    provenance:
      commit: 2f2fb03e5076e21ab00a352f86108fafe0bd27e9
      check_version: 1.0.0
      inputs_hash: 6cbd10118008f1cd
  - id: retrieval-regression
    family: retrieval-regression
    severity: hard-block
    status: GREEN
    findings: []
    provenance:
      commit: 2f2fb03e5076e21ab00a352f86108fafe0bd27e9
      check_version: 1.0.0
      inputs_hash: 8ebbdbb60248b716
  - id: secrets-indexing
    family: secrets-indexing
    severity: hard-block
    status: GREEN
    findings: []
    provenance:
      commit: 2f2fb03e5076e21ab00a352f86108fafe0bd27e9
      check_version: 1.0.0
      inputs_hash: d9137330720f1832
  - id: skill-regression-a
    family: skill regression
    severity: hard-block
    status: GREEN
    findings: []
    provenance:
      commit: 2f2fb03e5076e21ab00a352f86108fafe0bd27e9
      check_version: 1.0.0
      inputs_hash: 76bd4b0402b09401
  - id: skill-regression-b1
    family: skill regression
    severity: hard-block
    status: GREEN
    findings: []
    provenance:
      commit: 2f2fb03e5076e21ab00a352f86108fafe0bd27e9
      check_version: 1.0.0
      inputs_hash: 591c20e952ef60de
  - id: skill-regression-orchestration
    family: skill regression
    severity: hard-block
    status: GREEN
    findings: []
    provenance:
      commit: 2f2fb03e5076e21ab00a352f86108fafe0bd27e9
      check_version: 1.0.0
      inputs_hash: 918fe48dc4ffe455
  - id: openspec-validate
    family: product traceability
    severity: hard-block
    status: YELLOW
    findings:
    - code: OPENSPEC_ABSENT
      message: openspec is not on PATH
    provenance:
      commit: 2f2fb03e5076e21ab00a352f86108fafe0bd27e9
      check_version: 1.0.0
      inputs_hash: 959424ddf247e5c3
  - id: skill-version
    family: skill regression
    severity: hard-block
    status: GREEN
    findings: []
    provenance:
      commit: 2f2fb03e5076e21ab00a352f86108fafe0bd27e9
      check_version: 1.0.0
      inputs_hash: 76b528644e3e2d5a
  - id: readiness
    family: product traceability
    severity: hard-block
    status: GREEN
    findings: []
    provenance:
      commit: 2f2fb03e5076e21ab00a352f86108fafe0bd27e9
      check_version: 1.0.0
      inputs_hash: 679c1edf1cbfeecf
accepted_reds: []
load_sensitive: []
ticket_class: test-revision
disk:
  free_gib: 881.26
  free_inodes: 65387647
  close_free_gib_floor: 100
  close_free_inodes_floor: 10000000
governance_share:
  measured: not measured
  estimated: not measured
  total: not measured
---

# CL-DAEO-ebmh — Close record for DAEO-ebmh
