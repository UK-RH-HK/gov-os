#!/usr/bin/env bash
# Wait until the 1-minute load is under 20 and 4 GiB are available, at most 40 minutes.
for i in $(seq 1 120); do
  load=$(cut -d' ' -f1 /proc/loadavg)
  avail=$(free -g | awk 'NR==2 {print $7}')
  if awk -v l="$load" 'BEGIN {exit !(l < 20)}' && [ "$avail" -ge 4 ]; then
    echo "ready load=$load avail=${avail}G after $i checks"
    exit 0
  fi
  sleep 20
done
echo "still busy load=$(cat /proc/loadavg)"
exit 1
