#!/bin/bash
# Lead's run-5 driver: waits for no close and a 1-minute load under 20, then the seven batches side by side
# (W1-30 and W1-41 each alone in a batch of their own), each suite in its own pytest process.
cd /home/usain/gov-os-worktrees/W2-02 || exit 2
OUT=/home/usain/gov-os-worktrees/W2-02/.gov-runtime/scratch/lead/log/suites5
R=/home/usain/gov-os-worktrees/W2-02/.gov-runtime/scratch/lead/run_suites5.sh
until [ ! -e /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/CLOSE-RUNNING ]; do sleep 60; done
until awk '{exit !($1 < 20)}' /proc/loadavg; do sleep 60; done
bash "$R" A W1-30 &
bash "$R" B W1-41 &
bash "$R" C W2-50 W1-05 W1-26 &
bash "$R" D W2-54 W1-27 W1-47 W1-21 &
bash "$R" E W1-02 W1-16 W1-07 W1-50 &
bash "$R" F W1-38 W2-01 W1-39 W1-03 W1-46 W1-04 W1-20 W1-19 W2-53 unit &
bash "$R" G W1-15 W1-08 W1-32 W1-17 W1-35 W1-40 W1-31 W1-25 W1-28 W1-13 W1-09 W1-49 W1-45 W1-11 W1-24 W1-10 W1-14 W2-62 W1-22 W1-18 W1-01 W1-36 W1-12 W2-02 W1-33 W1-29 W1-23 W1-44 W1-06 W1-48 W1-42 W1-37 W1-34 &
wait
echo done > "$OUT/all.done"
