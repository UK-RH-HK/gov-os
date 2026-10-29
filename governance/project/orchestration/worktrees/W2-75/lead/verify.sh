#!/usr/bin/env bash
# DAEO-ebmh (W2-75): the full verification run in the close's form (DEC-889 items 6 and 12, DEC-904, DEC-905).
# Part 1: the parallel run; part 2: the serial-only cases alone. Each under the machine-wide lock, with JUnit XML.
set -u
WT=/home/usain/gov-os-worktrees/W2-75
L=$WT/.gov-runtime/scratch/lead/log/verify
mkdir -p "$L"
cd "$WT" || exit 9
NIGHT=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/NIGHTLY-RUNNING
CLOSE=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/CLOSE-RUNNING
gates() {
  until [ ! -e "$NIGHT" ] && [ ! -e "$CLOSE" ]; do sleep 60; done
  until awk '{exit !($1 < 20)}' /proc/loadavg; do sleep 60; done
  bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/disk_gate.sh || exit 8
  du -s --inodes "$WT/.gov-runtime" /tmp/gov-os-lead-W2-75
  du -sh "$WT/.gov-runtime" /tmp/gov-os-lead-W2-75
}
export TMPDIR=/tmp/gov-os-lead-W2-75
unset GOV_CLOSE_CHECK_RESULT
export PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH
export PYTHONPATH=$WT/src:$WT/src/gov/close/pytest_plugin
export GOV_CLOSE_SERIAL_ONLY_OF=$WT

if [ "${1:-all}" != "serial" ]; then
  gates > "$L/gates-parallel.txt" 2>&1
  date > "$L/parallel.start"
  flock /tmp/gov-os-verify.lock python3 -m pytest tests -n auto -q -p no:cacheprovider -p gov_close_serial_only \
    -o tmp_path_retention_policy=failed -rs --junitxml="$L/parallel.xml" > "$L/parallel.log" 2>&1
  echo $? > "$L/parallel.exit"
  date > "$L/parallel.end"
fi
[ "${1:-all}" = "parallel" ] && exit 0

grep -v '^#' tests/acceptance/serial-only.txt | sed 's/ #.*//; s/[[:space:]]*$//' | grep -v '^$' > "$L/serial-entries.txt"
gates > "$L/gates-serial.txt" 2>&1
date > "$L/serial.start"
GOV_CLOSE_SERIAL_ONLY_GIVEN="$(cat "$L/serial-entries.txt")" flock /tmp/gov-os-verify.lock \
  xargs -a "$L/serial-entries.txt" -d '\n' python3 -m pytest -q -p no:cacheprovider -p gov_close_serial_only \
  -o tmp_path_retention_policy=failed -rs --junitxml="$L/serial.xml" > "$L/serial.log" 2>&1
echo $? > "$L/serial.exit"
date > "$L/serial.end"
