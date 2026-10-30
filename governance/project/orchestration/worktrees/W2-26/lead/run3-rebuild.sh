#!/bin/bash
# W2-26 run 3: wait for load < 20, no close or nightly, then the full rebuild under the machine lock.
cd /home/usain/gov-os-worktrees/W2-26 || exit 90
LOG=/home/usain/gov-os-worktrees/W2-26/.gov-runtime/scratch/lead/log
until [ ! -e /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/CLOSE-RUNNING ] && [ ! -e /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/NIGHTLY-RUNNING ] && awk '{exit !($1 < 20)}' /proc/loadavg; do sleep 60; done
date > /home/usain/gov-os-worktrees/W2-26/.gov-runtime/scratch/lead/log/run3-rebuild.start
cat /proc/loadavg >> /home/usain/gov-os-worktrees/W2-26/.gov-runtime/scratch/lead/log/run3-rebuild.start
TMPDIR=/tmp/gov-os-lead-W2-26 PYTHONPATH=/home/usain/gov-os-worktrees/W2-26/src flock /tmp/gov-os-rebuild.lock python3 -m gov.cli.main rebuild --json > /home/usain/gov-os-worktrees/W2-26/.gov-runtime/scratch/lead/log/run3-rebuild.json 2> /home/usain/gov-os-worktrees/W2-26/.gov-runtime/scratch/lead/log/run3-rebuild.err
echo $? > /home/usain/gov-os-worktrees/W2-26/.gov-runtime/scratch/lead/log/run3-rebuild.exit
date >> /home/usain/gov-os-worktrees/W2-26/.gov-runtime/scratch/lead/log/run3-rebuild.start
