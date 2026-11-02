#!/bin/bash
# Lead's scoped verification, records-only repair, on head e78e6af7530d (DEC-952, DEC-968): disk gate, then scoped_run.py.
cd /home/usain/gov-os-worktrees/W2-81 || exit 9
bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/disk_gate.sh > /home/usain/gov-os-worktrees/W2-81/.gov-runtime/scratch/lead/log/scoped-5.disk 2>&1 || { echo 8 > /home/usain/gov-os-worktrees/W2-81/.gov-runtime/scratch/lead/log/scoped-5.exit; exit 8; }
cp /home/usain/gov-os-worktrees/W2-81/.gov-runtime/scratch/lead/log/select-5.json /home/usain/gov-os-worktrees/W2-81/.gov-runtime/scratch/lead/log/select.json
rm -f /home/usain/gov-os-worktrees/W2-81/.gov-runtime/scratch/lead/log/parallel.exit /home/usain/gov-os-worktrees/W2-81/.gov-runtime/scratch/lead/log/serial.exit
date > /home/usain/gov-os-worktrees/W2-81/.gov-runtime/scratch/lead/log/scoped-5.start
TMPDIR=/tmp/gov-os-lead-W2-81 PYTHONPATH=/home/usain/gov-os-worktrees/W2-81/src python3 /home/usain/gov-os-worktrees/W2-81/.gov-runtime/scratch/lead/scoped_run.py
echo $? > /home/usain/gov-os-worktrees/W2-81/.gov-runtime/scratch/lead/log/scoped-5.exit
date >> /home/usain/gov-os-worktrees/W2-81/.gov-runtime/scratch/lead/log/scoped-5.start
