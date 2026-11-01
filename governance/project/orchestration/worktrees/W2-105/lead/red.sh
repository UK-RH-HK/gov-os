#!/bin/bash
# Step 2's red check: the merged tests against the ticket's base. The tests worktree is the base (1f0bf2836dc2) with
# the tests branch's two commits, so it is that state, with no clone.
cd /home/usain/gov-os-worktrees/W2-105-tests || exit 9
export TMPDIR=/tmp/gov-os-lead-W2-105
L=/home/usain/gov-os-worktrees/W2-105/.gov-runtime/scratch/lead/log
until python3 -c "import os; l=os.getloadavg(); exit(0 if min(l[0], l[2]) < os.cpu_count() else 1)"; do sleep 60; done
PYTHONPATH=/home/usain/gov-os-worktrees/W2-105-tests/src python3 -c "import gov; print(gov.__file__)" > $L/red-govfile.txt 2>&1
PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-105-tests/src python3 -m pytest tests/acceptance/W2-105 tests/acceptance/W1-38/test_w1_38_test_folder_rule.py -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rs --junitxml=$L/red.xml > $L/red.txt 2>&1
echo $? > $L/red.exit
