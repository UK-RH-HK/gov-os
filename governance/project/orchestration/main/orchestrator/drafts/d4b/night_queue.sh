#!/usr/bin/env bash
# The night's structural steps 5-7 (DEC-1073 (1)), one GPU job after another in this one script (no waiter, no name
# match: L-0075). Each clone is built (measure_m.sh, BUILD_ONLY) and measured through the harness with the best
# structure's variant V, one run, all 80; scored on the 79 (score79.py).
#   V='<json without braces>' night_queue.sh
set -u
O=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/d4b
V=${V:?the best structure harness variant, as JSON members without braces}
P=f8a5fdadecef8744d494e9d07146bebbaa8a4f56   # w2/W2-32-proto: C1 heading_path_everywhere, C2 answer_units
G=e884675b                                   # w2/W2-92-proto: the stated links (kinds 1-4) and the bounded hop
step() {  # step <point> <commit> <flags|none> <harness extra JSON members or ''>
  local pt=$1 c=$2 f=$3 x=$4
  echo "#### $pt ($c, flags $f, harness +{$x}) $(date +%T)"
  BUILD_ONLY=1 bash $O/measure_m.sh "$pt" "$c" "$f" 2>&1 | grep -vE "^== .*D-4b" | tail -6 || return 1
  grep -q "built (BUILD_ONLY)" "$HOME/gov-os-runs/D4B/$pt/measure.log" || { echo "BUILD FAILED: $pt"; return 1; }
  CLONE=$HOME/gov-os-runs/D4B/$pt/repo bash $O/measure_rx.sh "$pt-rx" 1 v "{$V${x:+,$x}}" 2>&1 | tail -2
  python3 $O/score79.py "$HOME/gov-os-runs/D4B/$pt-rx/v/run1/measure.txt"
}
step p0 $P none ''                                                     # the prototypes' base: the control
step p1 $P heading_path_everywhere ''                                  # C1, its keyword half (its reranker half = decorate, measured in fix-d: not adopted)
step p2 $P answer_units ''                                             # C2
step p3 $P heading_path_everywhere,answer_units ''                     # C1 (keyword half) + C2
step g1 $G none ''                                                     # the stated links
echo "-- drift on the g1 store"; PYTHONPATH=$HOME/gov-os-runs/D4B/g1/repo/src python3 $HOME/gov-os-runs/D4B/g1/repo/docs/research/W2-92-proto-drift.py \
  $HOME/gov-os-runs/D4B/g1/repo $HOME/gov-os-runs/D4B/diag/drift-g1.json 2>&1 | tail -12
step g2 $G chunk_register_by_entry ''                                  # the stated links + M5 (DEC-1073 (3))
echo "== night queue done $(date +%T)"
