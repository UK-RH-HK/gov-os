#!/bin/bash
# The full store rebuild of this worktree, with this worktree's code, one at a time on the machine (DEC-939 item 2).
cd /home/usain/gov-os-worktrees/W2-105 || exit 9
export TMPDIR=/tmp/gov-os-lead-W2-105
until python3 -c "import os; l=os.getloadavg(); exit(0 if min(l[0], l[2]) < os.cpu_count() else 1)"; do sleep 60; done
bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/disk_gate.sh || exit 8
PYTHONPATH=/home/usain/gov-os-worktrees/W2-105/src flock /tmp/gov-os-rebuild.lock python3 -m gov.cli.main rebuild --json > /home/usain/gov-os-worktrees/W2-105/.gov-runtime/scratch/lead/log/rebuild-$1.json 2>&1
echo $? > /home/usain/gov-os-worktrees/W2-105/.gov-runtime/scratch/lead/log/rebuild-$1.exit
