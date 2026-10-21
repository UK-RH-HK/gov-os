#!/usr/bin/env bash
# Usage: timed2.sh <label> <uncached|cached>
# DEC-876 condition 4: the whole regression as a close runs it, through the lead's-run command: a parallel run of
# tests/ less the serial-only list's entries (-n auto), then those entries alone and serially; each timed.
# The store is in the lead's scratch (GOV_TESTCACHE_HOME), never in the tree. Waits for no close and load < 20.
cd /home/usain/gov-os-worktrees/W2-48 || exit 2
out=/home/usain/gov-os-worktrees/W2-48/.gov-runtime/scratch/lead/log/timed2
mkdir -p "$out"
label=$1; mode=$2
extra=()
[ "$mode" = uncached ] && extra=(--no-cache)
mapfile -t entries < <(sed -e 's/[[:space:]]#.*$//' -e 's/^#.*$//' -e 's/[[:space:]]*$//' tests/acceptance/serial-only.txt | grep -v '^$')
deselect=()
for e in "${entries[@]}"; do deselect+=(--deselect "$e"); done
for part in parallel serial; do
  until [ ! -e /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/CLOSE-RUNNING ] && awk '{exit !($1 < 20)}' /proc/loadavg; do sleep 60; done
  start=$(date +%s); load0=$(cut -d' ' -f1 /proc/loadavg)
  if [ "$part" = parallel ]; then
    GOV_TESTCACHE_HOME=/home/usain/gov-os-worktrees/W2-48/.gov-runtime/scratch/lead/testcache-store-2 PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-48/src python3 -m gov.testcache run --json "${extra[@]}" --workers auto tests -- "${deselect[@]}" > "$out/$label-$mode-$part.json" 2> "$out/$label-$mode-$part.err"
  else
    GOV_TESTCACHE_HOME=/home/usain/gov-os-worktrees/W2-48/.gov-runtime/scratch/lead/testcache-store-2 PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-48/src python3 -m gov.testcache run --json "${extra[@]}" "${entries[@]}" > "$out/$label-$mode-$part.json" 2> "$out/$label-$mode-$part.err"
  fi
  code=$?
  echo "$label $mode $part exit=$code $(( $(date +%s) - start ))s head=$(git rev-parse --short HEAD) dirty=$(git status --porcelain | wc -l) load_start=$load0 load_end=$(cut -d' ' -f1 /proc/loadavg)" >> "$out/times.txt"
done
echo done > "$out/$label-$mode.exit"
