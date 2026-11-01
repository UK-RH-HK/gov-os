#!/usr/bin/env bash
# Run 2, verification step 1: this ticket's acceptance suite and tests/unit/rebuild, this worktree's code, unsandboxed.
W=/home/usain/gov-os-worktrees/W2-76
LOG=$W/.gov-runtime/scratch/lead/log
cd "$W" || exit 2
until [ ! -e /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/NIGHTLY-RUNNING ]; do sleep 60; done
du -s --inodes /tmp/gov-os-lead-W2-76 "$W/.gov-runtime" > "$LOG/step1.scratch-before" 2>&1
date '+start %F %T' > "$LOG/step1.summary"
env -u PYTEST_ADDOPTS -u PYTEST_PLUGINS TMPDIR=/tmp/gov-os-lead-W2-76 "PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH" PYTHONPATH=$W/src \
  python3 -m pytest tests/acceptance/W2-76 tests/unit/rebuild -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rfEs \
  --junitxml="$LOG/step1.xml" > "$LOG/step1.out" 2>&1
code=$?
echo "end $(date '+%F %T') exit $code: $(tail -1 "$LOG/step1.out")" >> "$LOG/step1.summary"
echo "$code" > "$LOG/step1.exit"
