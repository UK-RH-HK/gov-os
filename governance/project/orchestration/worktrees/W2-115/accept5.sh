#!/usr/bin/env bash
# run 4: gov accept W2-115 at this head, through the heavy-job slot (outside the sandbox, DEC-1052)
export PYTHONUSERBASE=/home/usain/.local
export TMPDIR=/tmp/gov-os-lead-W2-115-accept5
mkdir -p "$TMPDIR"
cd /home/usain/gov-os-worktrees/W2-115 || exit 2
L=/home/usain/gov-os-worktrees/W2-115/.gov-runtime/scratch/lead/log
PYTHONPATH=/home/usain/gov-os-worktrees/W2-115/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh \
  python3 -m gov.cli.main accept W2-115 --root /home/usain/gov-os-worktrees/W2-115 > "$L/accept-7.txt" 2>&1
echo $? > "$L/accept-7.exit"
