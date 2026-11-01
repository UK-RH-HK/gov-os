#!/bin/bash
# Lead's check of the W2-81 suite at the current head (not the final verification): plain, then -n auto, then collect-only.
cd /home/usain/gov-os-worktrees/W2-81 || exit 9
until python3 -c "import os; l=os.getloadavg(); exit(0 if min(l[0], l[2]) < os.cpu_count() else 1)"; do sleep 60; done
bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/disk_gate.sh || exit 8
PYTHONPATH=/home/usain/gov-os-worktrees/W2-81/src python3 -c "import gov; print(gov.__file__)" > /home/usain/gov-os-worktrees/W2-81/.gov-runtime/scratch/lead/log/import.txt
/usr/bin/time -f "wall %e s" env PYTHONPATH=/home/usain/gov-os-worktrees/W2-81/src python3 -m pytest tests/acceptance/W2-81 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rs --junitxml=/home/usain/gov-os-worktrees/W2-81/.gov-runtime/scratch/lead/log/w2-81-plain.xml > /home/usain/gov-os-worktrees/W2-81/.gov-runtime/scratch/lead/log/w2-81-plain.txt 2>&1
echo $? > /home/usain/gov-os-worktrees/W2-81/.gov-runtime/scratch/lead/log/w2-81-plain.exit
/usr/bin/time -f "wall %e s" env PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:/usr/bin:/bin:/home/usain/.local/bin PYTHONPATH=/home/usain/gov-os-worktrees/W2-81/src:/home/usain/gov-os-worktrees/W2-81/src/gov/close/pytest_plugin GOV_CLOSE_SERIAL_ONLY_OF=/home/usain/gov-os-worktrees/W2-81 python3 -m pytest tests/acceptance/W2-81 -n auto -q -p no:cacheprovider -p gov_close_serial_only -o tmp_path_retention_policy=failed -rs --junitxml=/home/usain/gov-os-worktrees/W2-81/.gov-runtime/scratch/lead/log/w2-81-parallel.xml > /home/usain/gov-os-worktrees/W2-81/.gov-runtime/scratch/lead/log/w2-81-parallel.txt 2>&1
echo $? > /home/usain/gov-os-worktrees/W2-81/.gov-runtime/scratch/lead/log/w2-81-parallel.exit
PYTHONPATH=/home/usain/gov-os-worktrees/W2-81/src python3 -m pytest tests --collect-only -q -p no:cacheprovider --no-header > /home/usain/gov-os-worktrees/W2-81/.gov-runtime/scratch/lead/log/collect.txt 2>&1
echo $? > /home/usain/gov-os-worktrees/W2-81/.gov-runtime/scratch/lead/log/collect.exit
