#!/usr/bin/env bash
# start_cto.sh: the morning's fresh Gov OS CTO (DEC-1212 (1)), in tmux `cto-<yyyymmdd>` with Remote Control "Gov OS CTO",
# on Opus (claude-opus-5-5: the app's CTO is one of the two orchestrating roles that run Opus, DEC-1225 (1)) at high
# effort, in the no-prompt mode, the full window (no cap). No session runs Fable (DEC-1225 (3)).
# Run by the outgoing CTO at the handover, after it has written docs/emergency-2/CTO-HANDOVER.md; leads started with
# start_lead.sh keep running (their returns reach the CTO's inbox, ~/.gov-os/inbox/cto, read with `gov msg read cto`).
set -euo pipefail
REPO=/home/usain/Dynamic-Agentic-Engineering-OS
name=cto-$(date +%Y%m%d-%H%M)
model=claude-opus-5-5
tmux has-session -t "$name" 2>/dev/null && { echo "tmux $name already runs" >&2; exit 2; }
[ -s "$REPO/docs/emergency-2/CTO-HANDOVER.md" ] || { echo "no handover at docs/emergency-2/CTO-HANDOVER.md" >&2; exit 2; }
first="You are the Gov OS CTO, starting fresh (a handover; the outgoing CTO retires once you have taken over). Read in full, in this order: docs/emergency-2/EMERGENCY-2.md \
(the strategy in force), then docs/emergency-2/CTO-HANDOVER.md (the outgoing CTO's handover: what is landed, what runs, \
what is next), then the owner's latest decisions it names. Then write your session id to \
.gov-runtime/scratch/orchestrator/log/cto-session.txt, read your inbox with \
'PYTHONPATH=src python3 -m gov.cli.main msg read cto', and carry on from the handover's next steps."
tmux new-session -d -s "$name" -c "$REPO" \
  "env -u GOV_ROLE -u GOV_TICKET GOV_MSG_ADDRESS=cto ~/.local/bin/claude --remote-control 'Gov OS CTO' \
   --model $model --effort high --permission-mode bypassPermissions \"$first\""
echo "started the fresh CTO in tmux $name on $model (Remote Control: Gov OS CTO)"
