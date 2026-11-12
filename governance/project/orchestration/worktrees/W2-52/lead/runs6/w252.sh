#!/usr/bin/env bash
# W2-52's own suite, outside the sandbox, this worktree's code (run 6 check before lead_verify)
cd /home/usain/gov-os-worktrees/W2-52 || exit 9
OUT=/home/usain/gov-os-worktrees/W2-52/.gov-runtime/scratch/lead/runs6
TMPDIR=/tmp/gov-os-lead-W2-52 PYTHONPATH=/home/usain/gov-os-worktrees/W2-52/src timeout 1800 python3 -m pytest tests/acceptance/W2-52 -q -p no:cacheprovider -rs -o tmp_path_retention_policy=failed --junitxml=$OUT/w252.xml > $OUT/w252.log 2>&1
echo $? > $OUT/w252.exit
