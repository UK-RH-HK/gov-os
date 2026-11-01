"""Summarise a gov check --json log: every check that is not GREEN, with its summary."""
import json
import sys

text = open(sys.argv[1]).read()
data = json.loads(text[text.find("{"):])
print("ok:", data.get("ok"), "error:", json.dumps(data.get("error"))[:600])
result = data.get("result") or {}
checks = result.get("checks", result) if isinstance(result, dict) else result
items = checks.items() if isinstance(checks, dict) else [(c.get("name") or c.get("check"), c) for c in checks]
for name, check in items:
    status = check.get("status") if isinstance(check, dict) else check
    if str(status).upper() != "GREEN":
        detail = check.get("summary") or check.get("message") or check.get("findings") if isinstance(check, dict) else ""
        print(name, status, json.dumps(detail)[:400])
