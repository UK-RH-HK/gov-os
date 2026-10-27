#!/usr/bin/env bash
# Times rulesync --version and the portability check (both rulesync calls) every 20 s while a run loads the
# machine; stops when the stop file appears. Output: one line per sample (time, load, seconds, exit).
export PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH
OUT=/home/usain/gov-os-worktrees/W2-57/.gov-runtime/scratch/lead/log/verify/sampler.txt
STOP=/home/usain/gov-os-worktrees/W2-57/.gov-runtime/scratch/lead/log/verify/sampler.stop
cd /home/usain/gov-os-worktrees/W2-57 || exit 1
while [ ! -e "$STOP" ]; do
  load=$(cut -d' ' -f1 /proc/loadavg)
  s=$(date +%s.%N); rulesync --version > /dev/null 2>&1; e=$?; t=$(date +%s.%N)
  echo "$(date '+%F %T') load=$load version_s=$(echo "$t - $s" | bc) exit=$e" >> "$OUT"
  s=$(date +%s.%N); TMPDIR=/tmp/gov-os-lead-W2-57 PYTHONPATH=/home/usain/gov-os-worktrees/W2-57/src timeout 300 python3 -m gov.adapters.portability > /dev/null 2>&1; e=$?; t=$(date +%s.%N)
  echo "$(date '+%F %T') load=$(cut -d' ' -f1 /proc/loadavg) check_s=$(echo "$t - $s" | bc) exit=$e" >> "$OUT"
  sleep 20
done
