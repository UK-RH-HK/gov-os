"""Summarise gov check --json: each check's name and status, the non-green ones first, with a short reason."""
import json
import sys

doc = json.load(open(sys.argv[1], encoding="utf-8"))
print("ok", doc.get("ok"))
result = doc.get("result", doc)
checks = result.get("checks", result) if isinstance(result, dict) else result
items = checks.items() if isinstance(checks, dict) else ((c.get("name") or c.get("id"), c) for c in checks)
rows = []
for name, check in items:
    status = check.get("status") if isinstance(check, dict) else check
    rows.append((str(status), str(name), check))
for status, name, check in sorted(rows, key=lambda r: r[0] in ("GREEN", "green", "pass", "ok", "True")):
    reason = ""
    if isinstance(check, dict) and status not in ("GREEN", "green", "pass", "ok"):
        reason = json.dumps({k: v for k, v in check.items() if k != "status"})[:400]
    print(status, name, reason)
