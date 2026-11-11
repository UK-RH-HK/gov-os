#!/usr/bin/env bash
# Rebuild this tree's store in a heavy slot; exit code to log/rebuild.exit
L=/home/usain/gov-os-worktrees/W2-05/.gov-runtime/scratch/lead/log
mkdir -p /tmp/gov-os-lead-W2-05
rm -f "$L/rebuild.exit"
env TMPDIR=/tmp/gov-os-lead-W2-05 PYTHONPATH=/home/usain/gov-os-worktrees/W2-05/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/rebuild_slot.sh /home/usain/gov-os-worktrees/W2-05 > "$L/rebuild.log" 2>&1
echo $? > "$L/rebuild.exit"
