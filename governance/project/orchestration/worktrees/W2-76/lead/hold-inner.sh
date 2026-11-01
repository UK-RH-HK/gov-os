#!/usr/bin/env bash
# Under flock /tmp/gov-os-rebuild.lock (hold.sh): the clone's real rebuilds, by this worktree's code, repeated until
# the stop file (arg 1, a name under log/) exists or 90 minutes pass. Arg 2: a tag for the log names.
W=/home/usain/gov-os-worktrees/W2-76
LOG=$W/.gov-runtime/scratch/lead/log
C=/tmp/gov-os-lead-W2-76/clone
STOP=$1
TAG=$2
start=$(date +%s)
date '+taken %F %T' > "$LOG/$TAG.times"
grep -F ":$(stat -c %i /tmp/gov-os-rebuild.lock) " /proc/locks >> "$LOG/$TAG.times"
cd "$C" || exit 2
n=0
while :; do
  n=$((n + 1))
  date "+rebuild $n start %T" >> "$LOG/$TAG.times"
  PYTHONPATH=$W/src timeout 3600 python3 -m gov.cli.main rebuild --json > "$LOG/$TAG-rebuild-$n.json" 2> "$LOG/$TAG-rebuild-$n.err"
  echo "rebuild $n exit $? end $(date +%T)" >> "$LOG/$TAG.times"
  [ -e "$LOG/$STOP" ] && break
  [ $(( $(date +%s) - start )) -gt 5400 ] && break
done
date '+released %F %T' >> "$LOG/$TAG.times"
