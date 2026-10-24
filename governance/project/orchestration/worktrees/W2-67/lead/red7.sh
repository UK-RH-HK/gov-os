#!/bin/bash
# Run 3's red check of batch 7 (td-7): each plant against its revised W2-50 cases, then the head; JUnit XML under /tmp.
set -u
W=/home/usain/gov-os-worktrees/W2-67
P=$W/.gov-runtime/scratch/td-7/plant
OUT=/tmp/gov-os-lead-W2-67/red7
LOG=$W/.gov-runtime/scratch/lead/log/red7.txt
export TMPDIR=/tmp/gov-os-lead-W2-67
mkdir -p "$OUT"
cd "$W" || exit 99
F=tests/acceptance/W2-50/test_w2_50_secrets_scan_scale.py
CLEAN=$F::test_a_large_clean_store_is_decided_green
CANARY=$F::test_a_large_store_with_a_canary_across_its_middle_is_red_naming_it
POOL=$F::test_a_large_store_among_many_small_files_is_decided_by_gov_check
HANG="$F::test_a_scan_that_cannot_finish_fails_closed_and_records_nothing[hang]"
declare -A CASES=(
  [fixed-limit]="$CLEAN $CANARY $POOL"
  [first-half-pieces]="$CLEAN $POOL"
  [halves-at-middle]="$CANARY"
  [hang-green]="$HANG"
  [hang-records-clean]="$HANG"
)
: > "$LOG"
for plant in fixed-limit first-half-pieces halves-at-middle hang-green hang-records-clean; do
  until awk '{exit !($1 < 20)}' /proc/loadavg; do sleep 60; done
  PYTHONPATH=$P/$plant:$W/src python3 -m pytest -p no:cacheprovider -o tmp_path_retention_policy=failed -q --no-header \
    -n 3 -rA --junitxml="$OUT/$plant.xml" ${CASES[$plant]} > "$OUT/$plant.out" 2>&1
  echo "$plant exit=$? load=$(cut -d' ' -f1 /proc/loadavg) $(tail -1 "$OUT/$plant.out")" >> "$LOG"
done
until awk '{exit !($1 < 20)}' /proc/loadavg; do sleep 60; done
PYTHONPATH=$W/src python3 -m pytest -p no:cacheprovider -o tmp_path_retention_policy=failed -q --no-header -n 4 -rA \
  --durations=6 --junitxml="$OUT/head.xml" $F > "$OUT/head.out" 2>&1
echo "head exit=$? load=$(cut -d' ' -f1 /proc/loadavg) $(tail -1 "$OUT/head.out")" >> "$LOG"
echo done >> "$LOG"
