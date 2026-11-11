#!/usr/bin/env bash
# The dispatcher's launcher (DEC-1008 item 5): the owner's launch form (DEC-715), copied verbatim from
# tools/launch_when_gate_opens.sh without its wait on gate_check (admission is the dispatcher's, by peaks); the disk
# gate (DEC-898) is kept. Usage: launch_now.sh <W2 id> <ticket id> <brief file name> <log file name>
W2=$1; ID=$2; BRIEF=$3; LOGF=$4
ORCH=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator
echo "$(date '+%F %T') admitted by the dispatcher; launching $W2" >&2
bash "$ORCH/tools/disk_gate.sh" || exit 2
cd "/home/usain/gov-os-worktrees/$W2" || exit 2
# W2-153 S2 (DEC-1050): the lead gets its role template as the appended system prompt; no lead starts without it.
TEMPLATE="/home/usain/gov-os-worktrees/$W2/.claude/templates/role-lead.md"
if [ ! -f "$TEMPLATE" ]; then
  echo "$(date '+%F %T') LAUNCH_NO_TEMPLATE: the role template $TEMPLATE is missing; $W2 is not launched" >&2
  exit 2
fi
exec /home/usain/.local/bin/claude -p --model claude-opus-5-5 --effort high --output-format json --permission-mode acceptEdits \
  --allowedTools "Bash" "Read" "Edit" "Write" "Grep" "Glob" \
  --settings "{\"env\":{\"GOV_ROLE\":\"orchestrator\",\"GOV_TICKET\":\"$ID\",\"CLAUDE_CODE_SUBAGENT_MODEL\":\"claude-opus-5-5\"}}" \
  --append-system-prompt-file "$TEMPLATE" \
  < "$ORCH/briefs/$BRIEF" > "$ORCH/log/$LOGF"
