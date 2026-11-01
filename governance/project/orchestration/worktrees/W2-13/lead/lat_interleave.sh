#!/bin/bash
# lat_interleave.sh: fusion.search warm p95 on the lat-tiers, base code and head code alternately, two passes each.
cd /tmp || exit 9
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 TMPDIR=/tmp/gov-os-lead-W2-13
for pass in base-1 head-1 base-2 head-2; do
  case "$pass" in
    base-*) src=/home/usain/gov-os-runs/W2-13/base/src ;;
    head-*) src=/home/usain/gov-os-worktrees/W2-13/src ;;
  esac
  PYTHONPATH=$src python3 /home/usain/gov-os-worktrees/W2-13/.gov-runtime/scratch/lead/lat_time.py "$pass" >> /home/usain/gov-os-worktrees/W2-13/.gov-runtime/scratch/lead/log/lat-interleave.txt 2>> /home/usain/gov-os-worktrees/W2-13/.gov-runtime/scratch/lead/log/lat-interleave.err
done
echo 0 > /home/usain/gov-os-worktrees/W2-13/.gov-runtime/scratch/lead/log/lat-interleave.exit
