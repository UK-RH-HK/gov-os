#!/usr/bin/env bash
# r4: gov accept DAEO-zpdj --json, once, to the end; output and exit code into the lead's log folder
set -u
L=/home/usain/gov-os-worktrees/W2-105/.gov-runtime/scratch/lead/log
echo $$ > "$L/accept-r4.pid"
rm -f "$L/accept-r4.exit"
env TMPDIR=/tmp/gov-os-lead-W2-105 PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH \
  gov accept DAEO-zpdj --root /home/usain/gov-os-worktrees/W2-105 --json > "$L/accept-r4.json" 2> "$L/accept-r4.err"
echo $? > "$L/accept-r4.exit"
