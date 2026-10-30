#!/usr/bin/env bash
# The memory floor's guard (owner, DEC-947 item 5): with the floor at 3 GiB, if MemAvailable ever falls below 2 GiB, or
# the kernel journal shows an out-of-memory kill since this watch started, the floor goes back to 6.4 GiB at once
# (gate-config.json) and the event is logged to log/oom-watch.txt for the next package. Checked every 30 seconds.
ORCH=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator
CFG=$ORCH/tools/gate-config.json
OUT=$ORCH/log/oom-watch.txt
START=$(date '+%Y-%m-%d %H:%M:%S')
echo "$(date '+%F %T') watch started (floor 3 GiB; trip below 2 GiB available or on an OOM kill)" >> "$OUT"
while true; do
  avail=$(awk '/MemAvailable/{print $2}' /proc/meminfo)
  ooms=$(journalctl -k --since "$START" --no-pager 2>/dev/null | grep -ci "out of memory\|oom-kill\|oom_reaper")
  if [ "$avail" -lt 2097152 ] || [ "${ooms:-0}" -gt 0 ]; then
    python3 -c 'import json,sys; p=sys.argv[1]; c=json.load(open(p)); c["floor_kb"]=6710886; c["floor_note"]="put back to 6.4 GiB by oom_watch.sh (DEC-947 item 5)"; json.dump(c,open(p,"w"),indent=2)' "$CFG"
    echo "$(date '+%F %T') TRIPPED: MemAvailable ${avail} kB, OOM lines ${ooms}; floor put back to 6,710,886 kB" >> "$OUT"
    journalctl -k --since "$START" --no-pager 2>/dev/null | grep -i "out of memory\|oom-kill" | tail -5 >> "$OUT"
    exit 0
  fi
  sleep 30
done
