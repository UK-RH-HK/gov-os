#!/usr/bin/env bash
# One scoped pytest run of this worktree's code. Arg 1: tag; the rest: pytest arguments.
TAG=$1; shift
LOG=/home/usain/gov-os-worktrees/W2-76/.gov-runtime/scratch/lead/log
mkdir -p /tmp/gov-os-lead-W2-76
cd /home/usain/gov-os-worktrees/W2-76 || exit 2
until [ ! -e /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/NIGHTLY-RUNNING ]; do sleep 60; done
TMPDIR=/tmp/gov-os-lead-W2-76 PYTHONPATH=/home/usain/gov-os-worktrees/W2-76/src python3 -m pytest "$@" -p no:cacheprovider -o tmp_path_retention_policy=failed -rs --junitxml="$LOG/$TAG.xml" > "$LOG/$TAG.out" 2>&1
echo $? > "$LOG/$TAG.exit"
