#!/usr/bin/env bash
# Waits until any lead's output file in log/ (*-A5-*.json, written when its `claude -p` session ends) is non-empty and
# not yet seen, checked each minute; then prints its name, records it in log/returns-seen.txt and exits, so the
# orchestrator's session wakes (detached leads notify nobody). Re-arm after each return.
LOG=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/log
SEEN=$LOG/returns-seen.txt
touch "$SEEN"
while true; do
  for f in "$LOG"/*-A5-*.json; do
    [ -s "$f" ] || continue
    name=$(basename "$f")
    grep -qxF "$name" "$SEEN" && continue
    echo "$name" >> "$SEEN"
    echo "$(date '+%F %T') returned: $name"
    exit 0
  done
  sleep 60
done
