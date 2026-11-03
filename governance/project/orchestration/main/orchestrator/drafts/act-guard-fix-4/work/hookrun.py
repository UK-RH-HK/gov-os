"""Run a hook as Claude Code does: hookrun.py <hook.py> <role> <cwd> <command...> (Bash), prints the decision."""
import json
import os
import subprocess
import sys

PY = open(os.path.expanduser("~/.local/bin/gov")).readline()[2:].strip()
MAIN = "/home/usain/Dynamic-Agentic-Engineering-OS"


def run(hook, role, tool, tin, cwd=MAIN, root=None, agent=None, tmpdir=None, ticket="DAEO-sdxk"):
    event = {"tool_name": tool, "tool_input": tin, "cwd": cwd, "session_id": "guard-fix-4", "agent_type": agent}
    env = dict(os.environ, GOV_ROLE=role, GOV_TICKET=ticket, CLAUDE_PROJECT_DIR=root or cwd)
    env.pop("TMPDIR", None)
    env.pop("PYTHONPATH", None)
    if tmpdir:
        env["TMPDIR"] = tmpdir
    p = subprocess.run([PY, "-E", hook], input=json.dumps(event), capture_output=True, text=True, env=env, timeout=90)
    if p.returncode == 2:
        return "deny", "exit 2: " + p.stderr[-300:]
    if p.stdout.strip():
        h = json.loads(p.stdout)["hookSpecificOutput"]
        return h["permissionDecision"], h["permissionDecisionReason"]
    return "allow", ""


if __name__ == "__main__":
    hook, role, cwd = sys.argv[1:4]
    print(run(hook, role, "Bash", {"command": " ".join(sys.argv[4:])}, cwd=cwd))
