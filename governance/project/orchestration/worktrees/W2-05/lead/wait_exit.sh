#!/bin/bash
# Wait up to $1 seconds until file $2 is non-empty; print its content or "waiting", then the load and time.
END=$(( $(date +%s) + $1 ))
while [ "$(date +%s)" -lt "$END" ] && [ ! -s "$2" ]; do sleep 20; done
if [ -s "$2" ]; then echo "ready: $(cat "$2")"; else echo "waiting: $2"; fi
cat /proc/loadavg; date
