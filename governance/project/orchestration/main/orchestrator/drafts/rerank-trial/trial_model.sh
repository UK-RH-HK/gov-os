#!/usr/bin/env bash
# ACT-RERANK-TRIAL-1 section 4.4, one model (T2, T3 or T4), DEC-1069 (12): the trial copy on its own socket, the live
# service already stopped (T1). The load (timed to READY), the probe's peak at the padded bound, the product's own
# configuration on m6's clone through the harness's trial switch, all 80, one run, every search's ranked output kept;
# 10 and 20 at once (the probe, and the harness's own searches); the stop, and the GPU back to the base.
#   trial_model.sh <name> <model> <revision> <8bit 0|1> <HF_HOME>
set -uo pipefail
NAME=$1 MODEL=$2 REV=$3 BIT=$4 HFH=$5
R=/home/usain/Dynamic-Agentic-Engineering-OS; O=$R/.gov-runtime/scratch/orchestrator
T=$O/tools/tree_busy.sh; V=~/.local/share/gov-os/reranker-trial-venv; TR=~/.local/share/gov-os/rerank-trial
H=/home/usain/gov-os-worktrees/research-retrieval/docs/research/EXP-003/retrieval-survey/night/harness
CLONE=$HOME/gov-os-runs/D4B/m6/repo; OUT=$HOME/gov-os-runs/D4B/trial/$NAME; mkdir -p "$OUT"
exec > >(tee -a "$OUT/trial.log") 2>&1
gpu() { nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | head -1; }
echo "== $(date '+%F %T') $NAME: $MODEL@$REV 8bit=$BIT"
bash $T --cmd rerank_service.py 2>/dev/null | grep -q '^BUSY' && { echo "STOP: a rerank_service.py runs (the live one must be stopped: T1)"; exit 1; }
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
case "$STATE" in *READY*cuda*) ;; *) echo "FAILURE: the model did not load on the GPU"; tail -5 "$TR/run/service.log"; exit 2;; esac
echo "-- the probe's peak at the padded bound (the five worst shapes, one at a time)"
"$V/bin/python" -I "$TR/svc/rerank_trial_probe.py" "$TR/run/rerank.sock" peak --limit 14255; PEAKRC=$?
echo "probe rc $PEAKRC; GPU now $(gpu) MiB"
[ "$PEAKRC" = 0 ] || echo "NOT ELIGIBLE: a shape reached the budget"
echo "-- the product's configuration on m6's clone, all 80, through the trial switch"
nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -lms 1000 > "$OUT/gpu-during-run.txt" & SAMP=$!
GOV_RX_RERANK_DIR="$TR/run" GOV_RX_RERANK_MODEL="$MODEL@$REV" GOV_RX_GPU_LIMIT_MIB=14255 CLONE="$CLONE" \
  bash "$O/drafts/d4b/measure_rx.sh" "trial-$NAME" 1 "$NAME" '{}'
kill $SAMP 2>/dev/null; echo "run GPU peak: $(sort -n "$OUT/gpu-during-run.txt" | tail -1) MiB"
echo "-- 10 and 20 at once: the probe's load"
for N in 10 20; do "$V/bin/python" -I "$TR/svc/rerank_trial_probe.py" "$TR/run/rerank.sock" load $N --limit 14255; done
echo "-- 10 and 20 at once: the harness's own searches (the first N visible questions, each its own fresh cache)"
mapfile -t QS < <(python3 -c "
import yaml,glob
for f in sorted(glob.glob('$CLONE/fixtures/evaluation/memory-retrieval/visible/*.yaml'))[:20]:
    print(yaml.safe_load(open(f))['question'].replace('\n',' '))")
for N in 10 20; do
  D=$OUT/at-once-$N; mkdir -p "$D"; rm -rf /tmp/gov-os-emg-trial-c; mkdir -p /tmp/gov-os-emg-trial-c
  for i in $(seq 0 $((N-1))); do
    ( s=$(date +%s.%N)
      GOV_RX='{}' GOV_RX_CACHE=/tmp/gov-os-emg-trial-c/$i GOV_RX_RERANK_DIR="$TR/run" GOV_RX_RERANK_MODEL="$MODEL@$REV" \
        GOV_RX_GPU_LIMIT_MIB=14255 GOV_RX_LOG="$D/rx-$i.log" PYTHONPATH="$CLONE/src" \
        bash -c 'cd "$1" && shift && exec timeout 300 python3 "$@"' _ "$CLONE" "$H/rx.py" retrieve --batch-size 10 --bundle-budget 6000 "${QS[$i]}" --json > "$D/$i.json" 2> "$D/$i.err"
      echo "$? $(echo "$(date +%s.%N) - $s" | bc)" > "$D/$i.t" ) &
  done; wait
  python3 - "$D" "$N" <<'EOF'
import json,sys,glob,os
d,n=sys.argv[1],int(sys.argv[2]); ts=[];bad=0;unranked=0
for i in range(n):
    rc,t=open(f"{d}/{i}.t").read().split(); ts.append(float(t))
    if rc!='0': bad+=1; continue
    try:
        r=json.load(open(f"{d}/{i}.json")).get('result') or {}
        def f(o):
            if isinstance(o,dict):
                if isinstance(o.get('rerank'),dict): return o['rerank']
                for v in o.values():
                    x=f(v)
                    if x: return x
        rr=f(r) or {}
        if rr.get('by')!='service': unranked+=1
    except Exception: bad+=1
ts.sort(); print(f"{n} at once: median {ts[len(ts)//2]:.2f} s, slowest {ts[-1]:.2f} s, failed {bad}, unranked {unranked}")
EOF
done
echo "-- the stop (DEC-1068 (f): SIGTERM, 30 s, SIGKILL), by the trial file's own path"
M="$TR/svc/rerank_service.py"
for P in $(bash $T --cmd "$M" 2>/dev/null | awk '/^BUSY/{print $2}'); do kill -TERM $P; done
for i in $(seq 1 30); do bash $T --cmd "$M" > /dev/null 2>&1 || { echo "stopped ($i s)"; break; }; sleep 1; done
for P in $(bash $T --cmd "$M" 2>/dev/null | awk '/^BUSY/{print $2}'); do echo "SIGKILL $P"; kill -KILL $P; done
sleep 3; echo "GPU after the stop: $(gpu) MiB (base $BASE)"
echo "== $(date '+%F %T') $NAME done"
