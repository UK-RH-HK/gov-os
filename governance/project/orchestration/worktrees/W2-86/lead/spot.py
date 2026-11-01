"""W2-86 spot check (as W2-61's spot-q17): the pinned gov's own retrieve in a clone for one visible question; prints
the rank, path and lines of each item, and where the question's source paths appear. Scores and paths only.
usage: python3 spot.py <clone> <qNN> <out json>"""
import json
import os
import subprocess
import sys

import yaml

clone, qid, out = sys.argv[1], sys.argv[2], sys.argv[3]
question = yaml.safe_load(open(f"/home/usain/gov-os-runs/W2-86/measure/fixtures/evaluation/memory-retrieval/visible/{qid}.yaml"))
env = {k: v for k, v in os.environ.items() if k not in ("PYTHONPATH", "GOV_TICKET")}
gov = sys.argv[4] if len(sys.argv) > 4 else "/home/usain/.local/bin/gov"
run = subprocess.run([gov, "retrieve", question["question"], "--json"], cwd=clone, env=env,
                     capture_output=True, text=True)
open(out, "w").write(run.stdout)
data = json.loads(run.stdout[run.stdout.find("{"):])
wanted = sorted({piece["path"] for alternative in question["sources"] for piece in
                 (alternative if isinstance(alternative, list) else [alternative])})
print("exit", run.returncode, "keys", list(data))
result = data.get("result", data)
items = None
for key in ("evidence", "items", "bundle", "results"):
    if isinstance(result, dict) and isinstance(result.get(key), list):
        items = result[key]
        break
if items is None:
    print("result keys", list(result) if isinstance(result, dict) else type(result))
    sys.exit(0)
print("items", len(items), "item keys", list(items[0]) if items else None)
for rank, item in enumerate(items, 1):
    path = item.get("path") or (item.get("citation") or {}).get("path")
    mark = "  <== source" if path in wanted else ""
    print(rank, path, item.get("start_line"), item.get("end_line"), item.get("route") or item.get("routes"), mark)
print("source paths:", wanted)
