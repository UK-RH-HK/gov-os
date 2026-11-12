#!/bin/bash
# re-run the scoped run's non-W2-11 reds alone, by node id
T=/home/usain/gov-os-worktrees/W2-11/tests/unit
env TMPDIR=/tmp/gov-os-lead-W2-11 PYTHONPATH=/home/usain/gov-os-worktrees/W2-11/src python3 -m pytest -q -p no:cacheprovider -o tmp_path_retention_policy=failed --no-header --tb=line -rfE \
  "$T/accept/test_w2_96_run2.py::test_w2_96_r9_r12_a_signal_during_the_run_then_more_during_the_clean_up[2-more0]" \
  "$T/accept/test_w2_96_run2.py::test_w2_96_r9_r12_presses_until_gov_ends_never_kill_it[kinds0]" \
  "$T/accept/test_w2_96_run2.py::test_w2_96_r9_r12_ctrl_c_during_the_run_stops_it" \
  "$T/accept/test_w2_96_run2.py::test_w2_96_r9_r12_a_signal_during_the_clean_up_is_held_back[signals0]" \
  "$T/accept/test_w2_96_review3.py::test_w2_96_r14_a_stopped_run_keeps_128_plus_the_signal[True-2]" \
  "$T/accept/test_w2_96_review4.py::test_w2_96_r16_an_own_session_orphan_is_reaped_before_a_stopped_run_cleans_up[2]" \
  "$T/orchestration/test_w2_149_indep_launch.py::test_hidden_part_file_budget_15"
echo "exit $?"
