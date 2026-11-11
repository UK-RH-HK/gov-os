#!/usr/bin/env bash
# DEC-898 scratch measures
for d in /home/usain/gov-os-worktrees/W2-05/.gov-runtime/scratch /tmp/gov-os-lead-W2-05; do
  du -sh "$d" 2>/dev/null
  du -s --inodes "$d" 2>/dev/null
done
