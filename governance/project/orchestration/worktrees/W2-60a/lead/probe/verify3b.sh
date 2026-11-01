#!/bin/bash
# Round 3's verification, second start (the first was stopped at the tool's two-hour limit while queued at the gate).
# The rebuild of 06:31-06:44 stands. After the last commit: selection, scoped run (no full-run wrapper, DEC-968;
# the load gate kept), gov check, collect-only.
cd /home/usain/gov-os-worktrees/W2-60a || exit 9
export TMPDIR=/tmp/gov-os-lead-W2-60a
PYTHONPATH=/home/usain/gov-os-worktrees/W2-60a/src python3 /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/select_tests.py /home/usain/gov-os-worktrees/W2-60a W2-60a DAEO-cv58 > /home/usain/gov-os-worktrees/W2-60a/.gov-runtime/scratch/lead/log/v3b-selection.json 2> /home/usain/gov-os-worktrees/W2-60a/.gov-runtime/scratch/lead/log/v3b-selection.err
SEL=$?
echo "exit $SEL" > /home/usain/gov-os-worktrees/W2-60a/.gov-runtime/scratch/lead/log/v3b-selection.exit
if [ "$SEL" != "0" ]; then echo "selection exit $SEL" > /home/usain/gov-os-worktrees/W2-60a/.gov-runtime/scratch/lead/log/v3b.exit; exit 2; fi
until python3 -c "import os; l=os.getloadavg(); exit(0 if min(l[0], l[2]) < os.cpu_count() else 1)"; do sleep 60; done
bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/disk_gate.sh > /home/usain/gov-os-worktrees/W2-60a/.gov-runtime/scratch/lead/log/v3b-disk-gate.txt 2>&1 || { echo "disk gate shut" > /home/usain/gov-os-worktrees/W2-60a/.gov-runtime/scratch/lead/log/v3b.exit; exit 3; }
date > /home/usain/gov-os-worktrees/W2-60a/.gov-runtime/scratch/lead/log/v3b-run-start.txt
V3_NO_LOCK=1 python3 /home/usain/gov-os-worktrees/W2-60a/.gov-runtime/scratch/lead/probe/run_verify3.py /home/usain/gov-os-worktrees/W2-60a/.gov-runtime/scratch/lead/log/v3b-selection.json
PYTHONPATH=/home/usain/gov-os-worktrees/W2-60a/src python3 -m gov.cli.main check --json > /home/usain/gov-os-worktrees/W2-60a/.gov-runtime/scratch/lead/log/v3-check.json 2>&1
echo "exit $?" > /home/usain/gov-os-worktrees/W2-60a/.gov-runtime/scratch/lead/log/v3-check.exit
PYTHONPATH=/home/usain/gov-os-worktrees/W2-60a/src python3 -m pytest tests --collect-only -q -p no:cacheprovider --no-header > /home/usain/gov-os-worktrees/W2-60a/.gov-runtime/scratch/lead/log/v3-collect.txt 2>&1
echo "exit $?" > /home/usain/gov-os-worktrees/W2-60a/.gov-runtime/scratch/lead/log/v3-collect.exit
echo "done $(date)" > /home/usain/gov-os-worktrees/W2-60a/.gov-runtime/scratch/lead/log/v3b.exit
