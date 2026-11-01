#!/bin/bash
# This worktree's full rebuild before verification (DEC-719, DEC-732), timed: a real rebuild of the ticket's code with
# an empty scratch cache (cold), then, $1 = "twice", a second rebuild of the unchanged tree (warm). Under the machine lock.
set -u
export TMPDIR=/tmp/gov-os-lead-W2-107
L=/home/usain/gov-os-worktrees/W2-107/.gov-runtime/scratch/lead/log
M=/home/usain/gov-os-worktrees/W2-107/.gov-runtime/scratch/lead/measure_rebuild.py
cd /home/usain/gov-os-worktrees/W2-107 || exit 4
for label in worktree-after-first-cold worktree-after-second-unchanged; do
  until python3 -c "import os; l=os.getloadavg(); exit(0 if min(l[0], l[2]) < os.cpu_count() else 1)"; do sleep 60; done
  bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/disk_gate.sh || exit 3
  date -u +%FT%TZ >> /home/usain/gov-os-worktrees/W2-107/.gov-runtime/scratch/lead/log/rebuild.times
  flock /tmp/gov-os-rebuild.lock env GOV_SECRETS_CACHE=/tmp/gov-os-lead-W2-107/cache-worktree.sqlite PYTHONPATH=/home/usain/gov-os-worktrees/W2-107/src python3 "$M" "$label" >> /home/usain/gov-os-worktrees/W2-107/.gov-runtime/scratch/lead/log/rebuild.jsonl 2>> /home/usain/gov-os-worktrees/W2-107/.gov-runtime/scratch/lead/log/rebuild.err
  echo "$label exit $? $(date -u +%FT%TZ)" >> /home/usain/gov-os-worktrees/W2-107/.gov-runtime/scratch/lead/log/rebuild.times
  [ "${1:-once}" = twice ] || break
done
