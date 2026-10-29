#!/usr/bin/env bash
# The nightly's logs under a budget (owner, DEC-934 item 2), run by nightly_cron.sh before each night:
#   - cron logs (log/nightly/cron/<date>.log): the newest 30, and at most 20 MB together;
#   - run folders (log/nightly/<stamp>/): the newest 30, and at most 200 MB together;
#   - JUnit folders (/tmp/gov-os-nightly-junit/<stamp>/): the newest 3 (the estimate reads history.jsonl, not them).
# The oldest go first. history.jsonl, digest.txt and status.txt are one line a night and are kept.
ORCH=${NIGHTLY_ORCH:-/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator}
JUNIT_ROOT=${NIGHTLY_JUNIT_ROOT:-/tmp/gov-os-nightly-junit}

keep() {  # $1 = folder, $2 = glob, $3 = newest to keep, $4 = budget in KiB (0 = none)
  local dir=$1 glob=$2 count=$3 budget=$4
  [ -d "$dir" ] || return 0
  # newest first; everything past the count goes
  ls -1dt "$dir"/$glob 2>/dev/null | tail -n +$((count + 1)) | while read -r old; do
    echo "rotate: removed $old (past the newest $count)"; rm -rf "$old"
  done
  [ "$budget" -gt 0 ] || return 0
  while :; do
    total=$(du -sk "$dir"/$glob 2>/dev/null | awk '{s += $1} END {print s + 0}')
    [ "$total" -le "$budget" ] && break
    oldest=$(ls -1dtr "$dir"/$glob 2>/dev/null | head -1)
    [ -n "$oldest" ] || break
    echo "rotate: removed $oldest (over the budget, $total KiB of $budget)"; rm -rf "$oldest"
  done
}

keep "$ORCH/log/nightly/cron" "*.log" 30 20480
keep "$ORCH/log/nightly" "20[0-9][0-9][0-9][0-9][0-9][0-9]-[0-9][0-9][0-9][0-9]" 30 204800
keep "$JUNIT_ROOT" "20[0-9][0-9][0-9][0-9][0-9][0-9]-[0-9][0-9][0-9][0-9]" 3 0
echo "rotate: done"
