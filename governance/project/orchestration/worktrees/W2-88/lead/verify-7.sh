#!/bin/bash
# The lead's verify for run 7: rebuild, gov accept (results), then lead_verify (scoped run), in order.
cd /home/usain/gov-os-worktrees/W2-88 || exit 9
L=/home/usain/gov-os-worktrees/W2-88/.gov-runtime/scratch/lead/log
git rev-parse HEAD > "$L/verify-7.head"
env PYTHONPATH=/home/usain/gov-os-worktrees/W2-88/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/rebuild_slot.sh /home/usain/gov-os-worktrees/W2-88 > "$L/rebuild-7b.txt" 2>&1
echo $? > "$L/rebuild-7b.exit"
mkdir -p /home/usain/gov-os-runs/W2-88/tmp-lead
env TMPDIR=/home/usain/gov-os-runs/W2-88/tmp-lead PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-88/src \
  bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh \
  gov accept W2-88 --root /home/usain/gov-os-worktrees/W2-88 > "$L/accept-7.txt" 2>&1
echo $? > "$L/accept-7.exit"
bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/lead_verify.sh /home/usain/gov-os-worktrees/W2-88 W2-88 DAEO-2bdu > "$L/verify-7.txt" 2>&1
echo $? > "$L/verify-7.exit"
