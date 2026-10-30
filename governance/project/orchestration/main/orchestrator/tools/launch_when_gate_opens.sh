#!/usr/bin/env bash
# Launches a ticket lead in the owner's launch form (DEC-715) once the resource gate is open (DEC-942: measured on
# WSL as it is, tools/gate_check.py, checked each minute; then the disk gate, DEC-898).
# Usage: launch_when_gate_opens.sh <W2 id> <ticket id> <brief file name> <log file name>
W2=$1; ID=$2; BRIEF=$3; LOGF=$4
ORCH=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator
until line=$(python3 "$ORCH/tools/gate_check.py"); do
  echo "$(date '+%F %T') $line" >&2
  sleep 60
done
echo "$(date '+%F %T') gate $line; launching $W2" >&2
bash "$ORCH/tools/disk_gate.sh" || exit 2
cd "/home/usain/gov-os-worktrees/$W2" || exit 2
exec /home/usain/.local/bin/claude -p --model claude-opus-5-5 --effort high --output-format json --permission-mode acceptEdits \
  --allowedTools "Bash" "Read" "Edit" "Write" "Grep" "Glob" \
  --settings "{\"env\":{\"GOV_ROLE\":\"orchestrator\",\"GOV_TICKET\":\"$ID\",\"CLAUDE_CODE_SUBAGENT_MODEL\":\"claude-opus-5-5\"}}" \
  < "$ORCH/briefs/$BRIEF" > "$ORCH/log/$LOGF"
