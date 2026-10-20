#!/usr/bin/env bash
# Usage: timed.sh <batch-name> <path> [<path> ...]
# One uncached run and one cached re-run of the given test paths through the lead's-run command, on the same head,
# each timed; the store is in the lead's scratch (GOV_TESTCACHE_HOME), never in the tree.
cd /home/usain/gov-os-worktrees/W2-48 || exit 2
out=/home/usain/gov-os-worktrees/W2-48/.gov-runtime/scratch/lead/log/timed
mkdir -p "$out"
batch=$1; shift
for mode in uncached cached; do
  until [ ! -e /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/CLOSE-RUNNING ] && awk '{exit !($1 < 20)}' /proc/loadavg; do sleep 60; done
  extra=""
  [ "$mode" = uncached ] && extra="--no-cache"
  start=$(date +%s)
  GOV_TESTCACHE_HOME=/home/usain/gov-os-worktrees/W2-48/.gov-runtime/scratch/lead/testcache-store PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-48/src python3 -m gov.testcache run --json $extra --workers auto "$@" > "$out/$batch-$mode.json" 2> "$out/$batch-$mode.err"
  code=$?
  echo "$batch $mode exit=$code $(( $(date +%s) - start ))s head=$(git rev-parse --short HEAD) load=$(cut -d' ' -f1 /proc/loadavg)" >> "$out/times.txt"
done
echo done > "$out/$batch.exit"
