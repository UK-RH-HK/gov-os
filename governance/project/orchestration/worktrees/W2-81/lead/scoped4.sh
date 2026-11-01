#!/bin/bash
# Lead's scoped verification, round 3, on head 165d3057146a (DEC-952, DEC-968): disk gate, then scoped_run.py.
cd /home/usain/gov-os-worktrees/W2-81 || exit 9
bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/disk_gate.sh > /home/usain/gov-os-worktrees/W2-81/.gov-runtime/scratch/lead/log/scoped-4.disk 2>&1 || { echo 8 > /home/usain/gov-os-worktrees/W2-81/.gov-runtime/scratch/lead/log/scoped-4.exit; exit 8; }
cp /home/usain/gov-os-worktrees/W2-81/.gov-runtime/scratch/lead/log/select-4.json /home/usain/gov-os-worktrees/W2-81/.gov-runtime/scratch/lead/log/select.json
date > /home/usain/gov-os-worktrees/W2-81/.gov-runtime/scratch/lead/log/scoped-4.start
TMPDIR=/tmp/gov-os-lead-W2-81 python3 /home/usain/gov-os-worktrees/W2-81/.gov-runtime/scratch/lead/scoped_run.py
echo $? > /home/usain/gov-os-worktrees/W2-81/.gov-runtime/scratch/lead/log/scoped-4.exit
date >> /home/usain/gov-os-worktrees/W2-81/.gov-runtime/scratch/lead/log/scoped-4.start
