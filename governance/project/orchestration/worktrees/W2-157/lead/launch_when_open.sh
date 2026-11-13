#!/usr/bin/env bash
# Launch one worker as soon as the resource gate is open; a gate refusal at launch is a wait, retried (memory rule).
# usage: launch_when_open.sh <model> <projection> <role> <effort> <brief>
cd /home/usain/gov-os-worktrees/W2-157 || exit 2
for attempt in $(seq 1 40); do
  until gov resources --check >/dev/null 2>&1; do sleep 10; done
  out=$(bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/launch_worker.sh --model "$1" --class C2 --projection-usd "$2" "$3" "$4" "$5" 2>&1)
  echo "$out" | tail -3
  exitf=$(echo "$out" | sed -n 's/.*wait_for.sh \(.*\.exit\).*/\1/p' | tail -1)
  [ -n "$exitf" ] || { echo "no exit file named"; exit 1; }
  sleep 25
  if [ -f "$exitf" ] && grep -q 'LAUNCH_REFUSED: the resource gate is shut' "${exitf%.exit}.json" 2>/dev/null; then
    echo "attempt $attempt: gate refused at launch; waiting"
    continue
  fi
  echo "launched: $exitf"
  exit 0
done
echo "gave up after 40 gate refusals"
exit 1
