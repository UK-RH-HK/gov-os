#!/usr/bin/env bash
# The memory floor's guard (owner, DEC-947 item 5): with the floor at 3 GiB, if MemAvailable ever falls below 2 GiB, or
# the kernel journal shows an out-of-memory kill since this watch started, the floor goes back to 6.4 GiB at once
# (gate-config.json) and the event is logged to log/oom-watch.txt for the next package. Checked every 30 seconds.
ORCH=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator
CFG=$ORCH/tools/gate-config.json
OUT=$ORCH/log/oom-watch.txt
START=$(date '+%Y-%m-%d %H:%M:%S')
echo "$(date '+%F %T') watch started (floor 3 GiB; trip below 2 GiB available or on an OOM kill; rg tripwire at ${RG_TRIP:=200})" >> "$OUT"
INBOX=$ORCH/dispatch/inbox
RG_LAST=0
# The rg tripwire (owner, DEC-1132 (3) (a), row 142): on 11-11 at 14:19, 2,161 ripgrep processes held 19.3 GB and WSL ran
# out of memory, and nothing recorded who started them. Above RG_TRIP rg processes, one inbox item (at most every 10
# minutes) with the count, the memory left and each distinct parent (pid, command, cwd) with its child count, so the
# spawner is known. It stops nothing: a stop is by pid and is a decision (L-0075, DEC-1073).
rg_check() {
  local n now f
  n=$(ps -eo comm= | grep -cx rg)
  [ "${n:-0}" -le "$RG_TRIP" ] && return 0
  now=$(date +%s); [ $((now - RG_LAST)) -lt 600 ] && return 0
  RG_LAST=$now
  f="$INBOX/$(date '+%Y%m%d-%H%M%S')-rg-tripwire.txt"
  {
    echo "log: oom-watch.txt"
    echo "Memory: rg tripwire"
    echo "status: P1: $n rg processes running (trip at $RG_TRIP); MemAvailable $(awk '/MemAvailable/{print $2}' /proc/meminfo) kB"
    echo
    echo "parents (child count, pid, cwd, command):"
    ps -eo ppid=,comm= | awk '$2=="rg"{print $1}' | sort | uniq -c | sort -rn | head -10 | while read -r c p; do
      echo "  $c  $p  $(readlink /proc/$p/cwd 2>/dev/null)  $(tr '\0' ' ' < /proc/$p/cmdline 2>/dev/null | cut -c1-200)"
    done
  } > "$f"
  echo "$(date '+%F %T') RG TRIPWIRE: $n rg processes; item $f" >> "$OUT"
}
TRIPPED=0
while true; do
  rg_check
  avail=$(awk '/MemAvailable/{print $2}' /proc/meminfo)
  # Only a machine-wide kill counts (constraint=CONSTRAINT_NONE). A kill inside a capped cgroup (CONSTRAINT_MEMCG, e.g.
  # a MemoryMax test scope) is that scope working as designed: it tripped this watch falsely at 15:23:34 on 11-11.
  ooms=$(journalctl -k --since "$START" --no-pager 2>/dev/null | grep -c "oom-kill:constraint=CONSTRAINT_NONE")
  if [ "$TRIPPED" = 0 ] && { [ "$avail" -lt 2097152 ] || [ "${ooms:-0}" -gt 0 ]; }; then
    python3 -c 'import json,sys; p=sys.argv[1]; c=json.load(open(p)); c["floor_kb"]=6710886; c["floor_note"]="put back to 6.4 GiB by oom_watch.sh (DEC-947 item 5)"; json.dump(c,open(p,"w"),indent=2)' "$CFG"
    echo "$(date '+%F %T') TRIPPED: MemAvailable ${avail} kB, global OOM lines ${ooms}; floor put back to 6,710,886 kB" >> "$OUT"
    journalctl -k --since "$START" --no-pager 2>/dev/null | grep -i "out of memory\|oom-kill" | tail -5 >> "$OUT"
    TRIPPED=1  # the floor is reset once; the watch keeps running so the rg tripwire stays on
  fi
  sleep 30
done
