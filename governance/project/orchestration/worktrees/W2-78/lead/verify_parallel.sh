#!/bin/bash
# The parallel run in the close's form. $1 = "full" (takes the verification lock) or "scoped"; further arguments are
# scoped_plan.py's pytest_options. Waits for no close, no nightly and load < 20; disk gate; exit code to a file.
L=/home/usain/gov-os-worktrees/W2-78/.gov-runtime/scratch/lead/log
F=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator
cd /home/usain/gov-os-worktrees/W2-78 || exit 9
MODE=$1; shift
until [ ! -e "$F/CLOSE-RUNNING" ] && [ ! -e "$F/NIGHTLY-RUNNING" ] && awk '{exit !($1 < 20)}' /proc/loadavg; do sleep 60; done
bash "$F/tools/disk_gate.sh" > "$L/disk-gate-parallel.txt" 2>&1 || { echo 8 > "$L/parallel.exit"; exit 8; }
LOCK=""
if [ "$MODE" = "full" ]; then LOCK="flock /tmp/gov-os-verify.lock"; fi
date > "$L/parallel.start"
PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-78/src:/home/usain/gov-os-worktrees/W2-78/src/gov/close/pytest_plugin GOV_CLOSE_SERIAL_ONLY_OF=/home/usain/gov-os-worktrees/W2-78 TMPDIR=/tmp/gov-os-lead-W2-78 $LOCK python3 -m pytest tests -n auto -q -p no:cacheprovider -p gov_close_serial_only -o tmp_path_retention_policy=failed -rs --junitxml="$L/parallel.xml" "$@" > "$L/parallel.out" 2>&1
echo $? > "$L/parallel.exit"
date > "$L/parallel.end"
