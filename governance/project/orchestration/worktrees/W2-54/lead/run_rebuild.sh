#!/bin/sh
# Full rebuild of this worktree's store (never --no-embeddings); NAME names the log files.
cd /home/usain/gov-os-worktrees/W2-54 || exit 2
LOG=/home/usain/gov-os-worktrees/W2-54/.gov-runtime/scratch/lead/log
NAME="$1"
uptime > "$LOG/$NAME.time"
start=$(date +%s)
PYTHONPATH=/home/usain/gov-os-worktrees/W2-54/src python3 -m gov.cli.main rebuild --json > "$LOG/$NAME.json" 2> "$LOG/$NAME.err"
echo $? > "$LOG/$NAME.exit"
echo "seconds $(( $(date +%s) - start ))" >> "$LOG/$NAME.time"
uptime >> "$LOG/$NAME.time"
PYTHONPATH=/home/usain/gov-os-worktrees/W2-54/src python3 -c "import gov; print(gov.__file__)" > "$LOG/$NAME.import"
