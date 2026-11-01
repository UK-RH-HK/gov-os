"""Summarise gov check --json: each check's id and status; findings of the non-green ones, briefly."""
import json
import sys

text = open(sys.argv[1], encoding="utf-8").read()
data = json.loads(text[text.find("{"):])
result = data.get("result", data)
checks = result.get("checks") or result.get("results") or []
for check in checks:
    cid = check.get("id") or check.get("check")
    status = check.get("status") or check.get("verdict")
    print(f"{cid}: {status}")
    if str(status).lower() not in ("green", "pass", "ok"):
        detail = json.dumps(check.get("findings") or check.get("detail") or check.get("output") or "")[:700]
        print("   ", detail)
print("keys:", list(result.keys())[:12])
