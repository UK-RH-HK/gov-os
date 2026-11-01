#!/usr/bin/env bash
# Starts ready-list entries now, past the dispatcher's memory admission, on the owner's explicit order only
# (DEC-1018: W2-122 and W2-123 ahead of every other lead). Everything else is the dispatcher's own start: its
# readiness checks were run by the CTO first, the start is recorded in started.txt before the launch (so no pass starts
# it twice and its return is collected), the same launcher, under tick.lock so no pass runs meanwhile, 120 s apart.
# Usage: start_owner_order.sh "<W2> <ticket> <brief> <log>" ...
set -u
ORCH=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator
D=$ORCH/dispatch
CODE=/home/usain/Dynamic-Agentic-Engineering-OS/governance/project/orchestration/tools/dispatch
first=1
for entry in "$@"; do
  read -r w2 tid brief logf <<<"$entry"
  [ $first = 1 ] || sleep 120
  first=0
  (
    flock -w 300 9 || { echo "$(date '+%F %T') $w2: tick.lock not free in 300 s; not started" >&2; exit 1; }
    if grep -q " $w2 $brief $logf\$" "$D/started.txt" 2>/dev/null; then echo "$w2 already started for $logf" >&2; exit 0; fi
    echo "$(date '+%F %T') $w2 $brief $logf" >> "$D/started.txt"
    echo "$(date '+%F %T') started $w2 ($tid) $brief -> $logf (owner's order, DEC-1018; past the memory admission)" >> "$D/dispatch.log"
    setsid -f bash "$CODE/launch_now.sh" "$w2" "$tid" "$brief" "$logf" \
      2>> "$ORCH/log/$w2-$(date +%Y%m%d-%H%M)-launch.txt" < /dev/null > /dev/null 9>&-  # the lead must not inherit the lock
    echo "$(date '+%F %T') launched $w2"
  ) 9>"$D/tick.lock"
done
