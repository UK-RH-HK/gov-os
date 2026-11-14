#!/usr/bin/env bash
cd /home/usain/gov-os-worktrees/W2-94-fix || exit 2
mkdir -p /home/usain/gov-os-worktrees/W2-94-fix/.gov-runtime/scratch/empty-home /home/usain/gov-os-worktrees/W2-94-fix/.gov-runtime/scratch/tmp
env HOME=/home/usain/gov-os-worktrees/W2-94-fix/.gov-runtime/scratch/empty-home TMPDIR=/home/usain/gov-os-worktrees/W2-94-fix/.gov-runtime/scratch/tmp \
  PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-94-fix/src \
  bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh \
  python3 -m pytest tests/acceptance/W2-94/test_w2_94_s13_counts_fix.py -q -p no:cacheprovider \
  -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit" --tb=line -rf \
  > /home/usain/gov-os-worktrees/W2-94-fix/.gov-runtime/scratch/lead/red-s13.txt 2>&1
echo "rc=$?" >> /home/usain/gov-os-worktrees/W2-94-fix/.gov-runtime/scratch/lead/red-s13.txt
