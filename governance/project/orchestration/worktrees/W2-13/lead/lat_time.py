"""lat_time.py <label>: time fusion.search warm on both lat-tiers, as W2-13's real-model latency case does.

Three warm-up questions per tier, then each dev question of that tier's programme, one process, refresh=False,
limit None. Prints one JSON line: label, gov file, per-question seconds, p95 (nearest rank), and the three slowest.
"""
import json
import math
import os
import sys
import time
from pathlib import Path

import yaml

import gov
from gov.retrieval import fusion

DEV_TIERS = Path(os.environ.get("GOV_DEV_TIERS") or "~/gov-os-workbench/synthetic").expanduser()
TIERS = {"A": "a-dev", "B": "b-dev"}
WARM_UP = ("how is the configuration loaded", "where are errors logged", "which tests cover the parser")
queries = yaml.safe_load((DEV_TIERS / "dev-queryset.yaml").read_text(encoding="utf-8"))["queries"]
seconds = []
for programme, tier in TIERS.items():
    root = Path("/tmp/gov-os-lead-W2-13/lat-tiers") / tier
    for text in WARM_UP:
        fusion.search(root, text, None, refresh=False)
    for query in queries:
        if query.get("programme") != programme:
            continue
        start = time.perf_counter()
        fusion.search(root, query["query"], None, refresh=False)
        seconds.append(time.perf_counter() - start)
ordered = sorted(seconds)
p95 = ordered[max(0, math.ceil(0.95 * len(ordered)) - 1)]
print(json.dumps({"label": sys.argv[1], "gov": gov.__file__, "n": len(seconds), "p95": round(p95, 3),
                  "median": round(ordered[len(ordered) // 2], 3), "slowest": [round(v, 3) for v in ordered[-3:]],
                  "load": open("/proc/loadavg").read().split()[:3]}))
