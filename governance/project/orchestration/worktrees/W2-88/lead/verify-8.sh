#!/bin/bash
# The lead's verify for run 7: rebuild, gov accept (results), then lead_verify (scoped run), in order.
cd /home/usain/gov-os-worktrees/W2-88 || exit 9
L=/home/usain/gov-os-worktrees/W2-88/.gov-runtime/scratch/lead/log
git rev-parse HEAD > "$L/verify-8.head"
env PYTHONPATH=/home/usain/gov-os-worktrees/W2-88/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/rebuild_slot.sh /home/usain/gov-os-worktrees/W2-88 > "$L/rebuild-8.txt" 2>&1
echo $? > "$L/rebuild-8.exit"
mkdir -p /home/usain/gov-os-runs/W2-88/tmp-lead
env TMPDIR=/home/usain/gov-os-runs/W2-88/tmp-lead PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-88/src \
  bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh \
  gov accept W2-88 --root /home/usain/gov-os-worktrees/W2-88 > "$L/accept-8.txt" 2>&1
echo $? > "$L/accept-8.exit"
bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/lead_verify.sh /home/usain/gov-os-worktrees/W2-88 W2-88 DAEO-2bdu > "$L/verify-8.txt" 2>&1
echo $? > "$L/verify-8.exit"
bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/wait_for.sh /home/usain/gov-os-worktrees/W2-88/.gov-runtime/scratch/lead/log/verify/verify.exit > "$L/verify-8.wait1" 2>&1
until [ -f /home/usain/gov-os-worktrees/W2-88/.gov-runtime/scratch/lead/log/verify/verify.exit ]; do bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/wait_for.sh /home/usain/gov-os-worktrees/W2-88/.gov-runtime/scratch/lead/log/verify/verify.exit >> "$L/verify-8.wait1" 2>&1; done
sed 's/alone-7/alone-8/g' /home/usain/gov-os-worktrees/W2-88/.gov-runtime/scratch/lead/alone-7.sh > /home/usain/gov-os-worktrees/W2-88/.gov-runtime/scratch/lead/alone-8.sh
bash /home/usain/gov-os-worktrees/W2-88/.gov-runtime/scratch/lead/alone-8.sh
