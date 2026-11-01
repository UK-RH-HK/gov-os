#!/bin/bash
# Step 4, stage A: the full rebuild on the final head, with no worker running (DEC-719, DEC-732), one at a time.
cd /home/usain/gov-os-worktrees/W2-11 || exit 99
date -u +%FT%TZ > /home/usain/gov-os-worktrees/W2-11/.gov-runtime/scratch/lead/log/va-start.txt
until python3 -c "import os; l=os.getloadavg(); exit(0 if min(l[0], l[2]) < os.cpu_count() else 1)"; do sleep 60; done
bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/disk_gate.sh > /home/usain/gov-os-worktrees/W2-11/.gov-runtime/scratch/lead/log/va-disk.txt 2>&1
date -u +%FT%TZ >> /home/usain/gov-os-worktrees/W2-11/.gov-runtime/scratch/lead/log/va-start.txt
TMPDIR=/tmp/gov-os-lead-W2-11 PYTHONPATH=/home/usain/gov-os-worktrees/W2-11/src flock /tmp/gov-os-rebuild.lock python3 -m gov.cli.main rebuild --json > /home/usain/gov-os-worktrees/W2-11/.gov-runtime/scratch/lead/log/rebuild-2.json 2> /home/usain/gov-os-worktrees/W2-11/.gov-runtime/scratch/lead/log/rebuild-2.err
echo $? > /home/usain/gov-os-worktrees/W2-11/.gov-runtime/scratch/lead/log/rebuild-2.exit
