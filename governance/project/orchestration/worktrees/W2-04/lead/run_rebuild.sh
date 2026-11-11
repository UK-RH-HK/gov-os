#!/usr/bin/env bash
# The tree's store rebuild in a heavy-job slot, with an exit-code file (lead, DAEO-u4oz review run).
L=/home/usain/gov-os-worktrees/W2-04/.gov-runtime/scratch/lead/log
rm -f "$L/rebuild.exit"
env TMPDIR=/tmp/gov-os-lead-W2-04 PYTHONPATH=/home/usain/gov-os-worktrees/W2-04/src \
  bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/rebuild_slot.sh \
  /home/usain/gov-os-worktrees/W2-04 > "$L/rebuild.log" 2>&1
echo $? > "$L/rebuild.exit"
