#!/bin/bash
# Lead's full rebuild of this worktree's store (DEC-719, DEC-732), round 2, with the disk gate.
cd /home/usain/gov-os-worktrees/W2-81 || exit 9
bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/disk_gate.sh > /home/usain/gov-os-worktrees/W2-81/.gov-runtime/scratch/lead/log/rebuild-2.disk 2>&1 || { echo 8 > /home/usain/gov-os-worktrees/W2-81/.gov-runtime/scratch/lead/log/rebuild-2.exit; exit 8; }
date > /home/usain/gov-os-worktrees/W2-81/.gov-runtime/scratch/lead/log/rebuild-2.start
PYTHONPATH=/home/usain/gov-os-worktrees/W2-81/src flock /tmp/gov-os-rebuild.lock python3 -m gov.cli.main rebuild --json > /home/usain/gov-os-worktrees/W2-81/.gov-runtime/scratch/lead/log/rebuild-2.json 2> /home/usain/gov-os-worktrees/W2-81/.gov-runtime/scratch/lead/log/rebuild-2.err
echo $? > /home/usain/gov-os-worktrees/W2-81/.gov-runtime/scratch/lead/log/rebuild-2.exit
date >> /home/usain/gov-os-worktrees/W2-81/.gov-runtime/scratch/lead/log/rebuild-2.start
