#!/usr/bin/env bash
# DEC-1084's cells (D4B-SCORE-ONCE v6): each variant replayed from its own extended cache, checked against its window
# run (score138 --same), then McNemar against B0 (g-B0). Counts only.
S=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/score-once
D=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/d4b
X=$HOME/gov-os-runs/D4B/score-once-extend; R=$HOME/gov-os-runs/D4B/score-once-replay
B='"sem_uncut":true,"sem_k":60,"lex_k":60,"perfile":2,"dedup":true,"rq":"question","lift_norm":0.0766'
declare -A VAR=(
  [d80]="{${B},\"depth\":80}"
  [split]="{${B},\"depth\":40,\"split\":true}"
  [termmap]="{${B},\"depth\":40,\"termmap\":true}"
  [split-termmap]="{${B},\"depth\":40,\"split\":true,\"termmap\":true}"
)
for v in d80 split termmap split-termmap; do
  REPLAY_ROUTES=$X/caches/$v REPLAY_Q06=$X/caches/$v bash "$S/replay.sh" "ext-$v" "${VAR[$v]}" '{"kind":"alone","m":"q06"}' \
    > "$R/ext-$v.out" 2>&1 &
done
wait
for v in d80 split termmap split-termmap; do
  echo "== $v"
  tail -1 "$R/ext-$v.out"
  python3 "$D/score138.py" --same "$R/ext-$v/r80/measure.txt" "$R/ext-$v/r60/measure.txt" "$X/$v/r80/measure.txt" "$X/$v/r60/measure.txt"
  python3 "$S/mcnemar.py" "$R/g-B0/r80/measure.txt" "$R/g-B0/r60/measure.txt" "$R/ext-$v/r80/measure.txt" "$R/ext-$v/r60/measure.txt"
done
