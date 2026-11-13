#!/usr/bin/env bash
# run 3: the six W2-96 reds alone, once, on w2/integrate's head (0aec6e10c, a detached worktree) and on this head
export HOME=/home/usain/gov-os-worktrees/W2-115/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local
export TMPDIR=/tmp/gov-os-lead-W2-115-alone3
mkdir -p "$TMPDIR"
git -C /home/usain/gov-os-worktrees/W2-115 worktree add --detach /home/usain/gov-os-worktrees/W2-115-base 0aec6e10c >/dev/null 2>&1
for tree in /home/usain/gov-os-worktrees/W2-115-base /home/usain/gov-os-worktrees/W2-115; do
  echo "##### $tree $(git -C $tree rev-parse --short=12 HEAD)"
  cd "$tree" || exit 2
  PYTHONPATH=$tree/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh \
    python3 -m pytest -q -p no:cacheprovider -o tmp_path_retention_policy=failed --timeout 150 \
    "tests/unit/accept/test_w2_96_review3.py::test_w2_96_r14_a_stopped_run_keeps_128_plus_the_signal[True-2]" \
    "tests/unit/accept/test_w2_96_review4.py::test_w2_96_r16_an_own_session_orphan_is_reaped_before_a_stopped_run_cleans_up[2]" \
    "tests/unit/accept/test_w2_96_run2.py::test_w2_96_r9_r12_a_signal_during_the_clean_up_is_held_back[signals0]" \
    "tests/unit/accept/test_w2_96_run2.py::test_w2_96_r9_r12_a_signal_during_the_run_then_more_during_the_clean_up[2-more0]" \
    "tests/unit/accept/test_w2_96_run2.py::test_w2_96_r9_r12_presses_until_gov_ends_never_kill_it[kinds0]" \
    "tests/unit/accept/test_w2_96_run2.py::test_w2_96_r9_r12_ctrl_c_during_the_run_stops_it" 2>&1 | tail -10
  echo "exit ${PIPESTATUS[0]}"
done
git -C /home/usain/gov-os-worktrees/W2-115 worktree remove --force /home/usain/gov-os-worktrees/W2-115-base
echo done
