#!/bin/bash
# usage: scan.sh <outfile>   ; appends one line per non-closed ticket, skips ids already in outfile
cd /home/usain/Dynamic-Agentic-Engineering-OS
out=$1
touch "$out"
for f in .tickets/DAEO-*.md; do
  id=$(basename "$f" .md)
  if grep -q "^$id|" "$out"; then continue; fi
  st=$(sed -n '2,12p' "$f" | grep -m1 '^status:' | awk '{print $2}')
  if [ "$st" = "closed" ]; then continue; fi
  w2=$(grep -m1 '^wbs_id:' "$f" | awk '{print $2}')
  r=$(gov brief lead "$id" --run tests 2>&1 | grep -E "^gov brief: [A-Z_]+" | grep -v BRIEF_NOT_READY | sed 's/gov brief: //' | tr '\n' ';')
  nv=$(echo "$r" | grep -o "KPI_NO_VERIFY [SF][0-9]*" | sed 's/KPI_NO_VERIFY //' | tr '\n' ',')
  echo "$id|$w2|$st|$nv|$r" >> "$out"
done
echo DONE >> "$out.done"
