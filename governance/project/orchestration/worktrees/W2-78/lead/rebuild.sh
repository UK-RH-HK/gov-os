#!/bin/bash
# The store rebuild in this worktree: disk gate, then one full rebuild under the machine's rebuild lock; exit code to a file.
L=/home/usain/gov-os-worktrees/W2-78/.gov-runtime/scratch/lead/log
cd /home/usain/gov-os-worktrees/W2-78 || exit 9
bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/disk_gate.sh > "$L/disk-gate-rebuild.txt" 2>&1 || { echo 8 > "$L/rebuild.exit"; exit 8; }
PYTHONPATH=/home/usain/gov-os-worktrees/W2-78/src TMPDIR=/tmp/gov-os-lead-W2-78 flock /tmp/gov-os-rebuild.lock python3 -m gov.cli.main rebuild --json > "$L/rebuild.json" 2> "$L/rebuild.err"
echo $? > "$L/rebuild.exit"
