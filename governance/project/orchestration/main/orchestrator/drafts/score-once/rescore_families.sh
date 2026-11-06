#!/usr/bin/env bash
# DEC-1079: every kept run re-scored with source families (W2-61h S7, W2-134; merged 50d79efe), no retrieval, no GPU.
# The merged measure (the main tree's src) reads each run's kept outputs (--kept) twice:
#   nofam: --root the g1 clone at e884675b (no families declared): a control, must give the run's own counts;
#   fam:   --root ~/gov-os-runs/D4B/g1-fam, the same commit with integrate's evaluation_families block only.
# Counts only (score138.py); the per-question lines stay in ~/gov-os-runs.
set -uo pipefail
R=/home/usain/Dynamic-Agentic-Engineering-OS; D=$R/.gov-runtime/scratch/orchestrator/drafts/d4b
KEPT=$HOME/gov-os-eval/runs/score-once-replay; OUT=$HOME/gov-os-runs/D4B/rescore
NAMES="g-B0 g-A1 g-A2 g-A3 g-C1 g-C2 g-C3 g-C4 g-M1 g-M2 g-M3 g-M4 g-M5 g-M6 g-T1 g-T2 g-T3 a-q06 a-q4b a-gte a-zer ext-d80 ext-split ext-termmap ext-split-termmap l6"
for mode in nofam fam; do
  root=$HOME/gov-os-runs/D4B/g1/repo; [ $mode = fam ] && root=$HOME/gov-os-runs/D4B/g1-fam
  for n in $NAMES; do
    for set in r80 r60; do
      case $set in r80) MSET=memory-retrieval PART=all ;; r60) MSET=memory-verdict PART=hidden ;; esac
      o=$OUT/$mode/$n/$set; mkdir -p "$o"
      env -u GOV_TICKET GOV_ROLE=orchestrator PYTHONPATH="$R/src" python3 -m gov.retrieval.measure "$MSET" \
        --root "$root" --sets-root "$HOME/gov-os-eval" --part "$PART" --kept "$KEPT/$n-$set" --gov /bin/false \
        > "$o/measure.txt" 2> "$o/measure.err" || echo "RESCORE FAILED $mode $n $set (rc $?)"
    done
    echo "$mode $(python3 "$D/score138.py" "$n" "$OUT/$mode/$n/r80/measure.txt" "$OUT/$mode/$n/r60/measure.txt")"
    echo "$mode $n: unresolved $(cat "$OUT/$mode/$n"/r*/measure.txt "$OUT/$mode/$n"/r*/measure.err | grep -c unresolved); first line $(head -n 1 "$OUT/$mode/$n/r80/measure.txt")"
  done
done
echo "== the control (nofam) against each run's own counts"
for n in $NAMES; do
  python3 "$D/score138.py" --same "$OUT/nofam/$n/r80/measure.txt" "$OUT/nofam/$n/r60/measure.txt" \
    "$HOME/gov-os-runs/D4B/score-once-replay/$n/r80/measure.txt" "$HOME/gov-os-runs/D4B/score-once-replay/$n/r60/measure.txt" | sed "s/^/$n: /"
done
echo "== with families: each run against B0"
for n in $NAMES; do
  python3 "$R/.gov-runtime/scratch/orchestrator/drafts/score-once/mcnemar.py" "$OUT/fam/g-B0/r80/measure.txt" "$OUT/fam/g-B0/r60/measure.txt" \
    "$OUT/fam/$n/r80/measure.txt" "$OUT/fam/$n/r60/measure.txt" | sed "s/^/$n: /"
done
