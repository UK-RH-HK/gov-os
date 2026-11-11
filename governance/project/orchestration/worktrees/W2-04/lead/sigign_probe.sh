#!/usr/bin/env bash
# Shows the ignored-signal mask a child gets when started the way lead_verify.sh starts its run (setsid ... &).
OUT=/home/usain/gov-os-worktrees/W2-04/.gov-runtime/scratch/lead/log/sigign-probe.txt
echo "caller: $(grep SigIgn /proc/$$/status)" > "$OUT"
setsid bash /home/usain/gov-os-worktrees/W2-04/.gov-runtime/scratch/lead/sigign_child.sh < /dev/null >> "$OUT" 2>&1 &
wait
sleep 1
