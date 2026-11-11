#!/usr/bin/env bash
# Re-run the six W2-96 reds of the scoped run alone, once (load-sensitive check), through the heavy slot.
L=/home/usain/gov-os-worktrees/W2-175/.gov-runtime/scratch/lead/log
cd /home/usain/gov-os-worktrees/W2-175 || exit 2
env HOME=/home/usain/gov-os-worktrees/W2-175/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local \
  PYTHONPATH=/home/usain/gov-os-worktrees/W2-175/src TMPDIR=/tmp/gov-os-lead-W2-175 \
  bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh \
  python3 -m pytest -q -p no:cacheprovider -o tmp_path_retention_policy=failed \
  "tests/unit/accept/test_w2_96_review3.py::test_w2_96_r14_a_stopped_run_keeps_128_plus_the_signal[True-2]" \
  "tests/unit/accept/test_w2_96_review4.py::test_w2_96_r16_an_own_session_orphan_is_reaped_before_a_stopped_run_cleans_up[2]" \
  "tests/unit/accept/test_w2_96_run2.py::test_w2_96_r9_r12_a_signal_during_the_clean_up_is_held_back[signals0]" \
  "tests/unit/accept/test_w2_96_run2.py::test_w2_96_r9_r12_a_signal_during_the_run_then_more_during_the_clean_up[2-more0]" \
  "tests/unit/accept/test_w2_96_run2.py::test_w2_96_r9_r12_presses_until_gov_ends_never_kill_it[kinds0]" \
  "tests/unit/accept/test_w2_96_run2.py::test_w2_96_r9_r12_ctrl_c_during_the_run_stops_it" \
  --junitxml=$L/w296-alone.xml > $L/w296-alone.txt 2>&1
echo $? > $L/w296-alone.exit
