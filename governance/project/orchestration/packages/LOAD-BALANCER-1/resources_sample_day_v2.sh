#!/usr/bin/env bash
# PROPOSED, NOT RUN (helper, 11-11 window package). A sample day for DEC-1105 that differs from tools/resources_sample_day.sh in three ways:
#  1. it uses the current pin's own code (pin-797495bdfc70, where W2-20 now lives), not pin-bcea09060ebc plus the main tree's src;
#  2. it does NOT run --remeasure at the end: the CTO reads the samples first (see samples_summary.py), then runs it by hand;
#  3. it writes its own pid to <LOG>.pid so that it is stopped by pid (tools/proc.sh), never by name.
# Usage (CTO, detached):  setsid -f bash <this file>      Stop early: touch log/resources-sample-day.stop
set -u
ROOT=/home/usain/Dynamic-Agentic-Engineering-OS
ORCH=$ROOT/.gov-runtime/scratch/orchestrator
LOG=$ORCH/log/resources-sample-day.log
STOP=$ORCH/log/resources-sample-day.stop
PY=/home/usain/.local/share/gov-os/pin-797495bdfc70/bin/python
N=${N:-96}; EVERY=${EVERY:-300}
cd "$ROOT" || exit 2
echo "$$" > "$LOG.pid"
rm -f "$STOP"
echo "== $(date '+%F %T') start: $N samples every $EVERY s, pinned gov (pin-797495bdfc70), no remeasure at the end" >> "$LOG"
for i in $(seq 1 "$N"); do
  [ -e "$STOP" ] && { echo "-- $(date '+%T') stop file seen" >> "$LOG"; break; }
  out=$("$PY" -m gov.cli.main resources --sample 2>&1); rc=$?
  echo "$(date '+%T') sample $i rc $rc $(echo "$out" | tail -1 | cut -c1-200)" >> "$LOG"
  sleep "$EVERY"
done
echo "== $(date '+%F %T') done; next: read samples (samples_summary.py), then gov resources --remeasure by hand" >> "$LOG"
rm -f "$LOG.pid"
