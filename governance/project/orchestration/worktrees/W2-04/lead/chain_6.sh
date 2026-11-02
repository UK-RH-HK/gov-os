#!/usr/bin/env bash
# W2-04 resume 5 (DEC-1025): disk gate, the store's rebuild in a heavy-job slot (this tree's code), then the scoped run.
set -u
cd /home/usain/gov-os-worktrees/W2-04 || exit 2
bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/disk_gate.sh \
  > /home/usain/gov-os-worktrees/W2-04/.gov-runtime/scratch/lead/log/disk-6.txt 2>&1
echo $? > /home/usain/gov-os-worktrees/W2-04/.gov-runtime/scratch/lead/log/disk-6.rc
date -u +%FT%TZ > /home/usain/gov-os-worktrees/W2-04/.gov-runtime/scratch/lead/log/rebuild-9.start
PYTHONPATH=/home/usain/gov-os-worktrees/W2-04/src TMPDIR=/tmp/gov-os-lead-W2-04 \
  bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/rebuild_slot.sh \
  /home/usain/gov-os-worktrees/W2-04 > /home/usain/gov-os-worktrees/W2-04/.gov-runtime/scratch/lead/log/rebuild-9.txt 2>&1
echo $? > /home/usain/gov-os-worktrees/W2-04/.gov-runtime/scratch/lead/log/rebuild-9.rc
date -u +%FT%TZ > /home/usain/gov-os-worktrees/W2-04/.gov-runtime/scratch/lead/log/rebuild-9.end
if [ "$(cat /home/usain/gov-os-worktrees/W2-04/.gov-runtime/scratch/lead/log/rebuild-9.rc)" != "0" ]; then exit 3; fi
bash /home/usain/gov-os-worktrees/W2-04/.gov-runtime/scratch/lead/run_scoped_5.sh
