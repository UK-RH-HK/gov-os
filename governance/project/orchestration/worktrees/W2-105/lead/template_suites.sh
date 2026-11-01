#!/bin/bash
# KPI 4: the template's own suites, W1-38 and W1-39, once each on the change (W1-39 is outside the selection).
cd /home/usain/gov-os-worktrees/W2-105 || exit 9
export TMPDIR=/tmp/gov-os-lead-W2-105
L=/home/usain/gov-os-worktrees/W2-105/.gov-runtime/scratch/lead/log
for s in W1-38 W1-39; do
  PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-105/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/verify_lock.sh python3 -m pytest tests/acceptance/$s -n auto -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rs --junitxml=$L/suite-$s.xml > $L/suite-$s.txt 2>&1
  echo $? > $L/suite-$s.exit
done
