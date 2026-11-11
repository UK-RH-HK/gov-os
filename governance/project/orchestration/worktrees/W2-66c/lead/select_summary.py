import json
import sys

d = json.load(open(sys.argv[1]))
print("keys:", sorted(d))
for k in ("scope", "core_changed", "unplaced", "why_full", "changed"):
    if k in d:
        v = d[k]
        print(k, ":", json.dumps(v)[:800])
sel = d.get("selected") or []
print("selected:", len(sel))
for e in sel[:40]:
    t = e.get("target") if isinstance(e, dict) else e
    why = [w.get("reason") for w in (e.get("why") or [])] if isinstance(e, dict) else ""
    print("  ", t, why)
