#!/usr/bin/env bash
# The lead's full rebuild of this worktree's store, after the gates, under the rebuild lock (DEC-939 item 2).
LOG=/home/usain/gov-os-worktrees/W2-77/.gov-runtime/scratch/lead/log
rm -f "$LOG/rebuild.exit"
bash /home/usain/gov-os-worktrees/W2-77/.gov-runtime/scratch/lead/gates.sh > "$LOG/rebuild-gates.txt" 2>&1 || { echo 9 > "$LOG/rebuild.exit"; exit 9; }
cd /home/usain/gov-os-worktrees/W2-77 || exit 8
export TMPDIR=/tmp/gov-os-lead-W2-77
PYTHONPATH=/home/usain/gov-os-worktrees/W2-77/src flock /tmp/gov-os-rebuild.lock python3 -m gov.cli.main rebuild --json > "$LOG/rebuild.json" 2> "$LOG/rebuild.err"
echo $? > "$LOG/rebuild.exit"
