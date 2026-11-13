#!/usr/bin/env bash
# W2-111 run 2 (the lead's, for the test designer): one bounded load window, the CTO's form (bench.sh start_load):
# N unpinned busy loops at nice 0 in their own process group, each ended by `timeout SECONDS` whatever happens.
#   bash load_window.sh <N, at most 56> <SECONDS, at most 360>
# Prints and writes the process group to load_window.pgid; stop early with
#   bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/proc.sh stop --grace 5 -<pgid>
set -u
N=${1:?N}; S=${2:?SECONDS}
[ "$N" -le 56 ] || { echo "N at most 56"; exit 2; }
[ "$S" -le 360 ] || { echo "SECONDS at most 360"; exit 2; }
HERE=$(cd "$(dirname "$0")" && pwd)
setsid bash -c "for i in \$(seq $N); do timeout $S sh -c 'while :; do :; done' & done; wait" </dev/null >/dev/null 2>&1 &
pg=$!
echo "$pg" > "$HERE/load_window.pgid"
echo "load window: $N loops for at most $S s, pgid $pg, started $(date -Is), load $(cat /proc/loadavg)"
