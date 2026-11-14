#!/usr/bin/env bash
# usage: pt.sh <folder-or-node> [extra pytest args]
T=/home/usain/gov-os-worktrees/W2-187
target="$1"; shift
bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh env HOME=$T/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=$T/src python3 -m pytest "$target" -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit" "$@"
