#!/usr/bin/env bash
# DEC-1071 (3): the measurement set (memory-verdict, 60) measured ONCE, through the harness configuration that brought the halves within 3 points. Counts only.
# no-op equals the product on 24/24 digests) on all 48 questions, run by the CTO only (the hidden half is read only by
# the CTO's measures). Records go to ~/gov-os-runs/D4B/<point>/<name>/, never to the research branch (DEC-1067 (b)).
#   measure_rx.sh <point> <runs> <name> '<GOV_RX json>' [<name> '<json>' ...]
set -uo pipefail
POINT=$1; RUNS=$2; shift 2
R=/home/usain/Dynamic-Agentic-Engineering-OS
H=/home/usain/gov-os-worktrees/research-retrieval/docs/research/EXP-003/retrieval-survey/night/harness
CLONE=${CLONE:-$HOME/gov-os-runs/D4B/g1/repo}
OUT=$HOME/gov-os-runs/D4B/$POINT
TMP=/tmp/gov-os-emg-m3
mkdir -p "$OUT" "$TMP"
exec > >(tee -a "$OUT/measure.log") 2>&1
echo "== $(date '+%F %T') $POINT on $(git -C "$CLONE" rev-parse --short=12 HEAD)"
while [ $# -ge 2 ]; do
  NAME=$1 VARIANT=$2; shift 2
  for k in $(seq 1 "$RUNS"); do
    while u=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | head -1); [ "${u:-0}" -ge 15000 ]; do
      echo "GPU at $u MiB: waiting"; touch /tmp/gov-os-research-wait.flag; sleep 15; done
    CACHE=$TMP/cache-$NAME-$k; rm -rf "$CACHE"; D=$OUT/$NAME/run$k; mkdir -p "$D"
    # DEC-1068 (4): every search's ranked output kept, in call order, in the sets root (mode 700); no question text
    KEEP=$HOME/gov-os-eval/runs/$POINT/$NAME-run$k; mkdir -p "$KEEP"; chmod 700 "$HOME/gov-os-eval/runs"; : > "$KEEP/.n"
    cat > "$TMP/gov-$NAME" <<EOF
#!/usr/bin/env bash
case "\$1" in --version) PYTHONPATH="$CLONE/src" exec python3 $H/rx.py "\$@" ;; esac
s=\$(date +%s%N)
if [ "\$1" = retrieve ]; then n=\$(flock "$KEEP/.n.lock" sh -c 'n=\$(cat "\$0/.n" 2>/dev/null || echo 0); n=\$((n+1)); echo \$n > "\$0/.n"; echo \$n' "$KEEP"); out="$KEEP/\$(printf %05d \$n).json"; else out=/dev/null; fi
GOV_RX='$VARIANT' GOV_RX_CACHE="$CACHE" GOV_RX_LOG="$D/rx.log" GOV_RX_GPULOG="$OUT/gpu.log" GOV_RX_NAME="$NAME" PYTHONPATH="$CLONE/src" python3 $H/rx.py "\$@" | tee "\$out"
rc=\${PIPESTATUS[0]}
echo \$(( (\$(date +%s%N) - s) / 1000000 )) >> "$D/ms"
exit \$rc
EOF
    chmod +x "$TMP/gov-$NAME"; : > "$D/ms"
    t0=$(date +%s)
    env -u GOV_TICKET GOV_ROLE=orchestrator TMPDIR=$TMP PYTHONPATH="$CLONE/src" bash "$R/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh" \
      python3 -m gov.retrieval.measure memory-verdict --root "$CLONE" --sets-root "$HOME/gov-os-eval" --part hidden \
      --out "$D" --gov "$TMP/gov-$NAME" > "$D/measure.txt" 2> "$D/measure.err" || echo "MEASURE FAILED ($NAME run$k)"
    med=$(sort -n "$D/ms" | awk '{a[NR]=$1} END {if (NR) print a[int((NR+1)/2)]; else print "-"}')
    echo "$NAME run$k: $(( $(date +%s) - t0 )) s; median search $med ms; unscored $(grep -c '^UNSCORED' "$D/rx.log" 2>/dev/null)"
    rm -rf "$CACHE"
  done
done
echo "== $(date '+%F %T') done"
