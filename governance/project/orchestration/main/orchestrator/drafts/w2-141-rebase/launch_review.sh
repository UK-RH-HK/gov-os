#!/usr/bin/env bash
# W2-141 rebase review: start the reviewer once gov launch's resource gate is open (gov resources --check, each minute,
# at most 90 tries), through launch_worker.sh (detached). Writes launch_review.exit beside itself: 0 once launch_worker
# started the session, 3 when the gate stayed shut, else launch_worker's code.
set -u
HERE=$(cd "$(dirname "$0")" && pwd)
W=/home/usain/gov-os-worktrees/W2-141-rebase-review
ORCH=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator
rm -f "$HERE/launch_review.exit"
echo $$ > "$HERE/launch_review.pid"
for i in $(seq 1 90); do
  if (cd "$W" && PYTHONPATH="$W/src" python3 -m gov.cli.main resources --check > /dev/null 2>&1); then
    echo "$(date -u '+%F %T') gate open (try $i); launching"
    cd "$W" && LAUNCH_TICKET=DAEO-xwro bash "$ORCH/tools/launch_worker.sh" independent-auditor max \
      "$ORCH/briefs/W2-141-rebase-review.md"
    rc=$?
    echo "$rc" > "$HERE/launch_review.exit"; exit "$rc"
  fi
  echo "$(date -u '+%F %T') gate shut (try $i)"
  sleep 60
done
echo 3 > "$HERE/launch_review.exit"; exit 3
