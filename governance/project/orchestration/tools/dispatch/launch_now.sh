#!/usr/bin/env bash
# The dispatcher's launcher (DEC-1008 item 5): the owner's launch form (DEC-715), copied verbatim from
# tools/launch_when_gate_opens.sh without its wait on gate_check (admission is the dispatcher's, by peaks); the disk
# gate (DEC-898) is kept. Usage: launch_now.sh <W2 id> <ticket id> <brief file name> <log file name>
# DEC-1133 (3) (ACT-LOAD-BALANCER-A): the resource gate is checked in this command, before the lead starts, and the lead
# is entered in the machine registry (gov resources --register) under its own process id before it starts, so the gate
# and the sample day see every lead the dispatcher starts. Exit 2: the disk gate, the folder or the template; exit 3: the
# resource gate is shut or cannot be read (nothing starts); exit 4: the lead could not be registered (nothing starts).
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
# DEC-1133 (3): the gate, then the registry, then the start. The check's reading goes to this launch's log (stderr).
# A shut gate and a check that cannot run both stop the start (fail closed). The registry entry is for THIS process
# ($$): the exec below keeps the pid and the process's start, so the entry is the lead's own, in place before it runs.
/home/usain/.local/bin/gov resources --check >&2
rc=$?
if [ "$rc" -ne 0 ]; then
  echo "$(date '+%F %T') LAUNCH_GATE_SHUT: gov resources --check ended with exit $rc; $W2 is not launched (DEC-1133 (3))" >&2
  exit 3
fi
if ! /home/usain/.local/bin/gov resources --register "$$" --ticket "$ID" --session-role orchestrator >&2; then
  echo "$(date '+%F %T') LAUNCH_NOT_REGISTERED: gov resources --register $$ failed; $W2 is not launched (DEC-1133 (3))" >&2
  exit 4
fi
echo "$(date '+%F %T') gate open; $ID registered as pid $$; starting $W2" >&2
exec /home/usain/.local/bin/claude -p --model claude-opus-5-5 --effort high --output-format json --permission-mode acceptEdits \
  --allowedTools "Bash" "Read" "Edit" "Write" "Grep" "Glob" \
  --settings "{\"env\":{\"GOV_ROLE\":\"orchestrator\",\"GOV_TICKET\":\"$ID\",\"CLAUDE_CODE_SUBAGENT_MODEL\":\"claude-opus-5-5\"}}" \
  --append-system-prompt-file "$TEMPLATE" \
  < "$ORCH/briefs/$BRIEF" > "$ORCH/log/$LOGF"
