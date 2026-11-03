"""Print every non-green check of a `gov check --json` log with its first findings."""
import json
import sys

text = open(sys.argv[1]).read()
data = json.loads(text[text.find("{"):])
details = (data.get("error") or {}).get("details") or data.get("result") or {}
for check in details.get("checks", []):
    if check.get("status") == "GREEN":
        continue
    print(f"== {check.get('id')} ({check.get('family')}, {check.get('severity')}): {check.get('status')}")
    for finding in (check.get("findings") or [])[:6]:
        print("   -", json.dumps(finding)[:600])
    print("   findings:", len(check.get("findings") or []))
