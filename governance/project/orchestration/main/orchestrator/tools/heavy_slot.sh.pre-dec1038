#!/usr/bin/env bash
# The heavy-job limit (owner, DEC-979 item 1 D1; CAPACITY-1): a test run takes one of a few machine-wide slots and
# waits for one; everything else runs freely. Each slot's run also caps pytest-xdist's `-n auto` at WORKERS, so the
# slots together keep the load near the number of processors (SLOTS x WORKERS, about 18 of 20).
#   bash heavy_slot.sh <the run's command and arguments>
# Exits with the command's code. The sizes are in heavy_slots.conf beside this script (re-sized from the re-measure
# after W2-107 without a code change); GOV_HEAVY_SLOTS / GOV_HEAVY_WORKERS override them for a test.
# A slot is a lock file held for the whole run (flock -o: the lock is not passed to the run, so a daemon the run leaves
# behind never keeps it); the slot frees when the run's own process ends.
# Rebuilds are not slots here: they already run one at a time on the machine (the rebuild lock, W2-76).
HERE=$(cd "$(dirname "$0")" && pwd)
SLOTS=3 WORKERS=6 DIR=/tmp
[ -f "$HERE/heavy_slots.conf" ] && . "$HERE/heavy_slots.conf"
SLOTS=${GOV_HEAVY_SLOTS:-$SLOTS}
WORKERS=${GOV_HEAVY_WORKERS:-$WORKERS}
DIR=${GOV_HEAVY_DIR:-$DIR}
BUSY=213  # flock's exit when the slot is taken; any other code is the command's own
export PYTEST_XDIST_AUTO_NUM_WORKERS=${PYTEST_XDIST_AUTO_NUM_WORKERS:-$WORKERS}
# DEC-1011 (owner): the merge queue and the closes take the next free slot before any lead's heavy step, and no slot
# is kept idle. A priority caller (GOV_HEAVY_PRIORITY=1, set by merge_queue.py and close_build.py for their whole run)
# registers itself while it waits and checks every 2 s; any other caller does not take a free slot while a live
# priority waiter exists (a file for a dead process is ignored and removed).
PRIO=${GOV_HEAVY_PRIORITY:-}
MINE="$DIR/gov-os-heavy-prio-$$"
prio_waiting() {
  for f in "$DIR"/gov-os-heavy-prio-*; do
    [ -e "$f" ] || continue
    p=${f##*-}
    if kill -0 "$p" 2>/dev/null; then [ "$f" != "$MINE" ] && return 0; else rm -f "$f"; fi
  done
  return 1
}
[ -n "$PRIO" ] && { : > "$MINE"; trap 'rm -f "$MINE"' EXIT; }
said=""
while :; do
  if [ -z "$PRIO" ] && prio_waiting; then
    [ -z "$said" ] && { echo "heavy_slot: a landing or close waits first; waiting ($(date '+%F %T'))" >&2; said=1; }
    sleep 10; continue
  fi
  for i in $(seq 1 "$SLOTS"); do
    if [ -n "$PRIO" ]; then  # the registration ends the moment the slot is taken, not when the run ends
      flock -n -o -E "$BUSY" "$DIR/gov-os-heavy-slot-$i.lock" bash -c 'rm -f "$0"; exec "$@"' "$MINE" "$@"
    else
      flock -n -o -E "$BUSY" "$DIR/gov-os-heavy-slot-$i.lock" "$@"
    fi
    rc=$?
    [ "$rc" -ne "$BUSY" ] && { [ -n "$PRIO" ] && rm -f "$MINE"; exit "$rc"; }
  done
  [ -z "$said" ] && { echo "heavy_slot: all $SLOTS slots taken; waiting ($(date '+%F %T'))" >&2; said=1; }
  if [ -n "$PRIO" ]; then sleep 2; else sleep 10; fi
done
