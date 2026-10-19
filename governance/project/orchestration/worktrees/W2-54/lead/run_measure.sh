#!/bin/sh
# Run 3: the engineer's real-embedder measurement, then the full rebuild, then the context check timed (cold cache).
cd /home/usain/gov-os-worktrees/W2-54 || exit 2
LOG=/home/usain/gov-os-worktrees/W2-54/.gov-runtime/scratch/lead/log
git log --oneline -1 > "$LOG/m3-measure.txt"
PYTHONPATH=/home/usain/gov-os-worktrees/W2-54/src python3 /home/usain/gov-os-worktrees/W2-54/.gov-runtime/scratch/lead/eng3-measure.py >> "$LOG/m3-measure.txt" 2>&1
echo $? > "$LOG/m3-measure.exit"
PYTHONPATH=/home/usain/gov-os-worktrees/W2-54/src python3 -m gov.cli.main rebuild --json > "$LOG/rebuild7.json" 2>&1
echo $? > "$LOG/rebuild7.exit"
ls -la .gov-runtime/ > "$LOG/m3-ctx.txt"
{ git log --oneline -1; uptime; nproc; /usr/bin/time -v env PYTHONPATH=/home/usain/gov-os-worktrees/W2-54/src python3 -m gov.context.context_check; echo "exit $?"; uptime; } >> "$LOG/m3-ctx.txt" 2>&1
ls -la .gov-runtime/ >> "$LOG/m3-ctx.txt"
echo done > "$LOG/m3.done"
