"""Print select_tests.py's scope, core_changed, unplaced and the count of its options (no test bodies)."""
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
for key in ("scope", "core_changed", "unplaced", "base", "reasons"):
    if key in data:
        value = data[key]
        print(key, ":", value if not isinstance(value, list) or len(value) < 20 else f"{len(value)} items")
opts = data.get("pytest_options", [])
print("pytest_options:", len(opts), "items")
print("keys:", sorted(data))
