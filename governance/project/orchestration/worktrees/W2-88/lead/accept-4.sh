#!/usr/bin/env bash
# gov accept W2-88 through the heavy slot, TMPDIR outside the repository and ~/gov-os-runs
mkdir -p /tmp/gov-os-lead-W2-88 /home/usain/gov-os-worktrees/W2-88/.gov-runtime/scratch/empty-home
cd /home/usain/gov-os-worktrees/W2-88 || exit 2
env TMPDIR=/tmp/gov-os-lead-W2-88 PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-88/src \
  bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh \
  gov accept W2-88 --root /home/usain/gov-os-worktrees/W2-88 \
  > /home/usain/gov-os-worktrees/W2-88/.gov-runtime/scratch/lead/log/accept-4.txt 2>&1
rc=$?
echo "$rc" > /home/usain/gov-os-worktrees/W2-88/.gov-runtime/scratch/lead/log/accept-4.exit
exit "$rc"
