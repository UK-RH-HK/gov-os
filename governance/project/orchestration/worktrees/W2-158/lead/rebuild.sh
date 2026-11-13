#!/usr/bin/env bash
# Detached rebuild with an exit file for wait_for.sh (the Bash tool's limit cut the foreground one while it queued).
out=/home/usain/gov-os-worktrees/W2-158/.gov-runtime/scratch/lead/log
rm -f "$out/rebuild.exit"
setsid bash -c '
  env PYTHONPATH=/home/usain/gov-os-worktrees/W2-158/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/rebuild_slot.sh /home/usain/gov-os-worktrees/W2-158 > '"$out"'/rebuild.log 2>&1
  echo $? > '"$out"'/rebuild.exit.tmp && mv '"$out"'/rebuild.exit.tmp '"$out"'/rebuild.exit
' < /dev/null > /dev/null 2>&1 &
echo $! > "$out/rebuild.pid"
echo "rebuild started pid $(cat "$out/rebuild.pid")"
