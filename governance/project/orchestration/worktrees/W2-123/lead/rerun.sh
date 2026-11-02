#!/bin/bash
# rerun.sh <tree> <out folder> <ids file>: run each failing test id alone (one test is not heavy), with the tree's src.
tree=$1; out=$2; ids=$3
mkdir -p "$out"
cd "$tree" || exit 2
n=0
while IFS= read -r id; do
  [ -z "$id" ] && continue
  n=$((n + 1))
  PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH="$tree/src" TMPDIR=/tmp/gov-os-lead-W2-123 \
    timeout 900 python3 -m pytest "$id" -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rfE --tb=line \
    > "$out/rerun-$n.log" 2>&1
  echo "$n exit $? | $(tail -1 "$out/rerun-$n.log") | $id"
done < "$ids"
