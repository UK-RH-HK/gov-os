#!/bin/sh
# Round 4 verification: a full rebuild, gov check alone right after it, then every acceptance suite (each in its own
# pytest process, four groups side by side) and the builder tests. Logs v4-*.
cd /home/usain/gov-os-worktrees/W2-54 || exit 2
LOG=/home/usain/gov-os-worktrees/W2-54/.gov-runtime/scratch/lead/log
R=/home/usain/gov-os-worktrees/W2-54/.gov-runtime/scratch/lead/run_r3.sh
sh /home/usain/gov-os-worktrees/W2-54/.gov-runtime/scratch/lead/run_rebuild.sh rebuild10
git log --oneline -1 > "$LOG/v4-check.head"
uptime > "$LOG/v4-check.load"
PYTHONPATH=/home/usain/gov-os-worktrees/W2-54/src python3 -m gov.cli.main check --json > "$LOG/v4-check.json" 2> "$LOG/v4-check.err"
echo $? > "$LOG/v4-check.exit"
uptime >> "$LOG/v4-check.load"
sh $R v4 W1-41 W1-01 W1-02 W1-03 W1-04 W1-05 W1-06 W1-07 W1-08 W1-09 W1-10 &
sh $R v4 W1-30 W1-11 W1-12 W1-13 W1-14 W1-15 W1-16 W1-17 W1-18 W1-19 W1-20 &
sh $R v4 W1-46 W1-21 W1-22 W1-23 W1-24 W1-25 W1-26 W1-27 W1-28 W1-29 W1-31 W1-32 W1-33 W1-34 W1-35 &
sh $R v4 W2-54 W1-36 W1-37 W1-38 W1-39 W1-40 W1-42 W1-44 W1-45 W1-47 W1-48 W1-49 W1-50 W2-01 W2-53 &
wait
uptime > "$LOG/v4-unit.load"
PYTHONPATH=/home/usain/gov-os-worktrees/W2-54/src python3 -m pytest tests/unit -q -p no:cacheprovider > "$LOG/v4-unit.txt" 2>&1
echo $? > "$LOG/v4-unit.exit"
echo done > "$LOG/v4-all.done"
