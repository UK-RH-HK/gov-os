#!/usr/bin/env bash
# DEC-966, DEC-973: the designers' store, refreshed at most twice a day: right after the nightly ends (that night
# run's verdict; at the latest 10:00) and at 18:00. On request, run refresh_integration_store.sh by hand.
O=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator
refresh() { bash "$O/tools/refresh_integration_store.sh" >> "$O/log/integration-store.log" 2>&1; }
until_t() { local t; t=$(date -d "$1" +%s); [ "$t" -gt "$(date +%s)" ] && sleep $(( t - $(date +%s) )); }
nightly_done_today() {
  local r
  for r in "$O/log/nightly/$(date +%Y%m%d)"-0[2-7]*/run.txt; do
    [ -f "$r" ] && grep -qE "^verdict:|NOT STARTED" "$r" && return 0
  done
  return 1
}
while true; do
  hm=$((10#$(date +%H%M)))
  if [ "$hm" -lt 400 ]; then until_t "today 04:00"; continue; fi
  if [ "$hm" -lt 1000 ]; then  # the morning: right after the nightly ends, at the latest 10:00
    until nightly_done_today || [ "$((10#$(date +%H%M)))" -ge 1000 ]; do sleep 300; done
    refresh
  fi
  if [ "$((10#$(date +%H%M)))" -lt 1800 ]; then until_t "today 18:00"; refresh; fi
  until_t "tomorrow 04:00"
done
