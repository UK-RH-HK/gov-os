"""Writes ACT-EXAMIN-SETS-1/manifest.json from the bundle's files (their sha256) in the operator's form, as
acts/ACT-PERMISSIONS-3/manifest.json has it. Copies rehearsal.log into the bundle first.   python3 make_manifest.py"""
import hashlib
import json
import os
import shutil

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
B = os.path.join(D, "ACT-EXAMIN-SETS-1")
shutil.copyfile(os.path.join(D, "rehearsal.log"), os.path.join(B, "rehearsal.log"))


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


root, path, before, after = open(os.path.join(B, "list.txt")).read().strip().split("|")
rel = f"{root}/{path}"
assert sha(os.path.join(B, "before", rel)) == before and sha(os.path.join(B, "after", rel)) == after
files = {f"before/{rel}": before, f"after/{rel}": after}
for name in ("apply.sh", "list.txt", "rehearsal.log"):
    files[name] = sha(os.path.join(B, name))
check = ("python3 -I -c 'import yaml,sys; d=yaml.safe_load(open(\"governance/project/path-map.yaml\")); s=d[\"evaluation_sets\"]; "
         "sys.exit(0 if list(s)[-2:]==[\"examin\",\"adoption-proving-ground\"] and len(s)==6 and "
         "s[\"examin\"][\"hidden\"]==[\"fixtures/evaluation/examin/hidden/**\"] and "
         "s[\"adoption-proving-ground\"][\"hidden\"]==[\"fixtures/evaluation/adoption-proving-ground/hidden/**\"] and "
         "all(s[k][\"measures\"][\"roles\"]==s[\"memory-verdict-2\"][\"measures\"][\"roles\"] for k in list(s)[-2:]) else 1)'")
m = {
    "act": "ACT-EXAMIN-SETS-1",
    "dec": "DEC-1130, DEC-1101, DEC-957",
    "author": "cto",
    "claimed_class": "a",
    "touched": [{"root": root, "path": path, "before": before, "after": after}],
    "files": files,
    "checks": [
        {"cmd": "PYTHONPATH=src python3 -m gov.check.pathmap", "exit": 0, "count": None},
        {"cmd": check, "exit": 0, "count": None},
    ],
    "commands": [],
    "rehearsal": {"log": "rehearsal.log", "sha256": files["rehearsal.log"]},
}
with open(os.path.join(B, "manifest.json"), "w") as f:
    json.dump(m, f, indent=1)
    f.write("\n")
print("manifest.json written;", len(files), "files hashed")
