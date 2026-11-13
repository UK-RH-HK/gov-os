#!/bin/bash
cd /home/usain/gov-os-worktrees/W2-155
mkdir -p /tmp/gov-launch-t6q0frtj/claude-1000/w2-155-eng
env TMPDIR=/tmp/gov-launch-t6q0frtj/claude-1000/w2-155-eng PYTHONUSERBASE=/home/usain/.local HOME=/home/usain/gov-os-worktrees/W2-155/.gov-runtime/scratch/empty-home PYTHONPATH=/home/usain/gov-os-worktrees/W2-155/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest "$@" -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"
