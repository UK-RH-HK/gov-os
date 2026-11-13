L=/home/usain/gov-os-worktrees/W2-146/.gov-runtime/scratch/lead/log/accept
mkdir -p "$L" /tmp/gov-os-lead-W2-146-accept
rm -f "$L/accept.exit"
cd /home/usain/gov-os-worktrees/W2-146 || exit 2
env TMPDIR=/tmp/gov-os-lead-W2-146-accept PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-146/src \
  bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh \
  gov accept W2-146 --root /home/usain/gov-os-worktrees/W2-146 > "$L/accept.out" 2> "$L/accept.err"
rc=$?
echo "$rc" > "$L/accept.exit.tmp" && mv "$L/accept.exit.tmp" "$L/accept.exit"
