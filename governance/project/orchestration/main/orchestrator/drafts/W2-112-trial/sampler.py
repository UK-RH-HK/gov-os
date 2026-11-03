#!/usr/bin/env python3
"""W2-112 trial sampler: every 0.25 s, GPU memory used, reranker processes and RSS, GPU slot lock holders.

usage: sampler.py <out.jsonl> <stop-file>
Lock holders are read from /proc/locks (the kernel's own record of who holds each flock), matched to the
/tmp/gov-os-rerank-gpu-*.lock files by device and inode.
"""
import glob
import json
import os
import subprocess
import sys
import time

out_path, stop = sys.argv[1], sys.argv[2]


def gpu_used():
    try:
        r = subprocess.run(["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"],
                           capture_output=True, text=True, timeout=5)
        return int(r.stdout.strip().splitlines()[0])
    except Exception as e:  # noqa: BLE001
        return None


def procs():
    found = []
    for d in glob.glob("/proc/[0-9]*"):
        try:
            with open(d + "/cmdline", "rb") as f:
                cmd = f.read().split(b"\0")
        except OSError:
            continue
        kind = None
        for a in cmd:
            if a.endswith(b"rerank_service.py"):
                kind = "service"
            elif a.endswith(b"rerank_worker.py"):
                kind = "worker"
        if not kind:
            continue
        rss = None
        try:
            with open(d + "/status") as f:
                for line in f:
                    if line.startswith("VmRSS:"):
                        rss = int(line.split()[1])
        except OSError:
            continue
        found.append({"pid": int(d[6:]), "kind": kind, "rss_kb": rss})
    return found


def locks():
    files = {}
    for p in sorted(glob.glob("/tmp/gov-os-rerank-gpu-*.lock")):
        try:
            st = os.stat(p)
        except OSError:
            continue
        files[(os.major(st.st_dev), os.minor(st.st_dev), st.st_ino)] = os.path.basename(p)
    held = {name: [] for name in files.values()}
    try:
        with open("/proc/locks") as f:
            for line in f:
                parts = line.split()
                if "->" in parts:
                    continue
                # n: FLOCK ADVISORY WRITE pid maj:min:ino start end
                if len(parts) < 6 or parts[1] != "FLOCK":
                    continue
                pid = int(parts[4])
                maj, mnr, ino = parts[5].split(":")
                key = (int(maj, 16), int(mnr, 16), int(ino))
                if key in files:
                    held[files[key]].append(pid)
    except OSError:
        pass
    return held


with open(out_path, "a", buffering=1) as out:
    while not os.path.exists(stop):
        t0 = time.time()
        out.write(json.dumps({"t": round(t0, 3), "gpu_mib": gpu_used(), "procs": procs(), "locks": locks()}) + "\n")
        dt = time.time() - t0
        time.sleep(max(0.0, 0.25 - dt))
