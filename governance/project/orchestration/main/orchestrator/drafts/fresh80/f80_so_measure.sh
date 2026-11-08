#!/usr/bin/env bash
# The fresh 80, data only (DEC-1097 (1)(c), E4 on the 80): drafts/score-once/so_measure.sh for the set memory-verdict-2,
# part hidden. Changed from so_measure.sh, and only this: the set is fixed (no r80/r60); the sets root is the first
# argument, and every record and kept output goes under <root>/runs/fresh-80/data/e4/<point>/<name>/ (kept/ inside),
# derived here; a folder that exists is refused (never rm -rf, never reused); GOV_STORE and GOV_TICKET are unset for the
# measure (reviewer 1 S6); the summary line names the set "v80". rx.py, the cache and the pass-through switches are as
# in so_measure.sh. Counts only on standard output (the measure's own lines go to files).
#   f80_so_measure.sh <sets root> <point> <name> '<GOV_RX json>' <cache folder>
set -uo pipefail
SETS_ROOT=$1 POINT=$2 NAME=$3 VARIANT=$4 CACHE=$5
R=/home/usain/Dynamic-Agentic-Engineering-OS
H=$R/.gov-runtime/scratch/orchestrator/drafts/score-once
CLONE=${CLONE:-$HOME/gov-os-runs/D4B/w4-e0/repo}
ROOT=$(realpath -e "$SETS_ROOT" 2>/dev/null) || { echo "f80_so_measure: the sets root does not exist"; exit 2; }
OUT=$ROOT/runs/fresh-80/data/e4/$POINT; D=$OUT/$NAME; TMP=/tmp/gov-os-emg-f80so
[ -e "$D" ] && { echo "f80_so_measure: $POINT $NAME exists: refused (a new folder per run)"; exit 2; }
mkdir -p "$OUT" "$D" "$TMP" "$CACHE" 2>/dev/null
exec >> "$OUT/measure.log" 2>&1  # the log stays in the run folder; the caller prints counts from it
echo "== $(date '+%F %T') $POINT $NAME v80 on $(git -C "$CLONE" rev-parse --short=12 HEAD)"
waited=0  # a bounded wait (L-0075): at most 600 s, then this run fails and the window stops and restores
while u=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | head -1); [ "${u:-0}" -ge 15000 ]; do
  [ $waited -ge 600 ] && { echo "MEASURE FAILED ($NAME v80): the GPU stayed at $u MiB for 600 s"; exit 1; }
  echo "GPU at $u MiB: waiting"; sleep 15; waited=$((waited + 15)); done
KEEP=$D/kept; mkdir -p "$KEEP"; chmod 700 "$ROOT/runs"; : > "$KEEP/.n"
W=$TMP/gov-$POINT-$NAME
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
chmod 700 "$W"; : > "$D/ms"; : > "$D/rx.log"
t0=$(date +%s)
env -u GOV_TICKET -u GOV_STORE GOV_ROLE=orchestrator TMPDIR=$TMP PYTHONPATH="$CLONE/src" bash "$R/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh" \
  python3 -m gov.retrieval.measure memory-verdict-2 --root "$CLONE" --sets-root "$ROOT" --part hidden \
  --out "$D" --gov "$W" > "$D/measure.txt" 2> "$D/measure.err"; rc=$?
[ $rc -eq 0 ] || echo "MEASURE FAILED ($NAME v80, rc $rc)"
med=$(sort -n "$D/ms" | awk '{a[NR]=$1} END {if (NR) print a[int((NR+1)/2)]; else print "-"}')
sum_of() { awk -F'\t' -v k="$1" '$1 == k {n += $2} END {print n + 0}' "$D/rx.log"; }
echo "$NAME v80: $(( $(date +%s) - t0 )) s; median search $med ms; unscored $(grep -c '^UNSCORED' "$D/rx.log"); texts cut at the request bound $(sum_of TRUNC); texts cut by the model $(sum_of MODELCUT); combined passes $(grep -c '^combine' "$D/rx.log"); texts scored live (GOV_RX_LIVE_MISSING) $(sum_of LIVEMISS); texts read from the replay's own cache $(sum_of OWNCACHE)"
exit $rc
