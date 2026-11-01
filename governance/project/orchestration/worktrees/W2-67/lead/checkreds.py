"""Run 7: print each check of a gov check JSON that is not GREEN, with its first findings."""
import json
import sys

d = json.load(open(sys.argv[1], encoding="utf-8"))
details = d.get("error", {}).get("details", {}) or d.get("result", {})
checks = details.get("checks", [])
for c in checks:
    if c.get("status") != "GREEN":
        print("==", c.get("id"), c.get("family"), c.get("severity"), c.get("status"))
        for f in (c.get("findings") or [])[:6]:
            print("   ", json.dumps(f)[:400])
