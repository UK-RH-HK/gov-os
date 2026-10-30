#!/bin/bash
# W2-05's acceptance suite alone, gated (CLOSE-RUNNING, NIGHTLY-RUNNING, load < 20, disk gate), with an exit-code file.
# $1 = log name stem
cd /home/usain/gov-os-worktrees/W2-05 || exit 9
STEM="$1"
LOG=/home/usain/gov-os-worktrees/W2-05/.gov-runtime/scratch/lead/log
rm -f "$LOG/$STEM.exit"
until [ ! -e /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/CLOSE-RUNNING ]; do sleep 60; done
until [ ! -e /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/NIGHTLY-RUNNING ]; do sleep 60; done
until awk '{exit !($1 < 20)}' /proc/loadavg; do sleep 60; done
bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/disk_gate.sh || { echo 97 > "$LOG/$STEM.exit"; exit 97; }
date > "$LOG/$STEM.start"
cat /proc/loadavg >> "$LOG/$STEM.start"
PYTHONPATH=/home/usain/gov-os-worktrees/W2-05/src python3 -c "import gov; print(gov.__file__)" > "$LOG/$STEM-import.txt" 2>&1
TMPDIR=/tmp/gov-os-lead-W2-05 PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-05/src python3 -m pytest tests/acceptance/W2-05 -q -p no:cacheprovider -rs > "$LOG/$STEM.txt" 2>&1
echo $? > "$LOG/$STEM.exit"
date >> "$LOG/$STEM.start"
