"""Print the non-green checks of gov check's error JSON (the last line of check.err that is a JSON object)."""
import json
import sys

lines = [l for l in open(sys.argv[1]).read().splitlines() if l.startswith("{")]
doc = json.loads(lines[-1])
for c in doc["error"]["details"]["checks"]:
    if c["status"] != "GREEN":
        print("==", c["id"], c["family"], c["severity"], c["status"])
        for f in c.get("findings", [])[:15]:
            print("   ", json.dumps(f)[:700])
        if len(c.get("findings", [])) > 15:
            print("    ... and", len(c["findings"]) - 15, "more")
