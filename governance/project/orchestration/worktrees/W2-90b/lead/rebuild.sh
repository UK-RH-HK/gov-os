#!/usr/bin/env bash
cd /home/usain/gov-os-worktrees/W2-90b || exit 9
PYTHONPATH=/home/usain/gov-os-worktrees/W2-90b/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/rebuild_slot.sh /home/usain/gov-os-worktrees/W2-90b > /home/usain/gov-os-worktrees/W2-90b/.gov-runtime/scratch/lead/log/rebuild-2.json 2> /home/usain/gov-os-worktrees/W2-90b/.gov-runtime/scratch/lead/log/rebuild-2.err
echo $? > /home/usain/gov-os-worktrees/W2-90b/.gov-runtime/scratch/lead/log/rebuild-2.exit
