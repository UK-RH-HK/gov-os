#!/bin/bash
# Lead's full rebuild of this worktree's store (DEC-719, DEC-732), round 3 after batch 7, in a heavy-job slot (DEC-1001).
cd /home/usain/gov-os-worktrees/W2-81 || exit 9
bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/disk_gate.sh > /home/usain/gov-os-worktrees/W2-81/.gov-runtime/scratch/lead/log/rebuild-4.disk 2>&1 || { echo 8 > /home/usain/gov-os-worktrees/W2-81/.gov-runtime/scratch/lead/log/rebuild-4.exit; exit 8; }
date > /home/usain/gov-os-worktrees/W2-81/.gov-runtime/scratch/lead/log/rebuild-4.start
PYTHONPATH=/home/usain/gov-os-worktrees/W2-81/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/rebuild_slot.sh /home/usain/gov-os-worktrees/W2-81 > /home/usain/gov-os-worktrees/W2-81/.gov-runtime/scratch/lead/log/rebuild-4.json 2> /home/usain/gov-os-worktrees/W2-81/.gov-runtime/scratch/lead/log/rebuild-4.err
echo $? > /home/usain/gov-os-worktrees/W2-81/.gov-runtime/scratch/lead/log/rebuild-4.exit
date >> /home/usain/gov-os-worktrees/W2-81/.gov-runtime/scratch/lead/log/rebuild-4.start
