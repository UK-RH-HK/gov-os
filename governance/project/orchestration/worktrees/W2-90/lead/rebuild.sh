#!/bin/bash
# Lead W2-90: wait for load < 20, disk gate, then one full rebuild under the machine's rebuild lock.
cd /home/usain/gov-os-worktrees/W2-90 || exit 9
until awk '{exit !($1 < 20)}' /proc/loadavg; do sleep 60; done
bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/disk_gate.sh || { echo 8 > /home/usain/gov-os-worktrees/W2-90/.gov-runtime/scratch/lead/log/rebuild.exit; exit 8; }
date -u +%FT%TZ > /home/usain/gov-os-worktrees/W2-90/.gov-runtime/scratch/lead/log/rebuild.start
PYTHONPATH=/home/usain/gov-os-worktrees/W2-90/src flock /tmp/gov-os-rebuild.lock python3 -m gov.cli.main rebuild --json > /home/usain/gov-os-worktrees/W2-90/.gov-runtime/scratch/lead/log/rebuild.json 2> /home/usain/gov-os-worktrees/W2-90/.gov-runtime/scratch/lead/log/rebuild.err
echo $? > /home/usain/gov-os-worktrees/W2-90/.gov-runtime/scratch/lead/log/rebuild.exit
