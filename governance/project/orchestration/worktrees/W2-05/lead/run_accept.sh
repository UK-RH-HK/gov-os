#!/usr/bin/env bash
# gov accept W2-05 on this tree; $1 = label (baseline, after, ...)
L=/home/usain/gov-os-worktrees/W2-05/.gov-runtime/scratch/lead/log
label=${1:-run}
mkdir -p /tmp/gov-os-lead-W2-05
rm -f "$L/accept-$label.exit"
env TMPDIR=/tmp/gov-os-lead-W2-05 PYTHONPATH=/home/usain/gov-os-worktrees/W2-05/src gov accept W2-05 --root /home/usain/gov-os-worktrees/W2-05 > "$L/accept-$label.log" 2>&1
echo $? > "$L/accept-$label.exit"
