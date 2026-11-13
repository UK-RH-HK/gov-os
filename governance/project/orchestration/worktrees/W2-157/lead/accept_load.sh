#!/usr/bin/env bash
# gov accept W2-157 (installed runner, report kept) three times beside one busy loop per CPU of the heavy slot.
cd /home/usain/gov-os-worktrees/W2-157 || exit 2
OUT=/home/usain/gov-os-worktrees/W2-157/.gov-runtime/scratch/lead/accept-load.txt
: > "$OUT"
CPUS=$(OMP_NUM_THREADS= nproc)
PIDS=()
for _ in $(seq 1 "$CPUS"); do python3 -c "while True: pass" & PIDS+=($!); done
echo "load: $CPUS busy loops, cpus ${GOV_HEAVY_CPUS:-unconfined}" >> "$OUT"
for i in 1 2 3; do
  rm -rf /tmp/w2-157-lead/accept-keep
  timeout 900 /home/usain/.local/share/gov-os/pin-797495bdfc70/bin/python \
    /home/usain/gov-os-worktrees/W2-157/.gov-runtime/scratch/lead/accept_keep.py > /tmp/w2-157-lead/accept-load-run.txt 2>&1
  echo "run $i: exit $?" >> "$OUT"
  grep -A3 '"totals"' /tmp/w2-157-lead/accept-load-run.txt | tr -d '\n ' >> "$OUT"; echo >> "$OUT"
  sed -n '/^exit /,$p' /tmp/w2-157-lead/accept-load-run.txt >> "$OUT"
done
for p in "${PIDS[@]}"; do kill "$p" 2>/dev/null; done
wait 2>/dev/null
echo done >> "$OUT"
