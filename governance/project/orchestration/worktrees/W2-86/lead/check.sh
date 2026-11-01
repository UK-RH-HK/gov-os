#!/bin/bash
# gov check --json and gov doctor --json on this worktree's code (DEC-732). usage: check.sh <tag>
cd /home/usain/gov-os-worktrees/W2-86 || exit 9
L=/home/usain/gov-os-worktrees/W2-86/.gov-runtime/scratch/lead/log
PYTHONPATH=/home/usain/gov-os-worktrees/W2-86/src python3 -m gov.cli.main check --json > "$L/check-$1.json" 2> "$L/check-$1.err"
echo $? > "$L/check-$1.exit"
PYTHONPATH=/home/usain/gov-os-worktrees/W2-86/src python3 -m gov.cli.main doctor --json > "$L/doctor-$1.json" 2> "$L/doctor-$1.err"
echo $? > "$L/doctor-$1.exit"
