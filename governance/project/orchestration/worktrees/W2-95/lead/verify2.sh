#!/bin/bash
# W2-95 run 2 verification (step 4): load wait, disk gate, full rebuild, scoped parallel run, scoped serial-only run.
cd /home/usain/gov-os-worktrees/W2-95 || exit 9
export TMPDIR=/tmp/gov-os-lead-W2-95
L=/home/usain/gov-os-worktrees/W2-95/.gov-runtime/scratch/lead

waitload() {
  until python3 -c "import os; l=os.getloadavg(); exit(0 if min(l[0], l[2]) < os.cpu_count() else 1)"; do sleep 60; done
}

date -u +%FT%TZ > /home/usain/gov-os-worktrees/W2-95/.gov-runtime/scratch/lead/log/verify2-start.txt
waitload
bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/disk_gate.sh > /home/usain/gov-os-worktrees/W2-95/.gov-runtime/scratch/lead/log/disk-gate-3.txt 2>&1
PYTHONPATH=/home/usain/gov-os-worktrees/W2-95/src flock /tmp/gov-os-rebuild.lock python3 -m gov.cli.main rebuild --json > /home/usain/gov-os-worktrees/W2-95/.gov-runtime/scratch/lead/log/rebuild-3.json 2>&1
echo $? > /home/usain/gov-os-worktrees/W2-95/.gov-runtime/scratch/lead/log/rebuild-3.exit
date -u +%FT%TZ > /home/usain/gov-os-worktrees/W2-95/.gov-runtime/scratch/lead/log/rebuild-3-end.txt

mapfile -t OPTS < "$L/verify-opts.txt"
mapfile -t SERIAL < "$L/verify-serial.txt"

waitload
date -u +%FT%TZ > /home/usain/gov-os-worktrees/W2-95/.gov-runtime/scratch/lead/log/parallel-start.txt
PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-95/src:/home/usain/gov-os-worktrees/W2-95/src/gov/close/pytest_plugin GOV_CLOSE_SERIAL_ONLY_OF=/home/usain/gov-os-worktrees/W2-95 bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/verify_lock.sh python3 -m pytest tests -n auto -q -p no:cacheprovider -p gov_close_serial_only -o tmp_path_retention_policy=failed -rs --junitxml=/home/usain/gov-os-worktrees/W2-95/.gov-runtime/scratch/lead/log/parallel.xml "${OPTS[@]}" > /home/usain/gov-os-worktrees/W2-95/.gov-runtime/scratch/lead/log/parallel.txt 2>&1
echo $? > /home/usain/gov-os-worktrees/W2-95/.gov-runtime/scratch/lead/log/parallel.exit
date -u +%FT%TZ > /home/usain/gov-os-worktrees/W2-95/.gov-runtime/scratch/lead/log/parallel-end.txt

if [ "${#SERIAL[@]}" -gt 0 ]; then
  waitload
  GIVEN=$(printf '%s\n' "${SERIAL[@]}")
  PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-95/src:/home/usain/gov-os-worktrees/W2-95/src/gov/close/pytest_plugin GOV_CLOSE_SERIAL_ONLY_OF=/home/usain/gov-os-worktrees/W2-95 GOV_CLOSE_SERIAL_ONLY_GIVEN="$GIVEN" bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/verify_lock.sh python3 -m pytest -q -p no:cacheprovider -p gov_close_serial_only -o tmp_path_retention_policy=failed -rs --junitxml=/home/usain/gov-os-worktrees/W2-95/.gov-runtime/scratch/lead/log/serial.xml "${SERIAL[@]}" > /home/usain/gov-os-worktrees/W2-95/.gov-runtime/scratch/lead/log/serial.txt 2>&1
  echo $? > /home/usain/gov-os-worktrees/W2-95/.gov-runtime/scratch/lead/log/serial.exit
else
  echo none > /home/usain/gov-os-worktrees/W2-95/.gov-runtime/scratch/lead/log/serial.exit
fi
date -u +%FT%TZ > /home/usain/gov-os-worktrees/W2-95/.gov-runtime/scratch/lead/log/verify2-end.txt
