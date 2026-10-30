"""ACT 1 (DEC-953 item 2, DEC-954): rewires .rulesync/hooks.jsonc for the five-rule guard.
    python3 act1_hooks.py <repository root>
The preToolUse line runs .claude/hooks/pretooluse.py (the five rules) instead of the kernel's full guard; the
postToolUse and postToolUseFailure containment lines are removed. Every other hook (preCompact, sessionStart, stop,
subagentStop) is unchanged. Prints what changed, never a command's text."""
import json
import sys
from pathlib import Path

root = Path(sys.argv[1])
path = root / ".rulesync/hooks.jsonc"
data = json.loads(path.read_text(encoding="utf-8"))  # this file carries no comments
hooks = data["hooks"]
old = "$CLAUDE_PROJECT_DIR/template/governance/kernel/hooks/pretooluse.py"
new = "$CLAUDE_PROJECT_DIR/.claude/hooks/pretooluse.py"
pre = hooks["preToolUse"]
assert len(pre) == 1 and old in pre[0]["command"], "preToolUse is not the expected kernel guard line"
pre[0]["command"] = pre[0]["command"].replace(old, new)
removed = [k for k in ("postToolUse", "postToolUseFailure") if hooks.pop(k, None) is not None]
path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
print("preToolUse now runs .claude/hooks/pretooluse.py; removed:", ", ".join(removed), "; kept:",
      ", ".join(k for k in hooks if k != "preToolUse"))
