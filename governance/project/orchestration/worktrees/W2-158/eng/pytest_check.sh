#!/bin/bash
# usage: pytest_check.sh <folder or file> [extra pytest args]
# TMPDIR is the sandbox's own ($TMPDIR; /tmp/w2-158-eng is read-only here), outside the repository and ~/gov-os-runs.
set -u
T=/home/usain/gov-os-worktrees/W2-158
target="$1"; shift
cd "$T"
mkdir -p "$TMPDIR/w2-158-eng"
exec env HOME=$T/.gov-runtime/scratch/empty-home TMPDIR="$TMPDIR/w2-158-eng" PYTHONUSERBASE=/home/usain/.local PYTHONPATH=$T/src \
  bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest "$target" -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit" "$@"
