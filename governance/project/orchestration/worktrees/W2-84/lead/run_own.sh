#!/bin/bash
# The ticket's own suites (acceptance W2-84 and the builder tests), this worktree's code (DEC-732).
# Usage: run_own.sh <tag>   writes log/own-<tag>.out, .xml and .rc
cd /home/usain/gov-os-worktrees/W2-84 || exit 2
TAG="$1"
LOG=/home/usain/gov-os-worktrees/W2-84/.gov-runtime/scratch/lead/log
PYTHONPATH=/home/usain/gov-os-worktrees/W2-84/src python3 -c "import gov; print(gov.__file__)" > "$LOG/own-$TAG.out" 2>&1
TMPDIR=/tmp/gov-os-lead-W2-84 PYTHONPATH=/home/usain/gov-os-worktrees/W2-84/src python3 -m pytest tests/acceptance/W2-84 tests/unit/guard/test_w2_84_trees.py -q -p no:cacheprovider --no-header -o tmp_path_retention_policy=failed -n 4 --junitxml="$LOG/own-$TAG.xml" >> "$LOG/own-$TAG.out" 2>&1
echo $? > "$LOG/own-$TAG.rc"
