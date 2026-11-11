#!/usr/bin/env bash
# The six W2-96 signal cases alone, twice: the session's own HOME, then an empty HOME (row 133's cause).
set -u
T=/home/usain/gov-os-worktrees/W2-90b
L=$T/.gov-runtime/scratch/land
IDS=(
 "tests/unit/accept/test_w2_96_review3.py::test_w2_96_r14_a_stopped_run_keeps_128_plus_the_signal[True-2]"
 "tests/unit/accept/test_w2_96_review4.py::test_w2_96_r16_an_own_session_orphan_is_reaped_before_a_stopped_run_cleans_up[2]"
 "tests/unit/accept/test_w2_96_run2.py::test_w2_96_r9_r12_a_signal_during_the_clean_up_is_held_back[signals0]"
 "tests/unit/accept/test_w2_96_run2.py::test_w2_96_r9_r12_a_signal_during_the_run_then_more_during_the_clean_up[2-more0]"
 "tests/unit/accept/test_w2_96_run2.py::test_w2_96_r9_r12_presses_until_gov_ends_never_kill_it[kinds0]"
 "tests/unit/accept/test_w2_96_run2.py::test_w2_96_r9_r12_ctrl_c_during_the_run_stops_it"
)
cd $T
echo "== own HOME ($HOME)"
env TMPDIR=/tmp/gov-os-lead-W2-90b PYTHONPATH=$T/src python3 -m pytest "${IDS[@]}" -q -p no:cacheprovider -o tmp_path_retention_policy=failed --junitxml=$L/w296_ownhome.xml 2>&1 | tail -3
echo "== empty HOME"
env TMPDIR=/tmp/gov-os-lead-W2-90b HOME=$T/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=$T/src python3 -m pytest "${IDS[@]}" -q -p no:cacheprovider -o tmp_path_retention_policy=failed --junitxml=$L/w296_emptyhome.xml 2>&1 | tail -3
