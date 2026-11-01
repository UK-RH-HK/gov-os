"""Print the details of gov check's non-green families from its JSON envelope (the last JSON object in the file)."""
import json
import sys

text = open(sys.argv[1], encoding="utf-8").read()
data = json.loads(text[text.find('{"ok"'):])
details = data.get("error", {}).get("details", {})
for key, value in details.items():
    if key == "families":
        continue
    print("== detail key:", key, "| type:", type(value).__name__)
checks = details.get("checks") or details.get("results") or []
for check in checks:
    status = check.get("status")
    if status != "GREEN":
        print("#", check.get("id"), check.get("family"), status)
        print(json.dumps({k: v for k, v in check.items() if k not in ("id", "family", "status")})[:1500])
