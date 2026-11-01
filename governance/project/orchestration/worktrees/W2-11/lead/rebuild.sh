#!/bin/bash
# The worktree's store, built with this worktree's own code (DEC-732, DEC-979), one rebuild at a time (DEC-939 item 2).
cd /home/usain/gov-os-worktrees/W2-11 || exit 99
until python3 -c "import os; l=os.getloadavg(); exit(0 if min(l[0], l[2]) < os.cpu_count() else 1)"; do sleep 60; done
TMPDIR=/tmp/gov-os-lead-W2-11 PYTHONPATH=/home/usain/gov-os-worktrees/W2-11/src flock /tmp/gov-os-rebuild.lock python3 -m gov.cli.main rebuild --json > /home/usain/gov-os-worktrees/W2-11/.gov-runtime/scratch/lead/log/rebuild-1.json 2> /home/usain/gov-os-worktrees/W2-11/.gov-runtime/scratch/lead/log/rebuild-1.err
echo $? > /home/usain/gov-os-worktrees/W2-11/.gov-runtime/scratch/lead/log/rebuild-1.exit
