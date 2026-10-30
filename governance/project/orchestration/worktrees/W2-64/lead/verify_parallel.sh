#!/bin/bash
# Lead's verification, part 1 (DEC-952 scope full, DEC-889 items 6/12, DEC-905): the ticket's own suite, then the
# full parallel run with scoped_plan's options, under the verification lock. Exit codes to files.
L=/home/usain/gov-os-worktrees/W2-64/.gov-runtime/scratch/lead/log
F=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator
W=/home/usain/gov-os-worktrees/W2-64
until [ ! -e "$F/NIGHTLY-RUNNING" ] && [ ! -e "$F/CLOSE-RUNNING" ]; do sleep 60; done
until awk '{exit !($1 < 20)}' /proc/loadavg; do sleep 60; done
bash "$F/tools/disk_gate.sh" > "$L/disk-gate-verify.txt" 2>&1 || { echo 99 > "$L/parallel.exit"; exit 99; }
cd "$W" || exit 98
date > "$L/parallel.start"
PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH TMPDIR=/tmp/gov-os-lead-W2-64 PYTHONPATH=$W/src:$W/src/gov/close/pytest_plugin GOV_CLOSE_SERIAL_ONLY_OF=$W flock /tmp/gov-os-verify.lock python3 -m pytest tests/acceptance/W2-64 -q -p no:cacheprovider -p gov_close_serial_only -o tmp_path_retention_policy=failed -rs --junitxml=/home/usain/gov-os-worktrees/W2-64/.gov-runtime/scratch/lead/log/own.xml > /home/usain/gov-os-worktrees/W2-64/.gov-runtime/scratch/lead/log/own.txt 2>&1
echo $? > /home/usain/gov-os-worktrees/W2-64/.gov-runtime/scratch/lead/log/own.exit
PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH TMPDIR=/tmp/gov-os-lead-W2-64 PYTHONPATH=$W/src:$W/src/gov/close/pytest_plugin GOV_CLOSE_SERIAL_ONLY_OF=$W flock /tmp/gov-os-verify.lock python3 -m pytest tests -n auto -q -p no:cacheprovider -p gov_close_serial_only -o tmp_path_retention_policy=failed -rs --ignore=/home/usain/gov-os-worktrees/W2-64/tests/acceptance/W2-64 --junitxml=/home/usain/gov-os-worktrees/W2-64/.gov-runtime/scratch/lead/log/parallel.xml > /home/usain/gov-os-worktrees/W2-64/.gov-runtime/scratch/lead/log/parallel.txt 2>&1
echo $? > /home/usain/gov-os-worktrees/W2-64/.gov-runtime/scratch/lead/log/parallel.exit
date > "$L/parallel.end"
