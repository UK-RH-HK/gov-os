#!/bin/sh
# Run 5 verification, the rest after run_v6.sh reached the two-hour limit inside W2-50: W2-50; W1-30 and W1-41
# side by side; the builder tests; the pre-close gate's collection. Logs v7-*; the end is v7-collect.exit.
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
sh $R v7a W2-50
quiet
sh $R v7b W1-30 &
sh $R v7c W1-41 &
wait
quiet
uptime > "$LOG/v7-unit.load"
PYTHONPATH=/home/usain/gov-os-worktrees/W2-54/src python3 -m pytest tests/unit -q -p no:cacheprovider > "$LOG/v7-unit.txt" 2>&1
echo $? > "$LOG/v7-unit.exit"
uptime >> "$LOG/v7-unit.load"
PYTHONPATH=/home/usain/gov-os-worktrees/W2-54/src python3 -c "import gov; print(gov.__file__)" > "$LOG/v7-import.txt"
PYTHONPATH=/home/usain/gov-os-worktrees/W2-54/src python3 -m pytest tests --collect-only -q -p no:cacheprovider --no-header > "$LOG/v7-collect.txt" 2>&1
echo $? > "$LOG/v7-collect.exit"
