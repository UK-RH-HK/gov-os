#!/bin/bash
# Run 6: a full rebuild of this worktree (DEC-719, DEC-732), after the load wait (DEC-847, DEC-961) and the disk gate
# (DEC-898); under flock /tmp/gov-os-rebuild.lock (DEC-939 item 2); never --no-embeddings. Usage: rebuild6.sh <n>
set -u
W=/home/usain/gov-os-worktrees/W2-67
LOG=$W/.gov-runtime/scratch/lead/log
N=$1
cd "$W" || exit 99
until python3 -c "import os; l=os.getloadavg(); exit(0 if min(l[0], l[2]) < os.cpu_count() else 1)"; do sleep 60; done
bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/disk_gate.sh > "$LOG/rebuild-$N.gate" 2>&1 || { echo gate-shut > "$LOG/rebuild-$N.exit"; exit 1; }
date -Is > "$LOG/rebuild-$N.start"
PYTHONPATH=$W/src flock /tmp/gov-os-rebuild.lock python3 -m gov.cli.main rebuild --json > "$LOG/rebuild-$N.json" 2> "$LOG/rebuild-$N.err"
echo $? > "$LOG/rebuild-$N.exit"
date -Is >> "$LOG/rebuild-$N.start"
