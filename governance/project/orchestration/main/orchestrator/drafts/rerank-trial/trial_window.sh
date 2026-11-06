#!/usr/bin/env bash
# DEC-1076 (3), (4): the reranker trial's quiet window under ACT-RERANK-TRIAL-1 (T0 to T6), on the adopted structure.
# T0 the conditions and the hold; T1 the live service stopped by its own pid, the embedders warmed, the base; T2 the
# 0.6B on the trial copy, which must reproduce the live 0.6B's g1 + v456 records on every question, or the window ends;
# T3 mxbai-rerank-large-v2; T4 Qwen3-Reranker-4B in 8-bit (a load failure ends that model only); T6 the live service
# restored under class 3 and checked. Then the side-by-side table. Run it in its own process group (setsid).
set -uo pipefail
R=/home/usain/Dynamic-Agentic-Engineering-OS; O=$R/.gov-runtime/scratch/orchestrator; TD=$O/drafts/rerank-trial
OUT=$HOME/gov-os-runs/D4B/trial-w4; mkdir -p "$OUT"; C=~/.cache/gov-os-trial
exec > >(tee -a "$OUT/window.log") 2>&1
gpu() { nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | head -1; }
LIVE_LOG=~/.cache/gov-os/rerank.log
restore() {
  echo "-- T6 $(date '+%F %T'): the live service restored (class 3's start line, unchanged)"
  ( cd /home/usain/gov-os-worktrees/W2-00-store && GOV_RERANK_IDLE_S=43200 ~/.local/bin/gov retrieve "what decides a close" --json > /dev/null 2>&1 )
  tail -1 "$LIVE_LOG"
  by=$(cd /home/usain/gov-os-worktrees/W2-00-store && ~/.local/bin/gov retrieve "what decides a close" --json 2>/dev/null | python3 -c "import json,sys; print((json.load(sys.stdin)['result'].get('rerank') or {}).get('by'))")
  echo "class 3's check: rerank.by = $by; GPU $(gpu) MiB"
  printf '{"at": "%s", "class": 3, "reason": "the reranker trial window ended (DEC-1076)", "check": "rerank.by %s"}\n' "$(date '+%F %T')" "$by" >> $O/log/restarts.jsonl
  [ -e $O/log/act-in-progress.txt ] && mv $O/log/act-in-progress.txt $O/log/act-in-progress.ended-$(date +%H%M)-rerank-trial-w4.txt
}
echo "== $(date '+%F %T') the window (DEC-1076)"
# T0: the conditions (ACT-RERANK-TRIAL-1 4.3)
S=$O/dispatch/status.txt
grep -q "heavy slots held: none" $S && grep -q "^Jobs by phase: none" $S || { echo "STOP: the machine is not quiet"; grep -E "heavy slots held|Jobs by phase" $S; exit 1; }
printf 'ACT-RERANK-TRIAL-1 (DEC-1076): the CTO'"'"'s own hold for the trial window, from %s: the live reranker stopped, a trial service on its own socket\n' "$(date '+%F %T')" > $O/log/act-in-progress.txt
# T1: the live service stopped by the pid its own log names (never a text match)
LP=$(grep -E 'READY' "$LIVE_LOG" | tail -1 | grep -oE 'pid [0-9]+' | awk '{print $2}')
if [ -n "$LP" ] && tr '\0' ' ' < /proc/$LP/cmdline 2>/dev/null | grep -q 'gov/retrieval/rerank_service.py'; then
  echo "T1: the live service, pid $LP (its log's READY line; its command line checked)"
  bash $O/tools/proc.sh stop --grace 30 "$LP" || { echo "STOP: the live service did not stop"; restore; exit 1; }
else echo "T1: no live service running (pid ${LP:-none} not alive)"; fi
curl -s -m 120 http://127.0.0.1:11434/api/embed -d '{"model":"qwen3-embedding:0.6b","input":"warm","keep_alive":-1}' > /dev/null
curl -s -m 120 http://127.0.0.1:11435/api/embed -d '{"model":"qwen3-embedding:0.6b","input":"warm","keep_alive":-1}' > /dev/null
sleep 3; echo "T1 base GPU: $(gpu) MiB"
# T2: the 0.6B on the trial copy, and the faithfulness check
bash $TD/trial_w4.sh t2-qwen06b Qwen/Qwen3-Reranker-0.6B e61197ed45024b0ed8a2d74b80b4d909f1255473 0 ~/.cache/huggingface
P=$HOME/gov-os-runs/D4B
if ! python3 $O/drafts/d4b/score138.py --same $P/g1-rx/v/run1/measure.txt $P/verdict/v/run1/measure.txt \
     $P/trial-w4-t2-qwen06b/r80/run1/measure.txt $P/trial-w4-t2-qwen06b/r60/run1/measure.txt; then
  echo "STOP: T2 does not reproduce the live 0.6B on every question: the trial path is not faithful"; restore; exit 3
fi
echo "T2 faithful: the trial path reproduces the live 0.6B on all 138"
# T3, T4
bash $TD/trial_w4.sh t3-mxbai mixedbread-ai/mxbai-rerank-large-v2 ca7e1ee484c37c0ddd8d178a9a5c33cec575c5e6 0 $C/hf
bash $TD/trial_w4.sh t4-qwen4b-8bit Qwen/Qwen3-Reranker-4B 22e683669bc0f0bd69640a1354a6d0aebcfeede5 1 $C/hf
restore
echo "== side by side (DEC-1076 (4)); the trial logs hold the probe, the speed at once and the GPU per model"
for m in t2-qwen06b t3-mxbai t4-qwen4b-8bit; do
  [ -e $P/trial-w4-$m/r60/run1/measure.txt ] && python3 $O/drafts/d4b/score138.py $m $P/trial-w4-$m/r80/run1/measure.txt $P/trial-w4-$m/r60/run1/measure.txt
  grep -hE "^load:|probe rc|runs' GPU peak|run1: .*median search|at once: median|NOT ELIGIBLE|FAILURE|GPU after the stop" $OUT/$m/trial.log $P/trial-w4-$m/measure.log 2>/dev/null | sed "s/^/  $m  /"
done
echo "== $(date '+%F %T') the window ends"
