#!/usr/bin/env bash
# Lead verification, run 3, in the close's form (DEC-889 items 6 and 12, DEC-904, DEC-905): rebuild, collection,
# gov check, then the parallel run and the serial-only run, each under the machine-wide lock and with
# -o tmp_path_retention_policy=failed. Exit codes in log/v3-*.exit; log/v3.done at the end.
cd /home/usain/gov-os-worktrees/W2-07 || exit 90
L=/home/usain/gov-os-worktrees/W2-07/.gov-runtime/scratch/lead/log
GATE=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/disk_gate.sh
CLOSE=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/CLOSE-RUNNING
SRC=/home/usain/gov-os-worktrees/W2-07/src
export TMPDIR=/tmp/gov-os-lead-W2-07
mkdir -p "$TMPDIR"
rm -f "$L/v3.done"
trap 'echo done > "$L/v3.done"' EXIT
( until [ -e "$L/v3.done" ]; do
    echo "$(date -Is) $(cut -d' ' -f1 /proc/loadavg) $(du -s --inodes "$TMPDIR" 2>/dev/null | cut -f1) $(du -sb "$TMPDIR" 2>/dev/null | cut -f1)" >> "$L/v3-scratch-watch.txt"
    sleep 120
  done ) &

wait_machine() {
  until [ ! -e "$CLOSE" ]; do sleep 60; done
  until awk '{exit !($1 < 20)}' /proc/loadavg; do sleep 60; done
}

PYTHONPATH=$SRC python3 -c "import gov; print(gov.__file__)" > "$L/v3-gov-file.txt"
git log --oneline -1 > "$L/v3-head.txt"

# 1. The full rebuild
wait_machine
{ date -Is; cat /proc/loadavg; bash "$GATE"; du -s --inodes "$TMPDIR"; du -sh "$TMPDIR"; } > "$L/v3-rebuild.gate" 2>&1 \
  || { echo 91 > "$L/v3-rebuild.exit"; exit 91; }
PYTHONPATH=$SRC python3 -m gov.cli.main rebuild --json > "$L/v3-rebuild.json" 2>&1; echo $? > "$L/v3-rebuild.exit"

# 2. The collection, in one process, as the close runs it (DEC-868)
PYTHONPATH=$SRC python3 -m pytest tests --collect-only -q -p no:cacheprovider --no-header > "$L/v3-collect.txt" 2>&1; echo $? > "$L/v3-collect.exit"

# 3. gov check, no commit since the rebuild
PYTHONPATH=$SRC python3 -m gov.cli.main check --json > "$L/v3-check.json" 2>&1; echo $? > "$L/v3-check.exit"

# 4. The full parallel run, under the lock
wait_machine
{ date -Is; cat /proc/loadavg; bash "$GATE"; du -s --inodes "$TMPDIR"; du -sh "$TMPDIR"; } > "$L/v3-parallel.gate" 2>&1 \
  || { echo 91 > "$L/v3-parallel.exit"; exit 91; }
export PATH="/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH"
flock /tmp/gov-os-verify.lock env \
  PYTHONPATH=$SRC:$SRC/gov/close/pytest_plugin \
  GOV_CLOSE_SERIAL_ONLY_OF=/home/usain/gov-os-worktrees/W2-07 \
  bash -c "date -Is > $L/v3-parallel.start; exec python3 -m pytest tests -n auto -q -p no:cacheprovider -p gov_close_serial_only -o tmp_path_retention_policy=failed -rs --junitxml=$L/parallel3.xml" \
  > "$L/v3-parallel.txt" 2>&1; echo $? > "$L/v3-parallel.exit"
date -Is > "$L/v3-parallel.end"
{ du -s --inodes "$TMPDIR"; du -sh "$TMPDIR"; } >> "$L/v3-parallel.gate" 2>&1

# 5. The serial-only run, under the lock
wait_machine
{ date -Is; cat /proc/loadavg; bash "$GATE"; } > "$L/v3-serial.gate" 2>&1 || { echo 91 > "$L/v3-serial.exit"; exit 91; }
flock /tmp/gov-os-verify.lock bash /home/usain/gov-os-worktrees/W2-07/.gov-runtime/scratch/lead/serial3.sh "$L/serial3.xml" \
  > "$L/v3-serial.txt" 2>&1; echo $? > "$L/v3-serial.exit"
{ date -Is; du -s --inodes "$TMPDIR"; du -sh "$TMPDIR"; } >> "$L/v3-serial.gate" 2>&1
