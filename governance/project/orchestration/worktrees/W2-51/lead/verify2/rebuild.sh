#!/bin/bash
# Run 2 rebuild: gates, then one full rebuild under the machine's rebuild lock.
cd /home/usain/gov-os-worktrees/W2-51 || exit 99
O=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator
until [ ! -e $O/CLOSE-RUNNING ] && [ ! -e $O/NIGHTLY-RUNNING ]; do sleep 60; done
until awk '{exit !($1 < 20)}' /proc/loadavg; do sleep 60; done
bash $O/tools/disk_gate.sh > /home/usain/gov-os-worktrees/W2-51/.gov-runtime/scratch/lead/verify2/rebuild-disk.txt 2>&1
date > /home/usain/gov-os-worktrees/W2-51/.gov-runtime/scratch/lead/verify2/rebuild-start.txt
cat /proc/loadavg >> /home/usain/gov-os-worktrees/W2-51/.gov-runtime/scratch/lead/verify2/rebuild-start.txt
TMPDIR=/tmp/gov-os-lead-W2-51 PYTHONPATH=/home/usain/gov-os-worktrees/W2-51/src flock /tmp/gov-os-rebuild.lock python3 -m gov.cli.main rebuild --json > /home/usain/gov-os-worktrees/W2-51/.gov-runtime/scratch/lead/verify2/rebuild.json 2> /home/usain/gov-os-worktrees/W2-51/.gov-runtime/scratch/lead/verify2/rebuild.err
echo $? > /home/usain/gov-os-worktrees/W2-51/.gov-runtime/scratch/lead/verify2/rebuild.exit
date >> /home/usain/gov-os-worktrees/W2-51/.gov-runtime/scratch/lead/verify2/rebuild-start.txt
