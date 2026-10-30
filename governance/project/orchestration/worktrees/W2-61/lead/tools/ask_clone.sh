#!/bin/bash
# One pinned-gov retrieval in the clone, for a lead's spot check (no PYTHONPATH, no GOV_TICKET). Arguments: a label,
# then gov retrieve's own arguments. Output: runs/spot-<label>.json.
set -u
label="$1"; shift
cd /home/usain/gov-os-runs/W2-61/repo || exit 90
env -u PYTHONPATH -u GOV_TICKET /home/usain/.local/bin/gov retrieve --batch-size 10 --bundle-budget 6000 "$@" --json > /home/usain/gov-os-worktrees/W2-61/.gov-runtime/scratch/lead/runs/spot-"$label".json
echo "exit $?"
