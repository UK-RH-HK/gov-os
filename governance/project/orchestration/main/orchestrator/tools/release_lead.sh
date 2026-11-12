#!/usr/bin/env bash
# Releases one lead line into dispatch/ready.txt only after the pre-release checks pass (DEC-1140 (1)(a): every new brief
# checked before release; memory "Check before a ready line"). Usage:
#   release_lead.sh <W2> <ticket id> <brief.md> <log.json> "<comment>"
# Checks, each refusing with exit 2 and its reason, nothing written:
#   1. the worktree ~/gov-os-worktrees/<W2> exists and holds .claude/templates/role-lead.md (the launcher's template)
#   2. the brief exists under briefs/ and is non-empty (at least 2000 bytes)
#   3. the log name is unused (no log/<log> and no ready line already naming it)
#   4. the brief's model lines agree with RUBRIC-2 for the ticket's class in log/ticket-class.json: a C2, C1 or C0 ticket's
#      brief must not tell its engineer or test designer to run on Opus ("engineer ... Opus" or "every worker on Opus");
#      a ticket with no class in the map is refused (the CTO sets it first)
#   5. the ticket file exists and parses as YAML front matter
# On success: appends "# <UTC HH:MM> <comment>" and the line "<W2> <ticket> <brief> <log>", and prints it.
set -u
ORCH=${ORCH:-/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator}
MAIN=${MAIN:-/home/usain/Dynamic-Agentic-Engineering-OS} TREES=${TREES:-/home/usain/gov-os-worktrees}
[ $# = 5 ] || { sed -n '2,13p' "$0"; exit 2; }
W2=$1 ID=$2 BRIEF=$3 LOG=$4 NOTE=$5
no() { echo "release_lead: REFUSED $W2: $1" >&2; exit 2; }
[ -s "$TREES/$W2/.claude/templates/role-lead.md" ] || no "no .claude/templates/role-lead.md in $TREES/$W2 (merge integrate back first)"
b=$ORCH/briefs/$BRIEF
[ -f "$b" ] || no "no brief $b"
[ "$(wc -c < "$b")" -ge 2000 ] || no "the brief is empty or too short ($(wc -c < "$b") bytes): $b"
[ -e "$ORCH/log/$LOG" ] && no "the log name is used: $ORCH/log/$LOG"
grep -qE "^[^#].* $LOG\$" "$ORCH/dispatch/ready.txt" && no "a ready line already names $LOG"
python3 -I - "$MAIN/.tickets/$ID.md" <<'PY' || no "the ticket $ID does not parse"
import sys
try:
    import yaml
except ImportError:
    sys.exit(0)
yaml.safe_load(open(sys.argv[1]).read().split("---")[1])
PY
cls=$(python3 -I -c 'import json,sys
try: print(json.load(open(sys.argv[1])).get(sys.argv[2],""))
except Exception: print("")' "$ORCH/log/ticket-class.json" "$ID")
case "$cls" in C0|C1|C2|C3) ;; *) no "no class for $ID in log/ticket-class.json (the CTO sets it first)";; esac
if [ "$cls" != C3 ]; then
  if grep -inE "every worker on (claude-)?opus|(engineer|test designer)[^.;]{0,60}\bon opus" "$b" | grep -viE "not on opus|never on opus" | head -n 3 | grep -q .; then
    no "class $cls: the brief tells an engineer or test designer to run on Opus (RUBRIC-2: Sonnet, high); fix the brief"
  fi
fi
{ printf '# %s %s\n' "$(date -u '+%H:%M')" "$NOTE"; echo "$W2 $ID $BRIEF $LOG"; } >> "$ORCH/dispatch/ready.txt"
echo "release_lead: released $W2 $ID $BRIEF $LOG (class $cls)"
