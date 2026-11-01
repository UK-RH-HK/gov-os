import json
import sys

t = open(sys.argv[1], encoding="utf-8").read()
d = json.loads(t[t.find('{"ok"'):])
det = d["error"]["details"]
for c in det.get("checks", []):
    if c.get("status") not in ("GREEN",) and (len(sys.argv) < 3 or sys.argv[2] in json.dumps(c)):
        print(json.dumps(c, indent=1)[:4000])
