#!/usr/bin/env bash
# The lead's full rebuild of the measurement clone's store, with the base code (the clone's own src/), under the
# machine-wide rebuild lock. Writes log/rebuild-measure.{json,exit,start,end}.
cd /tmp/gov-os-lead-W2-108/measure || exit 9
LOG=/home/usain/gov-os-worktrees/W2-108/.gov-runtime/scratch/lead/log
until python3 -c "import os; l=os.getloadavg(); exit(0 if min(l[0], l[2]) < os.cpu_count() else 1)"; do sleep 60; done
bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/disk_gate.sh || { echo 8 > "$LOG/rebuild-measure.exit"; exit 8; }
date +%s > "$LOG/rebuild-measure.start"
TMPDIR=/tmp/gov-os-lead-W2-108 PYTHONPATH=/tmp/gov-os-lead-W2-108/measure/src flock /tmp/gov-os-rebuild.lock python3 -m gov.cli.main rebuild --json > "$LOG/rebuild-measure.json" 2>&1
echo $? > "$LOG/rebuild-measure.exit"
date +%s > "$LOG/rebuild-measure.end"
