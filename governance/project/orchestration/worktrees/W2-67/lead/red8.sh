#!/bin/bash
# Run 3's red check of batch 8 (td-8): the case under the lead's plant (release switched off), then the head.
set -u
W=/home/usain/gov-os-worktrees/W2-67
OUT=/tmp/gov-os-lead-W2-67/red8
LOG=$W/.gov-runtime/scratch/lead/log/red8.txt
export TMPDIR=/tmp/gov-os-lead-W2-67
mkdir -p "$OUT"
cd "$W" || exit 99
F=tests/acceptance/W1-27/test_w2_67_codegraph_folders.py
: > "$LOG"
: > "$OUT/marker"
until awk '{exit !($1 < 20)}' /proc/loadavg; do sleep 60; done
b=$(ls /tmp/gov-cbm-$(id -u) | wc -l)
LEAD_PLANT8_MARKER=$OUT/marker PYTHONPATH=$W/src:$W/.gov-runtime/scratch/lead/plant8 timeout 3000 \
  python3 -m pytest -p lead_plant8 -p no:cacheprovider -o tmp_path_retention_policy=failed -q --no-header -n 3 -rA \
  --junitxml="$OUT/plant.xml" $F > "$OUT/plant.out" 2>&1
echo "plant exit=$? $(tail -1 "$OUT/plant.out") marker_lines=$(wc -l < "$OUT/marker") cbm $b -> $(ls /tmp/gov-cbm-$(id -u) | wc -l)" >> "$LOG"
until awk '{exit !($1 < 20)}' /proc/loadavg; do sleep 60; done
b=$(ls /tmp/gov-cbm-$(id -u) | wc -l)
PYTHONPATH=$W/src timeout 3000 python3 -m pytest -p no:cacheprovider -o tmp_path_retention_policy=failed -q --no-header \
  -n 3 -rA --junitxml="$OUT/head.xml" $F > "$OUT/head.out" 2>&1
echo "head exit=$? $(tail -1 "$OUT/head.out") cbm $b -> $(ls /tmp/gov-cbm-$(id -u) | wc -l)" >> "$LOG"
echo done >> "$LOG"
