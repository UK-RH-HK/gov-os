#!/bin/bash
# Red check of review 4's W1 cases (R16) on the merged head, this worktree's code (DEC-732).
cd /home/usain/gov-os-worktrees/W2-96 || exit 9
L=/home/usain/gov-os-worktrees/W2-96/.gov-runtime/scratch/lead/log
date -u +%FT%TZ > "$L/red-r5.start"
PYTHONPATH=/home/usain/gov-os-worktrees/W2-96/src python3 -c "import gov; print(gov.__file__)" > "$L/govfile5.txt" 2>&1
TMPDIR=/tmp/gov-os-lead-W2-96 PYTHONPATH=/home/usain/gov-os-worktrees/W2-96/src python3 -m pytest tests/acceptance/W2-96 -q -p no:cacheprovider -o tmp_path_retention_policy=failed --tb=line -rf > "$L/red-r5.out" 2>&1
echo $? > "$L/red-r5.exit"
