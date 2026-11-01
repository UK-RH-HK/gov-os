#!/bin/bash
# Red check of review 3's cases on run 2's code (the tests worktree), behind the load gate (DEC-961).
until python3 -c "import os; l=os.getloadavg(); exit(0 if min(l[0], l[2]) < os.cpu_count() else 1)"; do sleep 30; done
date -u +%FT%TZ > /home/usain/gov-os-worktrees/W2-96/.gov-runtime/scratch/lead/log/red-r3.start
python3 /home/usain/gov-os-worktrees/W2-96/.gov-runtime/scratch/lead/red_check.py /home/usain/gov-os-worktrees/W2-96-tests /home/usain/gov-os-worktrees/W2-96/.gov-runtime/scratch/lead/log/red-r3.xml > /home/usain/gov-os-worktrees/W2-96/.gov-runtime/scratch/lead/log/red-r3.out 2>&1
echo $? > /home/usain/gov-os-worktrees/W2-96/.gov-runtime/scratch/lead/log/red-r3.exit
