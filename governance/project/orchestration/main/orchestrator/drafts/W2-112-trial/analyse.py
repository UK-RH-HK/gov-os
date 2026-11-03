#!/usr/bin/env python3
"""W2-112 trial: figures from samples.jsonl and searches.jsonl. usage: analyse.py <folder>"""
import json
import statistics
import sys
from collections import defaultdict

D = sys.argv[1]
SERVICE = 356621
WATCHER = 8416


def pct(xs, p):
    xs = sorted(xs)
    if not xs:
        return None
    k = (len(xs) - 1) * p / 100
    lo, hi = int(k), min(int(k) + 1, len(xs) - 1)
    return round(xs[lo] + (xs[hi] - xs[lo]) * (k - lo), 3)


searches = [json.loads(l) for l in open(f"{D}/searches.jsonl")]
by = defaultdict(list)
for s in searches:
    group = s["phase"].split("-")[0]
    by[group].append(s)
print("== searches")
for g, ss in by.items():
    w = [s["wall_s"] for s in ss]
    kinds = defaultdict(int)
    for s in ss:
        r = s.get("rerank") or {}
        kinds[(r.get("by"), r.get("device"), r.get("reason"), s.get("reranked"), s["rc"])] += 1
    print(f"{g}: n={len(ss)} p50={pct(w, 50)} p95={pct(w, 95)} max={max(w)} min={min(w)} mean={round(statistics.mean(w), 3)}"
          f" outcomes={dict(kinds)}")

samples = [json.loads(l) for l in open(f"{D}/samples.jsonl")]
print("== samples", len(samples), "from", samples[0]["t"], "to", samples[-1]["t"],
      "span_s", round(samples[-1]["t"] - samples[0]["t"], 1))
gaps = [b["t"] - a["t"] for a, b in zip(samples, samples[1:])]
print("sample gap p50", pct(gaps, 50), "max", round(max(gaps), 3))
gpu = [s["gpu_mib"] for s in samples if s["gpu_mib"] is not None]
peak = max(samples, key=lambda s: s["gpu_mib"] or 0)
print("gpu MiB min", min(gpu), "p50", pct(gpu, 50), "max", max(gpu), "at", peak["t"], "missing", len(samples) - len(gpu))
lock_bad = [s for s in samples if s["locks"].get("gov-os-rerank-gpu-0.lock") != [SERVICE]
            or s["locks"].get("gov-os-rerank-gpu-1.lock") != [WATCHER]]
print("samples where slot0 != [service] or slot1 != [watcher]:", len(lock_bad))
for s in lock_bad[:10]:
    print("  ", s["t"], s["locks"])
holders = defaultdict(set)
for s in samples:
    for k, v in s["locks"].items():
        holders[k].update(v)
print("all holders seen:", {k: sorted(v) for k, v in holders.items()})
svc_rss = [p["rss_kb"] for s in samples for p in s["procs"] if p["kind"] == "service"]
print("service RSS KiB min", min(svc_rss), "max", max(svc_rss), "GiB max", round(max(svc_rss) / 1048576, 3))
pids = defaultdict(set)
for s in samples:
    for p in s["procs"]:
        pids[p["kind"]].add(p["pid"])
print("reranker processes seen:", {k: sorted(v) for k, v in pids.items()})
no_service = [s["t"] for s in samples if not any(p["kind"] == "service" and p["pid"] == SERVICE for p in s["procs"])]
print("samples without the service pid:", len(no_service))
