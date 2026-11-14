"""Measures what each running ticket lead and its workers use (DEC-942 item 2): for every `claude -p` process whose
settings name GOV_ROLE orchestrator and a GOV_TICKET, the summed RSS of its whole process tree (the lead, its
workers' sessions, their suites and helpers), plus the machine's figures. With --record, appends one JSON line per
call to log/lead-mem.jsonl (the reservation is the peak per lead over those lines; see --summary).
Since 2026-11-14 (DEC-1149 (4), the two peaks re-measured from this ledger by 11-19) each line also holds "verify_kb":
the process-tree RSS of each heavy-slot run (its flock root in heavy_slot.sh, keyed "<slot>:<pid>"), and "rebuild_kb":
the same for a slot run whose tree runs `gov rebuild`, and for a `gov rebuild` outside any slot (keyed "-:<pid>"). --summary adds their sample counts, maximum and p95.
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


REBUILD = re.compile(r"(^|/)gov\s+rebuild\b|-m gov\.cli\.main\s+rebuild\b")
SLOT_ROOT = re.compile(r"^flock .*gov-os-heavy-slot-(\d+)\.lock")


def tree(kids, pid):
    out, stack = [], [pid]
    while stack:
        p = stack.pop()
        out.append(p)
        stack += kids.get(p, [])
    return out


def heavy(ps, kids):
    """Each heavy-slot run (its flock root, heavy_slot.sh) with its tree's RSS, as a verification run or, when its tree
    runs `gov rebuild`, a rebuild; plus each `gov rebuild` outside any slot. Keys are "<slot>:<pid>" or "-:<pid>"."""
    verify, rebuild, in_slot = {}, {}, set()
    for pid, (_, _, cmd) in ps.items():
        m = SLOT_ROOT.match(cmd)
        if not m:
            continue
        members = tree(kids, pid)
        in_slot.update(members)
        kb = sum(ps.get(p, (0, 0, ""))[1] for p in members)
        is_rebuild = any(REBUILD.search(ps.get(p, (0, 0, ""))[2]) for p in members)
        (rebuild if is_rebuild else verify)["%s:%d" % (m.group(1), pid)] = kb
    for pid, (ppid, _, cmd) in ps.items():
        if pid in in_slot or not REBUILD.search(cmd) or REBUILD.search(ps.get(ppid, (0, 0, ""))[2]):
            continue
        members = tree(kids, pid)
        if in_slot.intersection(members):
            continue  # a wrapper around a slot run, counted there
        rebuild["-:%d" % pid] = sum(ps.get(p, (0, 0, ""))[1] for p in members)
    return verify, rebuild


MIN_RUN_KB = 102400  # a run whose peak stays under 100 MB is a wrapper waiting for its slot, not a measured run


def p95(xs):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(round(0.95 * (len(xs) - 1))))] if xs else None


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
    verify, rebuild = heavy(ps, kids)
    return {"t": time.strftime("%Y-%m-%dT%H:%M:%S"), "nproc": os.cpu_count(), "load": load,
            "mem_total_kb": mi["MemTotal"], "mem_available_kb": mi["MemAvailable"], "leads_kb": leads,
            "verify_kb": verify, "rebuild_kb": rebuild}


if __name__ != "__main__":
    pass
elif "--summary" in sys.argv:
    peaks, n = {}, 0
    runs = {"verify_kb": {}, "rebuild_kb": {}}  # per run (its key), the run's peak over its samples
    try:
        with open(LOG) as f:
            for line in f:
                n += 1
                d = json.loads(line)
                for t, kb in d["leads_kb"].items():
                    peaks[t] = max(peaks.get(t, 0), kb)
                for k in runs:
                    for rid, kb in d.get(k, {}).items():
                        runs[k][rid] = max(runs[k].get(rid, 0), kb)
    except FileNotFoundError:
        pass
    out = {"samples": n, "peak_kb_per_lead": peaks, "max_peak_kb": max(peaks.values()) if peaks else None}
    for k, v in runs.items():
        v = [kb for kb in v.values() if kb >= MIN_RUN_KB]
        out[k.replace("_kb", "_runs")] = {"runs": len(v), "max_kb": max(v) if v else None, "p95_kb": p95(v)}
    print(json.dumps(out))
else:
    s = snapshot()
    if "--record" in sys.argv:
        with open(LOG, "a") as f:
            f.write(json.dumps(s) + "\n")
    print(json.dumps(s))
