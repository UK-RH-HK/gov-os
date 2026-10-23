#!/usr/bin/env bash
# The temp folder's size every 3 minutes until the verification ends (its peak goes in the return).
L=/home/usain/gov-os-worktrees/W2-07/.gov-runtime/scratch/lead/log
until [ -e "$L/v2.done" ] || [ -e "$L/v2-serial.exit" ]; do
  echo "$(date -Is) $(du -s --inodes /tmp/gov-os-lead-W2-07 2>/dev/null | cut -f1) $(du -sb /tmp/gov-os-lead-W2-07 2>/dev/null | cut -f1)" >> "$L/v2-scratch-watch.txt"
  sleep 180
done
echo "$(date -Is) $(du -s --inodes /tmp/gov-os-lead-W2-07 2>/dev/null | cut -f1) $(du -sb /tmp/gov-os-lead-W2-07 2>/dev/null | cut -f1)" >> "$L/v2-scratch-watch.txt"
