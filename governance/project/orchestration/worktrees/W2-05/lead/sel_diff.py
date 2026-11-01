"""Compare two select_tests.py outputs: scope, core_changed, unplaced, the selected targets and the options."""
import json
import sys

a, b = (json.load(open(p)) for p in sys.argv[1:3])
for key in ("scope", "core_changed", "unplaced"):
    if a.get(key) != b.get(key):
        print(key, "differs:", a.get(key), "->", b.get(key))
ta = [s["target"] for s in a["selected"]]
tb = [s["target"] for s in b["selected"]]
print("targets only in first:", sorted(set(ta) - set(tb)))
print("targets only in second:", sorted(set(tb) - set(ta)))
print("options only in first:", sorted(set(a["pytest_options"]) - set(b["pytest_options"])))
print("options only in second:", sorted(set(b["pytest_options"]) - set(a["pytest_options"])))
print("counts:", len(ta), len(tb), len(a["pytest_options"]), len(b["pytest_options"]), "scope", b.get("scope"),
      "core", len(b.get("core_changed") or []), "unplaced", b.get("unplaced"))
