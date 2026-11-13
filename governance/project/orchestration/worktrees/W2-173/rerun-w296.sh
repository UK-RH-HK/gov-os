#!/bin/bash
# Re-run the 6 load-sensitive W2-96 signal cases alone, once (role-lead build step 3).
cd /home/usain/gov-os-worktrees/W2-173 || exit 2
env HOME=/home/usain/gov-os-worktrees/W2-173/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local \
  PYTHONPATH=/home/usain/gov-os-worktrees/W2-173/src python3 -m pytest -q -p no:cacheprovider \
  -o tmp_path_retention_policy=failed \
  "tests/unit/accept/test_w2_96_review3.py::test_w2_96_r14_a_stopped_run_keeps_128_plus_the_signal" \
  "tests/unit/accept/test_w2_96_review4.py::test_w2_96_r16_an_own_session_orphan_is_reaped_before_a_stopped_run_cleans_up" \
  "tests/unit/accept/test_w2_96_run2.py::test_w2_96_r9_r12_a_signal_during_the_clean_up_is_held_back" \
  "tests/unit/accept/test_w2_96_run2.py::test_w2_96_r9_r12_a_signal_during_the_run_then_more_during_the_clean_up" \
  "tests/unit/accept/test_w2_96_run2.py::test_w2_96_r9_r12_presses_until_gov_ends_never_kill_it" \
  "tests/unit/accept/test_w2_96_run2.py::test_w2_96_r9_r12_ctrl_c_during_the_run_stops_it" 2>&1 | tail -5
echo "--- src/ and tests/unit/accept against the base 2f98aecbc:"
git diff --stat 2f98aecbc HEAD -- src tests/unit/accept | tail -2
