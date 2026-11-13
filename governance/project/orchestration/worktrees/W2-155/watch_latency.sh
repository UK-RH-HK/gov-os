#!/usr/bin/env bash
# Emits the latency run's slot/result lines as they change; exits when the run's load.txt has its end line.
D=/home/usain/gov-os-worktrees/W2-155/.gov-runtime/scratch/latency-013043
seen=""
until grep -q "^end" "$D/load.txt" 2>/dev/null; do
  l=$(grep -E "slot|passed|failed|error|PASSED|FAILED|ERROR" "$D/pytest.txt" 2>/dev/null | tail -1)
  if [ "$l" != "$seen" ]; then echo "$l"; seen="$l"; fi
  sleep 5
done
tail -1 "$D/load.txt"
