#!/bin/bash
# W1-35's suite on the head after ps-5 (the standing sentences word for word), through the heavy-job slot.
cd /home/usain/gov-os-worktrees/W2-11 || exit 99
TMPDIR=/tmp/gov-os-lead-W2-11 PYTHONPATH=/home/usain/gov-os-worktrees/W2-11/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/verify_lock.sh python3 -m pytest tests/acceptance/W1-35 -n auto -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rfE --tb=line --junitxml=/home/usain/gov-os-worktrees/W2-11/.gov-runtime/scratch/lead/log/w135.xml > /home/usain/gov-os-worktrees/W2-11/.gov-runtime/scratch/lead/log/w135.txt 2>&1
echo $? > /home/usain/gov-os-worktrees/W2-11/.gov-runtime/scratch/lead/log/w135.exit
