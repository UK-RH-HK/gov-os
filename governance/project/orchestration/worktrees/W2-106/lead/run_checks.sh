#!/bin/bash
# Lead's red check, green check and rebuild for DAEO-0mtg (W2-106). Each step waits for the machine's capacity.
LOG=/home/usain/gov-os-worktrees/W2-106/.gov-runtime/scratch/lead/log
export TMPDIR=/tmp/gov-os-lead-W2-106
export PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH

wait_load() {
  until python3 -c "import os; l=os.getloadavg(); exit(0 if min(l[0], l[2]) < os.cpu_count() else 1)"; do sleep 60; done
}

wait_load
date > /home/usain/gov-os-worktrees/W2-106/.gov-runtime/scratch/lead/log/red.start
cd /home/usain/gov-os-worktrees/W2-106-tests
PYTHONPATH=/home/usain/gov-os-worktrees/W2-106-tests/src python3 -c "import gov; print(gov.__file__)" > /home/usain/gov-os-worktrees/W2-106/.gov-runtime/scratch/lead/log/red.govfile 2>&1
PYTHONPATH=/home/usain/gov-os-worktrees/W2-106-tests/src python3 -m pytest tests/acceptance/W2-106 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rs --junitxml=/home/usain/gov-os-worktrees/W2-106/.gov-runtime/scratch/lead/log/red.xml > /home/usain/gov-os-worktrees/W2-106/.gov-runtime/scratch/lead/log/red.txt 2>&1
echo $? > /home/usain/gov-os-worktrees/W2-106/.gov-runtime/scratch/lead/log/red.exit

wait_load
cd /home/usain/gov-os-worktrees/W2-106
PYTHONPATH=/home/usain/gov-os-worktrees/W2-106/src python3 -c "import gov; print(gov.__file__)" > /home/usain/gov-os-worktrees/W2-106/.gov-runtime/scratch/lead/log/green.govfile 2>&1
PYTHONPATH=/home/usain/gov-os-worktrees/W2-106/src python3 -m pytest tests/acceptance/W2-106 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rs --junitxml=/home/usain/gov-os-worktrees/W2-106/.gov-runtime/scratch/lead/log/green.xml > /home/usain/gov-os-worktrees/W2-106/.gov-runtime/scratch/lead/log/green.txt 2>&1
echo $? > /home/usain/gov-os-worktrees/W2-106/.gov-runtime/scratch/lead/log/green.exit

wait_load
cd /home/usain/gov-os-worktrees/W2-106
PYTHONPATH=/home/usain/gov-os-worktrees/W2-106/src flock /tmp/gov-os-rebuild.lock python3 -m gov.cli.main rebuild --json > /home/usain/gov-os-worktrees/W2-106/.gov-runtime/scratch/lead/log/rebuild-2.json 2>&1
echo $? > /home/usain/gov-os-worktrees/W2-106/.gov-runtime/scratch/lead/log/rebuild-2.exit
