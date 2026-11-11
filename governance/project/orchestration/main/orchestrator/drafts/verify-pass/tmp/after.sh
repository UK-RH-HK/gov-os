#!/bin/bash
cd /home/usain/Dynamic-Agentic-Engineering-OS
out=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/verify-pass/tmp/after.txt
: > $out
for f in $(git diff --name-only); do
  id=$(basename $f .md)
  w2=$(grep -m1 '^wbs_id:' $f | awk '{print $2}')
  r=$(gov brief lead $id --run tests 2>&1 | grep -E "^gov brief: [A-Z_]+" | grep -v BRIEF_NOT_READY | sed 's/gov brief: //' | awk '{print $1}' | sort -u | tr '\n' ',')
  echo "$id|$w2|$r" >> $out
done
echo done > $out.done
