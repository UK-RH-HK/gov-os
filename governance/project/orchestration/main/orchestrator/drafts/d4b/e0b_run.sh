#!/usr/bin/env bash
# E0b (E0-DECLARATION §E0b; E0B-READINESS.md §3; review .gov-runtime/scratch/orchestrator/reviews/e0b-harness.md READY):
# the 138 through the score-once harness at window 4's commit on E0's clone, run A (no lift_norm, the new texts scored
# on the live 0.6B, the one light GPU job) and run B (L3's lift_norm 0.0766, strict, no GPU), then A against E0
# question for question. The review's ride-along fixes: a script, not a pasted block (F6), with its own process group
# and the backstop; the review pin checked first; GOV_RX_GPU_LIMIT_MIB always set (F4); CLONE not left exported after
# (F3); B's copy made fresh (F7). Counts only.
set -uo pipefail
S=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/score-once
O=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator; D=$O/drafts/d4b
K=$HOME/gov-os-runs/D4B/score-once/caches; X=$HOME/gov-os-runs/D4B/score-once-extend/caches
P=$HOME/gov-os-runs/D4B/e0b; E=$P/caches; W=$HOME/gov-os-runs/D4B/w4-e0/out; mkdir -p "$E"
exec > >(tee -a "$P/e0b.log") 2>&1
( cd "$S" && sha256sum -c E0B-REVIEWED.sha256 ) || { echo "STOP: the reviewed harness files changed since the review"; exit 1; }
G=$(ps -o pgid= -p $$ | tr -d ' '); setsid bash $O/tools/gpu_backstop.sh "$G" < /dev/null > /dev/null 2>&1 & BS=$!
echo "== $(date '+%F %T') E0b; backstop $BS on group $G"
[ -d "$E/seed" ] || python3 $S/seed_scores.py "$E/seed" $K/q06 $K/q06f $X/b0 $X/d80 $X/split $X/termmap $X/split-termmap
M=Qwen/Qwen3-Reranker-0.6B@e61197ed45024b0ed8a2d74b80b4d909f1255473
export CLONE=$HOME/gov-os-runs/D4B/w4-e0/repo GOV_RX_POOL_OFF=1 GOV_RX_GPU_LIMIT_MIB=14255
export GOV_RX_COMBINE="{\"models\":{\"q06\":\"$M\"},\"caches\":{\"q06\":\"$E/seed\"},\"rule\":{\"kind\":\"alone\",\"m\":\"q06\"}}"
V='{"sem_uncut":true,"sem_k":60,"lex_k":60,"depth":40,"perfile":2,"dedup":true,"rq":"question"}'
VL3='{"sem_uncut":true,"sem_k":60,"lex_k":60,"depth":40,"perfile":2,"dedup":true,"rq":"question","lift_norm":0.0766}'
echo "== run A (no lift_norm; live-missing on)"
GOV_RX_LIVE_MISSING=1 bash $S/so_measure.sh e0b a r80 "$V" "$E/a" || { echo "STOP: run A r80"; exit 1; }
GOV_RX_LIVE_MISSING=1 bash $S/so_measure.sh e0b a r60 "$V" "$E/a" || { echo "STOP: run A r60"; exit 1; }
echo "== run B (lift_norm 0.0766; strict)"
rm -rf "$E/b"; cp -a "$E/a" "$E/b"
bash $S/so_measure.sh e0b b r80 "$VL3" "$E/b" || { echo "STOP: run B r80"; exit 1; }
bash $S/so_measure.sh e0b b r60 "$VL3" "$E/b" || { echo "STOP: run B r60"; exit 1; }
unset CLONE GOV_RX_POOL_OFF GOV_RX_COMBINE GOV_RX_GPU_LIMIT_MIB
echo "== figures"
python3 -I $D/e0_figures.py "E0b A (harness, no lift)" $P/a/r80/measure.txt $P/a/r60/measure.txt
python3 -I $D/e0_figures.py "E0b B (harness, lift_norm)" $P/b/r80/measure.txt $P/b/r60/measure.txt
python3 -I $D/score138.py --same $W/r80/measure.txt $W/r60/measure.txt $P/a/r80/measure.txt $P/a/r60/measure.txt
bash $O/tools/proc.sh stop --grace 5 "$BS" > /dev/null 2>&1
echo "== $(date '+%F %T') E0b done"
