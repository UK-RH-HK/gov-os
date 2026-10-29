#!/usr/bin/env bash
# The lead's verification in the close's form (DEC-889 items 6 and 12, DEC-905): one parallel run, then the
# serial-only entries alone; each under the verification lock, with the retention option and JUnit XML.
# Usage: verify.sh parallel|serial
W=/home/usain/gov-os-worktrees/W2-68
L=$W/.gov-runtime/scratch/lead/log
O=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator
cd "$W" || exit 1
until [ ! -e "$O/CLOSE-RUNNING" ] && [ ! -e "$O/NIGHTLY-RUNNING" ]; do sleep 60; done
until awk '{exit !($1 < 20)}' /proc/loadavg; do sleep 60; done
bash "$O/tools/disk_gate.sh" > "$L/$1.disk" 2>&1 || { echo 90 > "$L/$1.exit"; exit 90; }
date '+%F %T start' > "$L/$1.times"
export TMPDIR=/tmp/gov-os-lead-W2-68
export PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH
export PYTHONPATH=$W/src:$W/src/gov/close/pytest_plugin
export GOV_CLOSE_SERIAL_ONLY_OF=$W
if [ "$1" = parallel ]; then
  flock /tmp/gov-os-verify.lock python3 -m pytest tests -n auto -q -p no:cacheprovider -p gov_close_serial_only \
    -o tmp_path_retention_policy=failed -rs --junitxml="$L/parallel.xml" > "$L/parallel.txt" 2>&1
else
  mapfile -t entries < "$L/serial-all.txt"
  GOV_CLOSE_SERIAL_ONLY_GIVEN="$(cat "$L/serial-all.txt")" flock /tmp/gov-os-verify.lock python3 -m pytest \
    "${entries[@]}" -q -p no:cacheprovider -p gov_close_serial_only -o tmp_path_retention_policy=failed -rs \
    --junitxml="$L/serial.xml" > "$L/serial.txt" 2>&1
fi
code=$?
date '+%F %T end' >> "$L/$1.times"
echo "$code" > "$L/$1.exit"
