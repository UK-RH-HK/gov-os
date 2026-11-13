#!/usr/bin/env bash
# run 5: the one verify red re-run alone once at b08fae150 (load-sensitive check)
mkdir -p /tmp/w2-115-lead-tmp
cd /home/usain/gov-os-worktrees/W2-115
env TMPDIR=/tmp/w2-115-lead-tmp HOME=/home/usain/gov-os-worktrees/W2-115/.gov-runtime/scratch/empty-home \
  PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-115/src \
  bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh \
  python3 -m pytest "tests/unit/resources/test_w2_157_backstop.py::test_l5b_the_own_group_is_stopped_after_every_other_group_the_trip_line_and_the_item" \
  -q -p no:cacheprovider -o tmp_path_retention_policy=failed --tb=short \
  > /home/usain/gov-os-worktrees/W2-115/.gov-runtime/scratch/lead/log/alone-5.txt 2>&1
echo "exit $?" >> /home/usain/gov-os-worktrees/W2-115/.gov-runtime/scratch/lead/log/alone-5.txt
