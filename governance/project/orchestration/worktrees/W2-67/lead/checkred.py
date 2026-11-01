"""Print the details of every non-GREEN family in a gov check --json log (error.details)."""
import json
import sys

text = open(sys.argv[1]).read()
data = json.loads(text[text.find("{"):])
details = (data.get("error") or {}).get("details") or {}
for key, value in details.items():
    if key == "families":
        continue
    print("==", key, json.dumps(value)[:300])
for check in details.get("checks") or []:
    if check.get("status") != "GREEN":
        print("##", check.get("id"), check.get("status"), json.dumps(check.get("findings"))[:900])
