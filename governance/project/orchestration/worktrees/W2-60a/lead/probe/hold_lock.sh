#!/bin/bash
# Take the machine-wide verification lock in the queue (at most 45 minutes), then hold it for the lead's run.
# Inside the lock (hold_inner.sh): wait for the other gates, mark the lock as held, and keep it until both phases of
# the run have written their exit files or the lead writes hold.release.
flock -E 75 -w 2700 /tmp/gov-os-verify.lock bash /home/usain/gov-os-worktrees/W2-60a/.gov-runtime/scratch/lead/probe/hold_inner.sh "$1"
echo "exit $?" > /home/usain/gov-os-worktrees/W2-60a/.gov-runtime/scratch/lead/log/hold$1.exit
