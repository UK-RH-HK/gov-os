#!/usr/bin/env bash
# re-run the outside reds alone, once, on the head (load-sensitive check)
cd /home/usain/gov-os-worktrees/W2-115 || exit 2
export HOME=/home/usain/gov-os-worktrees/W2-115/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-115/src
bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest -q -p no:cacheprovider -o tmp_path_retention_policy=failed \
  "tests/unit/accept/test_w2_96_review3.py::test_w2_96_r14_a_stopped_run_keeps_128_plus_the_signal" \
  "tests/unit/accept/test_w2_96_review4.py::test_w2_96_r16_an_own_session_orphan_is_reaped_before_a_stopped_run_cleans_up" \
  "tests/unit/accept/test_w2_96_run2.py" \
  "tests/unit/orchestration/test_w2_149_setup_a.py::test_trees_leave_out_the_briefs_and_set_up_a_also_the_guard" \
  "tests/unit/close/test_w2_115_select.py::test_s3_select_prints_the_set_and_options" 2>&1 | tail -40
echo "exit ${PIPESTATUS[0]}"
