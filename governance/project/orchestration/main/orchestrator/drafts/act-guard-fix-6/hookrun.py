"""ACT-GUARD-FIX-6: run the live hook as Claude Code runs it (the registered line's interpreter, the pin, -E), one call,
and say what it decided and by which rule.

  import hookrun
  hookrun.decide(hooks_dir, project, role, ticket, tool, tool_input, cwd=None, agent_type=None, tmpdir=None)
      -> (decision, rule, reason)    decision: allow | deny | ask | error

The guard's call log is pointed at a fresh temporary folder (GOV_GUARD_CALLS_DIR), never at ~/.gov-os, and its last line
gives the rule. Never writes bytecode."""
import glob
import json
import os
import shutil
import subprocess
import tempfile

PY = open(os.path.expanduser("~/.local/bin/gov")).readline()[2:].strip()


def decide(hooks, project, role, ticket, tool, tool_input, cwd=None, agent_type=None, tmpdir=None, timeout=120,
           extra_env=None):
    log = tempfile.mkdtemp(prefix="calls-", dir=os.environ.get("TMPDIR"))
    try:
        event = {"tool_name": tool, "tool_input": tool_input, "cwd": cwd or project, "session_id": "act-guard-fix-6"}
        if agent_type:
            event["agent_type"] = agent_type
        env = dict(os.environ, CLAUDE_PROJECT_DIR=project, GOV_GUARD_CALLS_DIR=log, PYTHONDONTWRITEBYTECODE="1")
        env.pop("PYTHONPATH", None)
        env.pop("GOV_ROLE", None)
        env.pop("GOV_TICKET", None)
        if role:
            env["GOV_ROLE"] = role
        if ticket:
            env["GOV_TICKET"] = ticket
        if tmpdir:
            env["TMPDIR"] = tmpdir
        env.update(extra_env or {})
        p = subprocess.run([PY, "-E", "-B", os.path.join(hooks, "pretooluse.py")], input=json.dumps(event),
                           capture_output=True, text=True, env=env, timeout=timeout)
        rule = ""
        for f in glob.glob(os.path.join(log, "*.jsonl")):
            lines = open(f).read().splitlines()
            if lines:
                try:
                    rule = json.loads(lines[-1]).get("rule", "")
                except ValueError:
                    pass
        reason = " ".join(p.stderr.split())
        if p.returncode == 2:
            return "deny", rule, reason
        if p.returncode != 0:
            return "error", rule, reason
        if not p.stdout.strip():
            return "allow", rule, ""
        out = json.loads(p.stdout)["hookSpecificOutput"]
        return out["permissionDecision"], rule, " ".join(str(out.get("permissionDecisionReason", "")).split())
    finally:
        shutil.rmtree(log, ignore_errors=True)


def bash(hooks, project, role, ticket, command, **kw):
    return decide(hooks, project, role, ticket, "Bash", {"command": command}, **kw)
