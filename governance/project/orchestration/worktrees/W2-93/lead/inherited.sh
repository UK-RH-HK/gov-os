#!/usr/bin/env bash
set -u
P=/tmp/w2-93-lead/probe-tree
OUT=/home/usain/gov-os-worktrees/W2-93/.gov-runtime/scratch/lead/log/inherited.txt
git -C /home/usain/gov-os-worktrees/W2-93 worktree add --detach $P 0a693c61aecb > $OUT 2>&1
git -C $P checkout 6d1b7815f -- docs/changes/W2-98-CIT-P.md >> $OUT 2>&1
cd $P
export TMPDIR=/tmp/w2-93-lead PYTHONUSERBASE=/home/usain/.local
for t in "with-fix"; do
  bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh env HOME=/home/usain/gov-os-worktrees/W2-93/.gov-runtime/scratch/empty-home PYTHONPATH=$P/src python3 -m pytest "tests/acceptance/W2-02/test_w2_02_green_here.py::test_core_schema_is_green_on_this_repository" -q -p no:cacheprovider -o tmp_path_retention_policy=failed >> $OUT 2>&1
  echo "$t exit $?" >> $OUT
done
git -C $P checkout HEAD -- docs/changes/W2-98-CIT-P.md >> $OUT 2>&1
cd /home/usain/gov-os-worktrees/W2-93
bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh env HOME=/home/usain/gov-os-worktrees/W2-93/.gov-runtime/scratch/empty-home PYTHONPATH=$P/src python3 -m pytest "$P/tests/acceptance/W2-02/test_w2_02_green_here.py::test_core_schema_is_green_on_this_repository" -q -p no:cacheprovider -o tmp_path_retention_policy=failed --rootdir $P >> $OUT 2>&1
echo "head-as-is exit $?" >> $OUT
git -C /home/usain/gov-os-worktrees/W2-93 worktree remove --force $P >> $OUT 2>&1
echo done >> $OUT
