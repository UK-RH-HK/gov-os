"""DEC-578: what Claude Code does with a PreToolUse hook that passes its time limit.

Three throwaway projects under /tmp/gov-hook-timeout-exp, one short headless session in each:
  a: the hook sleeps 25 s (limit 5 s), then would exit 0
  b: the hook sleeps 25 s (limit 5 s), then would refuse (exit 2)
  c: control, the hook refuses at once (exit 2)
The session is asked to run one command that creates ran.txt. Prints what happened.
"""
import json
import os
import subprocess
import time

BASE = "/tmp/gov-hook-timeout-exp"
CLAUDE = "/home/usain/.local/bin/claude"
HOOKS = {
    "a": "echo started >> B/a/hook.log; sleep 25; echo finished >> B/a/hook.log; exit 0",
    "b": "echo started >> B/b/hook.log; sleep 25; echo finished >> B/b/hook.log; "
         "echo 'refused by the experiment hook' >&2; exit 2",
    "c": "echo started >> B/c/hook.log; echo 'refused by the experiment hook' >&2; exit 2",
}

for key, command in HOOKS.items():
    project = os.path.join(BASE, key)
    os.makedirs(os.path.join(project, ".claude"), exist_ok=True)
    for name in ("hook.log", "ran.txt"):
        if os.path.exists(os.path.join(project, name)):
            os.remove(os.path.join(project, name))
    settings = {"hooks": {"PreToolUse": [{"matcher": "Bash", "hooks": [
        {"type": "command", "command": command.replace("B", BASE), "timeout": 5}]}]}}
    with open(os.path.join(project, ".claude", "settings.json"), "w") as f:
        json.dump(settings, f, indent=1)
    prompt = ("Run exactly this one bash command, once, and nothing else, then report its outcome "
              f"in one line: touch {project}/ran.txt")
    start = time.time()
    run = subprocess.run(
        [CLAUDE, "-p", prompt, "--model", "claude-haiku-4-5-20251001", "--output-format", "stream-json",
         "--verbose", "--allowedTools", "Bash"],
        cwd=project, capture_output=True, text=True, timeout=300)
    wall = round(time.time() - start, 1)
    with open(os.path.join(project, "out.jsonl"), "w") as f:
        f.write(run.stdout)
    print(f"== {key}: exit {run.returncode}, wall {wall} s")
    log = os.path.join(project, "hook.log")
    print("hook.log:", open(log).read().split() if os.path.exists(log) else "absent")
    print("ran.txt exists:", os.path.exists(os.path.join(project, "ran.txt")))
    for line in run.stdout.splitlines():
        try:
            o = json.loads(line)
        except ValueError:
            continue
        kind = o.get("type")
        if kind == "system" and o.get("subtype") == "init":
            print("version:", o.get("claude_code_version"))
        elif kind == "system":
            print("SYSTEM", json.dumps(o)[:500])
        elif kind == "user":
            content = o["message"]["content"]
            for c in content if isinstance(content, list) else []:
                if c.get("type") == "tool_result":
                    print("TOOL_RESULT is_error=%s %s" % (c.get("is_error"), str(c.get("content"))[:300]))
        elif kind == "result":
            print("RESULT", str(o.get("result"))[:300])
    if run.stderr.strip():
        print("STDERR", run.stderr[:300])
