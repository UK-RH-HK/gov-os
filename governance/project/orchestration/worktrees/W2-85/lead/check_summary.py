"""Summarise gov check --json: every check with its status; the message of each that is not GREEN."""
import json
import sys

d = json.load(open(sys.argv[1]))
checks = (d.get("result") or {}).get("checks") or ((d.get("error") or {}).get("details") or {}).get("checks") or []
print("ok:", d.get("ok"), "checks:", len(checks))
for c in checks:
    status = c.get("status")
    line = f"  {c.get('id')}: {status} ({c.get('severity')})"
    if status != "GREEN":
        line += " " + json.dumps(c.get("findings") or c.get("message") or c)[:300]
    print(line)
