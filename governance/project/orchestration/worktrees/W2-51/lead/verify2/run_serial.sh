#!/bin/bash
# Run 2, part 2: the close's serial phase (the serial-only list less its nightly-routed entries), alone, no -n.
cd /home/usain/gov-os-worktrees/W2-51 || exit 99
O=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator
PYTHONPATH=/home/usain/gov-os-worktrees/W2-51/src python3 /home/usain/gov-os-worktrees/W2-51/.gov-runtime/scratch/lead/verify2/serial_entries.py > /home/usain/gov-os-worktrees/W2-51/.gov-runtime/scratch/lead/verify2/serial-entries.txt
until [ ! -e $O/CLOSE-RUNNING ] && [ ! -e $O/NIGHTLY-RUNNING ]; do sleep 60; done
until awk '{exit !($1 < 20)}' /proc/loadavg; do sleep 60; done
bash $O/tools/disk_gate.sh > /home/usain/gov-os-worktrees/W2-51/.gov-runtime/scratch/lead/verify2/serial-gate.txt 2>&1
date >> /home/usain/gov-os-worktrees/W2-51/.gov-runtime/scratch/lead/verify2/serial-gate.txt
cat /proc/loadavg >> /home/usain/gov-os-worktrees/W2-51/.gov-runtime/scratch/lead/verify2/serial-gate.txt
GIVEN=$(cat /home/usain/gov-os-worktrees/W2-51/.gov-runtime/scratch/lead/verify2/serial-entries.txt)
mapfile -t ARGS < /home/usain/gov-os-worktrees/W2-51/.gov-runtime/scratch/lead/verify2/serial-entries.txt
TMPDIR=/tmp/gov-os-lead-W2-51 PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-51/src:/home/usain/gov-os-worktrees/W2-51/src/gov/close/pytest_plugin GOV_CLOSE_SERIAL_ONLY_OF=/home/usain/gov-os-worktrees/W2-51 GOV_CLOSE_SERIAL_ONLY_GIVEN="$GIVEN" flock /tmp/gov-os-verify.lock python3 -m pytest "${ARGS[@]}" -q -p no:cacheprovider -p gov_close_serial_only -o tmp_path_retention_policy=failed -rs --junitxml=/home/usain/gov-os-worktrees/W2-51/.gov-runtime/scratch/lead/verify2/serial.xml > /home/usain/gov-os-worktrees/W2-51/.gov-runtime/scratch/lead/verify2/serial.log 2>&1
echo $? > /home/usain/gov-os-worktrees/W2-51/.gov-runtime/scratch/lead/verify2/serial.exit
date >> /home/usain/gov-os-worktrees/W2-51/.gov-runtime/scratch/lead/verify2/serial-gate.txt
