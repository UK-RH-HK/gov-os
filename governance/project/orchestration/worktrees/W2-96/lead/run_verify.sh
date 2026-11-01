#!/bin/bash
# The scoped run: wait for the load gate (DEC-961), check the disk gate (DEC-898), then verify.py (parallel, then serial).
cd /home/usain/gov-os-worktrees/W2-96 || exit 9
until python3 -c "import os; l=os.getloadavg(); exit(0 if min(l[0], l[2]) < os.cpu_count() else 1)"; do sleep 60; done
bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/disk_gate.sh > /home/usain/gov-os-worktrees/W2-96/.gov-runtime/scratch/lead/log/disk-gate.txt 2>&1 || exit 8
date -u +%FT%TZ > /home/usain/gov-os-worktrees/W2-96/.gov-runtime/scratch/lead/log/verify.start
python3 /home/usain/gov-os-worktrees/W2-96/.gov-runtime/scratch/lead/verify.py both
echo done > /home/usain/gov-os-worktrees/W2-96/.gov-runtime/scratch/lead/log/verify.done
