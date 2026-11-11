#!/bin/bash
L=/home/usain/gov-os-worktrees/W2-05/.gov-runtime/scratch/lead/log
cd /home/usain/gov-os-worktrees/W2-05 || exit 9
env TMPDIR=/tmp/gov-os-lead-W2-05 PYTHONPATH=/home/usain/gov-os-worktrees/W2-05/src gov accept W2-05 --root /home/usain/gov-os-worktrees/W2-05 > $L/accept-r8-before.log 2>&1
echo $? > $L/accept-r8-before.exit
