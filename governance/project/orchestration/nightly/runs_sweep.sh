#!/usr/bin/env bash
# Removes old run clones (owner, DEC-941 item 5; annex C slip E4): the nightly's and the ACT clone runs' clones under
# ~/gov-os-runs/W2-00/, which the guard (rightly) refuses the orchestrator's sessions. The owner's crontab runs it,
# outside the guard, once a day:
#   15 6 * * * bash /home/usain/Dynamic-Agentic-Engineering-OS/governance/project/orchestration/nightly/runs_sweep.sh
# It removes ONLY a folder that:
#   - sits directly in ~/gov-os-runs/W2-00/nightly/ (named YYYYMMDD-HHMM) or ~/gov-os-runs/W2-00/act-runs/
#     (named <name>-YYYYMMDD-HHMM);
#   - is older than 24 hours (its newest file);
#   - no process holds open (lsof);
#   - and, for a nightly clone, belongs to a night whose verdict was not red, or is older than 7 days (a red night's
#     clone is kept a week for the diagnosis, DEC-934).
# Every removal and every kept folder is logged to log/nightly/cron/runs-sweep-<date>.log. Nothing else is touched.
RUNS=${SWEEP_RUNS:-/home/usain/gov-os-runs/W2-00}
ORCH=${SWEEP_ORCH:-/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator}
LOGDIR=$ORCH/log/nightly/cron
mkdir -p "$LOGDIR"
LOG=$LOGDIR/runs-sweep-$(date +%F).log
now=$(date +%s)
note() { echo "$(date '+%F %T') $1" >> "$LOG"; }
newest() { find "$1" -printf '%T@\n' 2>/dev/null | sort -n | tail -1 | cut -d. -f1; }
sweep() {  # $1 folder, $2 glob of names, $3 kind
  local base=$1 glob=$2 kind=$3 d name age stamp verdict
  [ -d "$base" ] || return 0
  for d in "$base"/$glob; do
    [ -d "$d" ] || continue
    name=${d##*/}
    age=$(( now - $(newest "$d") ))
    if [ "$age" -lt 86400 ]; then note "kept $kind $name: under 24 h"; continue; fi
    if lsof +D "$d" > /dev/null 2>&1; then note "kept $kind $name: held open"; continue; fi
    if [ "$kind" = nightly ]; then
      verdict=$(grep -h '^verdict:' "$ORCH/log/nightly/$name/run.txt" 2>/dev/null | tail -1)
      case "$verdict" in
        "verdict: red"*) if [ "$age" -lt 604800 ]; then note "kept nightly $name: a red night, kept 7 days"; continue; fi ;;
      esac
    fi
    rm -rf -- "$d" && note "removed $kind $name ($(( age / 3600 )) h old)"
  done
}
sweep "$RUNS/nightly" "20[0-9][0-9][0-9][0-9][0-9][0-9]-[0-9][0-9][0-9][0-9]" nightly
sweep "$RUNS/act-runs" "*-20[0-9][0-9][0-9][0-9][0-9][0-9]-[0-9][0-9][0-9][0-9]" act
note "done; $(du -sh "$RUNS" 2>/dev/null | cut -f1) left under $RUNS"
exit 0
