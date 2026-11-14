"""Measures what each running ticket lead and its workers use (DEC-942 item 2): for every `claude -p` process whose
settings name GOV_ROLE orchestrator and a GOV_TICKET, the summed RSS of its whole process tree (the lead, its
workers' sessions, their suites and helpers), plus the machine's figures. With --record, appends one JSON line per
call to log/lead-mem.jsonl (the reservation is the peak per lead over those lines; see --summary).
Usage: lead_mem.py [--record] | --summary"""
import json
import os
import re
import sys
import time

LOG = "/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/log/lead-mem.jsonl"


def procs():
    out = {}
    for pid in os.listdir("/proc"):
        if not pid.isdigit():
            continue
        try:
            with open("/proc/" + pid + "/stat") as f:
                stat = f.read()
            ppid = int(stat.rsplit(")", 1)[1].split()[1])
            rss = 0
            with open("/proc/" + pid + "/status") as f:
                for line in f:
                    if line.startswith("VmRSS:"):
                        rss = int(line.split()[1])
            with open("/proc/" + pid + "/cmdline", "rb") as f:
                cmd = f.read().replace(b"\0", b" ").decode("utf-8", "replace")
            out[int(pid)] = (ppid, rss, cmd)
        except (OSError, IndexError, ValueError):
            continue
    return out


def meminfo():
    vals = {}
    with open("/proc/meminfo") as f:
        for line in f:
            k, v = line.split(":", 1)
            vals[k] = int(v.split()[0])
    return vals


def snapshot():
    ps = procs()
    kids = {}
    for pid, (ppid, _, _) in ps.items():
        kids.setdefault(ppid, []).append(pid)
    leads = {}
    for pid, (_, _, cmd) in ps.items():
        if "claude" in cmd and '"GOV_ROLE":"orchestrator","GOV_TICKET":"' in cmd and " -p " in cmd + " ":
            ticket = re.search(r'"GOV_TICKET":"([^"]+)"', cmd).group(1)
            total, stack = 0, [pid]
            while stack:
                p = stack.pop()
                total += ps.get(p, (0, 0, ""))[1]
                stack += kids.get(p, [])
            leads[ticket] = total
    mi = meminfo()
    with open("/proc/loadavg") as f:
        load = [float(x) for x in f.read().split()[:3]]
    return {"t": time.strftime("%Y-%m-%dT%H:%M:%S"), "nproc": os.cpu_count(), "load": load,
            "mem_total_kb": mi["MemTotal"], "mem_available_kb": mi["MemAvailable"], "leads_kb": leads}


if __name__ != "__main__":
    pass
elif "--summary" in sys.argv:
    peaks, n = {}, 0
    try:
        with open(LOG) as f:
            for line in f:
                n += 1
                for t, kb in json.loads(line)["leads_kb"].items():
                    peaks[t] = max(peaks.get(t, 0), kb)
    except FileNotFoundError:
        pass
    print(json.dumps({"samples": n, "peak_kb_per_lead": peaks,
                      "max_peak_kb": max(peaks.values()) if peaks else None}))
else:
    s = snapshot()
    if "--record" in sys.argv:
        with open(LOG, "a") as f:
            f.write(json.dumps(s) + "\n")
    print(json.dumps(s))
