#!/bin/bash
# LIFT-CLOSES-1's five ready closes, one at a time, in order (W2-123 before W2-126; W2-96 last, never from a shell
# that ignores SIGHUP: its signal cases would show three false reds). Stops at the first refused close.
# Usage: lift_closes_1.sh   (log: log/lift-closes-1.log)
cd /home/usain/Dynamic-Agentic-Engineering-OS || exit 2
LOG=.gov-runtime/scratch/orchestrator/log/lift-closes-1.log
ign=$(awk '/^SigIgn:/{print $2}' /proc/self/status)
echo "$(date -u '+%F %T') start; SigIgn=$ign; gov=$(readlink -f ~/.local/bin/gov)" | tee -a "$LOG"
for t in DAEO-blwa DAEO-qzrq DAEO-jpr0 DAEO-n0wb DAEO-ouet; do
  if [ "$t" = DAEO-ouet ] && [ $(( 0x$ign & 1 )) -ne 0 ]; then
    echo "$(date -u '+%F %T') SKIP $t: this shell ignores SIGHUP; close it from a plain shell" | tee -a "$LOG"; continue
  fi
  # The close refuses a store of another commit (STORE_STALE); each close's own commit moves the head.
  echo "$(date -u '+%F %T') rebuild at $(git rev-parse --short HEAD)" | tee -a "$LOG"
  gov rebuild >> "$LOG" 2>&1 || { echo "STOP: rebuild rc=$? before $t" | tee -a "$LOG"; exit 3; }
  echo "$(date -u '+%F %T') close $t" | tee -a "$LOG"
  gov close "$t" >> "$LOG" 2>&1; rc=$?
  echo "$(date -u '+%F %T') $t rc=$rc; head $(git rev-parse --short HEAD)" | tee -a "$LOG"
  [ $rc -ne 0 ] && { echo "STOP at $t" | tee -a "$LOG"; exit $rc; }
done
echo "$(date -u '+%F %T') ALL DONE" | tee -a "$LOG"
