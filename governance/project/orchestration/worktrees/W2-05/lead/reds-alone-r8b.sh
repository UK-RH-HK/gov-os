#!/bin/bash
# The six W2-96 signal cases alone, foreground, normal HOME, no bytecode (r7's run_ab.sh form).
L=/home/usain/gov-os-worktrees/W2-05/.gov-runtime/scratch/lead/log
cd /home/usain/gov-os-worktrees/W2-05 || exit 9
env TMPDIR=/tmp/gov-os-lead-W2-05 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/home/usain/gov-os-worktrees/W2-05/src python3 -m pytest -q -p no:cacheprovider -o tmp_path_retention_policy=failed --junitxml=$L/reds-alone-r8b.xml \
  "tests/unit/accept/test_w2_96_review3.py::test_w2_96_r14_a_stopped_run_keeps_128_plus_the_signal[True-2]" \
  "tests/unit/accept/test_w2_96_review4.py::test_w2_96_r16_an_own_session_orphan_is_reaped_before_a_stopped_run_cleans_up[2]" \
  "tests/unit/accept/test_w2_96_run2.py::test_w2_96_r9_r12_a_signal_during_the_clean_up_is_held_back[signals0]" \
  "tests/unit/accept/test_w2_96_run2.py::test_w2_96_r9_r12_a_signal_during_the_run_then_more_during_the_clean_up[2-more0]" \
  "tests/unit/accept/test_w2_96_run2.py::test_w2_96_r9_r12_presses_until_gov_ends_never_kill_it[kinds0]" \
  "tests/unit/accept/test_w2_96_run2.py::test_w2_96_r9_r12_ctrl_c_during_the_run_stops_it"
