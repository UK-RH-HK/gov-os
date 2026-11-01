#!/bin/bash
# The lead's store rebuild for W2-110: waits while the machine is past capacity (DEC-961), checks the disk gate
# (DEC-898), then one full rebuild of this worktree's code under the rebuild lock (DEC-939 item 2).
cd /home/usain/gov-os-worktrees/W2-110 || exit 9
until python3 -c "import os; l=os.getloadavg(); exit(0 if min(l[0], l[2]) < os.cpu_count() else 1)"; do sleep 60; done
bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/disk_gate.sh || exit 8
date -u +%FT%TZ
TMPDIR=/tmp/gov-os-lead-W2-110 PYTHONPATH=/home/usain/gov-os-worktrees/W2-110/src flock /tmp/gov-os-rebuild.lock python3 -m gov.cli.main rebuild --json
code=$?
date -u +%FT%TZ
exit $code
