#!/usr/bin/env bash
# SCORE-ONCE (DEC-1081 (3)): one measure run through the score-once harness copy (drafts/score-once/rx.py), with a
# KEPT score cache (never removed: the replays read it). measure_rx.sh's and measure_verdict.sh's form otherwise: every
# search's ranked output kept in the sets root (mode 700), records in ~/gov-os-runs/D4B/<point>/<name>/. Counts only.
#   so_measure.sh <point> <name> r80|r60 '<GOV_RX json>' <cache folder>
# r80: memory-retrieval, all (the 79 and h24); r60: memory-verdict, hidden (the spent 59 and m60). GOV_RX_RERANK_DIR,
# GOV_RX_RERANK_MODEL, GOV_RX_COMBINE, GOV_RX_BATCH, GOV_RX_REQUEST_CHARS and GOV_RX_GPU_LIMIT_MIB pass through.
set -uo pipefail
POINT=$1 NAME=$2 SET=$3 VARIANT=$4 CACHE=$5
R=/home/usain/Dynamic-Agentic-Engineering-OS
H=$R/.gov-runtime/scratch/orchestrator/drafts/score-once
CLONE=${CLONE:-$HOME/gov-os-runs/D4B/g1/repo}
case "$SET" in
  r80) MSET=memory-retrieval PART=all ;;
  r60) MSET=memory-verdict PART=hidden ;;
  *) echo "so_measure: the set is r80 or r60"; exit 2 ;;
esac
OUT=$HOME/gov-os-runs/D4B/$POINT; D=$OUT/$NAME/$SET; TMP=/tmp/gov-os-emg-so
mkdir -p "$OUT" "$D" "$TMP" "$CACHE"
exec > >(tee -a "$OUT/measure.log") 2>&1
echo "== $(date '+%F %T') $POINT $NAME $SET on $(git -C "$CLONE" rev-parse --short=12 HEAD); cache $CACHE"
waited=0  # a bounded wait (L-0075): at most 600 s, then this run fails and the window stops and restores
while u=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | head -1); [ "${u:-0}" -ge 15000 ]; do
  [ $waited -ge 600 ] && { echo "MEASURE FAILED ($NAME $SET): the GPU stayed at $u MiB for 600 s"; exit 1; }
  echo "GPU at $u MiB: waiting"; sleep 15; waited=$((waited + 15)); done
KEEP=$HOME/gov-os-eval/runs/$POINT/$NAME-$SET; rm -rf "$KEEP"; mkdir -p "$KEEP"; chmod 700 "$HOME/gov-os-eval/runs"; : > "$KEEP/.n"
W=$TMP/gov-$NAME-$SET
cat > "$W" <<EOF
#!/usr/bin/env bash
case "\$1" in --version) PYTHONPATH="$CLONE/src" exec python3 $H/rx.py "\$@" ;; esac
s=\$(date +%s%N)
if [ "\$1" = retrieve ]; then n=\$(flock "$KEEP/.n.lock" sh -c 'n=\$(cat "\$0/.n" 2>/dev/null || echo 0); n=\$((n+1)); echo \$n > "\$0/.n"; echo \$n' "$KEEP"); out="$KEEP/\$(printf %05d \$n).json"; else out=/dev/null; fi
GOV_RX='$VARIANT' GOV_RX_CACHE="$CACHE" GOV_RX_LOG="$D/rx.log" GOV_RX_GPULOG="$OUT/gpu.log" GOV_RX_NAME="$NAME" PYTHONPATH="$CLONE/src" python3 $H/rx.py "\$@" 2>> "$D/rx.err" | tee "\$out"
rc=\${PIPESTATUS[0]}
echo \$(( (\$(date +%s%N) - s) / 1000000 )) >> "$D/ms"
exit \$rc
EOF
chmod +x "$W"; : > "$D/ms"; : > "$D/rx.log"
t0=$(date +%s)
env -u GOV_TICKET GOV_ROLE=orchestrator TMPDIR=$TMP PYTHONPATH="$CLONE/src" bash "$R/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh" \
  python3 -m gov.retrieval.measure "$MSET" --root "$CLONE" --sets-root "$HOME/gov-os-eval" --part "$PART" \
  --out "$D" --gov "$W" > "$D/measure.txt" 2> "$D/measure.err"; rc=$?
[ $rc -eq 0 ] || echo "MEASURE FAILED ($NAME $SET, rc $rc)"
med=$(sort -n "$D/ms" | awk '{a[NR]=$1} END {if (NR) print a[int((NR+1)/2)]; else print "-"}')
sum_of() { awk -F'\t' -v k="$1" '$1 == k {n += $2} END {print n + 0}' "$D/rx.log"; }
echo "$NAME $SET: $(( $(date +%s) - t0 )) s; median search $med ms; unscored $(grep -c '^UNSCORED' "$D/rx.log"); texts cut at the request bound $(sum_of TRUNC); texts cut by the model $(sum_of MODELCUT); combined passes $(grep -c '^combine' "$D/rx.log")"
exit $rc
