#!/usr/bin/env bash
# The grid (D4B-SCORE-ONCE §3, L3): B0 and the 16 cells as replays, three at a time, on v456 + rq question + L3.
#   run_grid.sh            (then grid_report.py)
S=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/score-once
V='{"sem_uncut":true,"sem_k":60,"lex_k":60,"depth":40,"perfile":2,"dedup":true,"rq":"question","lift_norm":0.0766}'
export S V
tr '\t' '\n' < "$S/grid.txt" | xargs -d '\n' -n 2 -P 3 sh -c 'bash "$S/replay.sh" "$0" "$V" "$1" > "$HOME/gov-os-runs/D4B/score-once-replay/$0.out" 2>&1; echo "$0 exit $?"'
