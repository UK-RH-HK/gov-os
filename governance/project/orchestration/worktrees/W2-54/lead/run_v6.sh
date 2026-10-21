#!/bin/sh
# Run 5 verification (DEC-874): a full rebuild, gov check right after it, W2-54 alone; then every other acceptance
# suite, each in its own pytest process, three groups side by side; W1-30 and W1-41 alone; the builder tests; the
# pre-close gate's collection. Each heavy step waits for no close and a 1-minute load under 20. Logs v6-*.
cd /home/usain/gov-os-worktrees/W2-54 || exit 2
L=/home/usain/gov-os-worktrees/W2-54/.gov-runtime/scratch/lead
LOG=$L/log
R=$L/run_r3.sh
FLAG=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/CLOSE-RUNNING
quiet() {
  until [ ! -e $FLAG ]; do sleep 60; done
  until awk '{exit !($1 < 20)}' /proc/loadavg; do sleep 60; done
}
quiet
sh $L/run_place.sh "$LOG/v6-place-before.txt"
sh $L/run_rebuild.sh rebuild13
git log --oneline -1 > "$LOG/v6-check.head"
uptime > "$LOG/v6-check.load"
PYTHONPATH=/home/usain/gov-os-worktrees/W2-54/src python3 -m gov.cli.main check --json > "$LOG/v6-check.json" 2> "$LOG/v6-check.err"
echo $? > "$LOG/v6-check.exit"
uptime >> "$LOG/v6-check.load"
quiet
sh $R v6 W2-54
quiet
sh $R v6g1 W1-01 W1-02 W1-03 W1-04 W1-05 W1-06 W1-07 W1-08 W1-09 W1-10 W1-11 W1-12 W1-13 W1-14 W1-15 W1-16 W2-50 &
sh $R v6g2 W1-46 W1-17 W1-18 W1-19 W1-20 W1-22 W1-23 W1-24 W1-25 W1-26 W1-27 W1-28 W1-29 W1-31 W2-62 &
sh $R v6g3 W1-21 W1-32 W1-33 W1-34 W1-35 W1-36 W1-37 W1-38 W1-39 W1-40 W1-42 W1-44 W1-45 W1-47 W1-48 W1-49 W1-50 W2-01 W2-53 &
wait
quiet
sh $R v6w30 W1-30
quiet
sh $R v6w41 W1-41
sh $L/run_place.sh "$LOG/v6-place-after.txt"
quiet
uptime > "$LOG/v6-unit.load"
PYTHONPATH=/home/usain/gov-os-worktrees/W2-54/src python3 -m pytest tests/unit -q -p no:cacheprovider > "$LOG/v6-unit.txt" 2>&1
echo $? > "$LOG/v6-unit.exit"
uptime >> "$LOG/v6-unit.load"
PYTHONPATH=/home/usain/gov-os-worktrees/W2-54/src python3 -m pytest tests --collect-only -q -p no:cacheprovider --no-header > "$LOG/v6-collect.txt" 2>&1
echo $? > "$LOG/v6-collect.exit"
PYTHONPATH=/home/usain/gov-os-worktrees/W2-54/src python3 -c "import gov; print(gov.__file__)" > "$LOG/v6-import.txt"
echo done > "$LOG/v6.done"
