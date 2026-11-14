#!/usr/bin/env bash
# Lead: real-model gov skilleval on the three W2-101 skills, one after another; each envelope saved.
cd /home/usain/gov-os-worktrees/W2-101 || exit 2
OUT=/home/usain/gov-os-worktrees/W2-101/.gov-runtime/scratch/lead/log
for s in frontend ui-ux devops; do
  PYTHONPATH=/home/usain/gov-os-worktrees/W2-101/src python3 -m gov.cli.main skilleval \
    template/governance/kernel/skills/$s --json > "$OUT/skilleval-$s.json" 2> "$OUT/skilleval-$s.err"
  echo "$s exit $?" >> "$OUT/skilleval.codes"
done
echo done >> "$OUT/skilleval.codes"
