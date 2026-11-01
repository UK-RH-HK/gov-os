#!/bin/bash
# Run 7: re-run named cases alone, in the close's environment (runner_env through runner6.py), this worktree's code.
#   rerun7.sh <tag> <node id> [<node id> ...]
cd /home/usain/gov-os-worktrees/W2-05 || exit 9
S=/home/usain/gov-os-worktrees/W2-05/.gov-runtime/scratch/lead
LOG=$S/log/v7
OUT=/tmp/gov-os-lead-W2-05/v7-results
TAG="$1"; shift
rm -f "$LOG/rerun-$TAG.exit"
date > "$LOG/rerun-$TAG.start"
TMPDIR=/tmp/gov-os-lead-W2-05 \
PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH \
PYTHONPATH=/home/usain/gov-os-worktrees/W2-05/src:/home/usain/gov-os-worktrees/W2-05/src/gov/close/pytest_plugin \
python3 "$S/runner6.py" \
  python3 -m pytest -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rfEs --tb=short \
  --junitxml="$OUT/rerun-$TAG.xml" "$@" > "$OUT/rerun-$TAG.txt" 2>&1
echo $? > "$LOG/rerun-$TAG.exit"
tail -3 "$OUT/rerun-$TAG.txt" > "$LOG/rerun-$TAG-tail.txt"
date >> "$LOG/rerun-$TAG.start"
