#!/usr/bin/env bash
# The parallel phase's ten lock-wait reds, each re-run alone after the suites, with the machine's rebuild lock's
# holder recorded before each (DEC-757 practice: a red that passes alone is load- or contention-made).
W=/home/usain/gov-os-worktrees/W2-76
LOG=$W/.gov-runtime/scratch/lead/log
cd "$W" || exit 2
until [ ! -e /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/NIGHTLY-RUNNING ]; do sleep 60; done
: > "$LOG/alone.out"
while read -r case; do
  [ -n "$case" ] || continue
  echo "== $(date '+%T') $case; lock holders: $(grep -c ' 08:30:427810 ' /proc/locks)" >> "$LOG/alone.out"
  env -u PYTEST_ADDOPTS -u PYTEST_PLUGINS TMPDIR=/tmp/gov-os-lead-W2-76 "PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH" PYTHONPATH=$W/src \
    python3 -m pytest "$case" -q -p no:cacheprovider -o tmp_path_retention_policy=failed --no-header >> "$LOG/alone.out" 2>&1
  echo "exit $?" >> "$LOG/alone.out"
done < "$W/.gov-runtime/scratch/lead/alone.txt"
echo done > "$LOG/alone.exit"
