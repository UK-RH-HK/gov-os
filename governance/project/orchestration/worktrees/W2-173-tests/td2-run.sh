#!/bin/bash
# td-2: run one acceptance folder in the brief's whole-folder form.
# PYTHONUSERBASE keeps the user's site-packages (pytest lives there) visible under the empty HOME.
# usage: td2-run.sh <folder> [extra pytest args]
cd /home/usain/gov-os-worktrees/W2-173-tests || exit 2
folder="$1"; shift
env HOME=/home/usain/gov-os-worktrees/W2-173-tests/.gov-runtime/scratch/empty-home \
    PYTHONUSERBASE=/home/usain/.local \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/home/usain/gov-os-worktrees/W2-173-tests/src \
    python3 -m pytest "$folder" -q -p no:cacheprovider -o tmp_path_retention_policy=failed \
    -m "not local_only" -k "not real and not green_here and not time_limit" "$@"
