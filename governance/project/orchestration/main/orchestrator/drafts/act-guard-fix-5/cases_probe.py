"""Every case of a cases file through the hook as Claude Code runs it, once per hook copy: python3 -B -I cases_probe.py
<cases.json> <project> <hooks dir>... Prints id|expect_after|decision per hook dir, in one line per case:
id|expect|d1|d2|... (the decisions in the order of the hook dirs). Exit 0."""
import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

cases_file, project, *hooks = sys.argv[1:]
PY = open(os.path.expanduser("~/.local/bin/gov")).readline()[2:].strip()


def decide(hdir, c):
    event = {"tool_name": "Bash", "tool_input": {"command": c["command"]}, "cwd": project, "session_id": "agf5"}
    env = dict(os.environ, GOV_ROLE=c.get("role", "engineer"), GOV_TICKET="DAEO-03ub", CLAUDE_PROJECT_DIR=project,
               PYTHONDONTWRITEBYTECODE="1")
    env.pop("PYTHONPATH", None)
    p = subprocess.run([PY, "-E", "-B", os.path.join(hdir, "pretooluse.py")], input=json.dumps(event),
                       capture_output=True, text=True, env=env, timeout=90)
    if p.returncode == 2:
        return "deny"
    if p.returncode:
        return "error"
    return json.loads(p.stdout)["hookSpecificOutput"]["permissionDecision"] if p.stdout.strip() else "allow"


def one(c):
    return "|".join([c["id"], c["expect_after"]] + [decide(h, c) for h in hooks])


with ThreadPoolExecutor(max_workers=6) as pool:
    for line in pool.map(one, json.load(open(cases_file))["cases"]):
        print(line)
