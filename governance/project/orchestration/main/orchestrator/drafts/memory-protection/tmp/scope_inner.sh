#!/usr/bin/env bash
# Runs INSIDE a transient user scope (TasksMax=40, MemoryHigh=150M, no MemoryMax so no kernel kill is possible).
CG=/sys/fs/cgroup$(cut -d: -f3 /proc/self/cgroup)
echo "scope cgroup: ${CG#/sys/fs/cgroup}"
echo "pids.max=$(cat $CG/pids.max) memory.high=$(cat $CG/memory.high) memory.max=$(cat $CG/memory.max)"
ok=0; fail=0
for i in $(seq 1 100); do
  if sleep 6 2>/dev/null & then ok=$((ok+1)); fi
done 2>/dev/null
sleep 0.5
echo "pids.current after 100 spawn attempts: $(cat $CG/pids.current); events: $(grep max $CG/pids.events)"
python3 -I - "$CG" <<'EOF'
import sys, time
cg = sys.argv[1]
buf = bytearray(400 * 1024 * 1024)
for i in range(0, len(buf), 4096):
    buf[i] = 1
time.sleep(1)
cur = int(open(cg + '/memory.current').read())
swap = int(open(cg + '/memory.swap.current').read())
print('hog 400 MB: memory.current %.0f MB, swapped out %.0f MB (high = 150 MB)' % (cur / 1e6, swap / 1e6))
print('memory.events:', open(cg + '/memory.events').read().replace('\n', ' '))
EOF
wait
