#!/usr/bin/env bash
# usage: suites.sh <outdir> <folder>...
out=$1; shift
cd /home/usain/gov-os-worktrees/W2-187
for f in "$@"; do
  n=$(basename "$f")
  TMPDIR=/tmp/gov-w2-187-lead bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh env HOME=/home/usain/gov-os-worktrees/W2-187/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-187/src python3 -m pytest "$f" -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit" -rfE > "$out/$n.txt" 2>&1
  echo "$n exit $?: $(tail -n 1 "$out/$n.txt")"
done
