#!/usr/bin/env bash
# Run W2-108's acceptance tests from this worktree against the code in <src>. usage: accept.sh <tag> <src>
# Writes log/accept-<tag>.{txt,xml,exit}
cd /home/usain/gov-os-worktrees/W2-108 || exit 9
TAG="$1"
SRC="$2"
LOG=/home/usain/gov-os-worktrees/W2-108/.gov-runtime/scratch/lead/log
until python3 -c "import os; l=os.getloadavg(); exit(0 if min(l[0], l[2]) < os.cpu_count() else 1)"; do sleep 60; done
PYTHONPATH="$SRC" python3 -c "import gov; print(gov.__file__)" > "$LOG/accept-$TAG.txt" 2>&1
TMPDIR=/tmp/gov-os-lead-W2-108 PYTHONPATH="$SRC" python3 -m pytest tests/acceptance/W2-108 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rs --junitxml="$LOG/accept-$TAG.xml" >> "$LOG/accept-$TAG.txt" 2>&1
echo $? > "$LOG/accept-$TAG.exit"
