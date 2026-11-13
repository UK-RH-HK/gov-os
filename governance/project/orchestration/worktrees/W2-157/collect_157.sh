#!/usr/bin/env bash
T=/home/usain/gov-os-worktrees/W2-157
cd "$T" || exit 2
env HOME="$T/.gov-runtime/scratch/empty-home" PYTHONUSERBASE=/home/usain/.local PYTHONPATH="$T/src" TMPDIR="$TMPDIR" \
  python3 -B -m pytest tests/acceptance/W2-157 --collect-only -q -p no:cacheprovider --rootdir="$T" >/dev/null 2>&1
echo "collect exit $?"
