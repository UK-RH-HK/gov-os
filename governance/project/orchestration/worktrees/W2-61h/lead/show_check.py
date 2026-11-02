"""Print the non-green families of a gov check --json log, with their findings trimmed (no file contents)."""
import json
import sys

d = json.load(open(sys.argv[1]))
e = d["error"]
print("code:", e["code"], "|", str(e["message"])[:200])
for c in e["details"]["checks"]:
    if c.get("status") == "GREEN":
        continue
    print("==", c["id"], "|", c["family"], "|", c["severity"], "|", c["status"], "| findings", len(c["findings"]))
    for f in c["findings"][:8]:
        print("   -", json.dumps(f)[:400])
