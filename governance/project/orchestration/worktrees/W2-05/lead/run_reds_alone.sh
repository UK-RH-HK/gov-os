#!/usr/bin/env bash
# Re-run the six W2-96 reds of the scoped run alone, serially (no -n), once.
L=/home/usain/gov-os-worktrees/W2-05/.gov-runtime/scratch/lead/log
T=/home/usain/gov-os-worktrees/W2-05
mkdir -p /tmp/gov-os-lead-W2-05 "$T/.gov-runtime/scratch/empty-home"
rm -f "$L/reds-alone.exit"
cd "$T" || exit 2
env TMPDIR=/tmp/gov-os-lead-W2-05 HOME=$T/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=$T/src \
  python3 -m pytest -q -p no:cacheprovider -o tmp_path_retention_policy=failed --junitxml="$L/reds-alone.xml" \
  "tests/unit/accept/test_w2_96_review3.py::test_w2_96_r14_a_stopped_run_keeps_128_plus_the_signal" \
  "tests/unit/accept/test_w2_96_review4.py::test_w2_96_r16_an_own_session_orphan_is_reaped_before_a_stopped_run_cleans_up" \
  "tests/unit/accept/test_w2_96_run2.py::test_w2_96_r9_r12_a_signal_during_the_clean_up_is_held_back" \
  "tests/unit/accept/test_w2_96_run2.py::test_w2_96_r9_r12_a_signal_during_the_run_then_more_during_the_clean_up" \
  "tests/unit/accept/test_w2_96_run2.py::test_w2_96_r9_r12_presses_until_gov_ends_never_kill_it" \
  "tests/unit/accept/test_w2_96_run2.py::test_w2_96_r9_r12_ctrl_c_during_the_run_stops_it" \
  > "$L/reds-alone.txt" 2>&1
echo $? > "$L/reds-alone.exit"
