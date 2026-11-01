#!/bin/bash
# The full store rebuild of this worktree, with this worktree's code, one at a time on the machine (DEC-939 item 2).
# No load wait any more (DEC-979 D1); the disk gate first (DEC-898).
cd /home/usain/gov-os-worktrees/W2-105 || exit 9
export TMPDIR=/tmp/gov-os-lead-W2-105
bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/disk_gate.sh || exit 8
date -Is > /home/usain/gov-os-worktrees/W2-105/.gov-runtime/scratch/lead/log/rebuild-$1.start
PYTHONPATH=/home/usain/gov-os-worktrees/W2-105/src flock /tmp/gov-os-rebuild.lock python3 -m gov.cli.main rebuild --json > /home/usain/gov-os-worktrees/W2-105/.gov-runtime/scratch/lead/log/rebuild-$1.json 2>&1
echo $? > /home/usain/gov-os-worktrees/W2-105/.gov-runtime/scratch/lead/log/rebuild-$1.exit
date -Is >> /home/usain/gov-os-worktrees/W2-105/.gov-runtime/scratch/lead/log/rebuild-$1.start
