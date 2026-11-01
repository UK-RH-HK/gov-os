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
said=""
while :; do
  for i in $(seq 1 "$SLOTS"); do
    flock -n -o -E "$BUSY" "$DIR/gov-os-heavy-slot-$i.lock" "$@"
    rc=$?
    [ "$rc" -ne "$BUSY" ] && exit "$rc"
  done
  [ -z "$said" ] && { echo "heavy_slot: all $SLOTS slots taken; waiting ($(date '+%F %T'))" >&2; said=1; }
  sleep 10
done
