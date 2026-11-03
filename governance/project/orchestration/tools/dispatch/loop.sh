#!/usr/bin/env bash
# A dispatcher pass every 60 s, for use only without the owner's crontab line. Start detached:
#   setsid -f bash /home/usain/Dynamic-Agentic-Engineering-OS/governance/project/orchestration/tools/dispatch/loop.sh
# One loop at a time (loop.lock in the state folder); stop it with: touch <state>/OFF, or kill the pid in loop.pid.
for v in $(compgen -v DISPATCH_); do unset "$v"; done   # no stray test variable reaches a real pass (review F3)
CODE=$(cd "$(dirname "$0")" && pwd)
STATE=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/dispatch
exec 9>>"$STATE/loop.lock"
flock -n 9 || { echo "$(date '+%F %T') loop: another loop runs" >> "$STATE/dispatch.log"; exit 0; }
echo $$ > "$STATE/loop.pid"
while true; do
  bash "$CODE/run_tick.sh" "$@"
  sleep 60
done
