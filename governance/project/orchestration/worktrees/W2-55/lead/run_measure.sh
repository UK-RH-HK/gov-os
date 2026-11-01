#!/bin/bash
# W2-61's measure, visible half only, on the head clone's store: the base's code (control), then this ticket's code.
BIN=/tmp/claude-1000/-home-usain-gov-os-worktrees-W2-55/6da4b34e-432d-4c67-aca8-152864ff266c/scratchpad/bin
LOG=/home/usain/gov-os-worktrees/W2-55/.gov-runtime/scratch/lead/log
mkdir -p /home/usain/gov-os-runs/W2-55/records
cd /home/usain/gov-os-runs/W2-55/head || exit 99
env -u GOV_TICKET PYTHONPATH=/home/usain/gov-os-runs/W2-55/measure/src python3 -m gov.retrieval.measure memory-retrieval \
  --root /home/usain/gov-os-runs/W2-55/head --sets-root /home/usain/gov-os-runs/W2-55/measure --part visible \
  --gov "$BIN/gov-base" --out /home/usain/gov-os-runs/W2-55/records --json > "$LOG/measure-control.json" 2> "$LOG/measure-control.err"
echo "control exit $?" > "$LOG/measure-status.txt"
CONTROL=$(ls -t /home/usain/gov-os-runs/W2-55/records/*.json | head -1)
echo "control record $CONTROL" >> "$LOG/measure-status.txt"
env -u GOV_TICKET PYTHONPATH=/home/usain/gov-os-runs/W2-55/measure/src python3 -m gov.retrieval.measure memory-retrieval \
  --root /home/usain/gov-os-runs/W2-55/head --sets-root /home/usain/gov-os-runs/W2-55/measure --part visible \
  --gov "$BIN/gov-head" --out /home/usain/gov-os-runs/W2-55/records --json --compare "$CONTROL" > "$LOG/measure-head.json" 2> "$LOG/measure-head.err"
echo "head exit $?" >> "$LOG/measure-status.txt"
ls -t /home/usain/gov-os-runs/W2-55/records/*.json | head -1 >> "$LOG/measure-status.txt"
echo done >> "$LOG/measure-status.txt"
