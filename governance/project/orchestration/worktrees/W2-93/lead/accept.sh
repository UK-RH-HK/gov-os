#!/usr/bin/env bash
cd /home/usain/gov-os-worktrees/W2-93
export TMPDIR=/tmp/w2-93-lead PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-93/src
bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh gov accept W2-93 --root /home/usain/gov-os-worktrees/W2-93 > /home/usain/gov-os-worktrees/W2-93/.gov-runtime/scratch/lead/log/accept-2.txt 2>&1
echo $? > /home/usain/gov-os-worktrees/W2-93/.gov-runtime/scratch/lead/log/accept-2.exit
