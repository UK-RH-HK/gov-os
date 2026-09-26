#!/usr/bin/env python3
"""BR-AR-0016 (OBS-BR-08): does a query command apply the task's retrieval_exclusions by itself? Runs the lexical and
semantic routes exactly as `govbridge search` does (no --exclude) and again with the task spec's exclusions passed
explicitly, for every public query text of the run-1 task, and counts hits whose occurrence paths fall under an
exclusion glob. Prints counts only."""
import json
import os
import sys

import yaml

root = os.popen("git rev-parse --show-toplevel").read().strip()
D = os.path.join(root, "release/orchestration/phase-2-context-bridge")
sys.path.insert(0, D)
from govbridge.core import pathrules  # noqa: E402
from govbridge.route import real_routes  # noqa: E402

task = yaml.safe_load(open(sys.argv[1]))
ex = task["retrieval_exclusions"]
qs = yaml.safe_load(open(os.path.join(D, "DEMONSTRATION/run-1/task-inputs/demonstration-queries.yaml")))["queries"]
routes = real_routes.build_real_routes(view_path=task["view"])
rows = []
for q in qs:
    if not q.get("text"):
        continue
    row = {"query": q["id"]}
    for mode, exc in (("cli_default_no_exclude", None), ("with_task_exclusions", ex)):
        n = 0
        for rn in ("lexical", "semantic"):
            for h in routes.run(rn, text=q["text"], k=8, exclude=exc):
                if any(pathrules.any_glob_match(o.path, ex) is not None for o in h.occurrences):
                    n += 1
        row[mode] = n
    rows.append(row)
tot = {m: sum(r[m] for r in rows) for m in ("cli_default_no_exclude", "with_task_exclusions")}
print(json.dumps({"per_query_excluded_hits": rows, "totals": tot}, indent=1))
