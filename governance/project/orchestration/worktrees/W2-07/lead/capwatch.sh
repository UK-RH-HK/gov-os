#!/usr/bin/env bash
# Watch the verification run's temp folder against DEC-904's cap; stop the run at 5.9M inodes or 59 GB.
L=/home/usain/gov-os-worktrees/W2-07/.gov-runtime/scratch/lead/log
for i in 1 2 3 4 5 6; do
  [ -e "$L/p2.done" ] && break
  n=$(du -s --inodes /tmp/gov-os-lead-W2-07 | cut -f1)
  b=$(du -sb /tmp/gov-os-lead-W2-07 | cut -f1)
  echo "$(date +%T) $n $b $(tail -c 120 "$L/v2-parallel.txt" | grep -o '\[ *[0-9]*%\]' | tail -1)" | tee -a "$L/p2-lead-watch.txt"
  if [ "$n" -gt 5900000 ] || [ "$b" -gt 59000000000 ]; then
    echo "CAP reached, stopping the run" | tee -a "$L/p2-lead-watch.txt"
    pkill -TERM -f "junitxml=$L/parallel.xml"
    break
  fi
  sleep 70
done
