"""Summarise a gov check --json output: python3 check_summary.py <check.json>. Prints each non-green check's details."""
import json
import sys

text = open(sys.argv[1]).read()
doc = json.loads(text[text.find('{"ok"'):])
details = (doc.get("error") or {}).get("details") or doc.get("result") or {}
for key, value in details.items():
    if key == "families":
        continue
    print("##", key)
    if isinstance(value, list):
        for item in value:
            if isinstance(item, dict) and item.get("status") not in ("GREEN", None):
                print("-", json.dumps(item)[:700])
            elif isinstance(item, dict) and item.get("status") is None:
                print("-", json.dumps(item)[:300])
    elif isinstance(value, dict):
        for k, v in value.items():
            s = json.dumps(v)
            if '"GREEN"' not in s[:60]:
                print("-", k, s[:700])
    else:
        print(str(value)[:300])
