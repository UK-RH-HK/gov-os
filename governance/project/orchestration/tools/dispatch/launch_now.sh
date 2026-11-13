#!/usr/bin/env bash
# The dispatcher's launcher (DEC-1008 item 5): the owner's launch form (DEC-715), copied verbatim from
# tools/launch_when_gate_opens.sh without its wait on gate_check (admission is the dispatcher's, by peaks); the disk
# gate (DEC-898) is kept. Usage: launch_now.sh <W2 id> <ticket id> <brief file name> <log file name>
# DEC-1133 (3) (ACT-LOAD-BALANCER-A): the resource gate is checked in this command, before the lead starts, and the lead
# is entered in the machine registry (gov resources --register) under its own process id before it starts, so the gate
# and the sample day see every lead the dispatcher starts. Exit 2: the disk gate, the folder or the template; exit 3: the
# resource gate is shut or cannot be read (nothing starts); exit 4: the lead could not be registered (nothing starts).
# DEC-1161 (2) (ACT-LEADS-ADD-DIR-1): the lead gets its own tests worktree and the runs root by --add-dir on its own
# line, not from the main checkout's .claude/settings.local.json (whose additionalDirectories the owner's operator
# removes at the handover: W2-60a's launcher refuses a worker launch while it is set, DEC-313). Only this lead line
# carries them; a worker starts through gov launch, which refuses --add-dir, so workers stay walled.
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
# DEC-1161 (2): the CLI drops a --add-dir whose folder is missing, without a word, and a lead makes its tests worktree
# after it starts (git worktree add takes an empty folder), so that folder is made here, empty, when nothing is there.
# The runs root is passed as it is and nothing is made in it here (DEC-751: an own folder is made and marked by gov
# launch alone); what a lead may write there stays the guard's (DEC-728, DEC-743).
TESTS="/home/usain/gov-os-worktrees/$W2-tests"
RUNS="/home/usain/gov-os-runs"
[ -e "$TESTS" ] || mkdir "$TESTS" || echo "$(date '+%F %T') LAUNCH_NO_TESTS_DIR: $TESTS could not be made; $W2 starts without it" >&2
echo "$(date '+%F %T') gate open; $ID registered as pid $$; starting $W2" >&2
exec /home/usain/.local/bin/claude -p --model claude-opus-5-5 --effort high --output-format json --permission-mode acceptEdits \
  --allowedTools "Bash" "Read" "Edit" "Write" "Grep" "Glob" \
  --settings "{\"env\":{\"GOV_ROLE\":\"orchestrator\",\"GOV_TICKET\":\"$ID\",\"CLAUDE_CODE_SUBAGENT_MODEL\":\"claude-opus-5-5\"}}" \
  --add-dir "$TESTS" --add-dir "$RUNS" \
  --append-system-prompt-file "$TEMPLATE" \
  < "$ORCH/briefs/$BRIEF" > "$ORCH/log/$LOGF"
