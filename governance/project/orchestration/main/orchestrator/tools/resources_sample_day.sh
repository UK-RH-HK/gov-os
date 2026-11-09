#!/usr/bin/env bash
# DEC-1105: W2-20's `gov resources --sample` over a working day (every 5 minutes, 8 hours), then `--remeasure`.
# Runs the merged integrate code (W2-20 is not on the pin until the lift's re-pin). Logs to log/resources-sample-day.log.
# Stop early: touch log/resources-sample-day.stop (the remeasure then runs on the samples taken).
set -u
ROOT=/home/usain/Dynamic-Agentic-Engineering-OS
LOG=$ROOT/.gov-runtime/scratch/orchestrator/log/resources-sample-day.log
STOP=$ROOT/.gov-runtime/scratch/orchestrator/log/resources-sample-day.stop
PY=/home/usain/.local/share/gov-os/pin-bcea09060ebc/bin/python
N=${N:-96}; EVERY=${EVERY:-300}
cd "$ROOT" || exit 2
echo "== $(date '+%F %T') start: $N samples every $EVERY s, code $(git rev-parse --short=9 HEAD)" >> "$LOG"
for i in $(seq 1 "$N"); do
  [ -e "$STOP" ] && { echo "-- $(date '+%T') stop file seen" >> "$LOG"; break; }
  out=$(PYTHONPATH=$ROOT/src "$PY" -m gov.cli.main resources --sample 2>&1); rc=$?
  echo "$(date '+%T') sample $i rc $rc $(echo "$out" | tail -1 | cut -c1-200)" >> "$LOG"
  sleep "$EVERY"
done
out=$(PYTHONPATH=$ROOT/src "$PY" -m gov.cli.main resources --remeasure 2>&1); rc=$?
echo "== $(date '+%F %T') remeasure rc $rc" >> "$LOG"; echo "$out" | tail -20 >> "$LOG"
exit "$rc"
