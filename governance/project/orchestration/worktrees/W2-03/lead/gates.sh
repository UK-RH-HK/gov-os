#!/bin/bash
# Gates before a rebuild or a full suite batch: close quiet window, nightly, load < 20, disk gate; then scratch measure.
ORCH=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator
until [ ! -e $ORCH/CLOSE-RUNNING ]; do echo "close running, waiting"; sleep 60; done
until [ ! -e $ORCH/NIGHTLY-RUNNING ]; do echo "nightly running, waiting"; sleep 60; done
until awk '{exit !($1 < 20)}' /proc/loadavg; do echo "load $(cut -d' ' -f1 /proc/loadavg), waiting"; sleep 60; done
date
cat /proc/loadavg
bash $ORCH/tools/disk_gate.sh
echo "disk_gate exit $?"
du -s --inodes /home/usain/gov-os-worktrees/W2-03/.gov-runtime /tmp/gov-os-lead-W2-03 2>/dev/null
du -sh /home/usain/gov-os-worktrees/W2-03/.gov-runtime /tmp/gov-os-lead-W2-03 2>/dev/null
cd /home/usain/gov-os-worktrees/W2-03 && git status --short --ignored | grep -v '^!! .gov-runtime/' | head -20
