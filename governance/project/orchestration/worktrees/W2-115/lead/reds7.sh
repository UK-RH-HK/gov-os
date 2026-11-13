#!/usr/bin/env bash
# run 5: the two B-5 reds at 93d722a38, --tb=short, for eng-7's brief (failing output only)
mkdir -p /tmp/w2-115-lead-tmp
cd /home/usain/gov-os-worktrees/W2-115
env TMPDIR=/tmp/w2-115-lead-tmp HOME=/home/usain/gov-os-worktrees/W2-115/.gov-runtime/scratch/empty-home \
  PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-115/src \
  bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh \
  python3 -m pytest \
  "tests/acceptance/W2-115/test_w2_115_reds.py::test_with_the_green_base_not_an_ancestor_a_red_the_parent_also_has_is_still_the_change_s" \
  "tests/acceptance/W2-115/test_w2_115_reds.py::test_with_no_green_record_a_red_an_untrailered_first_commit_caused_is_the_change_s" \
  -q -p no:cacheprovider -o tmp_path_retention_policy=failed --tb=short \
  > /home/usain/gov-os-worktrees/W2-115/.gov-runtime/scratch/brief/reds-7.txt 2>&1
echo "exit $?" >> /home/usain/gov-os-worktrees/W2-115/.gov-runtime/scratch/brief/reds-7.txt
