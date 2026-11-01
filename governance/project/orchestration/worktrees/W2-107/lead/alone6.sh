#!/bin/bash
# Run 2: the load-sensitive red of the serial part re-run alone after the other suites ended, then gov check alone
# (its two RED families were time-outs under load). Results in log/alone6.*, log/check7.*.
set -u
L=/home/usain/gov-os-worktrees/W2-107/.gov-runtime/scratch/lead/log
cd /home/usain/gov-os-worktrees/W2-107 || exit 4
export TMPDIR=/tmp/gov-os-lead-W2-107
export PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH
until python3 -c "import os; l=os.getloadavg(); exit(0 if min(l[0], l[2]) < os.cpu_count() else 1)"; do sleep 60; done
date -u +%FT%TZ > "$L/alone6.start"
uptime > "$L/alone6.load"
PYTHONPATH=/home/usain/gov-os-worktrees/W2-107/src python3 -m pytest "tests/acceptance/W2-54/test_w2_54_green_here.py::test_gov_check_gives_context_reproducibility_green_here" -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rs > "$L/alone6.out" 2>&1
echo $? > "$L/alone6.exit"
until python3 -c "import os; l=os.getloadavg(); exit(0 if min(l[0], l[2]) < os.cpu_count() else 1)"; do sleep 60; done
uptime >> "$L/alone6.load"
date -u +%FT%TZ > "$L/check7.start"
PYTHONPATH=/home/usain/gov-os-worktrees/W2-107/src python3 -m gov.cli.main check --json > "$L/check7.json" 2> "$L/check7.err"
echo $? > "$L/check7.exit"
date -u +%FT%TZ > "$L/check7.end"
