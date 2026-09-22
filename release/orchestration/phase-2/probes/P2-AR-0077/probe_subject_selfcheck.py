#!/usr/bin/env python3
"""P2-AR-0077 self-check: my Python `review_subject` equals the product's own.

Every later probe binds its review with my reimplementation. If it disagreed with
`gov_runtime::tools::review_subject`, every "conforming install" below would gate
for the wrong reason and every negative control would be worthless. So this runs
first and is the gate on all of it.
"""
import json
from harness4 import Proj, descriptor, review_subject, install, save

p = Proj("subjchk")
p.ok(["init", "--name", "subjchk", "--alias", "a-subjchk"])
p.commit_all("after init")

rows = []
for tag, over in [
    ("plain", {}),
    ("cmd", {"install_command": ["cp", "a", "b"], "health_check": {"kind": "command", "command": ["curl", "-sS", "https://pypi.org/simple/"], "expect_exit": 0}}),
    ("pins", {"pinned_files": [{"path": "x.sh", "sha256": "ab" * 32}], "cost_usd": 3}),
    ("unicode", {"name": "p77-éå中"}),
]:
    d = descriptor("RPT-NONE", **over)
    d.pop("security_review_record")
    e = install(p, d, f"subj-{tag}", execute=False)
    r = e.get("result") or (e.get("error") or {}).get("details") or {}
    got = ((r.get("change_class") or {}).get("security_review") or {}).get("review_subject_sha256")
    mine = review_subject(d)
    rows.append({"case": tag, "product": got, "mine": mine, "match": got == mine})
    print(rows[-1])

save("subject_selfcheck", rows)
assert all(r["match"] for r in rows), "review_subject reimplementation DIVERGES -- stop"
print("ALL MATCH")
