#!/usr/bin/env bash
# The lead's real gov skilleval runs (run 2), with the pass-through shim first on PATH so each reply is kept.
# Usage: run_skilleval2.sh <tag> <skill>...
set -u
tag=$1; shift
cd /home/usain/gov-os-worktrees/W2-100 || exit 2
OUT=/home/usain/gov-os-worktrees/W2-100/.gov-runtime/scratch/lead/skilleval
SHIM=/home/usain/gov-os-worktrees/W2-100/.gov-runtime/scratch/lead/shim
mkdir -p "$OUT"
pids=(); names=()
for s in "$@"; do
  env PATH="$SHIM:$PATH" PYTHONPATH=/home/usain/gov-os-worktrees/W2-100/src python3 -m gov.cli.main skilleval template/governance/kernel/skills/$s --json > "$OUT/$s-$tag.json" 2> "$OUT/$s-$tag.err" &
  pids+=($!); names+=("$s")
done
rc=0
for i in "${!pids[@]}"; do
  wait "${pids[$i]}"; c=$?
  echo "${names[$i]} exit $c" | tee -a "$OUT/exits-$tag.txt"
  [ $c = 0 ] || rc=1
done
exit $rc
