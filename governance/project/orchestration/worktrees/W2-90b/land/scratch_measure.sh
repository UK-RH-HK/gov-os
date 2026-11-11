#!/usr/bin/env bash
for d in /home/usain/gov-os-worktrees/W2-90b/.gov-runtime/scratch /tmp/gov-os-lead-W2-90b; do
  du -sh $d 2>/dev/null
  du -s --inodes $d 2>/dev/null
done
git -C /home/usain/gov-os-worktrees/W2-90b status --short
git -C /home/usain/gov-os-worktrees/W2-90b rev-parse --short=12 HEAD
