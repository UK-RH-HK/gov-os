#!/usr/bin/env bash
# One dispatcher pass (cron `* * * * *` and `@reboot`, or loop.sh). Sets the PATH a cron job lacks.
export HOME=/home/usain
export PATH=/home/usain/.local/bin:/home/usain/.nvm/versions/node/v22.23.3/bin:/usr/local/bin:/usr/bin:/bin
D=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/dispatch
[ -f "$D/OFF" ] && exit 0   # the CTO's off switch: a file named OFF here stops every pass
cd "$D" || exit 2
/usr/bin/python3 "$D/dispatcher.py" tick "$@" >> "$D/dispatch.log" 2>&1
