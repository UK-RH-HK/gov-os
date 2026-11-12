"""Print the non-green checks of a gov check --json log (line 20 onward holds the JSON)."""
import json
import sys

text = open(sys.argv[1]).read()
start = text.find('{"ok"')
data = json.loads(text[start:text.rfind("}") + 1])
for c in data["error"]["details"]["checks"]:
    if c.get("status") != "GREEN":
        print(c.get("status"), c.get("id"), c.get("family"))
        for k in ("reason", "summary", "message"):
            if c.get(k):
                print("   ", k, str(c[k])[:500])
        for f in (c.get("findings") or c.get("items") or [])[:6]:
            print("    -", str(f)[:300])
