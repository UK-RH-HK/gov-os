import json
import sys

text = open(sys.argv[1], encoding="utf-8").read()
doc = json.loads(text[text.find("{"):])
res = doc.get("result", doc)
print("ok", doc.get("ok"), "error", (doc.get("error") or {}).get("code"))
checks = res.get("checks") or res.get("results") or []
if isinstance(checks, dict):
    checks = [{"id": k, **(v if isinstance(v, dict) else {"status": v})} for k, v in checks.items()]
for c in checks:
    status = c.get("status") or c.get("verdict") or c.get("state")
    if status not in ("green", "GREEN", "pass", "PASS", "ok"):
        print(c.get("id") or c.get("name"), status, str(c.get("summary") or c.get("message") or c.get("output") or "")[:300].replace("\n", " | "))
print("keys", list(res.keys())[:20])
