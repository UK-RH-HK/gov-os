#!/bin/bash
# The worktree's first store, built by this worktree's code (DEC-732, DEC-943), under the rebuild lock.
cd /home/usain/gov-os-worktrees/W2-86 || exit 9
until python3 -c "import os; l=os.getloadavg(); exit(0 if min(l[0], l[2]) < os.cpu_count() else 1)"; do sleep 60; done
bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/disk_gate.sh || exit 8
PYTHONPATH=/home/usain/gov-os-worktrees/W2-86/src flock /tmp/gov-os-rebuild.lock python3 -m gov.cli.main rebuild --json > /home/usain/gov-os-worktrees/W2-86/.gov-runtime/scratch/lead/log/rebuild-wt-1.json 2> /home/usain/gov-os-worktrees/W2-86/.gov-runtime/scratch/lead/log/rebuild-wt-1.err
echo $? > /home/usain/gov-os-worktrees/W2-86/.gov-runtime/scratch/lead/log/rebuild-wt-1.exit
