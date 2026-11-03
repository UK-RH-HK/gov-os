"""Print each non-green check of a `gov check --json` output, with its findings (shortened)."""
import json
import sys

text = open(sys.argv[1]).read()
doc = json.loads(text[text.find('{"ok"'):])
for check in doc["error"]["details"]["checks"]:
    if check["status"] == "GREEN":
        continue
    print("==", check["id"], check["family"], check["status"], check.get("severity"))
    for finding in check.get("findings", [])[:8]:
        print("   ", json.dumps(finding)[:600])
    extra = {k: v for k, v in check.items() if k not in ("findings", "id", "family", "status", "severity")}
    if extra:
        print("    extra:", json.dumps(extra)[:600])
