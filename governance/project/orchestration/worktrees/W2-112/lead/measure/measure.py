"""The lead's measure of W2-112 on the real GPU (KPIs 3, 5, 6). Never asks the shared Ollama servers anything.

Usage: python3 measure.py <worktree> <candidates.json> <out.json>
Phases: baseline; cold (1 search, the service starts); warm20 (20 concurrent); warm10 (10 concurrent);
private (one private reranker scores the 20 questions: the same answers, and a private reranker's memory);
stop (the service is ended with SIGTERM; its GPU memory released).
A sampler records every 0.25 s: GPU memory used, the compute apps, the RSS of every reranker process, used RAM.
"""
import json
import os
import signal
import subprocess
import sys
import threading
import time

NVSMI = "/usr/lib/wsl/lib/nvidia-smi"
ROOT, CANDS, OUT = sys.argv[1:4]
DRIVER = os.path.join(ROOT, ".gov-runtime/scratch/lead/measure/driver.py")
ENV = {**os.environ, "PYTHONPATH": os.path.join(ROOT, "src"), "TMPDIR": "/tmp/gov-os-lead-W2-112"}
ENV.pop("GOV_RERANK_ALLOW_CPU", None)
samples, phase, stop = [], ["baseline"], threading.Event()


def sh(*args):
    return subprocess.run(args, capture_output=True, text=True).stdout


def rerankers():
    rows = []
    for line in sh("ps", "-eo", "pid=,rss=,args=").splitlines():
        if "rerank_service.py" in line or "rerank_worker.py" in line:
            pid, rss, args = line.split(None, 2)
            rows.append({"pid": int(pid), "rss_kb": int(rss), "kind": "service" if "rerank_service" in args else
                         "worker", "tree": args.split("/src/gov/")[0].split()[-1]})
    return rows


def gpu():
    used, total = sh(NVSMI, "--query-gpu=memory.used,memory.total", "--format=csv,noheader,nounits").split(",")
    return int(used), int(total)


def ram_used():
    for line in sh("free", "-b").splitlines():
        if line.startswith("Mem:"):
            return int(line.split()[2])


def sampler():
    while not stop.is_set():
        used, total = gpu()
        samples.append({"t": time.time(), "phase": phase[0], "gpu_used_mib": used, "gpu_total_mib": total,
                        "ram_used": ram_used(), "rerankers": rerankers()})
        stop.wait(0.25)


def sessions(indices, extra=()):
    procs = [subprocess.Popen([sys.executable, DRIVER, CANDS, str(i), *extra], env=ENV, text=True,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE) for i in indices]
    out = []
    for p in procs:
        o, e = p.communicate(timeout=600)
        out.append(json.loads(o.strip().splitlines()[-1]) if o.strip() else {"error": e[-600:]})
    return out


def main():
    record = {"start": time.time(), "slots": sh("bash", "-c", "fuser -v /tmp/gov-os-rerank-gpu-*.lock 2>&1"),
              "compute_apps_before": sh(NVSMI, "--query-compute-apps=pid,used_memory", "--format=csv"),
              "rerankers_before": rerankers(), "gpu_before": gpu(), "ram_before": ram_used()}
    threading.Thread(target=sampler, daemon=True).start()
    time.sleep(2)
    for name, indices in (("cold", [0]), ("warm20", range(20)), ("warm10", range(10))):
        phase[0] = name
        t = time.time()
        record[name] = {"sessions": sessions(indices), "wall_s": time.time() - t}
        time.sleep(1)
    record["compute_apps_service"] = sh(NVSMI, "--query-compute-apps=pid,used_memory", "--format=csv")
    phase[0] = "private"
    record["private"] = sessions([0], ("private",))[0]
    time.sleep(1)
    phase[0] = "stop"
    ours = [r for r in rerankers() if r["kind"] == "service" and r["tree"].startswith(ROOT)]
    for r in ours:
        os.kill(r["pid"], signal.SIGTERM)
    t = time.time()
    while time.time() - t < 30 and any(r["pid"] in {x["pid"] for x in rerankers()} for r in ours):
        time.sleep(0.5)
    time.sleep(3)
    record["stopped"] = {"pids": [r["pid"] for r in ours], "still_running": [r["pid"] for r in rerankers()
                         if r["pid"] in {o["pid"] for o in ours}], "gpu_after": gpu(),
                         "compute_apps_after": sh(NVSMI, "--query-compute-apps=pid,used_memory", "--format=csv"),
                         "socket_left": os.path.exists(os.path.expanduser("~/.cache/gov-os/rerank.sock"))}
    stop.set()
    time.sleep(0.5)
    record["samples"] = samples
    json.dump(record, open(OUT, "w"))
    print("written", OUT, len(samples), "samples")


if __name__ == "__main__":
    main()
