#!/bin/bash
# The "before" measure: a clone of the ticket's base, rebuilt twice (the second on the unchanged tree), then a second
# clone rebuilt after the first. Base code has no cache, so all three scan everything; the figures are the secrets
# stage's seconds. Waits for the load gate and the disk gate before each rebuild; every rebuild under the machine lock.
set -u
LOG=/home/usain/gov-os-worktrees/W2-107/.gov-runtime/scratch/lead/log
MEASURE=/home/usain/gov-os-worktrees/W2-107/.gov-runtime/scratch/lead/measure_rebuild.py
export TMPDIR=/tmp/gov-os-lead-W2-107

gate() {
  until python3 -c "import os; l=os.getloadavg(); exit(0 if min(l[0], l[2]) < os.cpu_count() else 1)"; do sleep 60; done
  bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/disk_gate.sh || exit 3
}

run() {  # $1 clone folder, $2 label
  gate
  date -u +%FT%TZ >> /tmp/gov-os-lead-W2-107/before.times
  (cd "$1" && flock /tmp/gov-os-rebuild.lock env PYTHONPATH="$1/src" python3 "$MEASURE" "$2") >> /tmp/gov-os-lead-W2-107/before.jsonl 2>> /tmp/gov-os-lead-W2-107/before.err
  echo "$2 exit $?" >> /tmp/gov-os-lead-W2-107/before.times
  cat /proc/loadavg >> /tmp/gov-os-lead-W2-107/before.times
}

git clone -q --no-hardlinks --branch w2/W2-107 /home/usain/gov-os-worktrees/W2-107 /tmp/gov-os-lead-W2-107/m-before-a
git -C /tmp/gov-os-lead-W2-107/m-before-a checkout -q 0062ed549674
run /tmp/gov-os-lead-W2-107/m-before-a before-first
run /tmp/gov-os-lead-W2-107/m-before-a before-second-unchanged
git clone -q --no-hardlinks --branch w2/W2-107 /home/usain/gov-os-worktrees/W2-107 /tmp/gov-os-lead-W2-107/m-before-b
git -C /tmp/gov-os-lead-W2-107/m-before-b checkout -q 0062ed549674
run /tmp/gov-os-lead-W2-107/m-before-b before-second-clone
echo done >> /tmp/gov-os-lead-W2-107/before.times
