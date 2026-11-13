#!/usr/bin/env bash
# The six W2-96 reds on w2/integrate's head (the main tree, clean in src/ and tests/): shared-base evidence for run 3.
mkdir -p /tmp/W2-171-lead-tmp
cd /home/usain/Dynamic-Agentic-Engineering-OS || exit 2
echo "integrate head: $(git rev-parse HEAD)"
TMPDIR=/tmp/W2-171-lead-tmp PYTHONDONTWRITEBYTECODE=1 bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh \
  env HOME=/home/usain/gov-os-worktrees/W2-171/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONDONTWRITEBYTECODE=1 \
  PYTHONPATH=/home/usain/Dynamic-Agentic-Engineering-OS/src python3 -m pytest \
  tests/unit/accept/test_w2_96_run2.py tests/unit/accept/test_w2_96_review3.py tests/unit/accept/test_w2_96_review4.py \
  -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit" 2>&1 | tail -12
