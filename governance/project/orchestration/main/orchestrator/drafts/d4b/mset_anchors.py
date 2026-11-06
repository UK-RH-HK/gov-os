#!/usr/bin/env python3
"""ACT-MSET-3: every gold source's path exists and its heading is found exactly once, at the head (RUBRIC R6 item 1).

    python3 -I mset_anchors.py --sets-root <root> --set <name> --part <hidden|visible> <repository root>
    python3 -I mset_anchors.py <questions folder> <repository root>      (the old form: a folder in a tree)

repin_gold.py falls back to a source's lines when its heading is not found (as the measure does), so a mistyped
heading passes it. This check names, by the folder's own question ids only, each source whose path is missing, whose
heading is on no line, or whose heading is on more than one line. Prints only ids and counts. The first form is the
one for a set in the sets root (DEC-1084, ACT-GUARD-SETS-1): the folder is built here (sets_form.py).
"""
import glob
import os
import sys

import yaml

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))  # sets_form.py beside this file (also under -I)
from sets_form import sets_argv  # noqa: E402

argv = sets_argv(sys.argv)
folder, root = argv[1], argv[2]
missing, absent, repeated, n = [], [], [], 0
for f in sorted(glob.glob(os.path.join(folder, "*.yaml"))):
    q = yaml.safe_load(open(f)) or {}
    qid = q.get("id") or os.path.basename(f)[:-5]
    for entry in q.get("sources") or []:
        for alt in entry if isinstance(entry, list) else [entry]:
            if not isinstance(alt, dict) or not alt.get("path"):
                continue
            n += 1
            p = os.path.join(root, alt["path"])
            if not os.path.isfile(p):
                missing.append(qid)
                continue
            h = alt.get("heading")
            if h:
                lines = open(p, encoding="utf-8", errors="replace").read().splitlines()
                k = sum(1 for line in lines if line == h)
                (absent if k == 0 else repeated if k > 1 else []).append(qid)
show = lambda xs: f"{len(xs)}" + (f" ({', '.join(sorted(set(xs)))})" if xs else "")
print(f"sources: {n}; path missing: {show(missing)}; heading on no line: {show(absent)}; heading on more than one line: {show(repeated)}")
sys.exit(0 if not (missing or absent or repeated) else 1)
