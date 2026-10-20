#!/usr/bin/env bash
# Run each named acceptance suite in its own pytest process, to its end (never -x), on this worktree's src (DEC-732).
# Usage: run_suites.sh <batch-name> <suite> [<suite> ...]
# Writes log/suites/<batch>/<suite>.txt per suite, log/suites/<batch>/summary.txt, and log/suites/<batch>.exit at the end.
W=/home/usain/gov-os-worktrees/W2-59
L=/home/usain/gov-os-worktrees/W2-59/.gov-runtime/scratch/lead/log/suites
batch="$1"; shift
mkdir -p "$L/$batch"
cd "$W" || exit 99
# Both gates at once: no close in its quiet window AND the 1-minute load below 20 (DEC-780, DEC-847).
until [ ! -e /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/CLOSE-RUNNING ] && awk '{exit !($1 < 20)}' /proc/loadavg; do sleep 60; done
date -Is > "$L/$batch/start.txt"
worst=0
for s in "$@"; do
  t0=$(date +%s)
  # Each suite its own temporary root: pytest keeps only the newest three numbered roots per user, so a parallel
  # pytest elsewhere could remove a running suite's fixtures (W1-25's setup error in run 2).
  bt="/tmp/claude-1000/-home-usain-gov-os-worktrees-W2-59/5116ebd4-4968-4639-ba28-0c5da4fd82d4/scratchpad/bt/$batch-$s"
  PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-59/src \
    python3 -m pytest "tests/acceptance/$s" -q -p no:cacheprovider -rs -rf --basetemp "$bt" > "$L/$batch/$s.txt" 2>&1
  rc=$?
  t1=$(date +%s)
  echo "$s rc=$rc secs=$((t1-t0)) :: $(tail -1 "$L/$batch/$s.txt")" >> "$L/$batch/summary.txt"
  [ "$rc" -gt "$worst" ] && worst=$rc
done
date -Is > "$L/$batch/end.txt"
echo "$worst" > "$L/$batch.exit"
