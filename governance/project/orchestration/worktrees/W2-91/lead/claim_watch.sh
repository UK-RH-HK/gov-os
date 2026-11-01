#!/bin/bash
# Waits until w2/integrate holds DAEO-a3u2 as in_progress (the CTO's claim commit), up to 60 minutes.
OUT=/home/usain/gov-os-worktrees/W2-91/.gov-runtime/scratch/lead/log/claim-watch.txt
for i in $(seq 1 120); do
  if git -C /home/usain/gov-os-worktrees/W2-91 show w2/integrate:.tickets/DAEO-a3u2.md 2>/dev/null | grep -q '^status: in_progress'; then
    git -C /home/usain/gov-os-worktrees/W2-91 log --format='%h %s' -1 w2/integrate -- .tickets/DAEO-a3u2.md > "$OUT"
    exit 0
  fi
  sleep 30
done
echo "no claim commit after 60 minutes" > "$OUT"
exit 1
