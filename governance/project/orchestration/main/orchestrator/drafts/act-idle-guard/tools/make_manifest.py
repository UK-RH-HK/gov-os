"""Writes acts/ACT-IDLE-GUARD-1/manifest.json from the bundle's files (their sha256), in the operator's form (as
acts/ACT-NIGHTLY-RESTART-1/manifest.json has it). Copies nothing: rehearsal.log is written into the bundle by
rehearse.sh's tee (../rehearsal.log is copied here first, so run it after rehearse.sh).
   python3 make_manifest.py"""
import hashlib
import json
import os
import shutil

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
B = os.path.join(D, "acts", "ACT-IDLE-GUARD-1")
shutil.copyfile(os.path.join(D, "rehearsal.log"), os.path.join(B, "rehearsal.log"))


def sha(p):
    with open(p, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


touched, files = [], {}
with open(os.path.join(B, "list.txt")) as f:
    for line in f:
        if not line.strip():
            continue
        root, path, before, after = line.strip().split("|")
        rel = f"{root}/{path}"
        assert sha(os.path.join(B, "before", rel)) == before and sha(os.path.join(B, "after", rel)) == after
        touched.append({"root": root, "path": path, "before": before, "after": after})
        files[f"before/{rel}"] = before
        files[f"after/{rel}"] = after
for name in ("apply.sh", "list.txt", "rehearsal.log"):
    files[name] = sha(os.path.join(B, name))
with open(os.path.join(D, "tools", "checks.json")) as f:
    checks = json.load(f)
m = {
    "act": "ACT-IDLE-GUARD-1",
    "dec": "DEC-1110, DEC-1109, DEC-936",
    "author": "cto",
    "claimed_class": "O",
    "touched": touched,
    "files": files,
    "checks": checks,
    "commands": [],
    "rehearsal": {"log": "rehearsal.log", "sha256": files["rehearsal.log"]},
}
with open(os.path.join(B, "manifest.json"), "w") as f:
    json.dump(m, f, indent=1)
    f.write("\n")
print("manifest.json written;", len(files), "files hashed; sha256", sha(os.path.join(B, "manifest.json")))
