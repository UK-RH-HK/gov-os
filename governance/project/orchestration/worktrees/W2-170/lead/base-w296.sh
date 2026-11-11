#!/usr/bin/env bash
# One W2-96 case on base code (W2-00-store-a, w2/integrate's line, no W2-170 change), same env as the re-run.
cd /home/usain/gov-os-worktrees/W2-00-store-a || exit 2
git rev-parse --short=12 HEAD
env HOME=/home/usain/gov-os-worktrees/W2-170/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local \
  PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/home/usain/gov-os-worktrees/W2-00-store-a/src TMPDIR=/tmp/gov-os-lead-W2-170 \
  python3 -m pytest -q -p no:cacheprovider -o tmp_path_retention_policy=failed \
  "tests/unit/accept/test_w2_96_review3.py::test_w2_96_r14_a_stopped_run_keeps_128_plus_the_signal[True-2]" \
  > /home/usain/gov-os-worktrees/W2-170/.gov-runtime/scratch/lead/log/base-w296.txt 2>&1
echo "exit $?"
tail -3 /home/usain/gov-os-worktrees/W2-170/.gov-runtime/scratch/lead/log/base-w296.txt
