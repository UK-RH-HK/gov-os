#!/usr/bin/env python3
"""BR-AR-0016: write a copy of the run-1 task spec whose view pins the records ref to the demonstration's records
commit (the committed canonical view follows the bridge tip, which has moved since run-1), so the run-1 compile can
be reproduced exactly. Usage: make_pinned_task.py <out_dir> <records_commit>"""
import os
import sys

import yaml

DOM = "release/orchestration/phase-2-context-bridge"
out, commit = sys.argv[1], sys.argv[2]
root = os.popen("git rev-parse --show-toplevel").read().strip()
D = os.path.join(root, DOM)
v = yaml.safe_load(open(os.path.join(D, "config/canonical-view.yaml")))
for r in v["refs"]:
    if r.get("name") == "records":
        r["follow"], r["pinned_commit"] = "pinned", commit
os.makedirs(out, exist_ok=True)
yaml.safe_dump(v, open(os.path.join(out, "view-pinned.yaml"), "w"), sort_keys=False)
t = yaml.safe_load(open(os.path.join(D, "DEMONSTRATION/run-1/packet/task_spec.yaml")))
t["view"] = os.path.join(out, "view-pinned.yaml")
t["queries"] = os.path.join(D, "DEMONSTRATION/run-1/task-inputs/demonstration-queries.yaml")
yaml.safe_dump(t, open(os.path.join(out, "task-pinned.yaml"), "w"), sort_keys=False)
print(os.path.join(out, "task-pinned.yaml"))
