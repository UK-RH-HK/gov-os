"""Summarise gov check --json: each check's status (names only, no messages that could hold hashes)."""
import json
import sys

data = json.load(open(sys.argv[1]))
result = data.get("result", data)
checks = result.get("checks") if isinstance(result, dict) else None
if checks is None:
    print(sorted(result.keys()) if isinstance(result, dict) else type(result))
    sys.exit(0)
by = {}
for c in checks:
    status = c.get("status") or c.get("result") or "?"
    by.setdefault(status, []).append(c.get("id") or c.get("name"))
for status, names in sorted(by.items()):
    print(status, len(names), names if status.upper() != "GREEN" else "")
print("ok:", data.get("ok"), "overall:", result.get("status") or result.get("overall"))
