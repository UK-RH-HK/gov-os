#!/usr/bin/env bash
# The three red checks of gov check, each alone, output to files (read later by summary lines only).
cd /home/usain/gov-os-worktrees/W2-90b || exit 9
export TMPDIR=/tmp/gov-os-lead-W2-90b
export PYTHONPATH=/home/usain/gov-os-worktrees/W2-90b/src
timeout 900 python3 -m gov.secrets > /home/usain/gov-os-worktrees/W2-90b/.gov-runtime/scratch/lead/log/chk-secrets.txt 2>&1
echo $? > /home/usain/gov-os-worktrees/W2-90b/.gov-runtime/scratch/lead/log/chk-secrets.exit
timeout 900 python3 -m gov.retrieval.retrieve_check > /home/usain/gov-os-worktrees/W2-90b/.gov-runtime/scratch/lead/log/chk-retrieval.txt 2>&1
echo $? > /home/usain/gov-os-worktrees/W2-90b/.gov-runtime/scratch/lead/log/chk-retrieval.exit
timeout 1800 python3 -m gov.context.context_check > /home/usain/gov-os-worktrees/W2-90b/.gov-runtime/scratch/lead/log/chk-context.txt 2>&1
echo $? > /home/usain/gov-os-worktrees/W2-90b/.gov-runtime/scratch/lead/log/chk-context.exit
