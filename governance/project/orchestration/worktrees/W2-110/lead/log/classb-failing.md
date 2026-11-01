104 cases

- tests/acceptance/W1-46/test_w1_46_research_installs.py::test_the_same_commands_stay_denied_for_the_other_worker_roles[config-file-add-engineer]
    AssertionError: `uv --config-file uv.toml add requests` by engineer in exp-901 was not denied by a rule: decision=deny exit=2 stdout='' stderr=''
- tests/acceptance/W1-46/test_w1_46_install_spellings.py::test_uv_run_w_with_its_value_joined_stays_denied_for_the_other_worker_roles[engineer]
    AssertionError: `uv run -wrequests script.py` by engineer was not denied by a rule: decision=deny exit=2 stdout='' stderr=''
- tests/acceptance/W1-46/test_w1_46_research_installs.py::test_the_same_commands_stay_denied_for_the_other_worker_roles[uv-run-with-independent-auditor]
    AssertionError: `uv run --with requests python script.py` by independent-auditor in exp-901 was not denied by a rule: decision=deny exit=2 stdout='' stderr=''
- tests/acceptance/W1-46/test_w1_46_research_installs.py::test_another_role_on_the_research_ticket_gets_no_install_through[independent-test-designer]
    AssertionError: `uv add requests` by independent-test-designer on the research ticket was not denied by a rule: decision=deny exit=2 stdout='' stderr=''
- tests/acceptance/W1-46/test_w1_46_research_installs.py::test_the_same_commands_stay_denied_for_the_other_worker_roles[uvx-engineer]
    AssertionError: `uvx ruff check .` by engineer in exp-901 was not denied by a rule: decision=deny exit=2 stdout='' stderr=''
- tests/acceptance/W1-46/test_w1_46_runtime_and_ln.py::test_scratch_stays_writable_for_every_role[independent-auditor]
    AssertionError: `echo x > .gov-runtime/scratch/w1-46/new.txt` by independent-auditor was not allowed: decision=deny exit=2 stdout='' stderr=''
- tests/acceptance/W1-46/test_w1_46_research_installs.py::test_the_same_commands_stay_denied_for_the_other_worker_roles[run-w-independent-test-designer]
    AssertionError: `uv run -w requests script.py` by independent-test-designer in exp-901 was not denied by a rule: decision=deny exit=2 stdout='' stderr=''
- tests/acceptance/W1-46/test_w1_46_research_installs.py::test_the_same_commands_stay_denied_for_the_other_worker_roles[uv-add-independent-auditor]
    AssertionError: `uv add requests` by independent-auditor in exp-901 was not denied by a rule: decision=deny exit=2 stdout='' stderr=''
- tests/acceptance/W1-46/test_w1_46_install_spellings.py::test_uv_run_w_with_its_value_joined_is_let_through_for_research_in_its_folder
    AssertionError: `uv run -wrequests script.py` by research in its experiment folder was not allowed: decision=deny exit=2 stdout='' stderr=''
- tests/acceptance/W1-46/test_w1_46_research_installs.py::test_the_same_commands_stay_denied_for_the_other_worker_roles[config-file-add-independent-test-designer]
    AssertionError: `uv --config-file uv.toml add requests` by independent-test-designer in exp-901 was not denied by a rule: decision=deny exit=2 stdout='' stderr=''
- tests/acceptance/W1-46/test_w1_46_research_installs.py::test_the_same_commands_stay_denied_for_the_other_worker_roles[uv-sync-engineer]
    AssertionError: `uv sync` by engineer in exp-901 was not denied by a rule: decision=deny exit=2 stdout='' stderr=''
- tests/acceptance/W1-46/test_w1_46_install_spellings.py::test_uv_run_w_with_its_value_joined_stays_denied_for_the_other_worker_roles[independent-test-designer]
    AssertionError: `uv run -wrequests script.py` by independent-test-designer was not denied by a rule: decision=deny exit=2 stdout='' stderr=''
- tests/acceptance/W1-46/test_w1_46_research_installs.py::test_another_role_on_the_research_ticket_gets_no_install_through[independent-auditor]
    AssertionError: `uv add requests` by independent-auditor on the research ticket was not denied by a rule: decision=deny exit=2 stdout='' stderr=''
- tests/acceptance/W1-46/test_w1_46_research_installs.py::test_the_same_commands_stay_denied_for_the_other_worker_roles[uvx-independent-test-designer]
    AssertionError: `uvx ruff check .` by independent-test-designer in exp-901 was not denied by a rule: decision=deny exit=2 stdout='' stderr=''
- tests/acceptance/W1-46/test_w1_46_runtime_and_ln.py::test_scratch_stays_writable_for_every_role[independent-test-designer]
    AssertionError: `echo x > .gov-runtime/scratch/w1-46/new.txt` by independent-test-designer was not allowed: decision=deny exit=2 stdout='' stderr=''
- tests/acceptance/W1-46/test_w1_46_research_installs.py::test_the_same_commands_stay_denied_for_the_other_worker_roles[run-w-independent-auditor]
    AssertionError: `uv run -w requests script.py` by independent-auditor in exp-901 was not denied by a rule: decision=deny exit=2 stdout='' stderr=''
- tests/acceptance/W1-46/test_w1_46_research_installs.py::test_the_same_commands_stay_denied_for_the_other_worker_roles[cache-dir-sync-engineer]
    AssertionError: `uv --cache-dir .uv-cache sync` by engineer in exp-901 was not denied by a rule: decision=deny exit=2 stdout='' stderr=''
- tests/acceptance/W1-46/test_w1_46_research_installs.py::test_the_same_commands_stay_denied_for_the_other_worker_roles[config-file-add-independent-auditor]
    AssertionError: `uv --config-file uv.toml add requests` by independent-auditor in exp-901 was not denied by a rule: decision=deny exit=2 stdout='' stderr=''
- tests/acceptance/W1-46/test_w1_46_install_spellings.py::test_uv_run_w_with_its_value_joined_stays_denied_for_the_other_worker_roles[independent-auditor]
    AssertionError: `uv run -wrequests script.py` by independent-auditor was not denied by a rule: decision=deny exit=2 stdout='' stderr=''
- tests/acceptance/W1-46/test_w1_46_research_installs.py::test_the_same_commands_stay_denied_for_the_other_worker_roles[uv-sync-independent-test-designer]
    AssertionError: `uv sync` by independent-test-designer in exp-901 was not denied by a rule: decision=deny exit=2 stdout='' stderr=''
- tests/acceptance/W1-46/test_w1_46_research_role.py::test_a_research_session_may_write_inside_its_experiment_folder_with_bash
    AssertionError: `mkdir -p experiments/spikes/exp-901/results` by research was not allowed: decision=deny exit=2 stdout='' stderr=''
- tests/acceptance/W1-46/test_w1_46_research_installs.py::test_the_same_commands_stay_denied_for_the_other_worker_roles[uvx-independent-auditor]
    AssertionError: `uvx ruff check .` by independent-auditor in exp-901 was not denied by a rule: decision=deny exit=2 stdout='' stderr=''
- tests/acceptance/W1-46/test_w1_46_install_spellings.py::test_a_uv_run_whose_script_argument_starts_with_w_is_no_install
    AssertionError: `uv run script.py -wide` by the engineer was not allowed: decision=deny exit=2 stdout='' stderr=''
- tests/acceptance/W1-46/test_w1_46_research_installs.py::test_the_same_commands_stay_denied_for_the_other_worker_roles[uv-add-engineer]
    AssertionError: `uv add requests` by engineer in exp-901 was not denied by a rule: decision=deny exit=2 stdout='' stderr=''
- tests/acceptance/W1-46/test_w1_46_research_installs.py::test_the_same_commands_stay_denied_for_the_other_worker_roles[run-w-engineer]
    AssertionError: `uv run -w requests script.py` by engineer in exp-901 was not denied by a rule: decision=deny exit=2 stdout='' stderr=''
- tests/acceptance/W1-46/test_w1_46_install_spellings.py::test_uv_run_w_with_its_value_joined_is_denied_to_research_outside_its_folder
    AssertionError: `uv run -wrequests script.py` by research in repo was not denied by a rule: decision=deny exit=2 stdout='' stderr=''
- tests/acceptance/W1-46/test_w1_46_runtime_and_ln.py::test_scratch_stays_writable_for_every_role[orchestrator]
    AssertionError: `echo x > .gov-runtime/scratch/w1-46/new.txt` by orchestrator was not allowed: decision=deny exit=2 stdout='' stderr=''
- tests/acceptance/W1-46/test_w1_46_research_installs.py::test_the_same_commands_stay_denied_for_the_other_worker_roles[cache-dir-sync-independent-test-designer]
    AssertionError: `uv --cache-dir .uv-cache sync` by independent-test-designer in exp-901 was not denied by a rule: decision=deny exit=2 stdout='' stderr=''
- tests/acceptance/W1-46/test_w1_46_research_installs.py::test_the_same_commands_stay_denied_for_the_other_worker_roles[uv-sync-independent-auditor]
    AssertionError: `uv sync` by independent-auditor in exp-901 was not denied by a rule: decision=deny exit=2 stdout='' stderr=''
- tests/acceptance/W1-46/test_w1_46_research_role.py::test_the_guard_grants_the_research_role_no_network_and_asks_nothing_for_it
    AssertionError: `curl -sI https://pypi.org/simple/` by research was not allowed: decision=deny exit=2 stdout='' stderr=''
- tests/acceptance/W1-46/test_w1_46_research_installs.py::test_another_role_on_the_research_ticket_gets_no_install_through[engineer]
    AssertionError: `uv add requests` by engineer on the research ticket was not denied by a rule: decision=deny exit=2 stdout='' stderr=''
- tests/acceptance/W1-47/test_w1_47_kernel_template.py::test_the_template_s_containment_check_leaves_a_change_in_scope_alone[PostToolUse]
    AssertionError: the PreToolUse commands of template/governance/kernel/settings.json did not let the fixture call through, so no Bash call would follow: decision=deny exit=2 stdout='' stderr=''
- tests/acceptance/W1-46/test_w1_46_research_installs.py::test_the_same_commands_stay_denied_for_the_other_worker_roles[uv-run-with-engineer]
    AssertionError: `uv run --with requests python script.py` by engineer in exp-901 was not denied by a rule: decision=deny exit=2 stdout='' stderr=''
- tests/acceptance/W1-46/test_w1_46_runtime_and_ln.py::test_scratch_stays_writable_for_every_role[engineer]
    AssertionError: `echo x > .gov-runtime/scratch/w1-46/new.txt` by engineer was not allowed: decision=deny exit=2 stdout='' stderr=''
- tests/acceptance/W1-46/test_w1_46_research_installs.py::test_the_same_commands_stay_denied_for_the_other_worker_roles[uv-add-independent-test-designer]
    AssertionError: `uv add requests` by independent-test-designer in exp-901 was not denied by a rule: decision=deny exit=2 stdout='' stderr=''
- tests/acceptance/W1-46/test_w1_46_runtime_and_ln.py::test_scratch_stays_writable_for_every_role[research]
    AssertionError: `echo x > .gov-runtime/scratch/w1-46/new.txt` by research was not allowed: decision=deny exit=2 stdout='' stderr=''
- tests/acceptance/W1-46/test_w1_46_research_installs.py::test_the_same_commands_stay_denied_for_the_other_worker_roles[cache-dir-sync-independent-auditor]
    AssertionError: `uv --cache-dir .uv-cache sync` by independent-auditor in exp-901 was not denied by a rule: decision=deny exit=2 stdout='' stderr=''
- tests/acceptance/W1-47/test_w1_47_kernel_template.py::test_the_template_s_containment_check_leaves_a_change_in_scope_alone[PostToolUseFailure]
    AssertionError: the PreToolUse commands of template/governance/kernel/settings.json did not let the fixture call through, so no Bash call would follow: decision=deny exit=2 stdout='' stderr=''
- tests/acceptance/W1-46/test_w1_46_options_after_the_destination.py::test_the_guard_does_not_refuse_cp_between_two_names_of_the_working_directory_inside_the_roles_paths
    AssertionError: `cp decide.py w1_46_copy.py` by an engineer, working directory src/gov/guard was not allowed: decision=deny exit=2 stdout='' stderr=''
- tests/acceptance/W1-46/test_w1_46_runtime_and_ln.py::test_scratch_stays_writable_for_every_role[product-spec]
    AssertionError: `echo x > .gov-runtime/scratch/w1-46/new.txt` by product-spec was not allowed: decision=deny exit=2 stdout='' stderr=''
- tests/acceptance/W1-46/test_w1_46_research_installs.py::test_a_research_install_inside_the_experiment_folder_is_let_through_by_the_kernel_s_wiring[run-w]
    AssertionError: `uv run -w requests script.py` by research in its experiment folder was not allowed: decision=deny exit=2 stdout='' stderr=''
- tests/acceptance/W1-46/test_w1_46_research_installs.py::test_the_same_commands_stay_denied_for_the_other_worker_roles[uv-run-with-independent-test-designer]
    AssertionError: `uv run --with requests python script.py` by independent-test-designer in exp-901 was not denied by a rule: decision=deny exit=2 stdout='' stderr=''
- tests/acceptance/W1-46/test_w1_46_hard_links_mv_and_install.py::test_the_test_designer_may_hard_link_one_acceptance_test_to_another_name_there
    AssertionError: `ln tests/acceptance/W1-90/test_fixture.py tests/acceptance/W1-90/test_w1_46_other_name.py` by the test designer was not allowed: decision=deny exit=2 stdout='' stderr=''
- tests/acceptance/W1-46/test_w1_46_research_installs.py::test_a_research_install_after_cd_into_the_experiment_folder_is_let_through
    AssertionError: `cd experiments/spikes/exp-901 && uv add requests` by research was not allowed: decision=deny exit=2 stdout='' stderr=''
- tests/acceptance/W1-46/test_w1_46_research_installs.py::test_a_research_install_inside_the_experiment_folder_is_let_through_by_the_kernel_s_wiring[uvx]
    AssertionError: `uvx ruff check .` by research in its experiment folder was not allowed: decision=deny exit=2 stdout='' stderr=''
- tests/acceptance/W1-46/test_w1_46_links_and_cp_targets.py::test_the_guard_does_not_refuse_a_link_whose_source_and_destination_are_inside_the_roles_paths[symbolic]
    AssertionError: `ln -s /tmp/gov-os-lead-W2-110/pytest-of-usain/pytest-25/popen-gw4/test_the_guard_does_not_refuse0/repo/src/gov/guard/decide.py src/gov/guard/w1_46_link.py` by an engineer was not allowed: decision=deny exit=2 stdout='' stderr=''
- tests/acceptance/W1-46/test_w1_46_runtime_and_ln.py::test_the_guard_does_not_refuse_ln_to_a_destination_the_role_may_write[inside-the-tickets-paths-hard]
    AssertionError: `ln .gov-runtime/scratch/w1-46/seed.txt src/gov/guard/w1_46_link.py` by an engineer was not allowed: decision=deny exit=2 stdout='' stderr=''
- tests/acceptance/W1-46/test_w1_46_research_installs.py::test_a_research_install_inside_the_experiment_folder_is_let_through_by_the_kernel_s_wiring[uv-add]
    AssertionError: `uv add requests` by research in its experiment folder was not allowed: decision=deny exit=2 stdout='' stderr=''
- tests/acceptance/W1-46/test_w1_46_research_installs.py::test_no_permission_mode_turns_the_research_install_into_a_prompt[acceptEdits]
    AssertionError: `uv add requests` by research in acceptEdits mode was not allowed: decision=deny exit=2 stdout='' stderr=''
- tests/acceptance/W1-46/test_w1_46_research_installs.py::test_no_permission_mode_turns_the_research_install_into_a_prompt[plan]
    AssertionError: `uv add requests` by research in plan mode was not allowed: decision=deny exit=2 stdout='' stderr=''
- tests/acceptance/W1-46/test_w1_46_research_installs.py::test_a_research_install_below_the_experiment_folder_is_let_through[uv-run-with]
    AssertionError: `uv run --with requests python script.py` by research below its experiment folder was not allowed: decision=deny exit=2 stdout='' stderr=''
- tests/acceptance/W1-46/test_w1_46_hard_links_mv_and_install.py::test_the_guard_does_not_refuse_a_hard_link_between_two_names_inside_the_roles_paths[link]
    AssertionError: `link src/gov/guard/decide.py src/gov/guard/w1_46_link.py` by an engineer was not allowed: decision=deny exit=2 stdout='' stderr=''
- tests/acceptance/W1-46/test_w1_46_research_installs.py::test_a_research_install_after_cd_into_another_folder_is_denied
    AssertionError: `cd experiments/spikes/exp-900 && uv add requests` by research from the repository root was not denied by a rule: decision=deny exit=2 stdout='' stderr=''
- tests/acceptance/W1-46/test_w1_46_links_and_cp_targets.py::test_the_guard_does_not_refuse_a_link_whose_source_and_destination_are_inside_the_roles_paths[hard]
    AssertionError: `ln src/gov/guard/decide.py src/gov/guard/w1_46_link.py` by an engineer was not allowed: decision=deny exit=2 stdout='' stderr=''
- tests/acceptance/W1-46/test_w1_46_runtime_and_ln.py::test_the_guard_does_not_refuse_ln_to_a_destination_the_role_may_write[inside-the-tickets-paths-symbolic]
    AssertionError: `ln -s .gov-runtime/scratch/w1-46/seed.txt src/gov/guard/w1_46_link.py` by an engineer was not allowed: decision=deny exit=2 stdout='' stderr=''
- tests/acceptance/W1-46/test_w1_46_research_installs.py::test_a_research_install_inside_the_experiment_folder_is_let_through_by_the_kernel_s_wiring[uv-pip-install]
    AssertionError: `uv pip install requests` by research in its experiment folder was not allowed: decision=deny exit=2 stdout='' stderr=''
- tests/acceptance/W1-46/test_w1_46_research_installs.py::test_a_research_install_inside_the_experiment_folder_is_let_through_by_the_kernel_s_wiring[cache-dir-sync]
    AssertionError: `uv --cache-dir .uv-cache sync` by research in its experiment folder was not allowed: decision=deny exit=2 stdout='' stderr=''
- tests/acceptance/W1-46/test_w1_46_research_installs.py::test_no_permission_mode_turns_the_research_install_into_a_prompt[auto]
    AssertionError: `uv add requests` by research in auto mode was not allowed: decision=deny exit=2 stdout='' stderr=''
- tests/acceptance/W1-46/test_w1_46_research_installs.py::test_a_research_install_outside_the_experiment_folder_is_denied[cache-dir-sync-repository-root]
    AssertionError: `uv --cache-dir .uv-cache sync` by research in repository-root was not denied by a rule: decision=deny exit=2 stdout='' stderr=''
- tests/acceptance/W1-46/test_w1_46_research_installs.py::test_a_research_install_below_the_experiment_folder_is_let_through[uv-sync]
    AssertionError: `uv sync` by research below its experiment folder was not allowed: decision=deny exit=2 stdout='' stderr=''
- tests/acceptance/W1-46/test_w1_46_hard_links_mv_and_install.py::test_the_guard_does_not_refuse_install_to_a_destination_inside_the_roles_paths
    AssertionError: `install src/gov/guard/decide.py src/gov/guard/w1_46_installed.py` by an engineer was not allowed: decision=deny exit=2 stdout='' stderr=''
- tests/acceptance/W1-46/test_w1_46_research_installs.py::test_a_research_install_inside_the_experiment_folder_is_let_through_by_the_kernel_s_wiring[venv-pip-install]
    AssertionError: `.venv/bin/pip install requests` by research in its experiment folder was not allowed: decision=deny exit=2 stdout='' stderr=''
- tests/acceptance/W1-46/test_w1_46_links_and_cp_targets.py::test_cp_with_the_destination_as_the_last_operand_is_judged_as_before
    AssertionError: `cp src/gov/guard/decide.py src/gov/guard/w1_46_copy.py` by an engineer was not allowed: decision=deny exit=2 stdout='' stderr=''
- tests/acceptance/W1-46/test_w1_46_runtime_and_ln.py::test_the_guard_does_not_refuse_ln_to_a_destination_the_role_may_write[scratch-hard]
    AssertionError: `ln .gov-runtime/scratch/w1-46/seed.txt .gov-runtime/scratch/w1-46/link.txt` by an engineer was not allowed: decision=deny exit=2 stdout='' stderr=''
- tests/acceptance/W1-46/test_w1_46_research_installs.py::test_a_research_install_inside_the_experiment_folder_is_let_through_by_the_kernel_s_wiring[uv-run-with]
    AssertionError: `uv run --with requests python script.py` by research in its experiment folder was not allowed: decision=deny exit=2 stdout='' stderr=''
- tests/acceptance/W1-46/test_w1_46_research_installs.py::test_a_research_install_inside_the_experiment_folder_is_let_through_by_the_kernel_s_wiring[config-file-add]
    AssertionError: `uv --config-file uv.toml add requests` by research in its experiment folder was not allowed: decision=deny exit=2 stdout='' stderr=''
- tests/acceptance/W1-46/test_w1_46_research_installs.py::test_no_permission_mode_turns_the_research_install_into_a_prompt[dontAsk]
    AssertionError: `uv add requests` by research in dontAsk mode was not allowed: decision=deny exit=2 stdout='' stderr=''
- tests/acceptance/W1-46/test_w1_46_research_installs.py::test_a_research_install_outside_the_experiment_folder_is_denied[cache-dir-sync-sibling-experiment]
    AssertionError: `uv --cache-dir .uv-cache sync` by research in sibling-experiment was not denied by a rule: decision=deny exit=2 stdout='' stderr=''
- tests/acceptance/W1-46/test_w1_46_research_installs.py::test_no_permission_mode_turns_the_research_install_into_a_prompt[default]
    AssertionError: `uv add requests` by research in default mode was not allowed: decision=deny exit=2 stdout='' stderr=''
- tests/acceptance/W1-46/test_w1_46_hard_links_mv_and_install.py::test_the_guard_does_not_refuse_mv_with_a_target_directory_inside_the_roles_paths
    AssertionError: `mv --target-directory=src/gov/guard/w1_46_directory src/gov/guard/decide.py` by an engineer was not allowed: decision=deny exit=2 stdout='' stderr=''
- tests/acceptance/W1-46/test_w1_46_hard_links_mv_and_install.py::test_the_guard_does_not_refuse_a_hard_link_between_two_names_inside_the_roles_paths[cp -l]
    AssertionError: `cp -l src/gov/guard/decide.py src/gov/guard/w1_46_link.py` by an engineer was not allowed: decision=deny exit=2 stdout='' stderr=''
- tests/acceptance/W1-46/test_w1_46_runtime_and_ln.py::test_the_guard_does_not_refuse_ln_to_a_destination_the_role_may_write[scratch-symbolic]
    AssertionError: `ln -s .gov-runtime/scratch/w1-46/seed.txt .gov-runtime/scratch/w1-46/link.txt` by an engineer was not allowed: decision=deny exit=2 stdout='' stderr=''
- tests/acceptance/W1-46/test_w1_46_options_after_the_destination.py::test_the_guard_does_not_refuse_install_with_its_option_before_the_operands
    AssertionError: `install -m 644 src/gov/guard/decide.py src/gov/guard/w1_46_installed.py` by an engineer was not allowed: decision=deny exit=2 stdout='' stderr=''
- tests/acceptance/W1-46/test_w1_46_research_installs.py::test_a_research_install_inside_the_experiment_folder_is_let_through_by_the_kernel_s_wiring[uv-sync]
    AssertionError: `uv sync` by research in its experiment folder was not allowed: decision=deny exit=2 stdout='' stderr=''
- tests/acceptance/W1-46/test_w1_46_research_installs.py::test_a_research_install_inside_the_experiment_folder_is_let_through_by_the_kernel_s_wiring[python-m-pip-install]
    AssertionError: `.venv/bin/python -m pip install requests` by research in its experiment folder was not allowed: decision=deny exit=2 stdout='' stderr=''
- tests/acceptance/W1-46/test_w1_46_research_installs.py::test_no_permission_mode_turns_the_research_install_into_a_prompt[bypassPermissions]
    AssertionError: `uv add requests` by research in bypassPermissions mode was not allowed: decision=deny exit=2 stdout='' stderr=''
- tests/acceptance/W1-46/test_w1_46_research_installs.py::test_a_research_install_outside_the_experiment_folder_is_denied[cache-dir-sync-source-tree]
    AssertionError: `uv --cache-dir .uv-cache sync` by research in source-tree was not denied by a rule: decision=deny exit=2 stdout='' stderr=''
- tests/acceptance/W1-46/test_w1_46_research_installs.py::test_a_research_install_outside_the_experiment_folder_is_denied[config-file-add-repository-root]
    AssertionError: `uv --config-file uv.toml add requests` by research in repository-root was not denied by a rule: decision=deny exit=2 stdout='' stderr=''
- tests/acceptance/W1-46/test_w1_46_research_installs.py::test_a_research_install_below_the_experiment_folder_is_let_through[uvx]
    AssertionError: `uvx ruff check .` by research below its experiment folder was not allowed: decision=deny exit=2 stdout='' stderr=''
- tests/acceptance/W1-46/test_w1_46_research_installs.py::test_a_research_install_below_the_experiment_folder_is_let_through[uv-add]
    AssertionError: `uv add requests` by research below its experiment folder was not allowed: decision=deny exit=2 stdout='' stderr=''
- tests/acceptance/W1-46/test_w1_46_research_installs.py::test_a_research_install_outside_the_experiment_folder_is_denied[run-w-sibling-experiment]
    AssertionError: `uv run -w requests script.py` by research in sibling-experiment was not denied by a rule: decision=deny exit=2 stdout='' stderr=''
- tests/acceptance/W1-46/test_w1_46_research_installs.py::test_a_research_install_outside_the_experiment_folder_is_denied[uv-run-with-source-tree]
    AssertionError: `uv run --with requests python script.py` by research in source-tree was not denied by a rule: decision=deny exit=2 stdout='' stderr=''
- tests/acceptance/W1-46/test_w1_46_research_installs.py::test_a_research_install_outside_the_experiment_folder_is_denied[uv-add-source-tree]
    AssertionError: `uv add requests` by research in source-tree was not denied by a rule: decision=deny exit=2 stdout='' stderr=''
- tests/acceptance/W1-46/test_w1_46_runtime_and_ln.py::test_the_guard_holds_a_research_ln_to_the_experiment_folder
    AssertionError: `ln -s README.md experiments/spikes/exp-901/w1-46-link.md` by research was not allowed: decision=deny exit=2 stdout='' stderr=''
- tests/acceptance/W1-46/test_w1_46_research_installs.py::test_a_research_install_outside_the_experiment_folder_is_denied[uv-sync-source-tree]
    AssertionError: `uv sync` by research in source-tree was not denied by a rule: decision=deny exit=2 stdout='' stderr=''
- tests/acceptance/W1-46/test_w1_46_research_installs.py::test_a_research_install_outside_the_experiment_folder_is_denied[uvx-source-tree]
    AssertionError: `uvx ruff check .` by research in source-tree was not denied by a rule: decision=deny exit=2 stdout='' stderr=''
- tests/acceptance/W1-46/test_w1_46_research_installs.py::test_a_research_install_outside_the_experiment_folder_is_denied[config-file-add-sibling-experiment]
    AssertionError: `uv --config-file uv.toml add requests` by research in sibling-experiment was not denied by a rule: decision=deny exit=2 stdout='' stderr=''
- tests/acceptance/W1-46/test_w1_46_research_installs.py::test_a_research_install_outside_the_experiment_folder_is_denied[run-w-source-tree]
    AssertionError: `uv run -w requests script.py` by research in source-tree was not denied by a rule: decision=deny exit=2 stdout='' stderr=''
- tests/acceptance/W1-46/test_w1_46_research_installs.py::test_a_research_install_outside_the_experiment_folder_is_denied[uv-sync-repository-root]
    AssertionError: `uv sync` by research in repository-root was not denied by a rule: decision=deny exit=2 stdout='' stderr=''
- tests/acceptance/W1-46/test_w1_46_research_installs.py::test_a_research_install_outside_the_experiment_folder_is_denied[uv-run-with-repository-root]
    AssertionError: `uv run --with requests python script.py` by research in repository-root was not denied by a rule: decision=deny exit=2 stdout='' stderr=''
- tests/acceptance/W1-46/test_w1_46_research_installs.py::test_a_research_install_outside_the_experiment_folder_is_denied[uvx-repository-root]
    AssertionError: `uvx ruff check .` by research in repository-root was not denied by a rule: decision=deny exit=2 stdout='' stderr=''
- tests/acceptance/W1-46/test_w1_46_research_installs.py::test_a_research_install_on_another_roles_ticket_is_denied
    AssertionError: `uv add requests` by research on the engineer's ticket was not denied by a rule: decision=deny exit=2 stdout='' stderr=''
- tests/acceptance/W1-46/test_w1_46_research_installs.py::test_a_research_install_outside_the_experiment_folder_is_denied[config-file-add-source-tree]
    AssertionError: `uv --config-file uv.toml add requests` by research in source-tree was not denied by a rule: decision=deny exit=2 stdout='' stderr=''
- tests/acceptance/W1-46/test_w1_46_research_installs.py::test_a_research_install_outside_the_experiment_folder_is_denied[uv-sync-sibling-experiment]
    AssertionError: `uv sync` by research in sibling-experiment was not denied by a rule: decision=deny exit=2 stdout='' stderr=''
- tests/acceptance/W1-46/test_w1_46_research_installs.py::test_a_research_install_outside_the_experiment_folder_is_denied[uv-add-repository-root]
    AssertionError: `uv add requests` by research in repository-root was not denied by a rule: decision=deny exit=2 stdout='' stderr=''
- tests/acceptance/W1-46/test_w1_46_research_installs.py::test_a_research_install_outside_the_experiment_folder_is_denied[uv-run-with-sibling-experiment]
    AssertionError: `uv run --with requests python script.py` by research in sibling-experiment was not denied by a rule: decision=deny exit=2 stdout='' stderr=''
- tests/acceptance/W1-46/test_w1_46_research_installs.py::test_a_research_install_outside_the_experiment_folder_is_denied[uvx-sibling-experiment]
    AssertionError: `uvx ruff check .` by research in sibling-experiment was not denied by a rule: decision=deny exit=2 stdout='' stderr=''
- tests/acceptance/W1-46/test_w1_46_research_installs.py::test_a_research_install_outside_the_experiment_folder_is_denied[run-w-repository-root]
    AssertionError: `uv run -w requests script.py` by research in repository-root was not denied by a rule: decision=deny exit=2 stdout='' stderr=''
- tests/acceptance/W1-46/test_w1_46_research_installs.py::test_a_research_install_outside_the_experiment_folder_is_denied[uv-add-sibling-experiment]
    AssertionError: `uv add requests` by research in sibling-experiment was not denied by a rule: decision=deny exit=2 stdout='' stderr=''
- tests/acceptance/W1-47/test_w1_47_failed_commands.py::test_a_failed_command_is_caught_through_the_committed_settings
    AssertionError: the registered PreToolUse commands did not let the fixture call `bash /tmp/gov-os-lead-W2-110/pytest-of-usain/pytest-25/popen-gw7/test_a_failed_command_is_caugh0/live-sandbox/calls/call-0001.sh` through, so no Bash call would follow: decision=deny (`h="$CLAUDE_PROJECT_DIR/governance/
- tests/acceptance/W1-47/test_w1_47_kernel_template.py::test_the_template_s_guard_lets_a_call_in_scope_through[Bash-listing]
    AssertionError: Bash-listing by the engineer was not let through by the commands of template/governance/kernel/settings.json: decision=deny (decision=deny exit=2 stdout='' stderr='')
- tests/acceptance/W1-47/test_w1_47_kernel_template.py::test_the_template_s_containment_check_catches_a_change_out_of_scope[PostToolUse]
    AssertionError: the PreToolUse commands of template/governance/kernel/settings.json did not let the fixture call through, so no Bash call would follow: decision=deny exit=2 stdout='' stderr=''
- tests/acceptance/W1-47/test_w1_47_kernel_template.py::test_the_template_s_containment_check_catches_a_change_out_of_scope[PostToolUseFailure]
    AssertionError: the PreToolUse commands of template/governance/kernel/settings.json did not let the fixture call through, so no Bash call would follow: decision=deny exit=2 stdout='' stderr=''
- tests/acceptance/W1-47/test_w1_47_kernel_template.py::test_the_template_s_containment_check_restores_an_acceptance_test_after_a_failed_command
    AssertionError: the PreToolUse commands of template/governance/kernel/settings.json did not let the fixture call through, so no Bash call would follow: decision=deny exit=2 stdout='' stderr=''

## Three full failure texts

### tests/acceptance/W1-46/test_w1_46_research_installs.py::test_the_same_commands_stay_denied_for_the_other_worker_roles[config-file-add-engineer]

```
kernel_guard = <function kernel_guard.<locals>._guard at 0x77313dcad8a0>
kernel_project = PosixPath('/tmp/gov-os-lead-W2-110/pytest-of-usain/pytest-25/popen-gw1/test_the_same_commands_stay_de0/repo')
kernel_folder = PosixPath('/tmp/gov-os-lead-W2-110/pytest-of-usain/pytest-25/popen-gw1/test_the_same_commands_stay_de0/repo/experiments/spikes/exp-901')
name = 'config-file-add', role = 'engineer'

    @pytest.mark.parametrize("role", support.EMPTY_ALLOWLIST_ROLES)
    @pytest.mark.parametrize("name", sorted(DEC_219_FORMS))
    def test_the_same_commands_stay_denied_for_the_other_worker_roles(kernel_guard, kernel_project, kernel_folder, name,
                                                                      role):
        """In the experiment folder and in the repository root. Holds before implementation; it must still hold after."""
        guard, project, folder = kernel_guard, kernel_project, kernel_folder
        for cwd in (folder, project):
            result = guard("Bash", w47.bash_input(DEC_219_FORMS[name]), role, cwd=cwd)
>           w47.assert_denied_by_rule(result, f"`{DEC_219_FORMS[name]}` by {role} in {cwd.name}")

tests/acceptance/W1-46/test_w1_46_research_installs.py:201: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

result = GuardResult(decision='deny', returncode=2, stdout='', stderr='')
what = '`uv --config-file uv.toml add requests` by engineer in exp-901'

    def assert_denied_by_rule(result, what):
        """The hook answered with a deny decision of its own: exit code 0 and ``permissionDecision: deny``.
    
        Exit code 2 also stops a call, but it is the hook's report of its own
        failure (DEC-110), not a rule. A rule this ticket adds must decide.
        """
>       assert result.decision == "deny" and result.returncode == 0, f"{what} was not denied by a rule: {result.describe()}"
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       AssertionError: `uv --config-file uv.toml add requests` by engineer in exp-901 was not denied by a rule: decision=deny exit=2 stdout='' stderr=''

tests/acceptance/W1-47/w1_47_support.py:451: AssertionError
```

### tests/acceptance/W1-46/test_w1_46_install_spellings.py::test_uv_run_w_with_its_value_joined_stays_denied_for_the_other_worker_roles[engineer]

```
kernel_guard = <function kernel_guard.<locals>._guard at 0x740983a758a0>
kernel_project = PosixPath('/tmp/gov-os-lead-W2-110/pytest-of-usain/pytest-25/popen-gw7/test_uv_run_w_with_its_value_j0/repo')
role = 'engineer'

    @pytest.mark.parametrize("role", support.EMPTY_ALLOWLIST_ROLES)
    def test_uv_run_w_with_its_value_joined_stays_denied_for_the_other_worker_roles(kernel_guard, kernel_project, role):
        guard, project = kernel_guard, kernel_project
        for command in JOINED:
            result = guard("Bash", w47.bash_input(command), role, cwd=project)
>           w47.assert_denied_by_rule(result, f"`{command}` by {role}")

tests/acceptance/W1-46/test_w1_46_install_spellings.py:42: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

result = GuardResult(decision='deny', returncode=2, stdout='', stderr='')
what = '`uv run -wrequests script.py` by engineer'

    def assert_denied_by_rule(result, what):
        """The hook answered with a deny decision of its own: exit code 0 and ``permissionDecision: deny``.
    
        Exit code 2 also stops a call, but it is the hook's report of its own
        failure (DEC-110), not a rule. A rule this ticket adds must decide.
        """
>       assert result.decision == "deny" and result.returncode == 0, f"{what} was not denied by a rule: {result.describe()}"
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       AssertionError: `uv run -wrequests script.py` by engineer was not denied by a rule: decision=deny exit=2 stdout='' stderr=''

tests/acceptance/W1-47/w1_47_support.py:451: AssertionError
```

### tests/acceptance/W1-46/test_w1_46_research_installs.py::test_the_same_commands_stay_denied_for_the_other_worker_roles[uv-run-with-independent-auditor]

```
kernel_guard = <function kernel_guard.<locals>._guard at 0x727a211258a0>
kernel_project = PosixPath('/tmp/gov-os-lead-W2-110/pytest-of-usain/pytest-25/popen-gw4/test_the_same_commands_stay_de0/repo')
kernel_folder = PosixPath('/tmp/gov-os-lead-W2-110/pytest-of-usain/pytest-25/popen-gw4/test_the_same_commands_stay_de0/repo/experiments/spikes/exp-901')
name = 'uv-run-with', role = 'independent-auditor'

    @pytest.mark.parametrize("role", support.EMPTY_ALLOWLIST_ROLES)
    @pytest.mark.parametrize("name", sorted(DEC_219_FORMS))
    def test_the_same_commands_stay_denied_for_the_other_worker_roles(kernel_guard, kernel_project, kernel_folder, name,
                                                                      role):
        """In the experiment folder and in the repository root. Holds before implementation; it must still hold after."""
        guard, project, folder = kernel_guard, kernel_project, kernel_folder
        for cwd in (folder, project):
            result = guard("Bash", w47.bash_input(DEC_219_FORMS[name]), role, cwd=cwd)
>           w47.assert_denied_by_rule(result, f"`{DEC_219_FORMS[name]}` by {role} in {cwd.name}")

tests/acceptance/W1-46/test_w1_46_research_installs.py:201: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

result = GuardResult(decision='deny', returncode=2, stdout='', stderr='')
what = '`uv run --with requests python script.py` by independent-auditor in exp-901'

    def assert_denied_by_rule(result, what):
        """The hook answered with a deny decision of its own: exit code 0 and ``permissionDecision: deny``.
    
        Exit code 2 also stops a call, but it is the hook's report of its own
        failure (DEC-110), not a rule. A rule this ticket adds must decide.
        """
>       assert result.decision == "deny" and result.returncode == 0, f"{what} was not denied by a rule: {result.describe()}"
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       AssertionError: `uv run --with requests python script.py` by independent-auditor in exp-901 was not denied by a rule: decision=deny exit=2 stdout='' stderr=''

tests/acceptance/W1-47/w1_47_support.py:451: AssertionError
```
