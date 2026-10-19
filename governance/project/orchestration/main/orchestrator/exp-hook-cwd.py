"""P-38: in which folder does Claude Code start a hook after the session's Bash calls changed directory,
and does it raise the failed-call event for a failed Bash command.

One throwaway project in the session scratchpad, one short headless session. Every hook entry appends its
event name and its working directory to hook.log. A second pre-call entry is registered in the relative form
of the template's hooks source (python3 hooks/rel.py) and records whether it could start.
"""
import json
import os
import shutil
import subprocess
import time

BASE = "/tmp/claude-1000/-home-usain-Dynamic-Agentic-Engineering-OS/45f2a529-6746-474d-b738-e1df6781c663/scratchpad/hook-cwd-exp"
CLAUDE = "/home/usain/.local/bin/claude"

shutil.rmtree(BASE, ignore_errors=True)
os.makedirs(os.path.join(BASE, ".claude"))
os.makedirs(os.path.join(BASE, "sub", "deep"))
os.makedirs(os.path.join(BASE, "hooks"))
LOG = os.path.join(BASE, "hook.log")
with open(os.path.join(BASE, "hooks", "rel.py"), "w") as f:
    f.write("import os\nopen(%r, 'a').write('REL-STARTED in ' + os.getcwd() + '\\n')\n" % LOG)


def entry(event):
    return {"type": "command", "command": f"echo \"{event} $(pwd)\" >> {LOG}", "timeout": 10}


settings = {"hooks": {
    "PreToolUse": [{"matcher": "Bash", "hooks": [
        entry("PreToolUse"),
        # the relative form; its failure must not block the experiment, so the error is swallowed and recorded
        {"type": "command", "timeout": 10,
         "command": f"python3 hooks/rel.py 2>/dev/null || echo \"REL-COULD-NOT-START in $(pwd)\" >> {LOG}"}]}],
    "PostToolUse": [{"matcher": "Bash", "hooks": [entry("PostToolUse")]}],
    "PostToolUseFailure": [{"matcher": "Bash", "hooks": [entry("PostToolUseFailure")]}],
}}
with open(os.path.join(BASE, ".claude", "settings.json"), "w") as f:
    json.dump(settings, f, indent=1)

prompt = ("Make exactly these four Bash tool calls, one after another, each as its own separate call, "
          "and nothing else; do not combine them and do not retry any of them:\n"
          "1. pwd\n2. cd sub/deep\n3. ls /this-path-does-not-exist-for-the-experiment\n4. pwd\n"
          "Then report in one line what the fourth call printed.")
start = time.time()
run = subprocess.run(
    [CLAUDE, "-p", prompt, "--model", "claude-haiku-4-5-20251001", "--output-format", "stream-json",
     "--verbose", "--allowedTools", "Bash"],
    cwd=BASE, capture_output=True, text=True, timeout=300)
print("exit", run.returncode, "wall", round(time.time() - start, 1), "s")
with open(os.path.join(BASE, "out.jsonl"), "w") as f:
    f.write(run.stdout)
print("--- hook.log")
print(open(LOG).read() if os.path.exists(LOG) else "absent")
print("--- session")
for line in run.stdout.splitlines():
    try:
        o = json.loads(line)
    except ValueError:
        continue
    kind = o.get("type")
    if kind == "system" and o.get("subtype") == "init":
        print("version:", o.get("claude_code_version"))
    elif kind == "assistant":
        for c in o["message"]["content"]:
            if c.get("type") == "tool_use":
                print("CALL", json.dumps(c.get("input"))[:200])
    elif kind == "user":
        content = o["message"]["content"]
        for c in content if isinstance(content, list) else []:
            if c.get("type") == "tool_result":
                print("  RESULT is_error=%s %s" % (c.get("is_error"), str(c.get("content"))[:200]))
    elif kind == "result":
        print("FINAL", str(o.get("result"))[:300])
if run.stderr.strip():
    print("STDERR", run.stderr[:300])
