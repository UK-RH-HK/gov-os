#!/bin/bash
# W2-61's §8 as W2-86 ran it: the control. The base clone's stores by the pinned gov, with embeddings; then the visible half.
L=/home/usain/gov-os-worktrees/W2-91/.gov-runtime/scratch/lead/log
export TMPDIR=/tmp/gov-os-lead-W2-91
cd /home/usain/gov-os-runs/W2-91/base || exit 90
bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/disk_gate.sh > /home/usain/gov-os-worktrees/W2-91/.gov-runtime/scratch/lead/log/base-gate.txt 2>&1 || { echo 91 > /home/usain/gov-os-worktrees/W2-91/.gov-runtime/scratch/lead/log/base-measure.exit; exit 91; }
date -u +%FT%TZ > /home/usain/gov-os-worktrees/W2-91/.gov-runtime/scratch/lead/log/base-rebuild.start
env -u PYTHONPATH -u GOV_TICKET flock /tmp/gov-os-rebuild.lock /home/usain/.local/bin/gov rebuild --json > /home/usain/gov-os-worktrees/W2-91/.gov-runtime/scratch/lead/log/base-rebuild.json 2> /home/usain/gov-os-worktrees/W2-91/.gov-runtime/scratch/lead/log/base-rebuild.err
echo $? > /home/usain/gov-os-worktrees/W2-91/.gov-runtime/scratch/lead/log/base-rebuild.exit
date -u +%FT%TZ > /home/usain/gov-os-worktrees/W2-91/.gov-runtime/scratch/lead/log/base-rebuild.end
sha256sum .gov-runtime/store.db .gov-runtime/codeintel/home/code.db .gov-runtime/codeintel/home/_config.db > /home/usain/gov-os-worktrees/W2-91/.gov-runtime/scratch/lead/log/base-sha.txt 2>&1
date -u +%FT%TZ > /home/usain/gov-os-worktrees/W2-91/.gov-runtime/scratch/lead/log/base-measure.start
env -u GOV_TICKET PYTHONPATH=/home/usain/gov-os-runs/W2-91/base/src python3 -m gov.retrieval.measure memory-retrieval --root /home/usain/gov-os-runs/W2-91/base --sets-root /home/usain/gov-os-runs/W2-91/base --part visible --gov /home/usain/.local/bin/gov --out /home/usain/gov-os-runs/W2-91/records --json > /home/usain/gov-os-worktrees/W2-91/.gov-runtime/scratch/lead/log/base-measure.json 2> /home/usain/gov-os-worktrees/W2-91/.gov-runtime/scratch/lead/log/base-measure.err
echo $? > /home/usain/gov-os-worktrees/W2-91/.gov-runtime/scratch/lead/log/base-measure.exit
date -u +%FT%TZ > /home/usain/gov-os-worktrees/W2-91/.gov-runtime/scratch/lead/log/base-measure.end
