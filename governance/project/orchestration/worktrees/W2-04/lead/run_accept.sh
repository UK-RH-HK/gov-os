#!/usr/bin/env bash
# One `gov accept W2-04` (the pinned judge, this tree as root), with an exit-code file (lead, DAEO-u4oz review run).
L=/home/usain/gov-os-worktrees/W2-04/.gov-runtime/scratch/lead/log
rm -f "$L/accept.exit"
cd /home/usain/gov-os-worktrees/W2-04 || exit 2
env TMPDIR=/tmp/gov-os-lead-W2-04 gov accept W2-04 --root /home/usain/gov-os-worktrees/W2-04 > "$L/accept.out" 2> "$L/accept.err"
echo $? > "$L/accept.exit"
