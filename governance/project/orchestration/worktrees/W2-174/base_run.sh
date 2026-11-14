#!/usr/bin/env bash
# Runs one test node on an export of the base f2b1d38af (src and tests), to tell a base red from this branch's.
set -u
T=/home/usain/gov-os-worktrees/W2-174
B=$T/.gov-runtime/scratch/base
rm -rf "$B" && mkdir -p "$B" /tmp/w2174t
git -C "$T" archive ${2:-f2b1d38af} src tests pyproject.toml | tar -x -C "$B" || exit 3
cd "$B" || exit 3
env PYTHONUSERBASE=/home/usain/.local HOME=$T/.gov-runtime/scratch/empty-home PYTHONPATH=$B/src TMPDIR=/tmp/w2174t \
  bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh \
  python3 -m pytest "$1" -q -p no:cacheprovider -o tmp_path_retention_policy=failed 2>&1 | tail -15
