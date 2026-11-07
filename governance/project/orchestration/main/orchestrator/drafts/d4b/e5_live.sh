#!/usr/bin/env bash
# E5's live part (E3-E5-DESIGN §1, DEC-1092): the 138 through the pinned gov on E0's clone (c00d525f, its store
# unchanged since E0) with a page of 40 (two batches of 20) within 12,000 tokens; every search's output kept in
# ~/gov-os-eval/runs/w4-e5/ so the reader run takes each question's first bundle. One GPU job, its own process group,
# the backstop armed. Counts only.
set -uo pipefail
O=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator; D=$O/drafts/d4b
RUN=$HOME/gov-os-runs/D4B/w4-e0; C=$RUN/repo; OUT=$HOME/gov-os-runs/D4B/w4-e5; mkdir -p "$OUT"
PINPY=$HOME/.local/share/gov-os/pin-bcea09060ebc/bin/python
exec > >(tee -a "$OUT/e5.log") 2>&1
unset GOV_STORE GOV_TICKET
G=$(ps -o pgid= -p $$ | tr -d ' '); setsid bash $O/tools/gpu_backstop.sh "$G" < /dev/null > /dev/null 2>&1 & BS=$!
echo "== $(date '+%F %T') E5 live: clone at $(git -C "$C" rev-parse --short=12 HEAD), page 40, budget 12000; backstop $BS"
for set in memory-retrieval:all:r80 memory-verdict:hidden:r60; do
  IFS=: read -r S PART N <<< "$set"; K=$HOME/gov-os-eval/runs/w4-e5/$N; mkdir -p "$K" "$OUT/$N"; : > "$K/.n"; : > "$OUT/$N/ms"
  t0=$(date +%s)
  env GOV_ROLE=orchestrator GOV_KEEP="$K" GOV_MS="$OUT/$N/ms" TMPDIR=/tmp/gov-os-emg-e5 \
    bash $O/tools/heavy_slot.sh "$PINPY" -m gov.retrieval.measure "$S" --root "$C" --sets-root "$HOME/gov-os-eval" --part "$PART" \
    --batch-size 20 --bundle-budget 12000 --out "$OUT/$N" --gov "$RUN/out/gov" > "$OUT/$N/measure.txt" 2> "$OUT/$N/measure.err" || echo "MEASURE FAILED ($N)"
  echo "$N: $(( $(date +%s) - t0 )) s"
done
python3 -I $D/e0_figures.py "E5 live (page 40, 12,000 tokens)" $OUT/r80/measure.txt $OUT/r60/measure.txt
bash $O/tools/proc.sh stop --grace 5 "$BS" > /dev/null 2>&1
echo "== $(date '+%F %T') E5 live done"
