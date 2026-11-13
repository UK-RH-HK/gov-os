#!/usr/bin/env bash
# Inside one heavy slot: alternate the request bound 48,000 (branch) / 24,000 (probe) over the same clones, 2 rounds.
O=$1
for round in 1 2; do
  for bound in 48000 24000; do
    W=$O/r$round-$bound; mkdir -p "$W"
    echo "round $round bound $bound start $(date +%T) load $(cut -d' ' -f1-3 /proc/loadavg) gpu $(/usr/lib/wsl/lib/nvidia-smi --query-gpu=utilization.gpu,memory.used --format=csv,noheader)" >> "$O/ab.txt"
    PROF_REUSE=/tmp/w2-155-prof/run-235032 PROF_REQUEST_CHARS=$bound \
      python3 /home/usain/gov-os-worktrees/W2-155/.gov-runtime/scratch/profile_warm.py "$W" > "$W/stdout.txt" 2> "$W/stderr.txt"
    echo "round $round bound $bound rc=$? end $(date +%T) load $(cut -d' ' -f1-3 /proc/loadavg)" >> "$O/ab.txt"
  done
done
