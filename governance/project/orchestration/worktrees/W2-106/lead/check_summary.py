import json
import sys

d = json.load(open(sys.argv[1]))
details = d.get("error", {}).get("details") or d.get("result", {})
for check in details.get("checks", []):
    if check.get("status") == "GREEN":
        continue
    print(f"--- {check['id']} [{check['family']}] {check['severity']} {check['status']}")
    for f in check.get("findings", [])[:12]:
        print("   ", json.dumps(f)[:400])
    if len(check.get("findings", [])) > 12:
        print("    ...", len(check["findings"]), "findings")
