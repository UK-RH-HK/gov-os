#!/usr/bin/env bash
# W2-112 trial: N searches at once (q01..qN), each timed by search.py; waits for all.
# usage: batch.sh <phase> <N> <out.jsonl>
HERE=$(cd "$(dirname "$0")" && pwd)
phase=$1 n=$2 out=$3
for i in $(seq 1 "$n"); do
  qid=$(printf 'q%02d' "$i")
  python3 "$HERE/search.py" "$phase" "$qid" "$out" &
done
wait
echo "batch $phase $n done $(date -u +%T)"
