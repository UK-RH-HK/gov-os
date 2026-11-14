#!/bin/bash
# $1 = tree, $2 = tmp, $3 = out
tree=$1; mkdir -p "$2"; cd "$tree"
mapfile -t IDS < /home/usain/gov-os-worktrees/W2-185/.gov-runtime/scratch/lead/log/verify-red-ids.txt
env GOV_TESTS_OPTIN=lifted,breadth TMPDIR="$2" PYTHONUSERBASE=/home/usain/.local HOME=/home/usain/gov-os-worktrees/W2-185/.gov-runtime/scratch/empty-home PYTHONPATH="$tree/src" bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest "${IDS[@]}" -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rf > "$3" 2>&1
echo "exit=$?" >> "$3"
