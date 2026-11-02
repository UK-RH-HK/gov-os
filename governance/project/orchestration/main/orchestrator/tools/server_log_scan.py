#!/usr/bin/env python3
"""Every crash or error in the embedding servers' logs over a window, for the morning package (owner, DEC-1030
item 3). Read-only. Usage: server_log_scan.py [--since "YYYY-MM-DD HH:MM"] [--until "YYYY-MM-DD HH:MM"] [--json]
(default: from yesterday 21:00 to now, local time). It reports, per server: CUDA errors and out-of-memory lines, model
loads with their layers on the GPU (a 0-layer load where the GPU is expected is an alert), runner exits and panics,
level=ERROR lines, and the /api/embed requests with their failures (status 4xx/5xx) and their latency (p50, p95, over
30 s, over 120 s). Lines without their own time take the time of the last timed line before them."""
import json
import re
import sys
from datetime import datetime, timedelta

LOGS = {"shared": ("/home/usain/.ollama/serve-11434.log", True), "query": ("/home/usain/.ollama/serve-11435.log", False)}
GIN = re.compile(r"\[GIN\] (\d{4}/\d\d/\d\d - \d\d:\d\d:\d\d) \| (\d+) \|\s+([\d.]+)(µs|ms|s|m[\d.]+s)\s*\|.*\"(\S+)\"")
TS = re.compile(r"time=(\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d)")
EVENTS = [("cuda_error", re.compile(r"CUDA error|cudaMalloc failed|out of memory", re.I)),
          ("load", re.compile(r"offloaded (\d+)/(\d+) layers to GPU")),
          ("runner_exit", re.compile(r"llama runner (?:process )?(?:has )?terminated|exit status|signal: ", re.I)),
          ("panic", re.compile(r"\bpanic\b|SIGSEGV|segmentation fault", re.I)),
          ("error", re.compile(r"level=ERROR"))]


def secs(v, unit):
    if unit == "µs":
        return float(v) / 1e6
    if unit == "ms":
        return float(v) / 1e3
    if unit == "s":
        return float(v)
    m = re.match(r"m([\d.]+)s", unit)
    return float(v) * 60 + float(m.group(1))


def scan(path, gpu_expected, since, until):
    out = {"embed": [], "embed_fail": 0, "events": {k: [] for k, _ in EVENTS}, "alerts": []}
    t = None
    try:
        handle = open(path, errors="replace")
    except OSError as exc:
        return {"unreadable": str(exc)}
    with handle:
        for line in handle:
            g = GIN.search(line)
            if g:
                t = datetime.strptime(g.group(1), "%Y/%m/%d - %H:%M:%S")
            else:
                m = TS.search(line)
                if m:
                    t = datetime.strptime(m.group(1), "%Y-%m-%dT%H:%M:%S")  # the log's own clock (UTC on WSL)
            if t is None or not (since <= t <= until):
                continue
            if g and g.group(5).startswith("/api/embed"):
                out["embed"].append(secs(g.group(3), g.group(4)))
                out["embed_fail"] += int(g.group(2)) >= 400
                continue
            for kind, pat in EVENTS:
                m = pat.search(line)
                if m:
                    out["events"][kind].append(f"{t:%F %T} {line.strip()[:200]}")
                    if kind == "cuda_error":
                        out["alerts"].append(f"{t:%F %T} CUDA error")
                    if kind == "load" and gpu_expected and m.group(1) == "0":
                        out["alerts"].append(f"{t:%F %T} model loaded with 0/{m.group(2)} layers on the GPU")
                    break
    lat = sorted(out.pop("embed"))
    q = (lambda f: round(lat[min(len(lat) - 1, int(f * len(lat)))], 2) if lat else None)
    out["embed_requests"] = {"count": len(lat), "failed": out.pop("embed_fail"), "p50_s": q(0.5), "p95_s": q(0.95),
                             "over_30_s": sum(x > 30 for x in lat), "over_120_s": sum(x > 120 for x in lat)}
    out["counts"] = {k: len(v) for k, v in out["events"].items()}
    return out


def main():
    args = sys.argv[1:]
    now = datetime.now()
    since = (now - timedelta(days=1)).replace(hour=21, minute=0, second=0, microsecond=0)
    until = now
    if "--since" in args:
        since = datetime.strptime(args[args.index("--since") + 1], "%Y-%m-%d %H:%M")
    if "--until" in args:
        until = datetime.strptime(args[args.index("--until") + 1], "%Y-%m-%d %H:%M")
    report = {"since": f"{since:%F %T}", "until": f"{until:%F %T}",
              "servers": {name: scan(path, gpu, since, until) for name, (path, gpu) in LOGS.items()}}
    if "--json" in args:
        print(json.dumps(report, indent=1))
        return 0
    print(f"Embedding servers' logs, {report['since']} to {report['until']} (the logs' own clock)")
    for name, r in report["servers"].items():
        if "unreadable" in r:
            print(f"- {name}: unreadable ({r['unreadable']})")
            continue
        e = r["embed_requests"]
        print(f"- {name}: {e['count']} embed requests, {e['failed']} failed, p50 {e['p50_s']} s, p95 {e['p95_s']} s, "
              f"{e['over_30_s']} over 30 s, {e['over_120_s']} over 120 s; events {r['counts']}")
        for a in r["alerts"]:
            print(f"  ALERT {a}")
        for line in r["events"]["load"][-3:]:
            print(f"  load: {line}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
