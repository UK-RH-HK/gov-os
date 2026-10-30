#!/bin/bash
# The sha256 of each store file in the clone (DEC-941 KPI 7's fingerprint, second form). Argument: the label.
set -u
cd /home/usain/gov-os-runs/W2-61/repo || exit 90
find .gov-runtime -type f -printf '%s %p\n' | sort -k2 > /home/usain/gov-os-worktrees/W2-61/.gov-runtime/scratch/lead/runs/stores-"$1".sizes
find .gov-runtime -type f -print0 | sort -z | xargs -0 sha256sum > /home/usain/gov-os-worktrees/W2-61/.gov-runtime/scratch/lead/runs/stores-"$1".sha256
date -u +%FT%TZ >> /home/usain/gov-os-worktrees/W2-61/.gov-runtime/scratch/lead/runs/stores-"$1".sizes
