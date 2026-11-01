#!/bin/bash
# Run 3's rebuild of this worktree's store on the final head: wait for the load gate, then the shared rebuild lock (DEC-939, DEC-961, DEC-979).
cd /home/usain/gov-os-worktrees/W2-96 || exit 9
until python3 -c "import os; l=os.getloadavg(); exit(0 if min(l[0], l[2]) < os.cpu_count() else 1)"; do sleep 60; done
bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/disk_gate.sh || exit 8
date -u +%FT%TZ > /home/usain/gov-os-worktrees/W2-96/.gov-runtime/scratch/lead/log/rebuild-4.start
TMPDIR=/tmp/gov-os-lead-W2-96 PYTHONPATH=/home/usain/gov-os-worktrees/W2-96/src flock /tmp/gov-os-rebuild.lock python3 -m gov.cli.main rebuild --json > /home/usain/gov-os-worktrees/W2-96/.gov-runtime/scratch/lead/log/rebuild-4.json 2>&1
echo $? > /home/usain/gov-os-worktrees/W2-96/.gov-runtime/scratch/lead/log/rebuild-4.exit
date -u +%FT%TZ >> /home/usain/gov-os-worktrees/W2-96/.gov-runtime/scratch/lead/log/rebuild-4.start
