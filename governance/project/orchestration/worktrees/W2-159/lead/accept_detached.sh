#!/usr/bin/env bash
# gov accept W2-159 through heavy_slot, detached; writes <name>.json, <name>.err, then <name>.exit last.
name=$1
L=/home/usain/gov-os-worktrees/W2-159/.gov-runtime/scratch/lead/log
mkdir -p /tmp/w2-159-lead
cd /home/usain/gov-os-worktrees/W2-159 || exit 2
env TMPDIR=/tmp/w2-159-lead PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-159/src \
  bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh \
  gov accept W2-159 --root /home/usain/gov-os-worktrees/W2-159 > "$L/$name.json" 2> "$L/$name.err"
echo $? > "$L/$name.exit.tmp" && mv "$L/$name.exit.tmp" "$L/$name.exit"
