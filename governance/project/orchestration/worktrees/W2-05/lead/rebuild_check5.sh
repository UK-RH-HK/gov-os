#!/bin/bash
# Run 5: the second full rebuild at the final head ecbdf689f283 (the first was before the repair merge), then gov check.
S=/home/usain/gov-os-worktrees/W2-05/.gov-runtime/scratch/lead
LOG=$S/log/v5
cd /home/usain/gov-os-worktrees/W2-05 || exit 9
rm -f "$LOG/rebuild2.exit" "$LOG/check2.exit"
until python3 -c "import os; l=os.getloadavg(); exit(0 if min(l[0], l[2]) < os.cpu_count() else 1)"; do sleep 60; done
bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/disk_gate.sh > "$LOG/rebuild2-disk.txt" 2>&1 || { echo 97 > "$LOG/rebuild2.exit"; exit 97; }
date > "$LOG/rebuild2.start"
cat /proc/loadavg >> "$LOG/rebuild2.start"
TMPDIR=/tmp/gov-os-lead-W2-05 PYTHONPATH=/home/usain/gov-os-worktrees/W2-05/src flock /tmp/gov-os-rebuild.lock python3 -m gov.cli.main rebuild --json > "$LOG/rebuild2.json" 2> "$LOG/rebuild2.err"
echo $? > "$LOG/rebuild2.exit"
date >> "$LOG/rebuild2.start"
TMPDIR=/tmp/gov-os-lead-W2-05 PYTHONPATH=/home/usain/gov-os-worktrees/W2-05/src timeout 3000 python3 -m gov.cli.main check --json > "$LOG/check2.json" 2> "$LOG/check2.err"
echo $? > "$LOG/check2.exit"
