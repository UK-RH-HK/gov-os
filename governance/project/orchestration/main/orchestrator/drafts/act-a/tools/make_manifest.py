"""Writes acts/ACT-LOAD-BALANCER-A/manifest.json from the bundle's files (their sha256), in the operator's form (as
acts/ACT-EXAMIN-SETS-1/manifest.json has it). Copies rehearsal.log into the bundle first, so run it after rehearse.sh.
   python3 make_manifest.py"""
import hashlib
import json
import os
import shutil

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
B = os.path.join(D, "acts", "ACT-LOAD-BALANCER-A")
shutil.copyfile(os.path.join(D, "rehearsal.log"), os.path.join(B, "rehearsal.log"))


def sha(p):
    with open(p, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


with open(os.path.join(B, "list.txt")) as f:
    root, path, before, after = f.read().strip().split("|")
rel = f"{root}/{path}"
assert sha(os.path.join(B, "before", rel)) == before and sha(os.path.join(B, "after", rel)) == after
files = {f"before/{rel}": before, f"after/{rel}": after}
for name in ("apply.sh", "list.txt", "rehearsal.log"):
    files[name] = sha(os.path.join(B, name))
with open(os.path.join(D, "tools", "checks.json")) as f:
    checks = json.load(f)
m = {
    "act": "ACT-LOAD-BALANCER-A",
    "dec": "DEC-1133, DEC-1105, DEC-1008, DEC-898",
    "author": "cto",
    "claimed_class": "b",
    "touched": [{"root": root, "path": path, "before": before, "after": after}],
    "files": files,
    "checks": checks,
    "commands": [],
    "rehearsal": {"log": "rehearsal.log", "sha256": files["rehearsal.log"]},
}
with open(os.path.join(B, "manifest.json"), "w") as f:
    json.dump(m, f, indent=1)
    f.write("\n")
print("manifest.json written;", len(files), "files hashed; sha256", sha(os.path.join(B, "manifest.json")))
