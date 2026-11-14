#!/usr/bin/env bash
# The revised cases of W2-182 on the ticket branch, alone (one pytest call), through the heavy slot.
cd /home/usain/gov-os-worktrees/W2-182 || exit 2
mkdir -p /tmp/w2-182-lead
A=tests/acceptance
env TMPDIR=/tmp/w2-182-lead PYTHONUSERBASE=/home/usain/.local \
  HOME=/home/usain/gov-os-worktrees/W2-182/.gov-runtime/scratch/empty-home \
  PYTHONPATH=/home/usain/gov-os-worktrees/W2-182/src \
  bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh \
  python3 -m pytest -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rfE \
  --junitxml=/home/usain/gov-os-worktrees/W2-182/.gov-runtime/scratch/lead/log/cases.xml \
  "$A/W1-32/test_w1_32_command_set.py::test_the_command_set_is_the_twelve_and_the_three_recorded_ones" \
  "$A/W1-18/test_w1_18_on_demand_start.py::test_with_the_server_not_answering_a_retrieval_answers_by_keywords_and_starts_nothing" \
  "$A/W2-123/test_w2_123_retry.py::test_after_the_last_failed_try_the_rebuild_states_the_tries_and_waits_and_no_partial_store_is_reported_built" \
  "$A/W2-121/test_s1_lock_off_status.py::test_s1_status_runs_no_pass_and_writes_nothing" \
  "$A/W2-136/test_w2_136_never_a_gate.py::test_s10_no_module_of_gov_outside_plan_and_launch_imports_or_calls_gov_plan" \
  "$A/W2-23/test_w2_23_space.py::test_s6_every_kernel_hook_exits_alike_with_a_space_in_the_project_dir" \
  "$A/W2-128/test_w2_128_rows.py::test_row_8_no_unit_carries_the_gov_accept_outside_the_sandbox_until_w2_56_line"
