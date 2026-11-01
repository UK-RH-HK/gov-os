#!/bin/bash
# Run 6: after the rebuild, the scoped parallel run, the serial run, the re-run of reds, then gov check.
S=/home/usain/gov-os-worktrees/W2-05/.gov-runtime/scratch/lead
LOG=$S/log/v6
until [ -s "$LOG/rebuild.exit" ]; do sleep 30; done
bash $S/verify6.sh parallel
bash $S/verify6.sh serial
bash $S/rerun6.sh
cd /home/usain/gov-os-worktrees/W2-05 || exit 9
PYTHONPATH=/home/usain/gov-os-worktrees/W2-05/src python3 -m gov.cli.main check --json > "$LOG/check.json" 2> "$LOG/check.err"
echo $? > "$LOG/check.exit"
echo done > "$LOG/chain.done"
