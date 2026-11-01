#!/usr/bin/env python3
"""List each gov check result's name and status; print the non-green ones with a short reason."""
import json
import sys

text = open(sys.argv[1], encoding="utf-8").read()
data = json.loads(text[text.find("{"):])
checks = data.get("checks") or data.get("results") or data
if isinstance(checks, dict):
    checks = [dict(name=k, **(v if isinstance(v, dict) else {"status": v})) for k, v in checks.items()]
green = []
for c in checks:
    if not isinstance(c, dict):
        continue
    status = str(c.get("status") or c.get("verdict") or c.get("state"))
    name = c.get("name") or c.get("check") or c.get("id")
    if status.lower() in ("green", "pass", "passed", "ok"):
        green.append(name)
    else:
        reason = json.dumps(c.get("reason") or c.get("detail") or c.get("message") or c.get("findings") or "")[:300]
        print(f"NOT GREEN {name}: {status} | {reason}")
print(f"green: {len(green)}; top-level keys: {sorted(data.keys()) if isinstance(data, dict) else type(data)}")
