#!/bin/bash
# Lead's verification, part 2: the serial-only cases alone, the way gov close runs them, under the verification lock.
L=/home/usain/gov-os-worktrees/W2-64/.gov-runtime/scratch/lead/log
F=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator
W=/home/usain/gov-os-worktrees/W2-64
until [ ! -e "$F/NIGHTLY-RUNNING" ] && [ ! -e "$F/CLOSE-RUNNING" ]; do sleep 60; done
until awk '{exit !($1 < 20)}' /proc/loadavg; do sleep 60; done
bash "$F/tools/disk_gate.sh" > "$L/disk-gate-serial.txt" 2>&1 || { echo 99 > "$L/serial.exit"; exit 99; }
cd "$W" || exit 98
python3 /home/usain/gov-os-worktrees/W2-64/.gov-runtime/scratch/lead/serial_entries.py "$W/tests/acceptance/serial-only.txt" > /home/usain/gov-os-worktrees/W2-64/.gov-runtime/scratch/lead/log/serial-entries.txt
mapfile -t ENTRIES < "$L/serial-entries.txt"
GIVEN=$(cat "$L/serial-entries.txt")
date > "$L/serial.start"
PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH TMPDIR=/tmp/gov-os-lead-W2-64 PYTHONPATH=$W/src:$W/src/gov/close/pytest_plugin GOV_CLOSE_SERIAL_ONLY_OF=$W GOV_CLOSE_SERIAL_ONLY_GIVEN="$GIVEN" flock /tmp/gov-os-verify.lock python3 -m pytest "${ENTRIES[@]}" -q -p no:cacheprovider -p gov_close_serial_only -o tmp_path_retention_policy=failed -rs --junitxml=/home/usain/gov-os-worktrees/W2-64/.gov-runtime/scratch/lead/log/serial.xml > /home/usain/gov-os-worktrees/W2-64/.gov-runtime/scratch/lead/log/serial.txt 2>&1
echo $? > /home/usain/gov-os-worktrees/W2-64/.gov-runtime/scratch/lead/log/serial.exit
date > "$L/serial.end"
