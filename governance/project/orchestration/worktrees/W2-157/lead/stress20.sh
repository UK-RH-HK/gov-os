#!/usr/bin/env bash
# The lead's proof (DEC-1144 (2)): the backstop unit file 20 times in a row under load, each under timeout 120.
# Runs inside heavy_slot.sh, so the busy loops share the slot's CPU set with pytest (load = one busy loop per CPU).
cd /home/usain/gov-os-worktrees/W2-157 || exit 2
mkdir -p /tmp/w2-157-lead
OUT=/home/usain/gov-os-worktrees/W2-157/.gov-runtime/scratch/lead/${STRESS_OUT:-stress20.txt}
: > "$OUT"
CPUS=$(OMP_NUM_THREADS= nproc)  # nproc honours OMP_NUM_THREADS (heavy_slot's thread budget); the slot's CPU set is wanted
PIDS=()
for _ in $(seq 1 "$CPUS"); do
  python3 -c "while True: pass" &
  PIDS+=($!)
done
echo "load: $CPUS busy loops on $(nproc) CPUs (slot ${GOV_HEAVY_SLOT:-?}, cpus ${GOV_HEAVY_CPUS:-unconfined}); pids ${PIDS[*]}" >> "$OUT"
for i in $(seq 1 20); do
  start=$(date +%s)
  timeout 120 env TMPDIR=/tmp/w2-157-lead HOME=/home/usain/gov-os-worktrees/W2-157/.gov-runtime/scratch/empty-home \
    PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-157/src \
    python3 -m pytest tests/unit/resources/test_w2_157_backstop.py -q -p no:cacheprovider \
    -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit" \
    > /tmp/w2-157-lead/run.out 2>&1
  code=$?
  line=$(tail -1 /tmp/w2-157-lead/run.out)
  echo "run $i: exit $code; $(( $(date +%s) - start )) s; $line" >> "$OUT"
done
for p in "${PIDS[@]}"; do kill "$p" 2>/dev/null; done
wait 2>/dev/null
echo "done" >> "$OUT"
