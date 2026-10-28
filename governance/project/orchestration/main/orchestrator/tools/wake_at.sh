#!/usr/bin/env bash
# Waits until the next HH:MM (local time) and then exits, printing its label: run in the background by the
# orchestrator's session, its exit wakes the session for the morning package (owner, standing, DEC-938). CronCreate
# is refused by the guard (DEC-685: a tool it does not know), so a background wait stands in for it.
# Usage: wake_at.sh <HH:MM> <label>
target=$(date -d "today $1" +%s)
now=$(date +%s)
[ "$target" -gt "$now" ] || target=$(date -d "tomorrow $1" +%s)
echo "$(date '+%F %T') waiting until $(date -d "@$target" '+%F %H:%M') for: $2"
sleep $(( target - now ))
echo "$(date '+%F %T') WAKE: $2"
