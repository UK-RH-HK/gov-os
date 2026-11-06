#!/usr/bin/env bash
# S11's check (DEC-1074 (5)): W2-32's build with the pool on, measured through the clone's own gov (the product's path;
# the harness's _phrased override cannot run on W2-32's new signature), on the 80 and the 60, against the harness's
# v456 on the control clone (w4-i: integrate's head, the same content but W2-32's own files). Counts only.
set -uo pipefail
O=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator; D=$O/drafts/d4b
RUN=$HOME/gov-os-runs/D4B/${1:-w4-32}; C=$RUN/repo; OUT=$HOME/gov-os-runs/D4B/${2:-w4-32-product}; mkdir -p "$OUT"
exec > >(tee -a "$OUT/measure.log") 2>&1
G=$(ps -o pgid= -p $$ | tr -d ' '); setsid bash $O/tools/gpu_backstop.sh "$G" < /dev/null > /dev/null 2>&1 & BS=$!
echo "== $(date '+%F %T') the product at $(git -C $C rev-parse --short=12 HEAD), pool on; backstop $BS"
cat > "$OUT/gov" <<EOG
#!/usr/bin/env bash
if [ "\$1" = retrieve ] && [ -n "\${GOV_KEEP:-}" ]; then
  n=\$(flock "\$GOV_KEEP/.n.lock" sh -c 'n=\$(cat "\$0/.n" 2>/dev/null || echo 0); n=\$((n+1)); echo \$n > "\$0/.n"; echo \$n' "\$GOV_KEEP")
  s=\$(date +%s%N); PYTHONPATH="$C/src" python3 -m gov.cli.main "\$@" | tee "\$GOV_KEEP/\$(printf %05d \$n).json"; rc=\${PIPESTATUS[0]}
  echo \$(( (\$(date +%s%N) - s) / 1000000 )) >> "\$GOV_MS"; exit \$rc
fi
PYTHONPATH="$C/src" exec python3 -m gov.cli.main "\$@"
EOG
chmod +x "$OUT/gov"
for set in memory-retrieval:all:r80 memory-verdict:hidden:r60; do
  IFS=: read -r S PART N <<< "$set"; K=$HOME/gov-os-eval/runs/$(basename $OUT)/$N; mkdir -p "$K" "$OUT/$N"; : > "$K/.n"; : > "$OUT/$N/ms"
  t0=$(date +%s)
  env -u GOV_TICKET GOV_ROLE=orchestrator GOV_KEEP="$K" GOV_MS="$OUT/$N/ms" TMPDIR=/tmp/gov-os-emg-m3 PYTHONPATH="$C/src" \
    bash $O/tools/heavy_slot.sh python3 -m gov.retrieval.measure "$S" --root "$C" --sets-root "$HOME/gov-os-eval" --part "$PART" \
    --out "$OUT/$N" --gov "$OUT/gov" > "$OUT/$N/measure.txt" 2> "$OUT/$N/measure.err" || echo "MEASURE FAILED ($N)"
  echo "$N: $(( $(date +%s) - t0 )) s; median call $(sort -n $OUT/$N/ms | awk '{a[NR]=$1} END {if (NR) print a[int((NR+1)/2)]}') ms"
done
python3 $D/score138.py product-pool-on $OUT/r80/measure.txt $OUT/r60/measure.txt
python3 $D/score138.py harness-v456-control $HOME/gov-os-runs/D4B/w4-i-rx/v456/run1/measure.txt $HOME/gov-os-runs/D4B/w4-i-rx/v456-60/run1/measure.txt
python3 $D/score138.py --same $OUT/r80/measure.txt $OUT/r60/measure.txt $HOME/gov-os-runs/D4B/w4-i-rx/v456/run1/measure.txt $HOME/gov-os-runs/D4B/w4-i-rx/v456-60/run1/measure.txt
python3 $D/score79.py $OUT/r80/measure.txt
bash $O/tools/proc.sh stop --grace 5 "$BS" > /dev/null 2>&1
echo "== $(date '+%F %T') done"
