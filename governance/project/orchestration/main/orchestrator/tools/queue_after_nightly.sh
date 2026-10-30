#!/usr/bin/env bash
# Starts the close queue once tonight's nightly is over (DEC-933 item 5: closes resume after it): waits until 03:00,
# then until NIGHTLY-RUNNING has been absent for 5 minutes in a row, then runs close_queue.sh with the given tickets
# (which takes its own lock and waits for quiet). Usage: queue_after_nightly.sh <tk id> [<tk id> ...]
ORCH=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator
until [ "$(date +%H%M)" -ge 0300 ] && [ "$(date +%H%M)" -lt 1200 ]; do sleep 60; done
clear=0
while [ "$clear" -lt 5 ]; do
  if [ -e "$ORCH/NIGHTLY-RUNNING" ]; then clear=0; else clear=$((clear + 1)); fi
  sleep 60
done
echo "$(date '+%F %T') nightly clear; starting the close queue: $*" >&2
exec bash "$ORCH/tools/close_queue.sh" "$@"
