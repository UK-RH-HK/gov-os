#!/bin/bash
# Run 6: gov check again after moving the hash-bearing test outputs out of .gov-runtime (row W2-L423's rule),
# then the code-index case alone once the machine-wide rebuild lock is free (it waited 300 s on another
# session's rebuild twice). Outputs outside the tracked tree.
OUT=/tmp/gov-os-lead-W2-05/v6-results
LOG=/home/usain/gov-os-worktrees/W2-05/.gov-runtime/scratch/lead/log/v6
cd /home/usain/gov-os-worktrees/W2-05 || exit 9
PYTHONPATH=/home/usain/gov-os-worktrees/W2-05/src python3 -m gov.cli.main check --json > "$OUT/check2.json" 2> "$OUT/check2.err"
echo $? > "$LOG/check2.exit"
until flock -n /tmp/gov-os-rebuild.lock true; do sleep 20; done
date > "$LOG/codeindex.start"
TMPDIR=/tmp/gov-os-lead-W2-05 PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH \
PYTHONPATH=/home/usain/gov-os-worktrees/W2-05/src \
  python3 /home/usain/gov-os-worktrees/W2-05/.gov-runtime/scratch/lead/runner6.py \
  python3 -m pytest "tests/acceptance/W2-05/test_w2_05_code_index_tool.py" -q -p no:cacheprovider \
  -o tmp_path_retention_policy=failed -rfEs > "$OUT/codeindex.txt" 2>&1
echo $? > "$LOG/codeindex.exit"
date >> "$LOG/codeindex.start"
