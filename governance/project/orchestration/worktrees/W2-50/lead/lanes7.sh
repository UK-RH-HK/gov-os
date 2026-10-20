#!/bin/bash
# W2-50 run 8 verification: three lanes of verify3.sh, started together after the gates, results in log/v7/.
S=/home/usain/gov-os-worktrees/W2-50/.gov-runtime/scratch/lead
until [ ! -e /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/CLOSE-RUNNING ]; do sleep 60; done
until awk '{exit !($1 < 20)}' /proc/loadavg; do sleep 60; done
cat /proc/loadavg > $S/log/v7-start.txt
bash $S/verify3.sh v7 W1-30 W1-41 W1-05 W1-02 W1-19 > $S/log/v7-lane1.out 2>&1 &
bash $S/verify3.sh v7 W2-50 W1-16 W1-27 W1-26 W1-07 W1-47 W1-21 W1-50 W1-38 W1-46 unit > $S/log/v7-lane2.out 2>&1 &
bash $S/verify3.sh v7 W1-01 W1-03 W1-04 W1-06 W1-08 W1-09 W1-10 W1-11 W1-12 W1-13 W1-14 W1-15 W1-17 W1-18 W1-20 W1-22 W1-23 W1-24 W1-25 W1-28 W1-29 W1-31 W1-32 W1-33 W1-34 W1-35 W1-36 W1-37 W1-39 W1-40 W1-42 W1-44 W1-45 W1-48 W1-49 W2-01 W2-53 W2-54 > $S/log/v7-lane3.out 2>&1 &
wait
echo done > $S/log/v7-all.done
