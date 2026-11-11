#!/bin/bash
# r6 rebuild, background, exit code to a file
LOG=/home/usain/gov-os-worktrees/W2-11/.gov-runtime/scratch/lead/log/rebuild-r6.log
EXITF=/home/usain/gov-os-worktrees/W2-11/.gov-runtime/scratch/lead/log/rebuild-r6.exit
rm -f "$EXITF"
env TMPDIR=/tmp/gov-os-lead-W2-11 PYTHONPATH=/home/usain/gov-os-worktrees/W2-11/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/rebuild_slot.sh /home/usain/gov-os-worktrees/W2-11 > "$LOG" 2>&1
echo $? > "$EXITF"
