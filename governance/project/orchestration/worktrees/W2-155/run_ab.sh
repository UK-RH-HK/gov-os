#!/usr/bin/env bash
O=/tmp/w2-155-prof/ab-$(date +%H%M%S)
mkdir -p "$O"
cd /tmp/w2-155-prof
env -u GOV_ROLE -u GOV_TICKET TMPDIR=/tmp/w2-155-prof PYTHONUSERBASE=/home/usain/.local HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 GIT_CONFIG_NOSYSTEM=1 \
  PYTHONPATH=/home/usain/gov-os-worktrees/W2-155/src \
  bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh \
  bash /home/usain/gov-os-worktrees/W2-155/.gov-runtime/scratch/ab_inner.sh "$O" > "$O/slot.txt" 2>&1
echo "exit=$? dir=$O"
cat "$O/ab.txt"
