#!/usr/bin/env bash
# Lead: real-model gov skilleval on the named W2-101 skills (default all three), one after another; each envelope
# saved; with CAPTURE=1 the pass-through claude wrapper is first on PATH so each reply lands in capture/replies.jsonl.
#   skilleval2.sh <tag> [skill...]   -> log/skilleval-<tag>.{pid,codes,exit}
cd /home/usain/gov-os-worktrees/W2-101 || exit 2
OUT=/home/usain/gov-os-worktrees/W2-101/.gov-runtime/scratch/lead/log
TAG=$1; shift
SKILLS=("$@"); [ ${#SKILLS[@]} -gt 0 ] || SKILLS=(frontend ui-ux devops)
echo $$ > "$OUT/skilleval-$TAG.pid"
if [ "${CAPTURE:-0}" = 1 ]; then PATH=/home/usain/gov-os-worktrees/W2-101/.gov-runtime/scratch/lead/capture/bin:$PATH; fi
worst=0
for s in "${SKILLS[@]}"; do
  PYTHONPATH=/home/usain/gov-os-worktrees/W2-101/src python3 -m gov.cli.main skilleval \
    template/governance/kernel/skills/$s --json > "$OUT/skilleval-$TAG-$s.json" 2> "$OUT/skilleval-$TAG-$s.err"
  rc=$?
  echo "$s exit $rc" >> "$OUT/skilleval-$TAG.codes"
  [ $rc -gt $worst ] && worst=$rc
done
echo "$worst" > "$OUT/skilleval-$TAG.exit"
