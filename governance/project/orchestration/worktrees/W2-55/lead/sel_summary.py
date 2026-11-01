import json
import sys

doc = json.load(open(sys.argv[1], encoding="utf-8"))
for key in ("scope", "why_full", "core_changed", "unplaced", "governance_left_out"):
    print(key, "=", doc.get(key))
print("selected:", [s["target"] for s in doc.get("selected", [])])
opts = doc.get("pytest_options", [])
print("pytest_options:", len(opts), "items")
with open(sys.argv[2], "w", encoding="utf-8") as out:
    out.write("\n".join(opts) + "\n")
print([k for k in doc if k not in ("selected", "changed", "pytest_options")])
