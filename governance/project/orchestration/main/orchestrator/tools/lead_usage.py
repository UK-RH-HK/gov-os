#!/usr/bin/env python3
"""Measure what each running lead uses, for the resource gate (owner's parallelism rule, DEC-847).

Every INTERVAL seconds, for each folder under ~/gov-os-worktrees/ and for the main tree, sum the resident
memory and CPU time of this user's processes whose working folder is inside it, and append one JSON line:
{"t": ..., "load1": ..., "mem_available_kb": ..., "trees": {"W2-59": {"procs": n, "rss_kb": ..., "cpu_pct": ...}}}.
Reads /proc only; writes only the log file named on the command line.

    python3 lead_usage.py <log.jsonl> [interval_s]
    python3 lead_usage.py --summary <log.jsonl>
"""
import json
import os
import sys
import time
from pathlib import Path

HOME = Path.home()
WORKTREES = HOME / "gov-os-worktrees"
MAIN = HOME / "Dynamic-Agentic-Engineering-OS"
TICK = os.sysconf("SC_CLK_TCK")


def tree_of(cwd: str) -> str | None:
    if cwd.startswith(str(WORKTREES) + "/"):
        return cwd[len(str(WORKTREES)) + 1:].split("/", 1)[0]
    if cwd == str(MAIN) or cwd.startswith(str(MAIN) + "/"):
        return "main"
    return None


def sample() -> dict:
    uid = os.getuid()
    out: dict[str, dict] = {}
    for pid in os.listdir("/proc"):
        if not pid.isdigit():
            continue
        try:
            if os.stat(f"/proc/{pid}").st_uid != uid:
                continue
            tree = tree_of(os.readlink(f"/proc/{pid}/cwd"))
            if tree is None:
                continue
            fields = open(f"/proc/{pid}/stat").read().rsplit(")", 1)[1].split()
            cpu = (int(fields[11]) + int(fields[12])) / TICK
            rss = 0
            for line in open(f"/proc/{pid}/status"):
                if line.startswith("VmRSS:"):
                    rss = int(line.split()[1])
        except (OSError, ValueError, IndexError):
            continue
        entry = out.setdefault(tree, {"procs": 0, "rss_kb": 0, "cpu_s": 0.0})
        entry["procs"] += 1
        entry["rss_kb"] += rss
        entry["cpu_s"] += cpu
    return out


def meminfo() -> int:
    for line in open("/proc/meminfo"):
        if line.startswith("MemAvailable:"):
            return int(line.split()[1])
    return 0


def run(log: str, interval: float) -> None:
    previous = sample()
    while True:
        time.sleep(interval)
        current = sample()
        trees = {}
        for tree, entry in current.items():
            before = previous.get(tree, {}).get("cpu_s", entry["cpu_s"])
            trees[tree] = {"procs": entry["procs"], "rss_kb": entry["rss_kb"],
                           "cpu_pct": round(max(0.0, entry["cpu_s"] - before) / interval * 100, 1)}
        previous = current
        record = {"t": time.strftime("%Y-%m-%dT%H:%M:%S"), "load1": float(open("/proc/loadavg").read().split()[0]),
                  "mem_available_kb": meminfo(), "trees": trees}
        with open(log, "a") as handle:
            handle.write(json.dumps(record) + "\n")


def summary(log: str) -> None:
    peak: dict[str, dict] = {}
    for line in open(log):
        record = json.loads(line)
        for tree, entry in record["trees"].items():
            p = peak.setdefault(tree, {"samples": 0, "peak_rss_kb": 0, "peak_cpu_pct": 0.0, "sum_cpu_pct": 0.0})
            p["samples"] += 1
            p["peak_rss_kb"] = max(p["peak_rss_kb"], entry["rss_kb"])
            p["peak_cpu_pct"] = max(p["peak_cpu_pct"], entry["cpu_pct"])
            p["sum_cpu_pct"] += entry["cpu_pct"]
    for tree, p in sorted(peak.items()):
        print(f"{tree}: samples {p['samples']}, peak RSS {p['peak_rss_kb'] / 1048576:.2f} GiB, "
              f"peak CPU {p['peak_cpu_pct'] / 100:.1f} cores, mean CPU {p['sum_cpu_pct'] / p['samples'] / 100:.1f} cores")


if __name__ == "__main__":
    if sys.argv[1] == "--summary":
        summary(sys.argv[2])
    else:
        run(sys.argv[1], float(sys.argv[2]) if len(sys.argv) > 2 else 30.0)
