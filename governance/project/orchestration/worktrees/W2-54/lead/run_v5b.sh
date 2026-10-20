#!/bin/sh
# Round 4c verification, part B: every other acceptance suite but W1-30 and W1-41, each in its own pytest process,
# three groups side by side; then the builder tests.
cd /home/usain/gov-os-worktrees/W2-54 || exit 2
L=/home/usain/gov-os-worktrees/W2-54/.gov-runtime/scratch/lead
LOG=$L/log
R=$L/run_r3.sh
sh $R v5g1 W1-01 W1-02 W1-03 W1-04 W1-05 W1-06 W1-07 W1-08 W1-09 W1-10 W1-11 W1-12 W1-13 W1-14 W1-15 W1-16 &
sh $R v5g2 W1-46 W1-17 W1-18 W1-19 W1-20 W1-22 W1-23 W1-24 W1-25 W1-26 W1-27 W1-28 W1-29 W1-31 &
sh $R v5g3 W1-21 W1-32 W1-33 W1-34 W1-35 W1-36 W1-37 W1-38 W1-39 W1-40 W1-42 W1-44 W1-45 W1-47 W1-48 W1-49 W1-50 W2-01 W2-53 &
wait
sh $L/run_place.sh "$LOG/v5b-place-after.txt"
uptime > "$LOG/v5-unit.load"
PYTHONPATH=/home/usain/gov-os-worktrees/W2-54/src python3 -m pytest tests/unit -q -p no:cacheprovider > "$LOG/v5-unit.txt" 2>&1
echo $? > "$LOG/v5-unit.exit"
uptime >> "$LOG/v5-unit.load"
echo done > "$LOG/v5b.done"
