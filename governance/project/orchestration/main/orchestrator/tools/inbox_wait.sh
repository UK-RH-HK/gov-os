#!/usr/bin/env bash
# Wakes the CTO's session when the dispatcher's inbox holds an unread item (DEC-1007): checks every 30 s, prints the
# unread item names and exits. Read-only: it never marks a return seen (the dispatcher alone does that), so it can
# never race the dispatcher. If the CTO forgets to re-arm it, the dispatcher's 30-minute stale-inbox file makes the
# sentinel push to the owner's phone; so nothing depends on this script. Usage: inbox_wait.sh
IN=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/dispatch/inbox
while true; do
  items=$(find "$IN" -maxdepth 1 -type f -name '*.txt' 2>/dev/null | sort)
  if [ -n "$items" ]; then
    echo "$(date '+%F %T') inbox:"; echo "$items" | sed 's#.*/#  #'
    exit 0
  fi
  sleep 30
done
