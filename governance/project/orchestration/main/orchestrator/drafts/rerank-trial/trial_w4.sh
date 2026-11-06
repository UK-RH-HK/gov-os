#!/usr/bin/env bash
# DEC-1076 (3), (4): one model of the reranker trial on the adopted structure (the g1 clone, e884675b: m6 + the stated
# links; the harness's v456), the live service already stopped (trial_window.sh). The load (timed to READY), the
# probe's peak at the padded bound, the 80 (memory-retrieval, all) and the 60 (memory-verdict, hidden) through the
# harness's trial switch, one run each, every search's ranked output kept; 10 and 20 at once (the probe, and the
# harness's own searches); the stop by the service's own pid; the GPU back to the base. Counts only.
#   trial_w4.sh <name> <model> <revision> <8bit 0|1> <HF_HOME>
set -uo pipefail
NAME=$1 MODEL=$2 REV=$3 BIT=$4 HFH=$5
R=/home/usain/Dynamic-Agentic-Engineering-OS; O=$R/.gov-runtime/scratch/orchestrator
V=~/.local/share/gov-os/reranker-trial-venv; TR=~/.local/share/gov-os/rerank-trial
H=/home/usain/gov-os-worktrees/research-retrieval/docs/research/EXP-003/retrieval-survey/night/harness
CLONE=$HOME/gov-os-runs/D4B/g1/repo; OUT=$HOME/gov-os-runs/D4B/trial-w4/$NAME; mkdir -p "$OUT"
V456=${VARIANT:-'{"sem_uncut":true,"sem_k":60,"lex_k":60,"depth":40,"perfile":2,"dedup":true}'}
exec > >(tee -a "$OUT/trial.log") 2>&1
gpu() { nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | head -1; }
echo "== $(date '+%F %T') $NAME: $MODEL@$REV 8bit=$BIT, on $(git -C "$CLONE" rev-parse --short=12 HEAD) with v456"
BASE=$(gpu); echo "base GPU: $BASE MiB"
# the load (the ACT's start_trial), timed
n=$(cat "$TR/run/rerank.log" 2>/dev/null | wc -l); t0=$(date +%s.%N)
( exec 9>"$TR/run/rerank.lock"; flock -n 9 || { echo "STOP: a trial service holds the lock"; exit 1; }
  HF_HOME="$HFH" HF_HUB_OFFLINE=1 GOV_RERANK_IDLE_S=3600 GOV_RERANK_TRIAL_8BIT="$BIT" GOV_RERANK_TRIAL_RELEASE=1 \
    setsid -f "$V/bin/python" -I "$TR/svc/rerank_service.py" "$MODEL" "$REV" "$TR/run/rerank.sock" 9 \
    >> "$TR/run/service.log" 2>&1 < /dev/null ) || exit 1
for i in $(seq 1 300); do tail -n +$((n+1)) "$TR/run/rerank.log" 2>/dev/null | grep -q -E 'READY|REFUSED|END' && break; sleep 1; done
LOAD=$(echo "$(date +%s.%N) - $t0" | bc); STATE=$(tail -n +$((n+1)) "$TR/run/rerank.log" | grep -E 'READY|REFUSED|END' | head -1)
echo "load: ${LOAD} s; $STATE; GPU after the load: $(gpu) MiB (base $BASE)"
SVC=$(printf '%s\n' "$STATE" | grep -oE 'pid [0-9]+' | awk '{print $2}')
case "$STATE" in *READY*cuda*) ;; *) echo "FAILURE: the model did not load on the GPU"; tail -5 "$TR/run/service.log"; exit 2;; esac
# the backstop on this script's group and the service's own group (it was started with setsid): never a text match
SG=$(bash $O/tools/proc.sh pgid "$SVC"); MG=$(ps -o pgid= -p $$ | tr -d ' ')
setsid bash $O/tools/gpu_backstop.sh "$MG" "$SG" < /dev/null > /dev/null 2>&1 & BS=$!
echo "service pid $SVC (group $SG); this script's group $MG; backstop pid $BS"
echo "-- the probe's peak at the padded bound (the five worst shapes, one at a time)"
"$V/bin/python" -I "$TR/svc/rerank_trial_probe.py" "$TR/run/rerank.sock" peak --limit 14255; PEAKRC=$?
echo "probe rc $PEAKRC; GPU now $(gpu) MiB"
[ "$PEAKRC" = 0 ] || echo "NOT ELIGIBLE: a shape reached the budget"
nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -lms 1000 > "$OUT/gpu-during-runs.txt" & SAMP=$!
export GOV_RX_RERANK_DIR="$TR/run" GOV_RX_RERANK_MODEL="$MODEL@$REV" GOV_RX_GPU_LIMIT_MIB=14255 CLONE="$CLONE"
echo "-- the 80 (memory-retrieval, all), v456, through the trial switch"
bash "$O/drafts/d4b/measure_rx.sh" "trial-w4-$NAME" 1 r80 "$V456"
echo "-- the 60 (memory-verdict, hidden), v456, through the trial switch"
bash "$O/drafts/d4b/measure_verdict.sh" "trial-w4-$NAME" 1 r60 "$V456"
kill $SAMP 2>/dev/null; echo "runs' GPU peak: $(sort -n "$OUT/gpu-during-runs.txt" | tail -1) MiB"
P=$HOME/gov-os-runs/D4B/trial-w4-$NAME
python3 "$O/drafts/d4b/score138.py" "$NAME" "$P/r80/run1/measure.txt" "$P/r60/run1/measure.txt"
echo "-- 10 and 20 at once: the probe's load"
for N in 10 20; do "$V/bin/python" -I "$TR/svc/rerank_trial_probe.py" "$TR/run/rerank.sock" load $N --limit 14255; done
echo "-- 10 and 20 at once: the harness's own searches (the first N visible questions, each its own fresh cache)"
mapfile -t QS < <(python3 -c "
import yaml,glob
for f in sorted(glob.glob('$CLONE/fixtures/evaluation/memory-retrieval/visible/*.yaml'))[:20]:
    print(yaml.safe_load(open(f))['question'].replace('\n',' '))")
for N in 10 20; do
  D=$OUT/at-once-$N; mkdir -p "$D"; rm -rf /tmp/gov-os-emg-trial-c; mkdir -p /tmp/gov-os-emg-trial-c
  PIDS=()
  for i in $(seq 0 $((N-1))); do
    ( s=$(date +%s.%N)
      GOV_RX="$V456" GOV_RX_CACHE=/tmp/gov-os-emg-trial-c/$i GOV_RX_LOG="$D/rx-$i.log" PYTHONPATH="$CLONE/src" \
        bash -c 'cd "$1" && shift && exec timeout 300 python3 "$@"' _ "$CLONE" "$H/rx.py" retrieve --batch-size 10 --bundle-budget 6000 "${QS[$i]}" --json > "$D/$i.json" 2> "$D/$i.err"
      echo "$? $(echo "$(date +%s.%N) - $s" | bc)" > "$D/$i.t" ) &
    PIDS+=($!)
  done
  bash $O/tools/proc.sh wait --max 600 "${PIDS[@]}" > /dev/null   # by pid only: never a bare `wait` on the log's tee
  python3 - "$D" "$N" <<'EOF'
import json,sys
d,n=sys.argv[1],int(sys.argv[2]); ts=[];bad=0;unranked=0
for i in range(n):
    try: rc,t=open(f"{d}/{i}.t").read().split()
    except Exception: bad+=1; continue
    ts.append(float(t))
    if rc!='0': bad+=1; continue
    try:
        r=json.load(open(f"{d}/{i}.json")).get('result') or {}
        rr=r.get('rerank') or {}
        if rr.get('by')!='service': unranked+=1
    except Exception: bad+=1
ts.sort(); print(f"{n} at once: median {ts[len(ts)//2]:.2f} s, slowest {ts[-1]:.2f} s, failed or timed out {bad}, unranked {unranked}")
EOF
done
echo "-- the stop, by the service's own pid (SIGTERM, 30 s, SIGKILL; DEC-1068 (f), L-0075)"
bash $O/tools/proc.sh stop --grace 30 "$SVC"; sleep 3
bash $O/tools/proc.sh stop --grace 5 "$BS" > /dev/null 2>&1
echo "GPU after the stop: $(gpu) MiB (base $BASE)"
echo "== $(date '+%F %T') $NAME done"
