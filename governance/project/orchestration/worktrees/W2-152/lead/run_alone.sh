#!/bin/bash
# The load-sensitive red re-run alone, then the pre-close collection check (DEC-868).
TREE=/home/usain/gov-os-worktrees/W2-152
cd "$TREE" || exit 90
export TMPDIR=/tmp/gov-os-lead-W2-152
export PYTHONUSERBASE=/home/usain/.local
export PYTHONPATH=$TREE/src
bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest \
  "tests/unit/resources/test_w2_157_backstop.py::test_l5b_the_own_group_is_stopped_after_every_other_group_the_trip_line_and_the_item[middle]" \
  -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rs \
  --junitxml=/home/usain/gov-os-worktrees/W2-152/.gov-runtime/scratch/lead/log/w2157-alone.xml \
  > /home/usain/gov-os-worktrees/W2-152/.gov-runtime/scratch/lead/log/w2157-alone.log 2>&1
echo $? > /home/usain/gov-os-worktrees/W2-152/.gov-runtime/scratch/lead/log/w2157-alone.exit
python3 -m pytest tests --collect-only -q -p no:cacheprovider --no-header \
  > /home/usain/gov-os-worktrees/W2-152/.gov-runtime/scratch/lead/log/collect.log 2>&1
echo $? > /home/usain/gov-os-worktrees/W2-152/.gov-runtime/scratch/lead/log/collect.exit
echo done > /home/usain/gov-os-worktrees/W2-152/.gov-runtime/scratch/lead/log/alone.done
