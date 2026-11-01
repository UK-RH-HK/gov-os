#!/bin/bash
# Light checks before the return: collection (DEC-868), trailer gate (DEC-927), keyword warning (DEC-911).
cd /home/usain/gov-os-worktrees/W2-97 || exit 9
rm -f /home/usain/gov-os-worktrees/W2-97/.gov-runtime/scratch/lead/log/checks.rc
TMPDIR=/tmp/gov-os-lead-W2-97 PYTHONPATH=/home/usain/gov-os-worktrees/W2-97/src python3 -m pytest tests --collect-only -q -p no:cacheprovider --no-header > /home/usain/gov-os-worktrees/W2-97/.gov-runtime/scratch/lead/log/collect.txt 2>&1
echo "collect exit $?" > /home/usain/gov-os-worktrees/W2-97/.gov-runtime/scratch/lead/log/checks.txt
PYTHONPATH=/home/usain/gov-os-worktrees/W2-97/src python3 /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/trailer_gate.py DAEO-wq2b /home/usain/gov-os-worktrees/W2-97 >> /home/usain/gov-os-worktrees/W2-97/.gov-runtime/scratch/lead/log/checks.txt 2>&1
echo "trailer_gate exit $?" >> /home/usain/gov-os-worktrees/W2-97/.gov-runtime/scratch/lead/log/checks.txt
python3 /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/keyword_warn.py /home/usain/gov-os-worktrees/W2-97 >> /home/usain/gov-os-worktrees/W2-97/.gov-runtime/scratch/lead/log/checks.txt 2>&1
echo "keyword_warn exit $?" >> /home/usain/gov-os-worktrees/W2-97/.gov-runtime/scratch/lead/log/checks.txt
echo done > /home/usain/gov-os-worktrees/W2-97/.gov-runtime/scratch/lead/log/checks.rc
