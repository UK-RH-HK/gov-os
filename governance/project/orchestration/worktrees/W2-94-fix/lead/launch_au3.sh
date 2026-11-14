#!/usr/bin/env bash
set -u
L=/home/usain/gov-os-worktrees/W2-94-fix/.gov-runtime/scratch/lead
B=$L/briefs
HEAD=$(git -C /home/usain/gov-os-worktrees/W2-94-fix rev-parse HEAD)
[ "$HEAD" = 900035fdd51c1e469038feb48510483cd095a1e0 ] || { echo "head moved: $HEAD"; exit 1; }
S="s/@HEAD@/$HEAD/g; s/@ENSESSION@/95f607d7-91f2-4012-b906-bac113e476b0/g; s/@ENCOMMIT@/900035fdd51c1e469038feb48510483cd095a1e0/g"
{
  sed "$S" $B/au-3.head.md
  cat /home/usain/gov-os-worktrees/W2-94-fix/governance/project/briefs/JUDGEMENT.md
  sed "$S" $B/au-3.tail.md
} > $B/au-3.md
grep -n '@[A-Z]*@\|{[A-Z_]*}' $B/au-3.md && { echo "unfilled"; exit 1; }
tail -n 4 $B/au-3.md
wc -l $B/au-3.md
cd /home/usain/gov-os-worktrees/W2-94-fix && LAUNCH_TREE=/home/usain/gov-os-worktrees/W2-94-fix LAUNCH_TICKET=DAEO-g87r bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/launch_worker.sh --model claude-opus-5-5 --class C3 independent-auditor high $B/au-3.md
echo "au-3 rc=$?"
