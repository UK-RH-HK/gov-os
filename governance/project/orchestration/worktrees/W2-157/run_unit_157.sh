#!/usr/bin/env bash
# usage: run_unit_157.sh <pytest args...>; the brief's whole-folder form, output to scratch/unit-157.out
T=/home/usain/gov-os-worktrees/W2-157
mkdir -p "$T/.gov-runtime/scratch/empty-home"
cd "$T" || exit 2
env HOME="$T/.gov-runtime/scratch/empty-home" PYTHONUSERBASE=/home/usain/.local PYTHONPATH="$T/src" \
  python3 -m pytest "$@" -q -p no:cacheprovider -o tmp_path_retention_policy=failed \
  > "$T/.gov-runtime/scratch/unit-157.out" 2>&1
echo "exit $?" >> "$T/.gov-runtime/scratch/unit-157.out"
