#!/usr/bin/env bash
# Re-run the eight load-sensitive reds of lead_verify (head 499543a836d3) alone, once, serially.
set -u
T=/home/usain/gov-os-worktrees/W2-181
mkdir -p /tmp/w2-181-rerun "$T/.gov-runtime/scratch/empty-home"
cd "$T" || exit 2
env HOME="$T/.gov-runtime/scratch/empty-home" TMPDIR=/tmp/w2-181-rerun PYTHONUSERBASE=/home/usain/.local PYTHONPATH="$T/src" \
  bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh \
  python3 -m pytest -q -p no:cacheprovider -o tmp_path_retention_policy=failed \
  "tests/unit/accept/test_w2_96_review3.py::test_w2_96_r14_a_stopped_run_keeps_128_plus_the_signal" \
  "tests/unit/accept/test_w2_96_review4.py::test_w2_96_r16_an_own_session_orphan_is_reaped_before_a_stopped_run_cleans_up" \
  "tests/unit/resources/test_w2_157_backstop.py::test_s1_below_then_above_the_limit_pauses_at_the_second_reading" \
  "tests/unit/resources/test_w2_157_backstop.py::test_l5b_the_own_group_is_stopped_after_every_other_group_the_trip_line_and_the_item" \
  "tests/unit/accept/test_w2_96_run2.py::test_w2_96_r9_r12_a_signal_during_the_clean_up_is_held_back" \
  "tests/unit/accept/test_w2_96_run2.py::test_w2_96_r9_r12_a_signal_during_the_run_then_more_during_the_clean_up" \
  "tests/unit/accept/test_w2_96_run2.py::test_w2_96_r9_r12_presses_until_gov_ends_never_kill_it" \
  "tests/unit/accept/test_w2_96_run2.py::test_w2_96_r9_r12_ctrl_c_during_the_run_stops_it" 2>&1 | tail -15
