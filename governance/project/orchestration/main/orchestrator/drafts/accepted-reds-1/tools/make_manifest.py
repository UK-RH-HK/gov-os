"""Writes ACT-ACCEPTED-REDS-1/manifest.json (the operator's form, as acts/ACT-EXAMIN-SETS-1/manifest.json has it).

  python3 make_manifest.py --draft   manifest without the rehearsal (the rehearsal reads its checks[] from it)
  python3 make_manifest.py           final manifest: copies ../rehearsal.log into the bundle and hashes it; refuses unless
                                     the log ends "failures: 0" and its checks[] equal the draft's that the rehearsal ran
"""
import hashlib
import json
import os
import shutil
import sys

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
B = os.path.join(D, "acts", "ACT-ACCEPTED-REDS-1")
DRAFT = os.path.join(D, "tmp", "manifest.draft.json")


def sha(p):
    with open(p, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


T1 = "tests/acceptance/W1-19/test_w1_19_real_models.py::test_a_warm_query_answers_within_half_a_second_at_p95"
T2 = "tests/acceptance/W2-13/test_w2_13_latency.py::test_a_warm_retrieval_with_the_real_models_answers_within_the_budget"
PROBE = ("python3 -I -c 'import yaml,sys; d=yaml.safe_load(open(\"governance/project/path-map.yaml\")); r=d[\"accepted_reds\"]; "
         f"t=[\"{T1}\",\"{T2}\"]; "
         "sys.exit(0 if [e[\"test\"] for e in r]==t and all(e[\"decision\"]==\"DEC-1134\" and e[\"fixed_by\"]==\"W2-155\" "
         "and e[\"reason\"].strip() for e in r) and \"examin\" in d[\"evaluation_sets\"] else 1)'")
CHECKS = [
    {"cmd": "PYTHONPATH=src python3 -m gov.check.pathmap", "exit": 0, "count": None},
    {"cmd": PROBE, "exit": 0, "count": None},
]

draft = "--draft" in sys.argv
root, path, before, after = open(os.path.join(B, "list.txt")).read().strip().split("|")
rel = f"{root}/{path}"
assert sha(os.path.join(B, "before", rel)) == before and sha(os.path.join(B, "after", rel)) == after
files = {f"before/{rel}": before, f"after/{rel}": after}
names = ["apply.sh", "list.txt"] + ([] if draft else ["rehearsal.log"])
if not draft:
    log = os.path.join(D, "rehearsal.log")
    tail = open(log).read().rstrip().splitlines()[-1]
    assert tail == "failures: 0", f"the rehearsal log ends {tail!r}"
    assert json.load(open(DRAFT))["checks"] == CHECKS, "the checks changed since the rehearsal read them"
    shutil.copyfile(log, os.path.join(B, "rehearsal.log"))
for name in names:
    files[name] = sha(os.path.join(B, name))
m = {
    "act": "ACT-ACCEPTED-REDS-1",
    "dec": "DEC-1134, DEC-1125, DEC-757, DEC-862",
    "author": "cto",
    "claimed_class": "O",
    "touched": [{"root": root, "path": path, "before": before, "after": after}],
    "files": files,
    "checks": CHECKS,
    "commands": [],
}
if not draft:
    m["rehearsal"] = {"log": "rehearsal.log", "sha256": files["rehearsal.log"]}
out = DRAFT if draft else os.path.join(B, "manifest.json")
with open(out, "w") as f:
    json.dump(m, f, indent=1)
    f.write("\n")
print(out, "written;", len(files), "files hashed;", "sha256", sha(out))
