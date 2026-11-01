#!/bin/bash
# lat_prep.sh: clone the two dev tiers and rebuild each with this worktree's code and the real embedder, in a heavy slot.
cd /tmp || exit 9
L=/home/usain/gov-os-worktrees/W2-13/.gov-runtime/scratch/lead
T=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 TMPDIR=/tmp/gov-os-lead-W2-13
PYTHONPATH=/home/usain/gov-os-worktrees/W2-13/src:/home/usain/gov-os-worktrees/W2-13/tests/acceptance/W2-13 python3 /home/usain/gov-os-worktrees/W2-13/.gov-runtime/scratch/lead/lat_prep.py > /home/usain/gov-os-worktrees/W2-13/.gov-runtime/scratch/lead/log/lat-prep.txt 2>&1 || { echo 1 > /home/usain/gov-os-worktrees/W2-13/.gov-runtime/scratch/lead/log/lat-prep.exit; exit 1; }
rc=0
for tier in a-dev b-dev; do
  PYTHONPATH=/home/usain/gov-os-worktrees/W2-13/src bash $T/rebuild_slot.sh /tmp/gov-os-lead-W2-13/lat-tiers/$tier >> /home/usain/gov-os-worktrees/W2-13/.gov-runtime/scratch/lead/log/lat-prep.txt 2>&1 || rc=$?
done
echo $rc > /home/usain/gov-os-worktrees/W2-13/.gov-runtime/scratch/lead/log/lat-prep.exit
