---
id: CL-DAEO-7rr2
type: close
status: ACTIVE
state_class: AUTHORITATIVE
task: DAEO-7rr2
created: '2026-10-20T14:53:19Z'
outputs:
- .tickets/DAEO-7rr2.md
- docs/checkpoints/DAEO-7rr2/CP-DAEO-7rr2-0004.md
- docs/checkpoints/DAEO-7rr2/CP-DAEO-7rr2-0007.md
- docs/checkpoints/DAEO-7rr2/CP-DAEO-7rr2-0008.md
- docs/checkpoints/DAEO-7rr2/CP-DAEO-7rr2-0009.md
- docs/checkpoints/DAEO-7rr2/CP-DAEO-7rr2-0010.md
- docs/checkpoints/DAEO-7rr2/CP-DAEO-7rr2-0011.md
- docs/probes/DAEO-7rr2/PR-DAEO-7rr2.md
- src/gov/close/command.py
- src/gov/close/history.py
- src/gov/close/pytest_plugin/gov_close_results.py
- src/gov/close/ratchet.py
- tests/acceptance/W1-30/README.md
- tests/acceptance/W1-30/test_w1_30_r14_probe_later_commits.py
- tests/acceptance/W2-53/README.md
- tests/acceptance/W2-53/conftest.py
- tests/acceptance/W2-53/test_w2_53_accepted_reds.py
- tests/acceptance/W2-53/test_w2_53_later_merges.py
- tests/acceptance/W2-53/test_w2_53_load_sensitive.py
- tests/acceptance/W2-53/test_w2_53_ratchet_core.py
- tests/acceptance/W2-53/test_w2_53_reopened.py
- tests/acceptance/W2-53/test_w2_53_ticket_file_edits.py
- tests/acceptance/W2-53/w2_53_support.py
- tests/unit/close/test_every_finding.py
- tests/unit/close/test_gates.py
- tests/unit/close/test_measured.py
- tests/unit/close/test_ratchet.py
- docs/close/DAEO-7rr2/CL-DAEO-7rr2.md
- docs/checkpoints/DAEO-7rr2/CP-DAEO-7rr2-0012.md
packet_hash: 8a9c25d03a20caa7a501dd4963da670bd7cc7faab9086f2292799bae550a396f
inputs:
- id: DAEO-7rr2
  hash: sha256:cb7cb47ead3fd36243270ac15f7a04a34eac13b20a5b8c2e5e093e5d8eb895a7
- id: DEC-750
  hash: sha256:8091f3c313073d696538109ae30b66a1b0bd0f2443ae05286228875935a0f3e7
- id: DEC-754
  hash: sha256:8091f3c313073d696538109ae30b66a1b0bd0f2443ae05286228875935a0f3e7
- id: DEC-757
  hash: sha256:8091f3c313073d696538109ae30b66a1b0bd0f2443ae05286228875935a0f3e7
- id: DEC-704
  hash: sha256:8091f3c313073d696538109ae30b66a1b0bd0f2443ae05286228875935a0f3e7
- id: DEC-498
  hash: sha256:8091f3c313073d696538109ae30b66a1b0bd0f2443ae05286228875935a0f3e7
- id: DAEO-g0ip
  hash: sha256:2c22d5a59d1808d3845f8b8acf122da18a2a75971bd062d588936eb621c08d4a
requirements_implemented:
- DEC-704
- DEC-754
- DEC-757
- DEC-768
- DEC-868
decisions_applied:
- DEC-750
- DEC-754
- DEC-757
- DEC-704
- DEC-498
tests_produced:
- tests/acceptance/W1-30/test_w1_30_r14_probe_later_commits.py
- tests/acceptance/W2-53/test_w2_53_accepted_reds.py
- tests/acceptance/W2-53/test_w2_53_later_merges.py
- tests/acceptance/W2-53/test_w2_53_load_sensitive.py
- tests/acceptance/W2-53/test_w2_53_ratchet_core.py
- tests/acceptance/W2-53/test_w2_53_reopened.py
- tests/acceptance/W2-53/test_w2_53_ticket_file_edits.py
- tests/unit/close/test_every_finding.py
- tests/unit/close/test_gates.py
- tests/unit/close/test_measured.py
- tests/unit/close/test_ratchet.py
tests_run:
  passed: 14652
  failed: 2
  errors: 0
  skipped: 31
test_runs:
- run: acceptance
  form: parallel
  seconds: 24.28
  passed: 57
  failed: 0
  errors: 0
  skipped: 0
  workers: auto
- run: regression
  form: parallel
  seconds: 1849.18
  passed: 14332
  failed: 2
  errors: 0
  skipped: 31
  workers: auto
- run: regression
  form: serial-afterwards
  seconds: 1746.13
  passed: 263
  failed: 0
  errors: 0
  skipped: 0
  cases:
  - tests/acceptance/W1-02/test_w1_02_guard_hook.py::test_decision_p95_is_under_100_ms
  - tests/acceptance/W1-05/test_w1_05_live_hooks.py::test_a_call_waits_under_100_ms_p95_for_the_hook
  - tests/acceptance/W1-05/test_w1_05_switch_over_record.py::test_the_dependencies_pass_their_acceptance_tests_at_the_switch_over
  - tests/acceptance/W1-50/test_w1_50_review_of_the_symmetric_rule.py::test_read_merge_answers_for_a_merge_commit_with_very_many_parents_in_time_and_never_calls_the_undone_test_brought
  - tests/acceptance/W1-50/test_w1_50_freeze_live_pause.py::test_a_flag_put_over_the_placeholder_during_a_command_stays
  - tests/acceptance/W1-50/test_w1_50_freeze_launcher.py::test_a_launched_session_leaves_no_placeholder_at_the_flag_s_path
  - tests/acceptance/W1-25/test_w1_25_live_session.py
  - tests/acceptance/W1-46/test_w1_46_live_sessions.py
  - tests/acceptance/W1-49/test_w1_49_live_session.py
  - tests/acceptance/W1-07/test_w1_07_help.py::test_help_answers_in_under_300_ms
  - tests/acceptance/W1-10/test_w1_10_dev_tier.py::test_a_full_load_of_a_dev_tier_takes_less_than_5_seconds
  - tests/acceptance/W1-17/test_w1_17_dev_tier.py::test_one_changed_file_is_re_indexed_by_the_next_retrieval_within_the_bound
  - tests/acceptance/W1-18/test_w1_18_deadline.py::test_a_daemon_that_never_becomes_healthy_is_given_up_at_the_deadline
  - tests/acceptance/W1-18/test_w1_18_deadline.py::test_an_endpoint_that_accepts_and_never_answers_does_not_hang_the_call
  - tests/acceptance/W1-19/test_w1_19_real_models.py
  - tests/acceptance/W1-20/test_w1_20_code.py
  - tests/acceptance/W1-21/test_w1_21_dev_tier.py
  - tests/acceptance/W1-09/test_w1_09_claims.py::test_claims_raced_from_separate_processes_give_exactly_one_holder
  - tests/acceptance/W1-09/test_w1_09_review.py::test_releases_and_claims_raced_from_separate_processes_never_remove_another_holders_claim
  - tests/acceptance/W1-15/test_w1_15_parallel_scan.py::test_the_check_ends_within_the_bound_on_the_stand_in_runtime_folder
  - tests/acceptance/W1-16/test_w1_16_builtin_allowlist_and_daemon_secrets.py
  - tests/acceptance/W1-16/test_w1_16_code_answers.py
  - tests/acceptance/W1-16/test_w1_16_one_daemon.py
  - tests/acceptance/W1-16/test_w1_16_paths_and_roots.py
  - tests/acceptance/W1-16/test_w1_16_secret_exclusion.py
  - tests/acceptance/W1-16/test_w1_16_ui_off.py
  - tests/acceptance/W1-16/test_w1_16_daemon_dir_and_names.py::test_a_body_that_begins_with_a_separator_is_flagged_only_when_the_rest_is_token_shaped
  - tests/acceptance/W1-16/test_w1_16_daemon_dir_and_names.py::test_a_directory_given_by_the_callers_environment_is_not_used
  - tests/acceptance/W1-16/test_w1_16_daemon_dir_and_names.py::test_a_file_with_a_token_whose_body_begins_with_a_separator_is_not_indexable
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
  - tests/acceptance/W1-16/test_w1_16_token_rule.py::test_a_body_with_a_digit_or_with_mixed_case_is_flagged
  - tests/acceptance/W1-16/test_w1_16_token_rule.py::test_a_body_without_a_digit_and_without_mixed_case_is_not_flagged
  - tests/acceptance/W1-16/test_w1_16_token_rule.py::test_a_file_whose_only_match_is_an_ordinary_identifier_is_indexable
  - tests/acceptance/W1-16/test_w1_16_token_rule.py::test_a_file_whose_only_match_is_an_ordinary_identifier_reaches_the_index
  - tests/acceptance/W1-16/test_w1_16_token_rule.py::test_a_file_with_a_token_shaped_string_is_not_indexable
  - tests/acceptance/W1-16/test_w1_16_token_rule.py::test_a_file_with_a_token_shaped_string_stays_out_of_the_index
  - tests/acceptance/W1-16/test_w1_16_token_rule.py::test_a_token_shaped_string_is_still_flagged
  - tests/acceptance/W1-16/test_w1_16_token_rule.py::test_every_file_holding_a_dev_canary_is_still_reported
  - tests/acceptance/W1-16/test_w1_16_token_rule.py::test_no_prefix_and_no_separator_flags_an_ordinary_identifier
  - tests/acceptance/W1-16/test_w1_16_token_rule.py::test_ordinary_identifiers_in_code_are_not_flagged
  - tests/acceptance/W1-16/test_w1_16_token_rule.py::test_the_length_floor_of_sixteen_characters_stays
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
- commit: a678e5b2fa8cc2dfe597a9376d4bb4c53737a2eb
  role: orchestrator
  model: Claude Opus 5.5 <noreply@anthropic.com>
- commit: 5b4b703f98b0246ae80cbb0ccb5dc3adbd158567
  role: orchestrator
  model: Claude Opus 5.5 <noreply@anthropic.com>
- commit: f082bc6899d2ca2ba2d7feed4be21b4f5cebc4c0
  role: orchestrator
  model: Claude Opus 5.5 <noreply@anthropic.com>
- commit: a10a9eb35098d91d4a588a5a8c33b0451b53b181
  role: independent-test-designer
  model: Claude Opus 5.5 <noreply@anthropic.com>
- commit: 49e4aca090f5c25a70c3bdff2ab14dee7e13a22b
  role: independent-test-designer
  model: Claude Opus 5.5 <noreply@anthropic.com>
- commit: 3618f3218fa54ec41702f61287fe3b8b44d16e50
  role: orchestrator
  model: Claude Opus 5.5 <noreply@anthropic.com>
- commit: fb694fe39c7f8339f0f2c4a9f6fdc76b7a88b100
  role: engineer
  model: Claude Opus 5.5 <noreply@anthropic.com>
- commit: 8a304166610b0416b7a22b8b3c32f11b9237d4c6
  role: engineer
  model: Claude Opus 5.5 <noreply@anthropic.com>
- commit: c8d3fb308fd3178206a67ec8a842cdc2ae34089b
  role: orchestrator
  model: Claude Opus 5.5 <noreply@anthropic.com>
- commit: 4f3d34053415a8cd78442722dfad9b82fa18d20b
  role: orchestrator
  model: Claude Opus 5.5 <noreply@anthropic.com>
- commit: c9537e3906190307cc369919f18290930a5e1fad
  role: orchestrator
  model: Claude Opus 5.5 <noreply@anthropic.com>
- commit: 5653a94148173f9e26256f4ae4b8ae9e4b65f037
  role: orchestrator
  model: Claude Opus 5.5 <noreply@anthropic.com>
- commit: e7bf7a3e895eb42a779dbdb5eed99ad94ab1b2cf
  role: orchestrator
  model: Claude Opus 5.5 <noreply@anthropic.com>
- commit: 851b6230603f9e63f60f45c92465c641b33b857f
  role: orchestrator
  model: Claude Opus 5.5 <noreply@anthropic.com>
- commit: 872874e63f8c3b85d224a7c7f53391e7e25b9de6
  role: orchestrator
  model: Claude Opus 5.5 <noreply@anthropic.com>
check_commit: 872874e63f8c3b85d224a7c7f53391e7e25b9de6
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
      commit: 872874e63f8c3b85d224a7c7f53391e7e25b9de6
      check_version: 1.0.0
      inputs_hash: cbcaa999d0e3efb5
  - id: audit-reproducibility
    family: audit reproducibility
    severity: hard-block
    status: GREEN
    findings: []
    provenance:
      commit: 872874e63f8c3b85d224a7c7f53391e7e25b9de6
      check_version: 1.0.0
      inputs_hash: b4670b449dd72f40
  - id: context-reproducibility
    family: context-reproducibility
    severity: hard-block
    status: GREEN
    findings: []
    provenance:
      commit: 872874e63f8c3b85d224a7c7f53391e7e25b9de6
      check_version: 1.0.0
      inputs_hash: 5e1d14e360a29f7b
  - id: core-authority
    family: authority/role limits
    severity: hard-block
    status: GREEN
    findings: []
    provenance:
      commit: 872874e63f8c3b85d224a7c7f53391e7e25b9de6
      check_version: 1.0.0
      inputs_hash: 363eaa9827e1eefc
  - id: core-claims
    family: concurrency/claims
    severity: hard-block
    status: GREEN
    findings: []
    provenance:
      commit: 872874e63f8c3b85d224a7c7f53391e7e25b9de6
      check_version: 1.0.0
      inputs_hash: c00b7e20636031bd
  - id: core-commands
    family: command-contract consistency
    severity: warning
    status: GREEN
    findings: []
    provenance:
      commit: 872874e63f8c3b85d224a7c7f53391e7e25b9de6
      check_version: 1.0.0
      inputs_hash: 3ff01c2afd1aaef8
  - id: core-decision-citations
    family: authority/role limits
    severity: warning
    status: YELLOW
    findings:
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
      commit: 872874e63f8c3b85d224a7c7f53391e7e25b9de6
      check_version: 1.0.0
      inputs_hash: 0a2477afcee820b7
  - id: core-graph
    family: graph integrity
    severity: hard-block
    status: GREEN
    findings: []
    provenance:
      commit: 872874e63f8c3b85d224a7c7f53391e7e25b9de6
      check_version: 1.0.0
      inputs_hash: 5cbf726bc85097b6
  - id: core-mutation
    family: mutation scope
    severity: hard-block
    status: GREEN
    findings: []
    provenance:
      commit: 872874e63f8c3b85d224a7c7f53391e7e25b9de6
      check_version: 1.0.0
      inputs_hash: 363f779ee1b3b4de
  - id: core-pathmap
    family: path-map compliance
    severity: hard-block
    status: GREEN
    findings: []
    provenance:
      commit: 872874e63f8c3b85d224a7c7f53391e7e25b9de6
      check_version: 1.0.0
      inputs_hash: ed191c97582a51e8
  - id: core-schema
    family: schema/invariants
    severity: hard-block
    status: GREEN
    findings: []
    provenance:
      commit: 872874e63f8c3b85d224a7c7f53391e7e25b9de6
      check_version: 1.0.0
      inputs_hash: 2faa9d980cbff2fb
  - id: fresh-agent-reconstruction
    family: fresh-agent-reconstruction
    severity: hard-block
    status: GREEN
    findings: []
    provenance:
      commit: 872874e63f8c3b85d224a7c7f53391e7e25b9de6
      check_version: 1.0.0
      inputs_hash: 5aa2c533138fc840
  - id: index-freshness
    family: index-freshness
    severity: hard-block
    status: GREEN
    findings: []
    provenance:
      commit: 872874e63f8c3b85d224a7c7f53391e7e25b9de6
      check_version: 1.0.0
      inputs_hash: 98cea23325d8cfe3
  - id: product-traceability-trailers
    family: product traceability
    severity: hard-block
    status: GREEN
    findings: []
    provenance:
      commit: 872874e63f8c3b85d224a7c7f53391e7e25b9de6
      check_version: 1.0.0
      inputs_hash: bb843a953028b425
  - id: recovery-rebuild
    family: recovery/rebuild
    severity: hard-block
    status: GREEN
    findings: []
    provenance:
      commit: 872874e63f8c3b85d224a7c7f53391e7e25b9de6
      check_version: 1.0.0
      inputs_hash: b22a8a57a3c8b4a3
  - id: retrieval-regression
    family: retrieval-regression
    severity: hard-block
    status: GREEN
    findings: []
    provenance:
      commit: 872874e63f8c3b85d224a7c7f53391e7e25b9de6
      check_version: 1.0.0
      inputs_hash: 4f3fc822c0ab5b6e
  - id: secrets-indexing
    family: secrets-indexing
    severity: hard-block
    status: GREEN
    findings: []
    provenance:
      commit: 872874e63f8c3b85d224a7c7f53391e7e25b9de6
      check_version: 1.0.0
      inputs_hash: f78790acfe3408d3
  - id: skill-regression-a
    family: skill regression
    severity: hard-block
    status: GREEN
    findings: []
    provenance:
      commit: 872874e63f8c3b85d224a7c7f53391e7e25b9de6
      check_version: 1.0.0
      inputs_hash: 58a8893e89fabd72
  - id: skill-regression-b1
    family: skill regression
    severity: hard-block
    status: GREEN
    findings: []
    provenance:
      commit: 872874e63f8c3b85d224a7c7f53391e7e25b9de6
      check_version: 1.0.0
      inputs_hash: 3c75515a789638a7
  - id: skill-regression-orchestration
    family: skill regression
    severity: hard-block
    status: GREEN
    findings: []
    provenance:
      commit: 872874e63f8c3b85d224a7c7f53391e7e25b9de6
      check_version: 1.0.0
      inputs_hash: e51d5f3a52866c43
  - id: openspec-validate
    family: product traceability
    severity: hard-block
    status: YELLOW
    findings:
    - code: OPENSPEC_ABSENT
      message: openspec is not on PATH
    provenance:
      commit: 872874e63f8c3b85d224a7c7f53391e7e25b9de6
      check_version: 1.0.0
      inputs_hash: e08f23f6b6d7f5d4
  - id: skill-version
    family: skill regression
    severity: hard-block
    status: GREEN
    findings: []
    provenance:
      commit: 872874e63f8c3b85d224a7c7f53391e7e25b9de6
      check_version: 1.0.0
      inputs_hash: c47999d690ccab15
  - id: readiness
    family: product traceability
    severity: hard-block
    status: GREEN
    findings: []
    provenance:
      commit: 872874e63f8c3b85d224a7c7f53391e7e25b9de6
      check_version: 1.0.0
      inputs_hash: 85c81a549f7852a8
accepted_reds:
- test: tests/acceptance/W1-42/test_w1_42_exit_report.py::test_retrieval_query_ran_with_bundles_expansions_notes_and_stopping_reason[RETR-X-02]
  decision: DEC-757
  reason: RETR-X-02 has no named parent expansion yet (DEC-714)
  fixed_by: W2-13
  result: failed
- test: tests/acceptance/W1-42/test_w1_42_exit_report.py::test_governance_share_is_measured_and_at_most_15_percent_on_each_programme
  decision: DEC-757
  reason: The governance share is not measured per programme yet (DEC-713)
  fixed_by: W2-14
  result: failed
load_sensitive: []
governance_share:
  measured: not measured
  estimated: not measured
  total: not measured
---

# CL-DAEO-7rr2 — Close record for DAEO-7rr2
