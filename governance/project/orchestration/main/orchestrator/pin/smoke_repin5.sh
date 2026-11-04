#!/usr/bin/env bash
# Re-pin window 3's smoke test after the switch, guard part (smoke_repin2.sh with the HOME named): the exact PreToolUse
# hook line of .claude/settings.json, run as Claude Code runs it, on three calls: a Read (allowed), a Write under
# tests/acceptance/ (refused for the orchestrator), and the same Read with no pinned gov reachable (the hook must
# refuse, exit 2).
#     bash smoke_repin5.sh <the HOME whose .local/bin/gov was switched (the operator's: $HOME)> <scratch dir>
LH=${1:?the HOME of the switched link}
S=${2:?a scratch directory}
R=/home/usain/Dynamic-Agentic-Engineering-OS
mkdir -p "$S"
LINE=$(python3 -c "import json; s = json.load(open('$R/.claude/settings.json')); print(s['hooks']['PreToolUse'][0]['hooks'][0]['command'])")
call() {  # $1 name, $2 tool json
  printf '%s' "$2" | env HOME="$LH" CLAUDE_PROJECT_DIR=$R GOV_ROLE=orchestrator GOV_TICKET=DAEO-sdxk bash -c "$LINE" > "$S/smoke-out.txt" 2> "$S/smoke-err.txt"
  code=$?
  echo "$1: exit $code; $(grep -o '"permissionDecision": *"[a-z]*"' "$S/smoke-out.txt" | head -1) $(head -c 160 "$S/smoke-err.txt" | tr '\n' ' ')"
}
READ='{"session_id":"smoke","hook_event_name":"PreToolUse","cwd":"'$R'","tool_name":"Read","tool_input":{"file_path":"'$R'/README.md"}}'
WRITE='{"session_id":"smoke","hook_event_name":"PreToolUse","cwd":"'$R'","tool_name":"Write","tool_input":{"file_path":"'$R'/tests/acceptance/W2-57/smoke.py","content":"x"}}'
call "1 Read README.md" "$READ"
call "2 Write tests/acceptance" "$WRITE"
# 3: no pinned gov: a HOME without .local/bin/gov and a PATH with no gov
mkdir -p "$S/smoke-nohome"
printf '%s' "$READ" | env -i HOME="$S/smoke-nohome" PATH=/usr/bin:/bin CLAUDE_PROJECT_DIR=$R GOV_ROLE=orchestrator bash -c "$LINE" > /dev/null 2> "$S/smoke-err.txt"
echo "3 no judge reachable: exit $?; $(head -c 160 "$S/smoke-err.txt" | tr '\n' ' ')"
