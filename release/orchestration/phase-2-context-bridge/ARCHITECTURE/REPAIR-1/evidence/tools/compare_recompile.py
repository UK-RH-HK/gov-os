#!/usr/bin/env python3
"""BR-AR-0016: prove the recompile reproduces the run-1 packet: same item ids per section and same content hashes."""
import json
import os
import sys

root = os.popen("git rev-parse --show-toplevel").read().strip()
orig = json.load(open(os.path.join(root, "release/orchestration/phase-2-context-bridge/DEMONSTRATION/run-1/packet/manifest.json")))
cap = json.load(open(sys.argv[1]))


def rows(m):
    out = {}
    for k, v in m["sections"].items():
        for sb, sv in (v.get("subblocks") or {}).items():
            out[sb] = {i["item_id"]: i.get("content_sha256") for i in sv["items"]}
        out[k] = {i["item_id"]: i.get("content_sha256") for i in v.get("items", [])}
    return out


a, b = rows(orig), rows(cap["manifest"])
res = {k: {"run1_items": len(a.get(k, {})), "recompile_items": len(b.get(k, {})), "identical": a.get(k) == b.get(k)}
       for k in sorted(set(a) | set(b))}
allsame = all(v["identical"] for v in res.values())
print(json.dumps({"per_section": res, "all_sections_identical": allsame,
                  "items_total": sum(len(v) for v in a.values())}, indent=1, sort_keys=True))
sys.exit(0 if allsame else 1)
