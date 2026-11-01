#!/bin/bash
# The worktree's store, rebuilt with this worktree's own code (DEC-732, DEC-979 item 2), under the rebuild lock.
cd /home/usain/gov-os-worktrees/W2-97 || exit 9
rm -f /home/usain/gov-os-worktrees/W2-97/.gov-runtime/scratch/lead/log/rebuild.rc
PYTHONPATH=/home/usain/gov-os-worktrees/W2-97/src flock /tmp/gov-os-rebuild.lock python3 -m gov.cli.main rebuild --json > /home/usain/gov-os-worktrees/W2-97/.gov-runtime/scratch/lead/log/rebuild-$1.json 2>&1
echo $? > /home/usain/gov-os-worktrees/W2-97/.gov-runtime/scratch/lead/log/rebuild.rc
