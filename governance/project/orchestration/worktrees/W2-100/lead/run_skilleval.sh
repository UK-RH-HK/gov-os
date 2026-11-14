#!/usr/bin/env bash
# The lead's real gov skilleval runs of the four skills (W2-100 order step 2), in parallel, each to its own JSON file.
set -u
cd /home/usain/gov-os-worktrees/W2-100 || exit 2
OUT=/home/usain/gov-os-worktrees/W2-100/.gov-runtime/scratch/lead/skilleval
mkdir -p "$OUT"
pids=()
for s in backend api data security; do
  env PYTHONPATH=/home/usain/gov-os-worktrees/W2-100/src python3 -m gov.cli.main skilleval template/governance/kernel/skills/$s --json > "$OUT/$s-1.json" 2> "$OUT/$s-1.err" &
  pids+=($!)
done
rc=0
i=0
for s in backend api data security; do
  wait "${pids[$i]}"; c=$?
  echo "$s exit $c" | tee -a "$OUT/exits-1.txt"
  [ $c = 0 ] || rc=1
  i=$((i+1))
done
exit $rc
