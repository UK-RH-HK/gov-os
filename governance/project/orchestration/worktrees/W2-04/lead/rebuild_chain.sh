#!/usr/bin/env bash
# Wait for rebuild-3 to end (it is stopped at its background limit); if it did not succeed, run rebuild-4 at once
# (the semantic stage embeds only the chunks that have no vector, so rebuild-3's progress is kept).
set -u
L=/home/usain/gov-os-worktrees/W2-04/.gov-runtime/scratch/lead/log
until [ -s "$L/rebuild-3.rc" ] || ! pgrep -f "gov-os-heavy-slot-2.lock python3 -m gov.cli.main rebuild" > /dev/null; do sleep 2; done
sleep 1
if [ "$(cat "$L/rebuild-3.rc" 2>/dev/null)" = "0" ]; then
  echo skipped > /home/usain/gov-os-worktrees/W2-04/.gov-runtime/scratch/lead/log/rebuild-4.rc
  exit 0
fi
cd /home/usain/gov-os-worktrees/W2-04 || exit 2
PYTHONPATH=/home/usain/gov-os-worktrees/W2-04/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/rebuild_slot.sh /home/usain/gov-os-worktrees/W2-04 > /home/usain/gov-os-worktrees/W2-04/.gov-runtime/scratch/lead/log/rebuild-4.json 2>&1
echo $? > /home/usain/gov-os-worktrees/W2-04/.gov-runtime/scratch/lead/log/rebuild-4.rc
