#!/bin/bash
# The lead's full rebuild of this worktree's store, with this worktree's own code (DEC-732), in a heavy-job slot
# with this tree's own lock (DEC-1001 (d), tools/rebuild_slot.sh). Argument: the run's number.
N=${1:-1}
cd /home/usain/gov-os-worktrees/W2-91 || exit 90
export TMPDIR=/tmp/gov-os-lead-W2-91
date -u +%FT%TZ > /home/usain/gov-os-worktrees/W2-91/.gov-runtime/scratch/lead/log/rebuild-$N.start
PYTHONPATH=/home/usain/gov-os-worktrees/W2-91/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/rebuild_slot.sh /home/usain/gov-os-worktrees/W2-91 > /home/usain/gov-os-worktrees/W2-91/.gov-runtime/scratch/lead/log/rebuild-$N.json 2> /home/usain/gov-os-worktrees/W2-91/.gov-runtime/scratch/lead/log/rebuild-$N.err
echo $? > /home/usain/gov-os-worktrees/W2-91/.gov-runtime/scratch/lead/log/rebuild-$N.exit
date -u +%FT%TZ > /home/usain/gov-os-worktrees/W2-91/.gov-runtime/scratch/lead/log/rebuild-$N.end
