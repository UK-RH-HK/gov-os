#!/usr/bin/env bash
# Runs W2-96's six signal cases alone, on w2/integrate's head (a detached worktree) and on W2-178's head.
set -u
T=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools
LOG=/home/usain/gov-os-worktrees/W2-178/.gov-runtime/scratch/lead/log
B=/home/usain/gov-os-worktrees/W2-178-base
git -C /home/usain/gov-os-worktrees/W2-178 worktree add --detach "$B" w2/integrate > /dev/null 2>&1 || true
git -C "$B" log --oneline -1
CASES=(tests/unit/accept/test_w2_96_review3.py tests/unit/accept/test_w2_96_review4.py tests/unit/accept/test_w2_96_run2.py)
for tree in "$B" /home/usain/gov-os-worktrees/W2-178; do
  name=$(basename "$tree")
  mkdir -p "$tree/.gov-runtime/scratch/empty-home" "/tmp/w2-178-lead-$name"
  ( cd "$tree" && env HOME="$tree/.gov-runtime/scratch/empty-home" PYTHONUSERBASE=/home/usain/.local TMPDIR="/tmp/w2-178-lead-$name" \
      PYTHONPATH="$tree/src" bash "$T/heavy_slot.sh" python3 -m pytest "${CASES[@]}" -q -p no:cacheprovider \
      -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit" \
      > "$LOG/w296-$name.txt" 2>&1 )
  echo "$name: $(tail -n 1 "$LOG/w296-$name.txt")"
  grep -E "^FAILED" "$LOG/w296-$name.txt" | cut -c1-160
done
git -C /home/usain/gov-os-worktrees/W2-178 worktree remove --force "$B"
