#!/usr/bin/env bash
# Runs a dispatcher pass every 60 s forever (until the owner's cron line replaces it). Start detached:
#   setsid -f bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/dispatch/loop.sh
# One loop at a time (loop.lock); stop it with: touch dispatch/OFF (passes stop) or kill the loop's pid (loop.pid).
D=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/dispatch
exec 9>>"$D/loop.lock"
flock -n 9 || { echo "$(date '+%F %T') loop: another loop runs" >> "$D/dispatch.log"; exit 0; }
echo $$ > "$D/loop.pid"
while true; do
  bash "$D/run_tick.sh" "$@"
  sleep 60
done
