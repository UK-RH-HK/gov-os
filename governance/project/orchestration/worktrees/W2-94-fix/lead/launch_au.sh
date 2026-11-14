#!/usr/bin/env bash
set -u
L=/home/usain/gov-os-worktrees/W2-94-fix/.gov-runtime/scratch/lead
B=$L/briefs
HEAD=$(git -C /home/usain/gov-os-worktrees/W2-94-fix rev-parse HEAD)
{
  sed "s/@HEAD@/$HEAD/g" $B/au-1.head.md
  cat /home/usain/gov-os-worktrees/W2-94-fix/governance/project/briefs/JUDGEMENT.md
  echo
  echo "## The fix flow's interface, as the lead gave it to the test designer and the engineer"
  sed -n '2,$p' $B/interface.md
  sed "s/@HEAD@/$HEAD/g" $B/au-1.tail.md
  echo '```'
  cat /home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-g87r.md
  echo '```'
} > $B/au-1.md
grep -n '@HEAD@\|{[A-Z_]*}' $B/au-1.md && { echo "unfilled"; exit 1; }
wc -l $B/au-1.md
cd /home/usain/gov-os-worktrees/W2-94-fix && LAUNCH_TREE=/home/usain/gov-os-worktrees/W2-94-fix LAUNCH_TICKET=DAEO-g87r bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/launch_worker.sh --model claude-opus-5-5 --class C2 independent-auditor high $B/au-1.md
