#!/usr/bin/env python3
"""One working hour of the embedding load (owner, DEC-1028 item 5 e): every INTERVAL s, each embedding server's
processes (the `ollama serve` and its llama-server runners) and any reranker: CPU (from /proc deltas, in cores) and
RSS; the GPU's use and memory; and every client connection to ports 11434 and 11435, attributed to who holds it
(a ticket's worktree, the merge queue, the nightly, a close, the dispatcher, other). At the end it reads the two
servers' logs for the window: /api/embed requests (count, latency p50/p95/max, how many over 120 s) and the runners'
task count (one per input text). Read-only. Usage: lb_measure.py [seconds] [interval] > out.jsonl; summary on stderr
and in <out>.summary.json when OUT is set."""
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

DUR = int(sys.argv[1]) if len(sys.argv) > 1 else 3600
INTERVAL = int(sys.argv[2]) if len(sys.argv) > 2 else 15
OUT = os.environ.get("OUT")
PORTS = {11434: "shared", 11435: "query"}
LOGS = {"shared": "/home/usain/.ollama/serve-11434.log", "query": "/home/usain/.ollama/serve-11435.log"}
TICK = os.sysconf("SC_CLK_TCK")


def procs():
    out = {}
    for d in Path("/proc").iterdir():
        if not d.name.isdigit():
            continue
        try:
            cmd = (d / "cmdline").read_bytes().replace(b"\0", b" ").decode(errors="replace").strip()
            stat = (d / "stat").read_text().rsplit(")", 1)[1].split()
            ppid, ut, st = int(stat[1]), int(stat[11]), int(stat[12])
            rss = int((d / "statm").read_text().split()[1]) * os.sysconf("SC_PAGE_SIZE")
            env = (d / "environ").read_bytes().decode(errors="replace") if "ollama" in cmd else ""
        except (OSError, IndexError, ValueError):
            continue
        out[int(d.name)] = {"cmd": cmd, "ppid": ppid, "ticks": ut + st, "rss": rss, "env": env}
    return out


def server_of(pid, ps):
    """'shared' or 'query' for an ollama serve or a runner under one; 'reranker' for a reranker; else None."""
    p = ps.get(pid)
    if not p:
        return None
    if "rerank" in p["cmd"].lower():
        return "reranker"
    if p["cmd"].endswith("ollama serve") or "/ollama serve" in p["cmd"]:
        return "query" if "OLLAMA_HOST=127.0.0.1:11435" in p["env"] else "shared"
    if "llama-server" in p["cmd"]:
        return server_of(p["ppid"], ps)
    return None


def label(pid):
    try:
        cwd = os.readlink(f"/proc/{pid}/cwd")
        cmd = Path(f"/proc/{pid}/cmdline").read_bytes().replace(b"\0", b" ").decode(errors="replace")
    except OSError:
        return "gone"
    m = re.search(r"gov-os-worktrees/(W2-[0-9a-z]+(?:-tests)?)", cwd)
    if m:
        return "worktree " + m.group(1)
    if "merge-queue" in cwd:
        return "merge queue"
    if "/nightly/" in cwd or "nightly" in cmd:
        return "nightly"
    if "/close/" in cwd:
        return "close"
    if "dispatch" in cwd or "dispatcher" in cmd:
        return "dispatcher"
    if "pytest-of-usain" in cwd or "/tmp/" in cwd:
        return "test temp " + cwd[:60]
    return "other " + cwd[:60]


def clients():
    try:
        text = subprocess.run(["ss", "-tnp"], capture_output=True, text=True, timeout=10).stdout
    except Exception:  # noqa: BLE001
        return {}
    seen = {}
    for line in text.splitlines():
        parts = line.split()
        if len(parts) < 5:
            continue
        peer = parts[4]
        port = int(peer.rsplit(":", 1)[1]) if peer.rsplit(":", 1)[-1].isdigit() else 0
        if port not in PORTS:
            continue
        m = re.search(r"pid=(\d+)", line)
        who = label(int(m.group(1))) if m else "unknown"
        key = f"{PORTS[port]}|{who}"
        seen[key] = seen.get(key, 0) + 1
    return seen


def gpu():
    try:
        r = subprocess.run(["nvidia-smi", "--query-gpu=utilization.gpu,memory.used", "--format=csv,noheader,nounits"],
                           capture_output=True, text=True, timeout=10).stdout.strip().split(",")
        return {"util": int(r[0]), "mem_mib": int(r[1])}
    except Exception:  # noqa: BLE001
        return None


def log_window(path, start, end):
    reqs, tasks = [], 0
    pat = re.compile(r"\[GIN\] (\d{4}/\d\d/\d\d - \d\d:\d\d:\d\d) \| (\d+) \|\s+([\d.]+)(µs|ms|s|m[\d.]*s?)\s*\|.*\"(/api/embed\w*)\"")
    try:
        for line in open(path, errors="replace"):
            if "task.n_tokens" in line:
                tasks += 1
            m = pat.search(line)
            if not m:
                continue
            t = datetime.strptime(m.group(1), "%Y/%m/%d - %H:%M:%S").timestamp()
            if not (start <= t <= end):
                continue
            val, unit = float(m.group(3)), m.group(4)
            secs = val / 1e6 if unit == "µs" else val / 1e3 if unit == "ms" else val
            reqs.append((secs, int(m.group(2))))
    except OSError:
        return None
    lat = sorted(r[0] for r in reqs)
    q = (lambda f: round(lat[min(len(lat) - 1, int(f * len(lat)))], 2) if lat else None)
    return {"embed_requests": len(lat), "errors": sum(1 for r in reqs if r[1] >= 400), "p50_s": q(0.5),
            "p95_s": q(0.95), "max_s": round(lat[-1], 2) if lat else None, "over_120_s": sum(1 for x in lat if x > 120),
            "runner_tasks_in_whole_log": tasks}


def main():
    start = time.time()
    prev = {pid: p["ticks"] for pid, p in procs().items()}
    prev_t = start
    agg = {}
    n = 0
    while time.time() - start < DUR:
        time.sleep(INTERVAL)
        ps = procs()
        now = time.time()
        rec = {"at": datetime.now().strftime("%F %T"), "servers": {}, "gpu": gpu(), "clients": clients(),
               "load": os.getloadavg()[0]}
        for pid, p in ps.items():
            s = server_of(pid, ps)
            if not s:
                continue
            cores = (p["ticks"] - prev.get(pid, p["ticks"])) / TICK / (now - prev_t)
            r = rec["servers"].setdefault(s, {"cores": 0.0, "rss_mb": 0, "procs": 0})
            r["cores"] = round(r["cores"] + cores, 2)
            r["rss_mb"] += p["rss"] // 2**20
            r["procs"] += 1
        prev = {pid: p["ticks"] for pid, p in ps.items()}
        prev_t = now
        print(json.dumps(rec), flush=True)
        n += 1
        for s, r in rec["servers"].items():
            a = agg.setdefault(s, {"cores": [], "rss_mb": []})
            a["cores"].append(r["cores"])
            a["rss_mb"].append(r["rss_mb"])
        for k, v in rec["clients"].items():
            agg.setdefault("clients", {}).setdefault(k, 0)
            agg["clients"][k] += v
        if rec["gpu"]:
            agg.setdefault("gpu_util", []).append(rec["gpu"]["util"])
    end = time.time()
    summary = {"from": datetime.fromtimestamp(start).strftime("%F %T"), "to": datetime.fromtimestamp(end).strftime("%F %T"),
               "samples": n, "interval_s": INTERVAL}
    for s in ("shared", "query", "reranker"):
        if s in agg:
            c = sorted(agg[s]["cores"])
            summary[s] = {"cores_mean": round(sum(c) / len(c), 2), "cores_p95": c[int(0.95 * (len(c) - 1))],
                          "rss_mb_max": max(agg[s]["rss_mb"])}
    if "gpu_util" in agg:
        g = agg["gpu_util"]
        summary["gpu_util_mean"] = round(sum(g) / len(g), 1)
    summary["client_connection_samples"] = dict(sorted(agg.get("clients", {}).items(), key=lambda kv: -kv[1]))
    for s, path in LOGS.items():
        summary.setdefault(s, {})["log"] = log_window(path, start, end)
    text = json.dumps(summary, indent=1)
    print(text, file=sys.stderr)
    if OUT:
        Path(OUT + ".summary.json").write_text(text)


if __name__ == "__main__":
    main()
