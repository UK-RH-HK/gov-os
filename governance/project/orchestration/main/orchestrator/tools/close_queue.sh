#!/usr/bin/env bash
# The close queue in one quiet window (DEC-780, DEC-806): hold the leads with the close lock, wait until their
# running batches have ended, then for each ticket in order: a full rebuild immediately before, `gov close` once.
# The queue stops at the first refusal (a shared cause must not spend another ticket's one attempt). Nothing is
# committed by this script. Literal paths only.
cd /home/usain/Dynamic-Agentic-Engineering-OS || exit 1
LOG=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/log/close-queue-2026-10-20
LOCK=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/CLOSE-RUNNING
mkdir -p "$LOG"
date '+%F %T close queue: lock set' > "$LOCK"
# Quiet: the 1-minute load under 3 for five checks in a row, a minute apart (the leads' running batches done).
quiet=0
while [ "$quiet" -lt 5 ]; do
  if awk '{exit !($1 < 3)}' /proc/loadavg; then quiet=$((quiet + 1)); else quiet=0; fi
  sleep 60
done
date '+%F %T quiet' >> "$LOG/queue.txt"
for ticket in DAEO-7rr2 DAEO-0rfi; do
  date '+%F %T rebuild before '"$ticket" >> "$LOG/queue.txt"
  gov rebuild > "$LOG/rebuild-$ticket.json" 2> "$LOG/rebuild-$ticket.err"; echo $? > "$LOG/rebuild-$ticket.exit"
  date '+%F %T close '"$ticket"' (load '"$(cut -d' ' -f1 /proc/loadavg)"')' >> "$LOG/queue.txt"
  gov close "$ticket" --json > "$LOG/close-$ticket.json" 2> "$LOG/close-$ticket.err"; code=$?
  echo "$code" > "$LOG/close-$ticket.exit"
  date '+%F %T close '"$ticket"' exit '"$code" >> "$LOG/queue.txt"
  [ "$code" -eq 0 ] || break
done
rm -f "$LOCK"
date '+%F %T lock removed' >> "$LOG/queue.txt"
