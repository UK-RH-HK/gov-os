#!/bin/bash
# usage: alone_f6.sh <tree> ; the one red alone, verify env (empty HOME), through the heavy slot
T=$1
cd "$T" || exit 2
export TMPDIR=$(mktemp -d /tmp/w2-177-f6.XXXXXX) || exit 3
env HOME=/home/usain/gov-os-worktrees/W2-177/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=$T/src \
  bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh \
  python3 -m pytest "tests/unit/orchestration/test_w2_149_indep_launch.py::test_f6_a_failed_canary_keeps_its_16_and_counts_its_trace" \
  -q -p no:cacheprovider -o tmp_path_retention_policy=failed 2>&1 | tail -25
rm -rf -- "$TMPDIR"
