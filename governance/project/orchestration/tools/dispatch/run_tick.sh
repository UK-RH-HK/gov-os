#!/usr/bin/env bash
# One dispatcher pass (the owner's crontab, every minute; or loop.sh). The code is this folder (committed, DEC-1010
# item 6); the state is the scratch folder below. Sets the PATH a cron job lacks.
export HOME=/home/usain
export PATH=/home/usain/.local/bin:/home/usain/.nvm/versions/node/v22.23.3/bin:/usr/local/bin:/usr/bin:/bin
for v in $(compgen -v DISPATCH_); do unset "$v"; done   # no stray test variable reaches a real pass (review F3)
CODE=$(cd "$(dirname "$0")" && pwd)
STATE=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/dispatch
mkdir -p "$STATE"
[ -f "$STATE/OFF" ] && exit 0   # the CTO's off switch: a file named OFF in the state folder stops every pass
cd "$STATE" || exit 2
/usr/bin/python3 "$CODE/dispatcher.py" tick "$@" >> "$STATE/dispatch.log" 2>&1
