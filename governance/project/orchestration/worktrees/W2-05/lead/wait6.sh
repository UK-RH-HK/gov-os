#!/bin/bash
# Wait up to $2 seconds (default 540) until every file named after it ($3...) is non-empty; print which are.
LIMIT="${1:-540}"; shift
END=$(( $(date +%s) + LIMIT ))
while [ "$(date +%s)" -lt "$END" ]; do
  ALL=1
  for f in "$@"; do grep -q "\"session_id\"" "$f" 2>/dev/null || ALL=0; done
  [ "$ALL" = 1 ] && break
  sleep 20
done
for f in "$@"; do if grep -q "\"session_id\"" "$f" 2>/dev/null; then echo "ready: $f"; else echo "waiting: $f"; fi; done
cat /proc/loadavg
