#!/usr/bin/env bash
# DEC-1077 (b2), (c): the second quiet window. T0 the conditions and the hold; T1 the live service stopped by its own
# pid; the 4B in 8-bit reranking 24 candidates (v456 with depth 24) through trial_w4.sh; T6 the live service restored
# (class 3); then the reranker off (v456 with rerank false: the fused order alone) on the 138, and the lift/push counts
# against the 0.6B's records. Run it in its own process group (setsid). Counts only.
set -uo pipefail
R=/home/usain/Dynamic-Agentic-Engineering-OS; O=$R/.gov-runtime/scratch/orchestrator; TD=$O/drafts/rerank-trial; D=$O/drafts/d4b
OUT=$HOME/gov-os-runs/D4B/trial-w4b; mkdir -p "$OUT"; C=~/.cache/gov-os-trial; P=$HOME/gov-os-runs/D4B
exec > >(tee -a "$OUT/window.log") 2>&1
gpu() { nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | head -1; }
LIVE_LOG=~/.cache/gov-os/rerank.log
restore() {
  echo "-- T6 $(date '+%F %T'): the live service restored (class 3's start line, unchanged)"
  ( cd /home/usain/gov-os-worktrees/W2-00-store && GOV_RERANK_IDLE_S=43200 ~/.local/bin/gov retrieve "what decides a close" --json > /dev/null 2>&1 )
  tail -1 "$LIVE_LOG"
  by=$(cd /home/usain/gov-os-worktrees/W2-00-store && ~/.local/bin/gov retrieve "what decides a close" --json 2>/dev/null | python3 -c "import json,sys; print((json.load(sys.stdin)['result'].get('rerank') or {}).get('by'))")
  echo "class 3's check: rerank.by = $by; GPU $(gpu) MiB"
  printf '{"at": "%s", "class": 3, "reason": "the second trial window ended (DEC-1077)", "check": "rerank.by %s"}\n' "$(date '+%F %T')" "$by" >> $O/log/restarts.jsonl
  [ -e $O/log/act-in-progress.txt ] && mv $O/log/act-in-progress.txt $O/log/act-in-progress.ended-$(date +%H%M)-rerank-trial-w4b.txt
}
echo "== $(date '+%F %T') the second window (DEC-1077)"
S=$O/dispatch/status.txt
grep -q "heavy slots held: none" $S && grep -q "^Jobs by phase: none" $S || { echo "STOP: the machine is not quiet"; grep -E "heavy slots held|Jobs by phase" $S; exit 1; }
printf 'ACT-RERANK-TRIAL-1 (DEC-1077): the CTO'"'"'s own hold for the second trial window, from %s\n' "$(date '+%F %T')" > $O/log/act-in-progress.txt
LP=$(grep -E 'READY' "$LIVE_LOG" | tail -1 | grep -oE 'pid [0-9]+' | awk '{print $2}')
if [ -n "$LP" ] && tr '\0' ' ' < /proc/$LP/cmdline 2>/dev/null | grep -q 'gov/retrieval/rerank_service.py'; then
  echo "T1: the live service, pid $LP"; bash $O/tools/proc.sh stop --grace 30 "$LP" || { echo "STOP: the live service did not stop"; restore; exit 1; }
else echo "T1: no live service running (pid ${LP:-none})"; fi
curl -s -m 120 http://127.0.0.1:11434/api/embed -d '{"model":"qwen3-embedding:0.6b","input":"warm","keep_alive":-1}' > /dev/null
curl -s -m 120 http://127.0.0.1:11435/api/embed -d '{"model":"qwen3-embedding:0.6b","input":"warm","keep_alive":-1}' > /dev/null
sleep 3; echo "T1 base GPU: $(gpu) MiB"
VARIANT='{"sem_uncut":true,"sem_k":60,"lex_k":60,"depth":24,"perfile":2,"dedup":true}' \
  bash $TD/trial_w4.sh t4b-qwen4b-8bit-d24 Qwen/Qwen3-Reranker-4B 22e683669bc0f0bd69640a1354a6d0aebcfeede5 1 $C/hf
restore
echo "-- (c) the reranker off: v456 with rerank false, the fused order alone, on the 138 (the g1 clone)"
export CLONE=$P/g1/repo
OFF='{"sem_uncut":true,"sem_k":60,"lex_k":60,"depth":40,"perfile":2,"dedup":true,"rerank":false}'
bash $D/measure_rx.sh trial-w4b-norerank 1 r80 "$OFF"
bash $D/measure_verdict.sh trial-w4b-norerank 1 r60 "$OFF"
python3 $D/score138.py no-reranker $P/trial-w4b-norerank/r80/run1/measure.txt $P/trial-w4b-norerank/r60/run1/measure.txt
python3 $D/score79.py $P/trial-w4b-norerank/r80/run1/measure.txt
python3 $D/lift_push.py $P/trial-w4-t2-qwen06b/r80/run1/measure.txt $P/trial-w4-t2-qwen06b/r60/run1/measure.txt \
  $P/trial-w4b-norerank/r80/run1/measure.txt $P/trial-w4b-norerank/r60/run1/measure.txt
echo "== side by side"
for m in t2-qwen06b t4-qwen4b-8bit; do python3 $D/score138.py $m $P/trial-w4-$m/r80/run1/measure.txt $P/trial-w4-$m/r60/run1/measure.txt; done
python3 $D/score138.py t4b-qwen4b-8bit-d24 $P/trial-w4-t4b-qwen4b-8bit-d24/r80/run1/measure.txt $P/trial-w4-t4b-qwen4b-8bit-d24/r60/run1/measure.txt
grep -hE "^load:|runs' GPU peak|at once: median|^load [0-9]+:" $OUT/../trial-w4/t4b-qwen4b-8bit-d24/trial.log 2>/dev/null | sed 's/^/  t4b  /'
echo "== $(date '+%F %T') the window ends"
