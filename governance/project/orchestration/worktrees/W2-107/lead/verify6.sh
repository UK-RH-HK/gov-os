#!/bin/bash
# Run 2, the scoped set again (verify5's background run was stopped at the tool's two-hour limit at 97% of its parallel
# part): $1 = parallel or serial. The rebuild and the selection of verify5 stand (no commit since). Exit codes in
# log/parallel6.exit and log/serial6.exit.
set -u
L=/home/usain/gov-os-worktrees/W2-107/.gov-runtime/scratch/lead/log
W=/home/usain/gov-os-worktrees/W2-107
T=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools
cd /home/usain/gov-os-worktrees/W2-107 || exit 4
export TMPDIR=/tmp/gov-os-lead-W2-107
export PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH
export GOV_CLOSE_SERIAL_ONLY_OF=/home/usain/gov-os-worktrees/W2-107
mapfile -t OPTS < /tmp/gov-os-lead-W2-107/options.txt
mapfile -t SERIAL < /tmp/gov-os-lead-W2-107/serial.txt
bash "$T/disk_gate.sh" >> "$L/disk-gate-verify6.txt" 2>&1 || exit 3
if [ "$1" = parallel ]; then
  du -s --inodes /tmp/gov-os-lead-W2-107 "$W/.gov-runtime" "$W/pytest-of-usain" > "$L/measure6-before.txt" 2>&1
  du -sh /tmp/gov-os-lead-W2-107 "$W/.gov-runtime" "$W/pytest-of-usain" >> "$L/measure6-before.txt" 2>&1
  date -u +%FT%TZ > "$L/parallel6.start"
  PYTHONPATH=/home/usain/gov-os-worktrees/W2-107/src:/home/usain/gov-os-worktrees/W2-107/src/gov/close/pytest_plugin bash "$T/verify_lock.sh" python3 -m pytest tests -n auto -q -p no:cacheprovider -p gov_close_serial_only -o tmp_path_retention_policy=failed -rs --junitxml="$L/parallel6.xml" "${OPTS[@]}" > "$L/parallel6.out" 2>&1
  echo $? > "$L/parallel6.exit"
  date -u +%FT%TZ > "$L/parallel6.end"
else
  date -u +%FT%TZ > "$L/serial6.start"
  GOV_CLOSE_SERIAL_ONLY_GIVEN="$(cat /tmp/gov-os-lead-W2-107/serial.txt)" PYTHONPATH=/home/usain/gov-os-worktrees/W2-107/src:/home/usain/gov-os-worktrees/W2-107/src/gov/close/pytest_plugin bash "$T/verify_lock.sh" python3 -m pytest -q -p no:cacheprovider -p gov_close_serial_only -o tmp_path_retention_policy=failed -rs --junitxml="$L/serial6.xml" "${OPTS[@]}" "${SERIAL[@]}" > "$L/serial6.out" 2>&1
  echo $? > "$L/serial6.exit"
  date -u +%FT%TZ > "$L/serial6.end"
  PYTHONPATH=/home/usain/gov-os-worktrees/W2-107/src python3 -m pytest tests --collect-only -q -p no:cacheprovider --no-header > "$L/collect6.out" 2>&1
  echo $? > "$L/collect6.exit"
  PYTHONPATH=/home/usain/gov-os-worktrees/W2-107/src python3 -m gov.cli.main check --json > "$L/check6.json" 2> "$L/check6.err"
  echo $? > "$L/check6.exit"
  du -s --inodes /tmp/gov-os-lead-W2-107 "$W/.gov-runtime" "$W/pytest-of-usain" > "$L/measure6-after.txt" 2>&1
  du -sh /tmp/gov-os-lead-W2-107 "$W/.gov-runtime" "$W/pytest-of-usain" >> "$L/measure6-after.txt" 2>&1
fi
