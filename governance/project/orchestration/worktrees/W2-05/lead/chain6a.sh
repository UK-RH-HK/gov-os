#!/bin/bash
# Run 6, part A: after the rebuild has ended, the scoped parallel run (its own background job, its own 2 h).
S=/home/usain/gov-os-worktrees/W2-05/.gov-runtime/scratch/lead
LOG=$S/log/v6
until [ -s "$LOG/rebuild.exit" ]; do sleep 30; done
bash $S/verify6.sh parallel
echo done > "$LOG/chainA.done"
