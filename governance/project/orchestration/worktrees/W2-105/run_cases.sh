#!/usr/bin/env bash
# r4: tests/acceptance/W2-105 alone, once, through heavy_slot.sh; usage: run_cases.sh <name> <target> [extra env assignments...]
set -u
T=/home/usain/gov-os-worktrees/W2-105
L=$T/.gov-runtime/scratch/lead/log
name=$1; target=$2; shift 2
mkdir -p "$L" "$T/.gov-runtime/scratch/empty-home" /tmp/gov-os-lead-W2-105
echo $$ > "$L/$name.pid"
rm -f "$L/$name.exit"
cd "$T" || exit 2
env "$@" TMPDIR=/tmp/gov-os-lead-W2-105 PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH \
  HOME=$T/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=$T/src \
  bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh \
  python3 -m pytest "$target" -q -p no:cacheprovider -o tmp_path_retention_policy=failed \
  -m "not local_only" -k "not real and not green_here and not time_limit" -rs \
  --junitxml="$L/$name.xml" > "$L/$name.log" 2>&1
echo $? > "$L/$name.exit"
