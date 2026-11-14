#!/usr/bin/env bash
cd /home/usain/gov-os-worktrees/W2-93
export TMPDIR=/tmp/w2-93-lead PYTHONUSERBASE=/home/usain/.local
bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh env HOME=/home/usain/gov-os-worktrees/W2-93/.gov-runtime/scratch/empty-home PYTHONPATH=/home/usain/gov-os-worktrees/W2-93/src python3 -m pytest ${1:-tests/acceptance/W2-93} -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit" -rf --tb=line > /home/usain/gov-os-worktrees/W2-93/.gov-runtime/scratch/lead/log/${2:-pt93-1}.txt 2>&1
echo $? > /home/usain/gov-os-worktrees/W2-93/.gov-runtime/scratch/lead/log/${2:-pt93-1}.exit
