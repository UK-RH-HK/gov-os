#!/bin/bash
# The lead's full verification, serial phase (the close's serial-afterwards run), DEC-889, DEC-905.
# Usage: verify-serial.sh <tag>   (reads serial-entries.txt, made by serial_list.py)
cd /home/usain/gov-os-worktrees/W2-84 || exit 2
TAG="$1"
ORCH=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator
LOG=/home/usain/gov-os-worktrees/W2-84/.gov-runtime/scratch/lead/log
LIST=/home/usain/gov-os-worktrees/W2-84/.gov-runtime/scratch/lead/serial-entries.txt
while [ -e "$ORCH/CLOSE-RUNNING" ] || [ -e "$ORCH/NIGHTLY-RUNNING" ]; do sleep 60; done
until awk '{exit !($1 < 20)}' /proc/loadavg; do sleep 60; done
bash "$ORCH/tools/disk_gate.sh" > "$LOG/serial-$TAG.out" 2>&1 || { echo 97 > "$LOG/serial-$TAG.rc"; exit 97; }
mkdir -p /tmp/gov-os-lead-W2-84
{ date; cat /proc/loadavg; } >> "$LOG/serial-$TAG.out" 2>&1
GIVEN="$(cat "$LIST")"
mapfile -t ENTRIES < "$LIST"
TMPDIR=/tmp/gov-os-lead-W2-84 PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-84/src:/home/usain/gov-os-worktrees/W2-84/src/gov/close/pytest_plugin GOV_CLOSE_SERIAL_ONLY_OF=/home/usain/gov-os-worktrees/W2-84 GOV_CLOSE_SERIAL_ONLY_GIVEN="$GIVEN" flock /tmp/gov-os-verify.lock python3 -m pytest "${ENTRIES[@]}" -q -p no:cacheprovider -p gov_close_serial_only -o tmp_path_retention_policy=failed -rs --junitxml="$LOG/serial-$TAG.xml" >> "$LOG/serial-$TAG.out" 2>&1
RC=$?
{ date; du -sh /tmp/gov-os-lead-W2-84; du -s --inodes /tmp/gov-os-lead-W2-84; } >> "$LOG/serial-$TAG.out" 2>&1
echo $RC > "$LOG/serial-$TAG.rc"
