#!/bin/bash
# Run 4 of the lead: the checks after the last commit (selection, collect-only, trailer_gate, keyword_warn, scratch).
cd /home/usain/gov-os-worktrees/W2-96 || exit 9
L=/home/usain/gov-os-worktrees/W2-96/.gov-runtime/scratch/lead/log
PYTHONPATH=/home/usain/gov-os-worktrees/W2-96/src python3 /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/select_tests.py /home/usain/gov-os-worktrees/W2-96 W2-96 DAEO-ouet > "$L/select6.json" 2> "$L/select6.err"
echo $? > "$L/select6.exit"
TMPDIR=/tmp/gov-os-lead-W2-96 PYTHONPATH=/home/usain/gov-os-worktrees/W2-96/src python3 -m pytest tests --collect-only -q -p no:cacheprovider --no-header > "$L/collect5.out" 2>&1
echo $? > "$L/collect5.exit"
PYTHONPATH=/home/usain/gov-os-worktrees/W2-96/src python3 /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/trailer_gate.py DAEO-ouet /home/usain/gov-os-worktrees/W2-96 > "$L/trailer5.out" 2>&1
python3 /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/keyword_warn.py /home/usain/gov-os-worktrees/W2-96 > "$L/keyword6.out" 2>&1
du -sh /tmp/gov-os-lead-W2-96 /home/usain/gov-os-worktrees/W2-96/.gov-runtime > "$L/scratch5-end.txt" 2>&1
du -s --inodes /tmp/gov-os-lead-W2-96 /home/usain/gov-os-worktrees/W2-96/.gov-runtime >> "$L/scratch5-end.txt" 2>&1
echo done > "$L/final5.done"
