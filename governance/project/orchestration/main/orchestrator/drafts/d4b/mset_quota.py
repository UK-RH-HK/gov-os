#!/usr/bin/env python3
"""ACT-MSET-3: the new verdict set's category counts against its table. Counts only.

    python3 -I mset_quota.py <questions folder>

Prints the count per category beside the table's, and PASS when every count is exact and the total is 80. The one
allowed shift (ACT-MSET-3 section 2): lesson memory is thin, so failure-memory may fall to 2, its shortfall moved
to decision (failure-memory + decision = 17).
"""
import collections
import glob
import os
import sys

import yaml

TABLE = {"decision": 13, "contract": 8, "plan": 8, "ticket": 8, "exact-string": 8, "callers": 8,
         "code-paraphrase": 7, "kernel-template": 7, "multi-file": 6, "failure-memory": 4, "history": 2,
         "nonexistent-id": 1}
files = sorted(glob.glob(os.path.join(sys.argv[1], "*.yaml")))
got = collections.Counter((yaml.safe_load(open(f)) or {}).get("category") for f in files)
bad = []
for k in sorted(set(TABLE) | set(got), key=str):
    want, have = TABLE.get(k, 0), got.get(k, 0)
    print(f"{k}: {have} of {want}")
    if want != have and k not in ("decision", "failure-memory"):
        bad.append(k)
fm, dec = got.get("failure-memory", 0), got.get("decision", 0)
shift = ""
if not (2 <= fm <= 4 and fm + dec == 17):
    bad.append("decision/failure-memory")
elif fm < 4:
    shift = f" (failure-memory short by {4 - fm}, moved to decision)"
print(f"total: {len(files)} of {sum(TABLE.values())}; "
      + ("PASS" + shift if not bad and len(files) == 80 else f"NOT YET: {', '.join(map(str, bad)) or 'the total'}"))
