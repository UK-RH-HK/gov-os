#!/usr/bin/env bash
# assemble the narrow check's brief: head + the run-5 interface + JUDGEMENT.md word for word + tail; fill the head and accept line
cd /home/usain/gov-os-worktrees/W2-88/.gov-runtime/scratch/lead/briefs || exit 2
HEAD_FULL=$(git -C /home/usain/gov-os-worktrees/W2-88 rev-parse HEAD)
{
  cat nc-1.head.md
  cat run5-interface.md
  echo
  echo "## The rules you judge by (governance/project/briefs/JUDGEMENT.md, word for word)"
  echo
  cat /home/usain/Dynamic-Agentic-Engineering-OS/governance/project/briefs/JUDGEMENT.md
  cat nc-1.tail.md
} > nc-1.md
sed -i "s/HEAD_SHA/$HEAD_FULL/g; s/ACCEPT_LINE/outcome pass, every KPI line pass, 214 passed, 0 failed, 0 skipped (log\/accept-5.txt)/" nc-1.md
rm nc-1.head.md nc-1.tail.md
echo "nc-1: $(wc -c < nc-1.md) bytes; slots: $(grep -cE '\{[A-Z_]+\}|HEAD_SHA|ACCEPT_LINE' nc-1.md); head $HEAD_FULL"
ls ../log | grep -E '^nc-1\.' || echo "log name unused"
