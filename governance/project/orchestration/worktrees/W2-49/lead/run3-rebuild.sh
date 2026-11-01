#!/bin/bash
# Run 3 rebuild of this worktree's store, under the machine's rebuild lock (DEC-939 item 2). Never --no-embeddings.
# Usage: bash run3-rebuild.sh <tag>
cd /home/usain/gov-os-worktrees/W2-49 || exit 9
LOG=/home/usain/gov-os-worktrees/W2-49/.gov-runtime/scratch/lead/log
until python3 -c "import os; l=os.getloadavg(); exit(0 if min(l[0], l[2]) < os.cpu_count() else 1)"; do sleep 60; done
TMPDIR=/tmp/gov-os-lead-W2-49 PYTHONPATH=/home/usain/gov-os-worktrees/W2-49/src flock /tmp/gov-os-rebuild.lock python3 -m gov.cli.main rebuild --json > "$LOG/run3-rebuild-$1.txt" 2>&1
echo $? > "$LOG/run3-rebuild-$1.exit"
