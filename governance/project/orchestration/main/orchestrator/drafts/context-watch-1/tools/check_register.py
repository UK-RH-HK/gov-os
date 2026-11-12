"""ACT-CONTEXT-WATCH-1's check of the registration (run from the repository root with `python3 -I - < this file`, in the
manifest as a here-document; no pytest, no byte-code). Reads .claude/settings.json and .rulesync/hooks.jsonc and asserts the
one change and nothing else: the hook events are PreToolUse, PostToolUse, PreCompact, SessionStart, Stop, SubagentStop in
that order; PostToolUse is one block with matcher Bash and one command hook, timeout 10, whose command is the PreCompact
hook's command with precompact.py replaced by context_watch.py; the same entry stands in the rulesync source (postToolUse);
the other five events keep one block each. Prints 6 and exits 0 when all six hold."""
import json
import re
import sys

sys.dont_write_bytecode = True
settings = json.load(open(".claude/settings.json"))["hooks"]
source = json.loads(re.sub(r"(?m)^\s*//.*$", "", open(".rulesync/hooks.jsonc").read()))["hooks"]
n = 0


def ok(cond, what):
    global n
    if not cond:
        sys.stderr.write("FAIL: " + what + "\n")
        sys.exit(1)
    n += 1


ok(list(settings) == ["PreToolUse", "PostToolUse", "PreCompact", "SessionStart", "Stop", "SubagentStop"], "settings events")
pre = settings["PreCompact"][0]["hooks"][0]["command"]
want = pre.replace("precompact.py", "context_watch.py")
post = settings["PostToolUse"]
ok(len(post) == 1 and post[0].get("matcher") == "Bash" and len(post[0]["hooks"]) == 1, "one Bash block")
h = post[0]["hooks"][0]
ok(h == {"type": "command", "command": want, "timeout": 10}, "the command hook")
ok("template/governance/kernel/hooks/context_watch.py" in h["command"] and "precompact.py" not in h["command"], "the script path")
s = source["postToolUse"]
ok(len(s) == 1 and s[0] == {"type": "command", "matcher": "Bash", "command": want, "timeout": 10}, "the rulesync source entry")
ok(all(len(settings[e]) == 1 for e in ("PreToolUse", "PreCompact", "SessionStart", "Stop", "SubagentStop"))
   and list(source) == ["preToolUse", "postToolUse", "preCompact", "sessionStart", "stop", "subagentStop"], "the other events keep one block each")
print(n)
