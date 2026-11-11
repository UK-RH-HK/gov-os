#!/usr/bin/env bash
# Re-run W2-96's load-sensitive signal cases alone once (the build run's verify step 3), and W1-01's history case.
cd /home/usain/gov-os-worktrees/W2-170 || exit 2
mkdir -p /tmp/gov-os-lead-W2-170
env HOME=/home/usain/gov-os-worktrees/W2-170/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local \
  PYTHONPATH=/home/usain/gov-os-worktrees/W2-170/src TMPDIR=/tmp/gov-os-lead-W2-170 \
  python3 -m pytest -q -p no:cacheprovider -o tmp_path_retention_policy=failed \
  "tests/unit/accept/test_w2_96_review3.py::test_w2_96_r14_a_stopped_run_keeps_128_plus_the_signal" \
  "tests/unit/accept/test_w2_96_review4.py::test_w2_96_r16_an_own_session_orphan_is_reaped_before_a_stopped_run_cleans_up" \
  "tests/unit/accept/test_w2_96_run2.py::test_w2_96_r9_r12_a_signal_during_the_clean_up_is_held_back" \
  "tests/unit/accept/test_w2_96_run2.py::test_w2_96_r9_r12_a_signal_during_the_run_then_more_during_the_clean_up" \
  "tests/unit/accept/test_w2_96_run2.py::test_w2_96_r9_r12_presses_until_gov_ends_never_kill_it" \
  "tests/unit/accept/test_w2_96_run2.py::test_w2_96_r9_r12_ctrl_c_during_the_run_stops_it" \
  --junitxml=/home/usain/gov-os-worktrees/W2-170/.gov-runtime/scratch/lead/log/rerun-w296.xml \
  > /home/usain/gov-os-worktrees/W2-170/.gov-runtime/scratch/lead/log/rerun-w296.txt 2>&1
echo "exit $?"
tail -3 /home/usain/gov-os-worktrees/W2-170/.gov-runtime/scratch/lead/log/rerun-w296.txt
