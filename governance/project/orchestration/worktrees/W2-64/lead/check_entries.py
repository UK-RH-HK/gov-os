"""Print each non-green check of gov check --json with its first findings, and the core-schema entry (lead's scratch)."""
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
details = (data.get("error") or {}).get("details") or data.get("result") or {}
checks = details.get("checks") or []
for c in checks:
    if c.get("id") == "core-schema" or c.get("status") != "GREEN":
        print(c.get("id"), c.get("family"), c.get("status"))
        for f in (c.get("findings") or [])[:3]:
            print("   ", json.dumps(f)[:400])
if not checks:
    print(sorted(details.keys()))
