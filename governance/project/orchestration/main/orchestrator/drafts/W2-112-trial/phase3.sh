#!/usr/bin/env bash
# W2-112 trial phase 3: two plain Claude sessions and one sandboxed `gov launch` worker, each running three searches,
# with scripted 10-at-once batches through the gate while they run (at most 6 batches, so they overlap the sessions).
D=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/W2-112-trial
GATE=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh
STORE=/home/usain/gov-os-worktrees/W2-00-store
export TMPDIR=/tmp/gov-os-w2-112-trial
cd "$STORE" || exit 1
SET='{"env":{"GOV_ROLE":"research","GOV_TICKET":"DAEO-clon"}}'
echo "s1 start $(date -u +%T.%N)" >> "$D/phase3.times"
~/.local/bin/claude -p --model claude-haiku-5-5 --max-turns 8 --output-format json --permission-mode acceptEdits \
  --allowedTools "Bash" --settings "$SET" < "$D/prompt-s1.txt" > "$D/s1.json" 2> "$D/s1.err" &
P1=$!
echo "s2 start $(date -u +%T.%N)" >> "$D/phase3.times"
~/.local/bin/claude -p --model claude-haiku-5-5 --max-turns 8 --output-format json --permission-mode acceptEdits \
  --allowedTools "Bash" --settings "$SET" < "$D/prompt-s2.txt" > "$D/s2.json" 2> "$D/s2.err" &
P2=$!
echo "s3 start $(date -u +%T.%N)" >> "$D/phase3.times"
~/.local/bin/gov launch research DAEO-clon -- -p --model claude-haiku-5-5 --max-turns 8 --output-format json \
  --permission-mode acceptEdits --allowedTools "Bash" < "$D/prompt-s3.txt" > "$D/s3.json" 2>&1 &
P3=$!
sleep 8
for k in 1 2 3 4 5 6; do
  alive=0
  for p in $P1 $P2 $P3; do kill -0 "$p" 2>/dev/null && alive=1; done
  [ "$alive" = 1 ] || break
  echo "batch agents10-$k start $(date -u +%T.%N)" >> "$D/phase3.times"
  bash "$GATE" bash "$D/batch.sh" "agents10-$k" 10 "$D/searches.jsonl"
  sleep 2
done
wait $P1; echo "s1 rc $? $(date -u +%T.%N)" >> "$D/phase3.times"
wait $P2; echo "s2 rc $? $(date -u +%T.%N)" >> "$D/phase3.times"
wait $P3; echo "s3 rc $? $(date -u +%T.%N)" >> "$D/phase3.times"
echo "phase3 done $(date -u +%T.%N)" >> "$D/phase3.times"
