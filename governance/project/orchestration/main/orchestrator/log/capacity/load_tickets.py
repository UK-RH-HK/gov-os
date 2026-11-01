"""CAPACITY-1, bigger machine: the Wave 2 tickets still to finish, with dependencies, paths and profiles.
Writes tickets.json beside it."""
import glob
import json
import os
import re
import sys

import yaml

ROOT = "/home/usain/Dynamic-Agentic-Engineering-OS"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tickets.json")

rows = {}
for p in glob.glob(ROOT + "/.tickets/*.md"):
    text = open(p, encoding="utf-8").read()
    parts = text.split("\n---", 1)
    head = parts[0].lstrip("-\n")
    try:
        fm = yaml.safe_load(head) or {}
    except yaml.YAMLError:
        continue
    tid = os.path.basename(p)[:-3]
    tags = [str(t) for t in (fm.get("tags") or [])]
    body = parts[1] if len(parts) > 1 else ""
    deps = [str(d) for d in (fm.get("depends_on") or [])] + [str(d) for d in (fm.get("deps") or [])]
    rows[tid] = {
        "id": tid, "wbs": str(fm.get("wbs_id") or fm.get("external-ref") or ""), "status": fm.get("status"),
        "profile": str(fm.get("profile") or "").upper(), "tags": tags, "priority": fm.get("priority"),
        "deps": sorted(set(deps)), "paths": [str(x) for x in (fm.get("allowed_paths") or [])],
        "role": fm.get("role"), "title": str(fm.get("title") or "")[:110],
        "body_after_act2": "after ACT 2" in body or "ACT 2" in " ".join(tags),
        "body_after_w2_11": "after W2-11 r1" in body or "W2-11 r1 merges" in body,
    }
json.dump(rows, open(OUT, "w"), indent=1)
w2 = [r for r in rows.values() if r["wbs"].startswith("W2-") and r["wbs"] != "W2-00"]
out_of = [r for r in w2 if any(t in r["tags"] for t in ("wave-3", "deferred", "withdrawn", "parked"))]
live = [r for r in w2 if r not in out_of]
by = {}
for r in live:
    by.setdefault(r["status"], []).append(r["wbs"])
print("W2 tickets", len(w2), "left the plan", len(out_of), "live", len(live))
for k, v in by.items():
    print(k, len(v))
