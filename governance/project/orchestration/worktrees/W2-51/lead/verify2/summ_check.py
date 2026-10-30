"""Summarise gov check --json: every check that is not green, by name, with its message."""
import json
import sys

doc = json.load(open(sys.argv[1]))
res = doc.get("result", doc)
checks = res.get("checks") if isinstance(res, dict) else res
if checks is None:
    print(json.dumps(doc)[:3000])
    sys.exit(0)
print("top-level keys:", list(doc.keys()), "ok:", doc.get("ok"))
counts = {}
for c in checks:
    st = c.get("status") or c.get("result") or c.get("state")
    counts[st] = counts.get(st, 0) + 1
    if str(st).lower() not in ("green", "pass", "ok"):
        msg = c.get("message") or c.get("reason") or c.get("detail") or ""
        print("-", c.get("id") or c.get("name"), st, "|", str(msg)[:600])
print("counts:", counts)
