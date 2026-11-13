#!/usr/bin/env bash
# Proof (a) with the real embedder, the lead's run outside the sandbox (RV1-7 / S5's scan time); output under ~/gov-os-runs/W2-88
mkdir -p /tmp/gov-os-lead-W2-88
cd /home/usain/gov-os-runs/W2-88 || exit 2
env TMPDIR=/tmp/gov-os-lead-W2-88 PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-88/src \
  bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh \
  python3 /home/usain/gov-os-runs/W2-88/proof_a_real.py \
  > /home/usain/gov-os-worktrees/W2-88/.gov-runtime/scratch/lead/log/proof-real.txt 2>&1
rc=$?
echo "$rc" > /home/usain/gov-os-worktrees/W2-88/.gov-runtime/scratch/lead/log/proof-real.exit
exit "$rc"
