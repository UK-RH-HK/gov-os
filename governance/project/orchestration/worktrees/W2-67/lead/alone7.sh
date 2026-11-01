#!/bin/bash
# Run 7: part B's two errors (W2-54's green_here file: its session fixture's gov check passed the 900 s limit under a
# load of ~45 on 20 processors) re-run alone after the suite parts ended, in the close's form; then gov check again.
LOG=/home/usain/gov-os-worktrees/W2-67/.gov-runtime/scratch/lead/log
W=/home/usain/gov-os-worktrees/W2-67
cd "$W" || exit 99
export TMPDIR=/tmp/gov-os-lead-W2-67
date -Is > "$LOG/alone-7.start"
PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=$W/src:$W/src/gov/close/pytest_plugin GOV_CLOSE_SERIAL_ONLY_OF=$W \
  python3 -m pytest tests/acceptance/W2-54/test_w2_54_green_here.py -q -p no:cacheprovider -p gov_close_serial_only \
  --timeout=900 --timeout_method=signal -o tmp_path_retention_policy=failed -rs > "$LOG/alone-7.out" 2>&1
echo $? > "$LOG/alone-7.exit"
date -Is >> "$LOG/alone-7.start"
bash "$W/.gov-runtime/scratch/lead/check7.sh"
