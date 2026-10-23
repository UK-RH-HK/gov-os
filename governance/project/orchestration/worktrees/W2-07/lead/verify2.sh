#!/usr/bin/env bash
# Lead verification, run 2, in the close's form (DEC-889 items 6 and 12, DEC-904): rebuild, collection, gov check,
# then the parallel run and the serial-only run, each under the machine-wide lock. Exit codes in log/v2-*.exit.
cd /home/usain/gov-os-worktrees/W2-07 || exit 90
L=/home/usain/gov-os-worktrees/W2-07/.gov-runtime/scratch/lead/log
GATE=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/disk_gate.sh
CLOSE=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/CLOSE-RUNNING
SRC=/home/usain/gov-os-worktrees/W2-07/src
export TMPDIR=/tmp/gov-os-lead-W2-07
mkdir -p "$TMPDIR"
rm -f "$L/v2.done"
trap 'echo done > "$L/v2.done"' EXIT
bash /home/usain/gov-os-worktrees/W2-07/.gov-runtime/scratch/lead/watch2.sh &

wait_machine() {
  until [ ! -e "$CLOSE" ]; do sleep 60; done
  until awk '{exit !($1 < 20)}' /proc/loadavg; do sleep 60; done
}

PYTHONPATH=$SRC python3 -c "import gov; print(gov.__file__)" > "$L/v2-gov-file.txt"

# 1. The full rebuild
wait_machine
{ date -Is; cat /proc/loadavg; bash "$GATE"; } > "$L/v2-rebuild.gate" 2>&1 || { echo 91 > "$L/v2-rebuild.exit"; exit 91; }
PYTHONPATH=$SRC python3 -m gov.cli.main rebuild --json > "$L/v2-rebuild.json" 2>&1; echo $? > "$L/v2-rebuild.exit"

# 2. The collection, in one process, as the close runs it (DEC-868)
PYTHONPATH=$SRC python3 -m pytest tests --collect-only -q -p no:cacheprovider --no-header > "$L/v2-collect.txt" 2>&1; echo $? > "$L/v2-collect.exit"

# 3. gov check, no commit since the rebuild
PYTHONPATH=$SRC python3 -m gov.cli.main check --json > "$L/v2-check.json" 2>&1; echo $? > "$L/v2-check.exit"
PYTHONPATH=$SRC python3 -m gov.secrets > "$L/v2-secrets.txt" 2>&1; echo $? > "$L/v2-secrets.exit"

# 4. The full parallel run, under the lock
wait_machine
{ date -Is; cat /proc/loadavg; bash "$GATE"; du -s --inodes "$TMPDIR"; du -sh "$TMPDIR"; } > "$L/v2-parallel.gate" 2>&1 \
  || { echo 91 > "$L/v2-parallel.exit"; exit 91; }
flock /tmp/gov-os-verify.lock env \
  PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH \
  PYTHONPATH=$SRC:$SRC/gov/close/pytest_plugin \
  GOV_CLOSE_SERIAL_ONLY_OF=/home/usain/gov-os-worktrees/W2-07 \
  bash -c "date -Is > $L/v2-parallel.start; exec python3 -m pytest tests -n auto -q -p no:cacheprovider -p gov_close_serial_only -rs --junitxml=$L/parallel.xml" \
  > "$L/v2-parallel.txt" 2>&1; echo $? > "$L/v2-parallel.exit"
date -Is > "$L/v2-parallel.end"
{ du -s --inodes "$TMPDIR"; du -sh "$TMPDIR"; } >> "$L/v2-parallel.gate" 2>&1

# 5. The serial-only run, under the lock
wait_machine
{ date -Is; cat /proc/loadavg; bash "$GATE"; } > "$L/v2-serial.gate" 2>&1 || { echo 91 > "$L/v2-serial.exit"; exit 91; }
flock /tmp/gov-os-verify.lock bash /home/usain/gov-os-worktrees/W2-07/.gov-runtime/scratch/lead/serial.sh "$L/serial.xml" \
  > "$L/v2-serial.txt" 2>&1; echo $? > "$L/v2-serial.exit"
{ du -s --inodes "$TMPDIR"; du -sh "$TMPDIR"; } >> "$L/v2-serial.gate" 2>&1
