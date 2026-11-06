#!/usr/bin/env bash
# L6 (D4B-SCORE-ONCE v7): the B0 control and the work_tier cell, both replayed from E1's extended cache (no GPU), then
# the control against g-B0 (score138 --same) and the cell against g-B0 (McNemar). Counts only.
S=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/score-once
D=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/d4b
C=$HOME/gov-os-runs/D4B/score-once-extend/caches/d80; R=$HOME/gov-os-runs/D4B/score-once-replay
B='"sem_uncut":true,"sem_k":60,"lex_k":60,"depth":40,"perfile":2,"dedup":true,"rq":"question","lift_norm":0.0766'
W='["docs/close/**","docs/checkpoints/**","governance/project/orchestration/closes/**","governance/project/orchestration/reviews/**","governance/project/orchestration/sessions/**","governance/project/orchestration/nightly/**","governance/project/orchestration/main/orchestrator/CHECKPOINT.md","governance/project/orchestration/main/orchestrator/PR-*.md"]'
REPLAY_ROUTES=$C REPLAY_Q06=$C bash "$S/replay.sh" l6-b0 "{${B}}" '{"kind":"alone","m":"q06"}' > "$R/l6-b0.out" 2>&1 &
REPLAY_ROUTES=$C REPLAY_Q06=$C bash "$S/replay.sh" l6 "{${B},\"work_tier\":${W}}" '{"kind":"alone","m":"q06"}' > "$R/l6.out" 2>&1 &
wait
for v in l6-b0 l6; do echo "== $v"; tail -n 2 "$R/$v.out"; done
echo "== the control against g-B0"
python3 "$D/score138.py" --same "$R/l6-b0/r80/measure.txt" "$R/l6-b0/r60/measure.txt" "$R/g-B0/r80/measure.txt" "$R/g-B0/r60/measure.txt"
echo "== L6 against g-B0"
python3 "$S/mcnemar.py" "$R/g-B0/r80/measure.txt" "$R/g-B0/r60/measure.txt" "$R/l6/r80/measure.txt" "$R/l6/r60/measure.txt"
