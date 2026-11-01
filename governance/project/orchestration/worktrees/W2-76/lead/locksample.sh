#!/usr/bin/env bash
# Every 10 s until the stop file (arg 1, a name under log/) exists: the holders and the blocked waiters ("->" lines)
# on the machine's rebuild lock in /proc/locks, with the load. Arg 2: the output's name under log/.
LOG=/home/usain/gov-os-worktrees/W2-76/.gov-runtime/scratch/lead/log
INO=$(stat -c %i /tmp/gov-os-rebuild.lock)
: > "$LOG/$2"
while [ ! -e "$LOG/$1" ]; do
  h=$(grep -F ":$INO " /proc/locks | grep -vc -- '->')
  w=$(grep -F ":$INO " /proc/locks | grep -c -- '->')
  echo "$(date +%T) holders=$h waiters=$w load=$(cut -d' ' -f1 /proc/loadavg)" >> "$LOG/$2"
  sleep 10
done
echo "stopped $(date +%T)" >> "$LOG/$2"
