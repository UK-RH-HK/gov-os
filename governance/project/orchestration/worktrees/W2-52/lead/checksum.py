"""Summarise gov check --json: every check not green, with its findings (paths and codes only)."""
import json
import sys

text = open(sys.argv[1]).read()
start = text.find("{")
data = json.loads(text[start:])
checks = data.get("checks", data)
items = checks.items() if isinstance(checks, dict) else ((c.get("name"), c) for c in checks)
for name, c in items:
    status = c.get("status") if isinstance(c, dict) else c
    if status not in ("pass", "green", "ok"):
        print("==", name, status)
        if isinstance(c, dict):
            for f in (c.get("findings") or [])[:20]:
                print("   ", json.dumps(f)[:300])
            for k in ("summary", "message", "line"):
                if k in c:
                    print("   ", k, str(c[k])[:300])
print("top-level keys:", list(data.keys())[:12])
for k in ("status", "summary", "verdict"):
    if k in data:
        print(k, str(data[k])[:300])
