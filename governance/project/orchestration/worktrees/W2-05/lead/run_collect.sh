#!/usr/bin/env bash
# DEC-868: one-process collection of tests/ in this tree; last line to log/collect.txt
T=/home/usain/gov-os-worktrees/W2-05
L=$T/.gov-runtime/scratch/lead/log
cd "$T" || exit 2
env TMPDIR=/tmp/gov-os-lead-W2-05 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$T/src python3 -m pytest tests --collect-only -q -p no:cacheprovider --no-header > "$L/collect-full.txt" 2>&1
echo "exit $?" > "$L/collect.txt"
tail -1 "$L/collect-full.txt" >> "$L/collect.txt"
