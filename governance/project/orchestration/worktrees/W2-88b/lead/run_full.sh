#!/usr/bin/env bash
# W2-88b: one full proof run (path map, A0..A9 lite, the real embedder, the shared reranker, the code graph), one
# process per repository, through the heavy slot (DEC-1001 (d)); the lead's run outside the sandbox, real HOME.
# Usage: bash run_full.sh <name> <root> [extra args]
set -u
W=/home/usain/gov-os-worktrees/W2-88b
name=$1 root=$2; shift 2
cd "$W" || exit 2
echo "full $name start $(date -Is)"
env PYTHONPATH=$W/src PYTHONUSERBASE=/home/usain/.local \
  bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh \
  python3 experiments/W2-88/proof_bc.py --repo "$name" --root "$root" --runs /home/usain/gov-os-runs/W2-88b "$@"
echo "full $name rc=$? end $(date -Is)"
