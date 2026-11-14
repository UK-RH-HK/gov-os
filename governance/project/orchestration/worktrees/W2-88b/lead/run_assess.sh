#!/usr/bin/env bash
# W2-88b: the assessment only (MA, --assess-only: writes nothing in the clone), one process per repository, through
# the heavy slot (DEC-1001 (d)); the lead's run outside the sandbox. Usage: bash run_assess.sh <name> <root> [extra args]
set -u
W=/home/usain/gov-os-worktrees/W2-88b
name=$1 root=$2; shift 2
cd "$W" || exit 2
echo "assess $name start $(date -Is)"
env PYTHONPATH=$W/src PYTHONUSERBASE=/home/usain/.local \
  bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh \
  python3 experiments/W2-88/proof_bc.py --repo "$name-assess" --root "$root" --runs /home/usain/gov-os-runs/W2-88b \
  --assess-only "$@"
echo "assess $name rc=$? end $(date -Is)"
