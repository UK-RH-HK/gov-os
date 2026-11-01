"""The findings of every check of `gov check --json` that is not GREEN (ids, statuses and finding texts, cut short)."""
import json
import sys

data = json.load(open(sys.argv[1]))
for check in data["error"]["details"]["checks"]:
    if check["status"] != "GREEN":
        print(check["id"], check["family"], check["severity"], check["status"])
        for finding in check["findings"][:8]:
            print("   ", json.dumps(finding)[:400])
        if len(check["findings"]) > 8:
            print("    ...", len(check["findings"]), "findings in all")
