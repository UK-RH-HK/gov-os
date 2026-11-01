#!/bin/bash
# Run 6: one full rebuild of this worktree's store before the verification (DEC-719, DEC-732, DEC-939 item 2),
# after the load gate (DEC-847, DEC-961) and the disk gate (DEC-898). Never --no-embeddings.
cd /home/usain/gov-os-worktrees/W2-05 || exit 9
LOG=/home/usain/gov-os-worktrees/W2-05/.gov-runtime/scratch/lead/log/v6
mkdir -p "$LOG"
rm -f "$LOG/rebuild.exit"
until python3 -c "import os; l=os.getloadavg(); exit(0 if min(l[0], l[2]) < os.cpu_count() else 1)"; do sleep 60; done
bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/disk_gate.sh > "$LOG/rebuild-disk.txt" 2>&1 || { echo 97 > "$LOG/rebuild.exit"; exit 97; }
date > "$LOG/rebuild.start"
cat /proc/loadavg >> "$LOG/rebuild.start"
PYTHONPATH=/home/usain/gov-os-worktrees/W2-05/src python3 -c "import gov; print(gov.__file__)" > "$LOG/import.txt" 2>&1
TMPDIR=/tmp/gov-os-lead-W2-05 PYTHONPATH=/home/usain/gov-os-worktrees/W2-05/src flock /tmp/gov-os-rebuild.lock python3 -m gov.cli.main rebuild --json > "$LOG/rebuild.json" 2> "$LOG/rebuild.err"
echo $? > "$LOG/rebuild.exit"
date >> "$LOG/rebuild.start"
