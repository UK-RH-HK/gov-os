#!/bin/bash
# Run 4's red check: W2-07's acceptance suite against this worktree's src, to its end.
cd /home/usain/gov-os-worktrees/W2-07 || exit 9
L=/home/usain/gov-os-worktrees/W2-07/.gov-runtime/scratch/lead/log
until [ ! -e /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/CLOSE-RUNNING ]; do sleep 60; done
until awk '{exit !($1 < 20)}' /proc/loadavg; do sleep 60; done
mkdir -p /tmp/gov-os-lead-W2-07
PYTHONPATH=/home/usain/gov-os-worktrees/W2-07/src python3 -c "import gov; print(gov.__file__)" > $L/red4.gov 2>&1
TMPDIR=/tmp/gov-os-lead-W2-07 PYTHONPATH=/home/usain/gov-os-worktrees/W2-07/src python3 -m pytest tests/acceptance/W2-07 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rs -n 6 --junitxml=$L/red4.xml > $L/red4.txt 2>&1
echo $? > $L/red4.exit
