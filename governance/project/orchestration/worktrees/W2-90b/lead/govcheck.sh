#!/usr/bin/env bash
cd /home/usain/gov-os-worktrees/W2-90b || exit 9
TMPDIR=/tmp/gov-os-lead-W2-90b PYTHONPATH=/home/usain/gov-os-worktrees/W2-90b/src python3 -m gov.cli.main check --json > /home/usain/gov-os-worktrees/W2-90b/.gov-runtime/scratch/lead/log/govcheck.json 2> /home/usain/gov-os-worktrees/W2-90b/.gov-runtime/scratch/lead/log/govcheck.err
echo $? > /home/usain/gov-os-worktrees/W2-90b/.gov-runtime/scratch/lead/log/govcheck.exit
