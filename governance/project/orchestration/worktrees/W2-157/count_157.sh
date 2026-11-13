#!/usr/bin/env bash
T=/home/usain/gov-os-worktrees/W2-157
cd "$T" || exit 2
env HOME="$T/.gov-runtime/scratch/empty-home" PYTHONUSERBASE=/home/usain/.local PYTHONPATH="$T/src" \
  python3 -B -m pytest tests/acceptance/W2-157 -q --tb=no -rN --no-header -p no:cacheprovider --rootdir="$T" \
  -o tmp_path_retention_policy=failed > "$T/.gov-runtime/scratch/count-157.out" 2>&1
echo "exit $?"
tail -n 1 "$T/.gov-runtime/scratch/count-157.out"
