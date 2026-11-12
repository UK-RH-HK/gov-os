"""Fills the package templates from the bundle and the rehearsal logs.  python3 fill_package.py dispatch|guard2
Reads acts/<ACT>/manifest.json, list.txt and the rehearsal log; writes <ACT>.md beside the templates."""
import hashlib
import json
import os
import re
import sys

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
which = sys.argv[1]
ACT = {"dispatch": "ACT-DISPATCH-1", "guard2": "ACT-IDLE-GUARD-2"}[which]
B = os.path.join(D, "acts", ACT)
rows = [r.split("|") for r in open(os.path.join(B, "list.txt")).read().split("\n") if r]
man = open(os.path.join(B, "manifest.json"), "rb").read()
sha64 = hashlib.sha256(man).hexdigest()
log = open(os.path.join(B, "rehearsal.log")).read()
m = re.search(r"baseline: (.*?) \| new cases on the old (?:code|hook): (.*?) \| after the apply: (.*?)(?: \| new file on the round-1 hook: (.*))?$", log, re.M)
base, red, green, r1red = m.groups()
old = re.search(r"old test files on the new code: (.*)", log)
vals = {"SHA64": sha64, "SHA8": sha64[:8], "BASE": base, "RED": red, "GREEN": green,
        "OLDTESTS": old.group(1) if old else "-", "R1RED": r1red or "-", "OKN": str(len(re.findall(r"^ok ", log, re.M)))}
for i, r in enumerate(rows):
    vals[f"B{i}"], vals[f"A{i}"] = r[2][:16], r[3][:16]
nred = re.search(r"(\d+) failed", red)
vals["RED_NOTE"] = (f"on the old code {nred.group(1)} of the 18 fail, among them the three cap cases, the idle cause cases and the forecast cases; "
                    "the others are \"does not fire\" or \"stays as it was\" cases that pass on the old code by nature" if nred else "")
vals["TESTNOTE"] = (f"On the old hook {nred.group(1)} of the new file's cases fail (rehearsal C); the others are the cases that already hold on the old code. "
                    if nred else "")
text = open(os.path.join(D, f"{ACT}.md.tmpl")).read()
for k, v in vals.items():
    text = text.replace(f"[[{k}]]", v)
assert "[[" not in text, re.findall(r"\[\[\w+\]\]", text)
open(os.path.join(D, f"{ACT}.md"), "w").write(text)
print(ACT, "package written; manifest sha256", sha64)
