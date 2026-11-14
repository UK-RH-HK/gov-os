"""Every case of W2-42a's F1 fixture through the hook before and after, as an engineer: python3 -I fx_probe.py
<hooks-before> <hooks-after> <project> <fixture.json>. Prints id|expect|before|after per case, then the counts; exit 0
when the counts are those the ACT states (12 of the 15 shell spellings allowed before, 14 refused after, the one let
through the unquoted-delimiter case; the 4 data controls the same before and after; nothing refused before allowed after)."""
import json
import os
import subprocess
import sys

before, after, project, fixture = sys.argv[1:5]
PY = open(os.path.expanduser("~/.local/bin/gov")).readline()[2:].strip()
LET_THROUGH = {"bash-eu-o-pipefail-unquoted"}


def decide(hooks, command):
    event = {"tool_name": "Bash", "tool_input": {"command": command}, "cwd": project, "session_id": "agf5"}
    env = dict(os.environ, GOV_ROLE="engineer", GOV_TICKET="DAEO-03ub", CLAUDE_PROJECT_DIR=project)
    env.pop("PYTHONPATH", None)
    p = subprocess.run([PY, "-E", os.path.join(hooks, "pretooluse.py")], input=json.dumps(event), capture_output=True,
                       text=True, env=env, timeout=90)
    if p.returncode == 2:
        return "deny"
    if p.returncode:
        return "error"
    return json.loads(p.stdout)["hookSpecificOutput"]["permissionDecision"] if p.stdout.strip() else "allow"


rows = []
for c in json.load(open(fixture))["cases"]:
    rows.append((c["id"], c["expect"], decide(before, c["command"]), decide(after, c["command"])))
    print("%-34s %-9s before=%-6s after=%s" % rows[-1])
shell = [r for r in rows if r[1] == "write"]
data = [r for r in rows if r[1] == "no-write"]
allowed_before = sum(r[2] == "allow" for r in shell)
denied_after = sum(r[3] == "deny" for r in shell)
still = sorted(r[0] for r in shell if r[3] != "deny")
print(f"shell spellings {len(shell)}: allowed before {allowed_before}, refused after {denied_after}; allowed after: {still}")
print(f"data controls {len(data)}: same before and after {sum(r[2] == r[3] for r in data)}, allowed {sum(r[3] == 'allow' for r in data)}")
lost = [r[0] for r in rows if r[2] == "deny" and r[3] != "deny"]
good = (len(shell) == 15 and len(data) == 4 and allowed_before == 12 and denied_after == 14 and set(still) == LET_THROUGH
        and all(r[2] == r[3] == "allow" for r in data) and not lost)
print("fixture: " + ("as stated" if good else "NOT as stated"))
sys.exit(0 if good else 1)
