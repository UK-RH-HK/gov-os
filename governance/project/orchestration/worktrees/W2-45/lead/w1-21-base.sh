#!/usr/bin/env bash
# Lead: W1-21's merge file at the base 0098b58d5, from a git archive copy outside the repository.
set -u
D=/tmp/gov-os-lead-W2-45/base-0098b58d5
rm -rf /tmp/gov-os-lead-W2-45/base-0098b58d5
mkdir -p /tmp/gov-os-lead-W2-45/base-0098b58d5
git -C /home/usain/gov-os-worktrees/W2-45 archive 0098b58d5 | tar -x -C "$D"
cd "$D" || exit 2
env GOV_TESTS_OPTIN=lifted,breadth TMPDIR=/tmp/gov-os-lead-W2-45 PYTHONUSERBASE=/home/usain/.local \
  HOME=/home/usain/gov-os-worktrees/W2-45/.gov-runtime/scratch/empty-home PYTHONPATH="$D/src" \
  bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh \
  python3 -m pytest tests/acceptance/W1-21/test_w1_21_merge.py -q -p no:cacheprovider -o tmp_path_retention_policy=failed
echo "exit $?"
cd /tmp && rm -rf /tmp/gov-os-lead-W2-45/base-0098b58d5
