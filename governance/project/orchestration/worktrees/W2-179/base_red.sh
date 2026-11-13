#!/usr/bin/env bash
# The base-red rule: run W2-96's six failing unit cases on w2/integrate's head in a temporary detached worktree.
set -u
T=/home/usain/gov-os-worktrees/W2-179-base
OUT=/home/usain/gov-os-worktrees/W2-179/.gov-runtime/scratch/lead/log/base-red.txt
HS=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh
git -C /home/usain/gov-os-worktrees/W2-179 worktree add --detach "$T" w2/integrate > /dev/null 2>&1 || { echo "worktree add failed" > "$OUT"; exit 2; }
mkdir -p "$T/.gov-runtime/scratch/empty-home"
{
  echo "w2/integrate head $(git -C "$T" rev-parse HEAD | cut -c1-12)"
  cd "$T" && env HOME="$T/.gov-runtime/scratch/empty-home" PYTHONUSERBASE=/home/usain/.local TMPDIR=/tmp PYTHONPATH="$T/src" \
    bash "$HS" python3 -m pytest -q -p no:cacheprovider -o tmp_path_retention_policy=failed \
    "tests/unit/accept/test_w2_96_review3.py::test_w2_96_r14_a_stopped_run_keeps_128_plus_the_signal[True-2]" \
    "tests/unit/accept/test_w2_96_review4.py::test_w2_96_r16_an_own_session_orphan_is_reaped_before_a_stopped_run_cleans_up[2]" \
    "tests/unit/accept/test_w2_96_run2.py::test_w2_96_r9_r12_a_signal_during_the_clean_up_is_held_back[signals0]" \
    "tests/unit/accept/test_w2_96_run2.py::test_w2_96_r9_r12_a_signal_during_the_run_then_more_during_the_clean_up[2-more0]" \
    "tests/unit/accept/test_w2_96_run2.py::test_w2_96_r9_r12_presses_until_gov_ends_never_kill_it[kinds0]" \
    "tests/unit/accept/test_w2_96_run2.py::test_w2_96_r9_r12_ctrl_c_during_the_run_stops_it" 2>&1 | grep -E "^(FAILED|PASSED|ERROR)|passed|failed"
} > "$OUT" 2>&1
cd /home/usain/gov-os-worktrees/W2-179 && git worktree remove --force "$T"
cat "$OUT"
