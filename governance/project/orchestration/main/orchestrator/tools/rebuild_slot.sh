#!/usr/bin/env bash
# A store rebuild in a heavy-job slot (owner, DEC-1001 (d)): the machine-wide one-rebuild-at-a-time lock ended;
# rebuilds share the heavy-job slots with test runs (tools/heavy_slot.sh, heavy_slots.conf), so at most SLOTS heavy
# jobs run at once. Two rebuilds of the same tree still exclude each other: the product's own lock (gov rebuild,
# src/gov/rebuild/watch.py) is pointed at a lock of this tree's own through GOV_REBUILD_LOCK.
#   bash rebuild_slot.sh <tree> [extra gov rebuild arguments]
# Runs `${GOV_REBUILD_PYTHON:-python3} -m gov.cli.main rebuild --json` in <tree> with the caller's environment (its PYTHONPATH names the
# tree's own src/, DEC-732); exits with the rebuild's code. GOV_REBUILD_SLOT_DRY=1 prints the lock and the command
# instead of running them (tests only).
set -u
HERE=$(cd "$(dirname "$0")" && pwd)
[ $# -ge 1 ] || { echo "usage: rebuild_slot.sh <tree> [args]" >&2; exit 2; }
tree=$(cd "$1" 2>/dev/null && pwd -P) || { echo "rebuild_slot: no such tree: $1" >&2; exit 2; }
shift
lock="/tmp/gov-os-rebuild-$(printf '%s' "$tree" | sha1sum | cut -c1-12).lock"
export GOV_REBUILD_LOCK="$lock"
cd "$tree" || exit 2
if [ -n "${GOV_REBUILD_SLOT_DRY:-}" ]; then
  echo "lock=$lock tree=$tree cmd=${GOV_REBUILD_PYTHON:-python3} -m gov.cli.main rebuild --json $*"
  exit 0
fi
# A rebuild that answers "ok" with the semantic store not recreated, when it was asked for, is a FAILED rebuild here
# (exit 75): a hung or stopped embedding server once left three stores partial while every tool read them as built
# (owner, 2026-11-01, DEC-1015). The output is passed through unchanged.
out=$(mktemp "${TMPDIR:-/tmp}/rebuild-slot-out.XXXXXX")
bash "$HERE/heavy_slot.sh" "${GOV_REBUILD_PYTHON:-python3}" -m gov.cli.main rebuild --json "$@" > "$out"
rc=$?
cat "$out"
if [ $rc -eq 0 ]; then
  why=$(python3 "$HERE/rebuild_semantic_check.py" "$out")
  if [ -n "$why" ]; then
    echo "rebuild_slot: REBUILD INCOMPLETE in $tree: $why" >&2
    rc=75
  fi
fi
rm -f -- "$out"
exit $rc
