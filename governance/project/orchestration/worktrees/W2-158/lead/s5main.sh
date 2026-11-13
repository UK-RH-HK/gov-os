#!/usr/bin/env bash
# S5 on the repository's main tree, with this head's code; no <base>, so links' mark there is not moved.
M=/home/usain/Dynamic-Agentic-Engineering-OS
echo "main head $(git -C $M rev-parse --short=12 HEAD); status lines before: $(git -C $M status --porcelain | wc -l)"
s=$(date +%s.%N)
env PYTHONPATH=/home/usain/gov-os-worktrees/W2-158/src python3 -m gov.cli.main check --structural --root $M
rc=$?
e=$(date +%s.%N)
echo "exit $rc wall $(python3 -c "print(round($e-$s,2))") s"
echo "status lines after: $(git -C $M status --porcelain | wc -l)"
