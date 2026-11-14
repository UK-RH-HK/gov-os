#!/usr/bin/env bash
# Run 4: the 81 acceptance cases through heavy_slot, then gov accept W2-130.
cd /home/usain/gov-os-worktrees/W2-130 || exit 2
mkdir -p /home/usain/gov-os-runs/w2-130-tmp
export TMPDIR=/home/usain/gov-os-runs/w2-130-tmp
env PYTHONUSERBASE=/home/usain/.local HOME=/home/usain/gov-os-worktrees/W2-130/.gov-runtime/scratch/empty-home PYTHONPATH=/home/usain/gov-os-worktrees/W2-130/src \
  bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh \
  python3 -m pytest tests/acceptance/W2-130 -q -p no:cacheprovider -o tmp_path_retention_policy=failed \
  --junitxml=/home/usain/gov-os-worktrees/W2-130/.gov-runtime/scratch/lead/log/junit-r4.xml \
  > /home/usain/gov-os-worktrees/W2-130/.gov-runtime/scratch/lead/log/pytest-r4.out 2>&1
echo "pytest exit $?" >> /home/usain/gov-os-worktrees/W2-130/.gov-runtime/scratch/lead/log/pytest-r4.out
env PYTHONUSERBASE=/home/usain/.local bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh \
  gov accept W2-130 --root /home/usain/gov-os-worktrees/W2-130 \
  > /home/usain/gov-os-worktrees/W2-130/.gov-runtime/scratch/lead/log/accept-r4.out 2>&1
echo "accept exit $?" >> /home/usain/gov-os-worktrees/W2-130/.gov-runtime/scratch/lead/log/accept-r4.out
