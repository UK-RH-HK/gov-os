#!/usr/bin/env bash
# Run 2, verification step 2 (DEC-956 item 2): a real rebuild of a scratch clone holds the machine's rebuild lock
# while suites run. Arg 1: the stop file's name under log/; arg 2: a tag for the log names (hold-inner.sh).
W=/home/usain/gov-os-worktrees/W2-76
LOG=$W/.gov-runtime/scratch/lead/log
C=/tmp/gov-os-lead-W2-76/clone
cd /tmp/gov-os-lead-W2-76 || exit 2
until python3 /home/usain/gov-os-worktrees/W2-76/.gov-runtime/scratch/lead/loadok.py; do sleep 60; done
bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/disk_gate.sh > "$LOG/$2.gate" 2>&1 || { echo 3 > "$LOG/$2.exit"; exit 3; }
if [ ! -d "$C/.git" ]; then
  git clone -q --shared -b w2/W2-76 "$W" "$C" > "$LOG/$2-clone.out" 2>&1 || { echo 5 > "$LOG/$2.exit"; exit 5; }
fi
TMPDIR=/tmp/gov-os-lead-W2-76 flock /tmp/gov-os-rebuild.lock bash "$W/.gov-runtime/scratch/lead/hold-inner.sh" "$1" "$2"
echo $? > "$LOG/$2.exit"
