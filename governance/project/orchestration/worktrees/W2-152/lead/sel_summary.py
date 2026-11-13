import json
import sys

d = json.load(open(sys.argv[1]))
print("keys:", list(d.keys()))
print("scope:", d.get("scope"), "core_changed:", d.get("core_changed"), "unplaced:", d.get("unplaced"))
print("selected:", len(d.get("selected", [])))
opts = d.get("pytest_options")
print("pytest_options count:", len(opts) if opts else opts)
if opts:
    with open(sys.argv[2], "w") as fh:
        fh.write("\n".join(opts) + "\n")
    print("first options:", opts[:6])
