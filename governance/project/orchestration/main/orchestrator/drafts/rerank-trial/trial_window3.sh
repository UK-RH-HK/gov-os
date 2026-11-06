#!/usr/bin/env bash
# DEC-1077 (b2), (c): the two 80-question runs again (the first attempt read a visible label from W2-32's branch that the
# CTO's script had copied into the sets root; restored). The 4B at 24 candidates on the trial copy (r80 only: its 60, its
# speed and GPU figures stand), then the live service restored, then the reranker off (r80 only). Own process group.
set -uo pipefail
R=/home/usain/Dynamic-Agentic-Engineering-OS; O=$R/.gov-runtime/scratch/orchestrator; D=$O/drafts/d4b; P=$HOME/gov-os-runs/D4B
V=~/.local/share/gov-os/reranker-trial-venv; TR=~/.local/share/gov-os/rerank-trial; C=~/.cache/gov-os-trial
OUT=$P/trial-w4b; exec > >(tee -a "$OUT/window3.log") 2>&1
gpu() { nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | head -1; }
LIVE_LOG=~/.cache/gov-os/rerank.log
restore() {
  ( cd /home/usain/gov-os-worktrees/W2-00-store && GOV_RERANK_IDLE_S=43200 ~/.local/bin/gov retrieve "what decides a close" --json > /dev/null 2>&1 )
  by=$(cd /home/usain/gov-os-worktrees/W2-00-store && ~/.local/bin/gov retrieve "what decides a close" --json 2>/dev/null | python3 -c "import json,sys; print((json.load(sys.stdin)['result'].get('rerank') or {}).get('by'))")
  echo "T6: $(tail -1 $LIVE_LOG); class 3's check: rerank.by = $by; GPU $(gpu) MiB"
  printf '{"at": "%s", "class": 3, "reason": "the third trial window ended (DEC-1077)", "check": "rerank.by %s"}\n' "$(date '+%F %T')" "$by" >> $O/log/restarts.jsonl
  [ -e $O/log/act-in-progress.txt ] && mv $O/log/act-in-progress.txt $O/log/act-in-progress.ended-$(date +%H%M)-rerank-trial-w4c.txt
}
echo "== $(date '+%F %T') the third window (DEC-1077)"
diff -rq $R/fixtures/evaluation/memory-retrieval/visible $HOME/gov-os-eval/fixtures/evaluation/memory-retrieval/visible > /dev/null || { echo "STOP: the sets root's visible half is not integrate's"; exit 1; }
grep -q "heavy slots held: none" $O/dispatch/status.txt && grep -q "^Jobs by phase: none" $O/dispatch/status.txt || { echo "STOP: not quiet"; exit 1; }
printf 'ACT-RERANK-TRIAL-1 (DEC-1077): the CTO'"'"'s own hold for the third trial window, from %s\n' "$(date '+%F %T')" > $O/log/act-in-progress.txt
LP=$(grep READY $LIVE_LOG | tail -1 | grep -oE 'pid [0-9]+' | awk '{print $2}')
if [ -n "$LP" ] && tr '\0' ' ' < /proc/$LP/cmdline 2>/dev/null | grep -q 'gov/retrieval/rerank_service.py'; then bash $O/tools/proc.sh stop --grace 30 "$LP" || { restore; exit 1; }; fi
echo "base GPU: $(gpu) MiB"
n=$(wc -l < $TR/run/rerank.log)
( exec 9>"$TR/run/rerank.lock"; flock -n 9 || exit 1
  HF_HOME=$C/hf HF_HUB_OFFLINE=1 GOV_RERANK_IDLE_S=3600 GOV_RERANK_TRIAL_8BIT=1 GOV_RERANK_TRIAL_RELEASE=1 \
    setsid -f "$V/bin/python" -I "$TR/svc/rerank_service.py" Qwen/Qwen3-Reranker-4B 22e683669bc0f0bd69640a1354a6d0aebcfeede5 "$TR/run/rerank.sock" 9 >> "$TR/run/service.log" 2>&1 < /dev/null ) || { restore; exit 1; }
for i in $(seq 1 300); do tail -n +$((n+1)) $TR/run/rerank.log | grep -qE 'READY|REFUSED|END' && break; sleep 1; done
ST=$(tail -n +$((n+1)) $TR/run/rerank.log | grep -E 'READY|REFUSED|END' | head -1); echo "$ST"
SVC=$(echo "$ST" | grep -oE 'pid [0-9]+' | awk '{print $2}')
case "$ST" in *READY*cuda*) ;; *) echo "FAILURE: the 4B did not load"; restore; exit 2;; esac
setsid bash $O/tools/gpu_backstop.sh "$(ps -o pgid= -p $$ | tr -d ' ')" "$(bash $O/tools/proc.sh pgid $SVC)" < /dev/null > /dev/null 2>&1 & BS=$!
rm -rf $P/trial-w4-t4b-qwen4b-8bit-d24/r80
GOV_RX_RERANK_DIR=$TR/run GOV_RX_RERANK_MODEL="Qwen/Qwen3-Reranker-4B@22e683669bc0f0bd69640a1354a6d0aebcfeede5" GOV_RX_GPU_LIMIT_MIB=14255 CLONE=$P/g1/repo \
  bash $D/measure_rx.sh trial-w4-t4b-qwen4b-8bit-d24 1 r80 '{"sem_uncut":true,"sem_k":60,"lex_k":60,"depth":24,"perfile":2,"dedup":true}'
bash $O/tools/proc.sh stop --grace 30 "$SVC"; bash $O/tools/proc.sh stop --grace 5 "$BS" > /dev/null 2>&1; sleep 3
restore
rm -rf $P/trial-w4b-norerank/r80
CLONE=$P/g1/repo bash $D/measure_rx.sh trial-w4b-norerank 1 r80 '{"sem_uncut":true,"sem_k":60,"lex_k":60,"depth":40,"perfile":2,"dedup":true,"rerank":false}'
echo "== side by side"
for m in t2-qwen06b t4-qwen4b-8bit t4b-qwen4b-8bit-d24; do python3 $D/score138.py $m $P/trial-w4-$m/r80/run1/measure.txt $P/trial-w4-$m/r60/run1/measure.txt; python3 $D/score79.py $P/trial-w4-$m/r80/run1/measure.txt; done
python3 $D/score138.py no-reranker $P/trial-w4b-norerank/r80/run1/measure.txt $P/trial-w4b-norerank/r60/run1/measure.txt; python3 $D/score79.py $P/trial-w4b-norerank/r80/run1/measure.txt
python3 $D/lift_push.py $P/trial-w4-t2-qwen06b/r80/run1/measure.txt $P/trial-w4-t2-qwen06b/r60/run1/measure.txt $P/trial-w4b-norerank/r80/run1/measure.txt $P/trial-w4b-norerank/r60/run1/measure.txt
echo "== $(date '+%F %T') the window ends"
