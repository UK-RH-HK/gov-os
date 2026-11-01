#!/bin/bash
# Step 4: the scoped set select_tests.py chose, in the close's form: one parallel run, then the selected serial-only
# cases alone. Waits for this worktree's first rebuild to end. Exit codes in log/parallel.exit and log/serial.exit.
set -u
L=/home/usain/gov-os-worktrees/W2-107/.gov-runtime/scratch/lead/log
cd /home/usain/gov-os-worktrees/W2-107 || exit 4
until [ -s "$L/rebuild2.exit" ]; do sleep 30; done  # both rebuilds ended: no store write during the suite
mapfile -t OPTS < /tmp/gov-os-lead-W2-107/options.txt
mapfile -t SERIAL < /tmp/gov-os-lead-W2-107/serial.txt
export TMPDIR=/tmp/gov-os-lead-W2-107
export PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH
export PYTHONPATH=/home/usain/gov-os-worktrees/W2-107/src:/home/usain/gov-os-worktrees/W2-107/src/gov/close/pytest_plugin
export GOV_CLOSE_SERIAL_ONLY_OF=/home/usain/gov-os-worktrees/W2-107
until python3 -c "import os; l=os.getloadavg(); exit(0 if min(l[0], l[2]) < os.cpu_count() else 1)"; do sleep 60; done
bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/disk_gate.sh > "$L/disk-gate-verify2.txt" 2>&1 || exit 3
python3 -c "import gov; print(gov.__file__)" > "$L/govfile2.txt"
date -u +%FT%TZ > "$L/parallel2.start"
bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/verify_lock.sh python3 -m pytest tests -n auto -q -p no:cacheprovider -p gov_close_serial_only -o tmp_path_retention_policy=failed -rs --timeout=900 --timeout_method=signal --junitxml="$L/parallel2.xml" "${OPTS[@]}" > "$L/parallel2.out" 2>&1
echo $? > "$L/parallel2.exit"
date -u +%FT%TZ > "$L/serial2.start"
GOV_CLOSE_SERIAL_ONLY_GIVEN="$(cat /tmp/gov-os-lead-W2-107/serial.txt)" bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/verify_lock.sh python3 -m pytest -q -p no:cacheprovider -p gov_close_serial_only -o tmp_path_retention_policy=failed -rs --timeout=900 --timeout_method=signal --junitxml="$L/serial2.xml" "${OPTS[@]}" "${SERIAL[@]}" > "$L/serial2.out" 2>&1
echo $? > "$L/serial2.exit"
date -u +%FT%TZ > "$L/serial2.end"
