#!/usr/bin/env python3
"""One timed search: `gov retrieve "<question>" --json` in the integration store, one JSON line appended.

usage: search.py <phase> <qid e.g. q03> <out.jsonl>
"""
import json
import os
import subprocess
import sys
import time

import yaml

phase, qid, out_path = sys.argv[1], sys.argv[2], sys.argv[3]
STORE = "/home/usain/gov-os-worktrees/W2-00-store"
GOV = os.path.expanduser("~/.local/bin/gov")
q = yaml.safe_load(open(f"{STORE}/fixtures/evaluation/memory-retrieval/visible/{qid}.yaml"))["question"]
start = time.time()
r = subprocess.run([GOV, "retrieve", str(q), "--json"], cwd=STORE, capture_output=True, text=True)
wall = time.time() - start
line = {"phase": phase, "qid": qid, "start": round(start, 3), "wall_s": round(wall, 3), "rc": r.returncode}
try:
    doc = json.loads(r.stdout)
    res = doc.get("result", doc)
    line["rerank"] = res.get("rerank")
    line["reranked"] = (res.get("merge") or {}).get("reranked")
    line["ok"] = doc.get("ok")
except Exception as e:  # noqa: BLE001
    line["parse_error"] = repr(e)
    line["stdout_tail"] = r.stdout[-400:]
if r.returncode != 0 or "parse_error" in line:
    line["stderr_tail"] = r.stderr[-600:]
with open(out_path, "a") as f:
    f.write(json.dumps(line) + "\n")
