#!/bin/bash
# usage: evid.sh <tk> <w2>   prints one line of review evidence
cd /home/usain/Dynamic-Agentic-Engineering-OS
tk=$1; w2=$2
lc=$(echo "$w2" | tr 'A-Z' 'a-z')
rev=""
# filename matches
for d in governance/project/orchestration/reviews .gov-runtime/scratch/orchestrator/reviews; do
  for f in $(ls $d 2>/dev/null | grep -i -E "(^|[^0-9a-z])(${lc}|${tk})([^0-9a-z]|$)"); do rev="$rev $d/$f"; done
done
# header matches (first 40 lines)
for f in governance/project/orchestration/reviews/*.md .gov-runtime/scratch/orchestrator/reviews/*.md; do
  [ -f "$f" ] || continue
  if head -40 "$f" | grep -q -E "(^|[^0-9A-Za-z-])(${w2}|${tk})([^0-9a-z]|$)"; then rev="$rev H:$f"; fi
done
probe=""
[ -d docs/probes/$tk ] && probe="probes/$tk"
acc=""
[ -d tests/acceptance/$w2 ] && acc="acc"
tr=$(git log --format=%s -i --grep="TESTS-READY" | grep -c -E "(^|[^0-9A-Za-z-])${w2}([^0-9a-z]|$)")
nc=$(git log --format=%H --all-match --grep="$w2" | wc -l)
tkc=$(git log --format=%H --grep="Task: $tk" | wc -l)
rr=$(git log --format=%s -i --grep="$w2" | grep -i -E "review|round|r[0-9] " | head -3 | cut -c1-90 | tr '\n' '~')
echo "$tk|$w2|rev=[$rev]|probe=$probe|acc=$acc|TR=$tr|commits_w2=$nc|commits_tk=$tkc|rr=$rr"
