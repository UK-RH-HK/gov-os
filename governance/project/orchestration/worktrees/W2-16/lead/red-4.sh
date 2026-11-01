#!/bin/bash
# The lead's red check of round 3: the merged tests against the ticket's base code (the tests worktree's src/).
until python3 -c "import os; l=os.getloadavg(); exit(0 if min(l[0], l[2]) < os.cpu_count() else 1)"; do sleep 60; done
mkdir -p /home/usain/gov-os-worktrees/W2-16/.gov-runtime/scratch/lead/log/red-4
cd /home/usain/gov-os-worktrees/W2-16-tests || exit 9
PYTHONPATH=/home/usain/gov-os-worktrees/W2-16-tests/src python3 -c "import gov; print(gov.__file__)" > /home/usain/gov-os-worktrees/W2-16/.gov-runtime/scratch/lead/log/red-4/gov-file.txt
PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH TMPDIR=/tmp/gov-os-lead-W2-16 PYTHONPATH=/home/usain/gov-os-worktrees/W2-16-tests/src \
  python3 -m pytest tests/acceptance/W2-16 -q -p no:cacheprovider -rfEs -o tmp_path_retention_policy=failed \
  --junitxml=/home/usain/gov-os-worktrees/W2-16/.gov-runtime/scratch/lead/log/red-4/red.xml \
  > /home/usain/gov-os-worktrees/W2-16/.gov-runtime/scratch/lead/log/red-4/red.txt 2>&1
echo $? > /home/usain/gov-os-worktrees/W2-16/.gov-runtime/scratch/lead/log/red-4/red.exit
