#!/bin/bash
# Red check (step 2): the designer's tests on the ticket's base (the tests worktree = 4c064bab02b4 + the tests).
cd /home/usain/gov-os-worktrees/W2-11-tests || exit 99
until python3 -c "import os; l=os.getloadavg(); exit(0 if min(l[0], l[2]) < os.cpu_count() else 1)"; do sleep 60; done
PYTHONPATH=/home/usain/gov-os-worktrees/W2-11-tests/src python3 -c "import gov; print(gov.__file__)" > /home/usain/gov-os-worktrees/W2-11/.gov-runtime/scratch/lead/log/red-gov-file.txt
TMPDIR=/tmp/gov-os-lead-W2-11 PYTHONPATH=/home/usain/gov-os-worktrees/W2-11-tests/src python3 -m pytest tests/acceptance/W2-11 tests/acceptance/W1-35 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rfEs --junitxml=/home/usain/gov-os-worktrees/W2-11/.gov-runtime/scratch/lead/log/red.xml > /home/usain/gov-os-worktrees/W2-11/.gov-runtime/scratch/lead/log/red.txt 2>&1
echo $? > /home/usain/gov-os-worktrees/W2-11/.gov-runtime/scratch/lead/log/red.exit
