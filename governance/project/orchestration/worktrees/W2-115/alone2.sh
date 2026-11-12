#!/usr/bin/env bash
# the outside reds alone, once, each tree: the head (W2-115) and the code without the change (W2-115-tests)
export HOME=/home/usain/gov-os-worktrees/W2-115/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local
for tree in /home/usain/gov-os-worktrees/W2-115 /home/usain/gov-os-worktrees/W2-115-tests; do
  echo "##### $tree $(git -C $tree rev-parse --short=12 HEAD)"
  cd "$tree" || exit 2
  PYTHONPATH=$tree/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh \
    python3 -m pytest -q -p no:cacheprovider -o tmp_path_retention_policy=failed --timeout 150 \
    "tests/unit/accept/test_w2_96_review3.py::test_w2_96_r14_a_stopped_run_keeps_128_plus_the_signal" \
    "tests/unit/accept/test_w2_96_review4.py::test_w2_96_r16_an_own_session_orphan_is_reaped_before_a_stopped_run_cleans_up" \
    "tests/unit/accept/test_w2_96_run2.py::test_w2_96_r9_r12_ctrl_c_during_the_run_stops_it" \
    "tests/unit/orchestration/test_w2_149_setup_a.py::test_trees_leave_out_the_briefs_and_set_up_a_also_the_guard" 2>&1 | tail -15
  echo "exit ${PIPESTATUS[0]}"
done
