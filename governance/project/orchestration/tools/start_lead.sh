#!/usr/bin/env bash
# start_lead.sh <name> <brief file>: one ticket lead as its own headless session, independent of the CTO's session, so
# a CTO handover (a fresh CTO each morning, DEC-1212 (1)) never stops it. Sonnet at effort medium, the rubric's lead line (DEC-1236 (2))
# (DEC-1212 (3)); the no-prompt mode (EMERGENCY-2 2.3). Its return is log/leads/<name>.json (the CLI's JSON result);
# when it ends, one wake message goes to the CTO's inbox (gov msg, the run-time tool's RT-2), naming the file.
#   bash governance/project/orchestration/tools/start_lead.sh gov-queue-2 /path/to/brief.md
set -euo pipefail
[ $# -eq 2 ] || { echo "usage: start_lead.sh <name> <brief file>" >&2; exit 2; }
name=$1; brief=$(readlink -f "$2")
[[ "$name" =~ ^[a-z0-9][a-z0-9-]*$ ]] || { echo "the lead's name is lower-case letters, digits and '-'" >&2; exit 2; }
[ -s "$brief" ] || { echo "no brief at $brief" >&2; exit 2; }
REPO=/home/usain/Dynamic-Agentic-Engineering-OS
L=$REPO/.gov-runtime/scratch/orchestrator/log/leads
mkdir -p "$L"
[ ! -e "$L/$name.json" ] || { echo "a lead named $name already ran ($L/$name.json): pick another name" >&2; exit 2; }
cd "$REPO"
setsid nohup bash -c '
  env -u CLAUDECODE GOV_ROLE=orchestrator GOV_MSG_ADDRESS="lead:$1" CLAUDE_CODE_SUBAGENT_MODEL=claude-sonnet-5-5 CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS=0 \
    "$HOME/.local/bin/claude" -p --model claude-sonnet-5-5 --effort medium --permission-mode bypassPermissions \
    --output-format json < "$2" > "$3/$1.json" 2> "$3/$1.err"
  echo $? > "$3/$1.exit"
  env PYTHONPATH="$4/src" python3 -m gov.cli.main msg send --from "lead:$1" --id "lead-$1-end" cto wake \
    "lead $1 ended (exit $(cat "$3/$1.exit")): its return is $3/$1.json" || true
' start_lead "$name" "$brief" "$L" "$REPO" > /dev/null 2>&1 < /dev/null &
echo "started lead $name (pid $!): its return will be $L/$name.json"
