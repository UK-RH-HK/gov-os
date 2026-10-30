#!/bin/bash
# The serial phase in the close's form: the serial-route entries alone, without -n. $1 = "full" (verification lock) or
# "scoped"; $2 = the file of entries, one per line. Exit code to a file.
L=/home/usain/gov-os-worktrees/W2-78/.gov-runtime/scratch/lead/log
F=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator
cd /home/usain/gov-os-worktrees/W2-78 || exit 9
MODE=$1; ENTRIES=$2
until [ ! -e "$F/CLOSE-RUNNING" ] && [ ! -e "$F/NIGHTLY-RUNNING" ] && awk '{exit !($1 < 20)}' /proc/loadavg; do sleep 60; done
LOCK=""
if [ "$MODE" = "full" ]; then LOCK="flock /tmp/gov-os-verify.lock"; fi
mapfile -t ARGS < "$ENTRIES"
date > "$L/serial.start"
PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-78/src:/home/usain/gov-os-worktrees/W2-78/src/gov/close/pytest_plugin GOV_CLOSE_SERIAL_ONLY_OF=/home/usain/gov-os-worktrees/W2-78 GOV_CLOSE_SERIAL_ONLY_GIVEN="$(cat "$ENTRIES")" TMPDIR=/tmp/gov-os-lead-W2-78 $LOCK python3 -m pytest -q -p no:cacheprovider -p gov_close_serial_only -o tmp_path_retention_policy=failed -rs --junitxml="$L/serial.xml" "${ARGS[@]}" > "$L/serial.out" 2>&1
echo $? > "$L/serial.exit"
date > "$L/serial.end"
