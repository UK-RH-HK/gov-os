"""Print every non-green family of a `gov check --json` log and its non-green checks' messages (shortened)."""
import json
import sys

text = open(sys.argv[1], encoding="utf-8").read()
data = json.loads(text[text.index('{"ok"'):])
for check in data["result"]["checks"]:
    if check.get("status") == "GREEN":
        continue
    print(check.get("family"), "|", check.get("id"), check.get("status"), check.get("severity"),
          "findings:", len(check.get("findings", [])))
    for finding in check.get("findings", [])[:5]:
        print("    ", str(finding)[:300])
