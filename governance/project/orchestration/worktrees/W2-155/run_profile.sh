#!/usr/bin/env bash
W=/tmp/w2-155-prof/run-$(date +%H%M%S)
mkdir -p "$W"
cd /tmp/w2-155-prof
env -u GOV_ROLE -u GOV_TICKET TMPDIR=/tmp/w2-155-prof PYTHONUSERBASE=/home/usain/.local HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 GIT_CONFIG_NOSYSTEM=1 \
  PYTHONPATH=/home/usain/gov-os-worktrees/W2-155/src \
  bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh \
  python3 /home/usain/gov-os-worktrees/W2-155/.gov-runtime/scratch/profile_warm.py "$W" "$@" > "$W/stdout.txt" 2> "$W/stderr.txt"
echo "exit=$? dir=$W"
