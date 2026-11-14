#!/bin/bash
# usage: pt.sh <pytest args...>   (every run through the heavy slot)
export TMPDIR="${TMPDIR:-/tmp/gov-launch-43mabuy1/claude-1000}"
mkdir -p "$TMPDIR"
env TMPDIR="$TMPDIR" PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-116/src \
  bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh \
  python3 -m pytest "$@" -q -p no:cacheprovider -o tmp_path_retention_policy=failed
