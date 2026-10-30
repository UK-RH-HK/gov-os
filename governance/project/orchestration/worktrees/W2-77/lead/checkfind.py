"""Print the non-green checks of a gov check --json output with their first findings."""
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
result = data.get("result", data)
checks = result.get("checks", result)
items = checks.items() if isinstance(checks, dict) else ((c.get("id"), c) for c in checks)
for name, entry in items:
    if isinstance(entry, dict) and entry.get("status") != "GREEN":
        print(name, entry.get("status"))
        for f in (entry.get("findings") or [])[:5]:
            print("   ", json.dumps(f)[:300])
