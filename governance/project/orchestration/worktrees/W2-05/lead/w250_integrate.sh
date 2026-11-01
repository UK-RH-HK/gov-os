#!/bin/bash
# Run 7: W2-50's gov-check case on the integration tree's own code (W2-00-store-a, d88a1fff, W2-107 merged), in the
# close's environment, to tell whether the red is this ticket's. Writes no bytecode there; temp under the lead's folder.
cd /home/usain/gov-os-worktrees/W2-00-store-a || exit 9
LOG=/home/usain/gov-os-worktrees/W2-05/.gov-runtime/scratch/lead/log/v7
OUT=/tmp/gov-os-lead-W2-05/v7-results
rm -f "$LOG/w250-integrate.exit"
PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/gov-os-lead-W2-05 \
PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH \
PYTHONPATH=/home/usain/gov-os-worktrees/W2-00-store-a/src \
env -u GIT_DIR -u GIT_WORK_TREE -u GIT_INDEX_FILE GIT_CONFIG_NOSYSTEM=1 \
  python3 -m pytest -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rfEs --tb=short \
  tests/acceptance/W2-50/test_w2_50_secrets_scan_scale.py::test_a_large_store_among_many_small_files_is_decided_by_gov_check \
  > "$OUT/w250-integrate.txt" 2>&1
echo $? > "$LOG/w250-integrate.exit"
tail -2 "$OUT/w250-integrate.txt" > "$LOG/w250-integrate-tail.txt"
