#!/bin/bash
# Run 7: one full rebuild of this worktree's store (DEC-719, DEC-732, DEC-939 item 2), after the load gate
# (DEC-847, DEC-961) and the disk gate (DEC-898). Never --no-embeddings. Usage: rebuild7.sh <tag>
cd /home/usain/gov-os-worktrees/W2-05 || exit 9
TAG="${1:-a}"
LOG=/home/usain/gov-os-worktrees/W2-05/.gov-runtime/scratch/lead/log/v7
mkdir -p "$LOG" /tmp/gov-os-lead-W2-05
# DEC-983 item 6: the load wait is replaced by the heavy-job slots; a rebuild keeps only its one-at-a-time lock.
bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/disk_gate.sh > "$LOG/rebuild-$TAG-disk.txt" 2>&1 || { echo 97 > "$LOG/rebuild-$TAG.exit"; exit 97; }
date > "$LOG/rebuild-$TAG.start"
cat /proc/loadavg >> "$LOG/rebuild-$TAG.start"
PYTHONPATH=/home/usain/gov-os-worktrees/W2-05/src python3 -c "import gov; print(gov.__file__)" > "$LOG/import-$TAG.txt" 2>&1
TMPDIR=/tmp/gov-os-lead-W2-05 PYTHONPATH=/home/usain/gov-os-worktrees/W2-05/src flock /tmp/gov-os-rebuild.lock python3 -m gov.cli.main rebuild --json > "$LOG/rebuild-$TAG.json" 2> "$LOG/rebuild-$TAG.err"
echo $? > "$LOG/rebuild-$TAG.exit"
date >> "$LOG/rebuild-$TAG.start"
