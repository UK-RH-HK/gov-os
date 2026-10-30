#!/bin/bash
# The lead's red check of tests/acceptance/W2-84 (this worktree's src, DEC-732).
cd /home/usain/gov-os-worktrees/W2-84 || exit 2
ORCH=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator
LOG=/home/usain/gov-os-worktrees/W2-84/.gov-runtime/scratch/lead/log
while [ -e "$ORCH/CLOSE-RUNNING" ] || [ -e "$ORCH/NIGHTLY-RUNNING" ]; do sleep 60; done
mkdir -p /tmp/gov-os-lead-W2-84
PYTHONPATH=/home/usain/gov-os-worktrees/W2-84/src python3 -c "import gov; print(gov.__file__)" > "$LOG/red.out" 2>&1
cat /proc/loadavg >> "$LOG/red.out"
TMPDIR=/tmp/gov-os-lead-W2-84 PYTHONPATH=/home/usain/gov-os-worktrees/W2-84/src python3 -m pytest tests/acceptance/W2-84 -q -p no:cacheprovider -rs -o tmp_path_retention_policy=failed --junitxml="$LOG/red.xml" >> "$LOG/red.out" 2>&1
echo $? > "$LOG/red.rc"
