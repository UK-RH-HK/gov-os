#!/bin/bash
# Run under the verify lock: start the run only if it can still end before 02:00 UTC and no close or nightly runs
# (DEC-939 item 6, DEC-933); otherwise exit 76 so the caller waits and tries again. Arguments: the run's seconds,
# then the run's command.
needed="$1"; shift
orch=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator
[ -e "$orch/NIGHTLY-RUNNING" ] && exit 76
[ -e "$orch/CLOSE-RUNNING" ] && exit 76
now=$(date -u +%s)
of_day=$(( now % 86400 ))
if [ "$of_day" -lt 7200 ] && [ $(( of_day + needed )) -gt 7200 ]; then exit 76; fi
if [ "$of_day" -ge 79200 ] && [ $(( of_day + needed )) -gt 93600 ]; then exit 76; fi
exec "$@"
