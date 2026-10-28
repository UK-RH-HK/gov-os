#!/usr/bin/env bash
# Lead run 5, step 4: the suites the merge touches, first (W2-07, W2-57 acceptance; tests/unit/close), from this
# worktree's src, in one process without -n (serial-only entries among them run alone this way), with the retention
# option (DEC-905). Exit code in log/r5-touched.exit.
cd /home/usain/gov-os-worktrees/W2-07 || exit 90
L=/home/usain/gov-os-worktrees/W2-07/.gov-runtime/scratch/lead/log
CLOSE=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/CLOSE-RUNNING
export TMPDIR=/tmp/gov-os-lead-W2-07
mkdir -p "$TMPDIR"
until [ ! -e "$CLOSE" ]; do sleep 60; done
until awk '{exit !($1 < 20)}' /proc/loadavg; do sleep 60; done
{ date -Is; cat /proc/loadavg; bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/disk_gate.sh; du -s --inodes "$TMPDIR"; du -sh "$TMPDIR"; } > "$L/r5-touched.gate" 2>&1 \
  || { echo 91 > "$L/r5-touched.exit"; exit 91; }
export PATH="/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH"
PYTHONPATH=/home/usain/gov-os-worktrees/W2-07/src python3 -m pytest tests/acceptance/W2-07 tests/acceptance/W2-57 tests/unit/close \
  -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rs --junitxml="$L/r5-touched.xml" > "$L/r5-touched.txt" 2>&1
echo $? > "$L/r5-touched.exit"
{ date -Is; du -s --inodes "$TMPDIR"; du -sh "$TMPDIR"; } >> "$L/r5-touched.gate" 2>&1
