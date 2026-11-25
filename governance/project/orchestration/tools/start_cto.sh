#!/usr/bin/env bash
# start_cto.sh: the morning's FRESH Gov OS CTO (golden workflow rule 10; DEC-1253: the handover method), Opus at high effort
# (the role table, DEC-1225, DEC-1242 R-4), in its own tmux session with Remote Control and bypassPermissions, from the
# outgoing CTO's handover. No old session is resumed. The one start script: the scratch copy calls this file.
# Run by the outgoing CTO after it wrote and recorded the handover, or by the owner in a plain WSL terminal.
set -eu
R=/home/usain/Dynamic-Agentic-Engineering-OS; S=cto-$(date +%m%d-%H%M)
H=$R/docs/emergency-2/CTO-HANDOVER.md
[ -f "$H" ] || { echo "no handover at $H"; exit 1; }
P="You are the Gov OS CTO, starting fresh this morning from the outgoing CTO's handover (no old session is resumed). First read, whole and never cut (long files in consecutive pages with the Read tool, never head, tail or a pipe), in this order: template/governance/kernel/templates/role-cto.md (your operating card), docs/emergency-2/GOLDEN-WORKFLOW.md, docs/emergency-2/EMERGENCY-2.md with its section 13, docs/emergency-2/CTO-HANDOVER.md and every decision it names by id in docs/DECISION_REGISTER.md, then from docs/emergency-2/integration/INTEGRATION-PLAN.md the current and the next phase the handover names (the rest on demand), docs/emergency-2/integration/FINDINGS.md and the latest decisions page with its answer sheet. Then take over exactly as the card's 'Take over' section says (the checkpoint's hash, HEAD, the live gov, tmux, the tracked watcher with no heartbeat, everything the handover lists as running, your inbox, your session id and your tmux name $S written to .gov-runtime/scratch/orchestrator/log/cto-session.txt and cto-tmux.txt), send the owner one takeover message (the progress block, what you checked and its result, your first action), and only then carry on from the handover's NEXT ACTIONS."
tmux new-session -d -s "$S" -c "$R" "env -u CLAUDECODE GOV_ROLE=orchestrator $HOME/.local/bin/claude --remote-control 'Gov OS CTO' --model claude-opus-5-5 --effort high --permission-mode bypassPermissions \"$P\""
echo "started $S (tmux attach -t =$S)"
