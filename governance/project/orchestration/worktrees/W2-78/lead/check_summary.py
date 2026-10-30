"""Summarises gov check --json: each check's id and status; the details of every check that is not green."""
import json
import sys

d = json.load(open(sys.argv[1]))
r = d.get("result", d)
checks = r.get("checks", [])
counts = {}
for c in checks:
    s = c.get("status") or c.get("result") or ("ok" if c.get("ok") else "?")
    counts[s] = counts.get(s, 0) + 1
    if s not in ("pass", "green", "ok", "passed"):
        print(c.get("id"), s, json.dumps({k: v for k, v in c.items() if k not in ("id", "status")})[:600])
print("counts:", counts)
print("families:", json.dumps(r.get("families"))[:800])
