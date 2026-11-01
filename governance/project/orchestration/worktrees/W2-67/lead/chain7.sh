#!/bin/bash
# Run 7: wait for rebuild-9's exit file; if it is 0, run verify7.sh (which waits for the load and the disk gate itself).
LOG=/home/usain/gov-os-worktrees/W2-67/.gov-runtime/scratch/lead/log
until [ -s "$LOG/rebuild-9.exit" ]; do sleep 30; done
if [ "$(cat "$LOG/rebuild-9.exit")" = "0" ]; then
  bash /home/usain/gov-os-worktrees/W2-67/.gov-runtime/scratch/lead/verify7.sh
else
  echo "rebuild-9 exit $(cat "$LOG/rebuild-9.exit"): verify7 not started" > "$LOG/verify-r7.done"
fi
