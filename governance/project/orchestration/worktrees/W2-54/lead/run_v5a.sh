#!/bin/sh
# Round 4c verification, part A: a full rebuild, gov check right after it; a second full rebuild, then W2-54 alone
# (its green-here cases run gov check and the context check). Logs v5-*.
cd /home/usain/gov-os-worktrees/W2-54 || exit 2
L=/home/usain/gov-os-worktrees/W2-54/.gov-runtime/scratch/lead
LOG=$L/log
sh $L/run_place.sh "$LOG/v5a-place-before.txt"
sh $L/run_rebuild.sh rebuild11
git log --oneline -1 > "$LOG/v5-check.head"
uptime > "$LOG/v5-check.load"
PYTHONPATH=/home/usain/gov-os-worktrees/W2-54/src python3 -m gov.cli.main check --json > "$LOG/v5-check.json" 2> "$LOG/v5-check.err"
echo $? > "$LOG/v5-check.exit"
uptime >> "$LOG/v5-check.load"
sh $L/run_rebuild.sh rebuild12
sh $L/run_r3.sh v5 W2-54
sh $L/run_place.sh "$LOG/v5a-place-after.txt"
echo done > "$LOG/v5a.done"
