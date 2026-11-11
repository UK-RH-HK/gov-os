#!/bin/bash
# Re-run the six W2-96 cases that failed in the scoped parallel run, alone, one process, the tree's own code.
T=/home/usain/gov-os-worktrees/W2-81
env TMPDIR=/tmp/gov-os-lead-W2-81 PYTHONPATH=$T/src python3 -m pytest -q -p no:cacheprovider -o tmp_path_retention_policy=failed \
  "$T/tests/unit/accept/test_w2_96_review3.py::test_w2_96_r14_a_stopped_run_keeps_128_plus_the_signal[True-2]" \
  "$T/tests/unit/accept/test_w2_96_review4.py::test_w2_96_r16_an_own_session_orphan_is_reaped_before_a_stopped_run_cleans_up[2]" \
  "$T/tests/unit/accept/test_w2_96_run2.py::test_w2_96_r9_r12_a_signal_during_the_clean_up_is_held_back[signals0]" \
  "$T/tests/unit/accept/test_w2_96_run2.py::test_w2_96_r9_r12_a_signal_during_the_run_then_more_during_the_clean_up[2-more0]" \
  "$T/tests/unit/accept/test_w2_96_run2.py::test_w2_96_r9_r12_presses_until_gov_ends_never_kill_it[kinds0]" \
  "$T/tests/unit/accept/test_w2_96_run2.py::test_w2_96_r9_r12_ctrl_c_during_the_run_stops_it" \
  > /home/usain/gov-os-worktrees/W2-81/.gov-runtime/scratch/land/rerun_six.txt 2>&1
echo $? > /home/usain/gov-os-worktrees/W2-81/.gov-runtime/scratch/land/rerun_six.exit
