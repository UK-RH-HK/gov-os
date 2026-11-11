#!/usr/bin/env python3
"""A continuous memory sampler for the lead ledger (the owner's order, chat 2026-11-11 ~18:45).

Every --every seconds (default 60) it writes one JSON line to log/lead-mem-watch.jsonl: per lead worktree, the summed
RSS of every process whose working directory is in that worktree (~/gov-os-worktrees/<W2> and <W2>-*), so a lead's
workers and suites count even though each runs in its own process group. It reads /proc only; it never stops, holds
or signals anything, and has none of lead_hour_watch.py's hold logic (that script is unchanged).

No process-name matching (DEC-1073 (4), read with DEC-1135): a lead is found by the lead list in dispatch/status.json
or by a worktree that has a process with its working directory in it (the CTO's own W2-00 worktrees are left out
unless status.json lists W2-00). One line holds {"at": UTC, "avail_mb": MemAvailable,
"leads": {"<W2>": {"mb": N, "kb": N, "procs": N, "in_status": true|false}}}; a line with an empty "leads" is a sample
with no lead running (so a gap in the file means the sampler was down, never "no lead").

The file is bounded: at --max-bytes (default 20 MB) it is renamed to <file>.1 (replacing the older one) and a new file
starts, so at most about 40 MB is ever held. Stop it by pid: --pidfile <file> writes its pid, and
`bash tools/proc.sh stop $(cat <pidfile>)` ends it.

Usage: lead_mem_watch.py [--every 60] [--count N] [--out <jsonl>] [--max-bytes 20971520] [--status-json <file>]
                         [--wt <worktrees dir>] [--pidfile <file>]        (--count 0 = until stopped)
"""
import argparse
import json
import os
import re
import time

ORCH = "/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator"
WT = "/home/usain/gov-os-worktrees"
EXCLUDE = {"W2-00"}


def mem_available_kb():
    try:
        with open("/proc/meminfo") as f:
            for line in f:
                if line.startswith("MemAvailable:"):
                    return int(line.split()[1])
    except OSError:
        pass
    return None


def status_leads(path):
    try:
        with open(path) as f:
            return [str(x) for x in (json.load(f).get("leads") or [])]
    except (OSError, ValueError, AttributeError):
        return []


def owner_of(folder, leads):
    """The lead a worktree folder belongs to: the longest listed lead it equals or starts with (<lead>-...), else the
    ticket id at its front (W2-129-d6 -> W2-129), else None."""
    best = None
    for n in leads:
        if (folder == n or folder.startswith(n + "-")) and (best is None or len(n) > len(best)):
            best = n
    if best:
        return best
    m = re.match(r"^(W[12]-[0-9]+[A-Za-z]?)(?:-.*)?$", folder)
    return m.group(1) if m else None


def sample(wt=WT, leads_listed=(), proc="/proc"):
    """{W2: {"kb": summed RSS, "procs": n}} for every worktree with a process whose cwd is inside it."""
    out = {}
    base = wt.rstrip("/") + "/"
    try:
        pids = [p for p in os.listdir(proc) if p.isdigit()]
    except OSError:
        return out
    for pid in pids:
        try:
            cwd = os.readlink(f"{proc}/{pid}/cwd")
        except OSError:
            continue
        if not cwd.startswith(base):
            continue
        folder = cwd[len(base):].split("/", 1)[0]
        w2 = owner_of(folder, leads_listed)
        if w2 is None or (w2 in EXCLUDE and w2 not in leads_listed):
            continue
        try:
            with open(f"{proc}/{pid}/status") as f:
                rss = next((int(l.split()[1]) for l in f if l.startswith("VmRSS:")), 0)
        except OSError:
            continue
        d = out.setdefault(w2, {"kb": 0, "procs": 0})
        d["kb"] += rss
        d["procs"] += 1
    return out


def make_row(wt, status_json, now=None, proc="/proc"):
    listed = status_leads(status_json)
    found = sample(wt, listed, proc)
    leads = {}
    for w2 in sorted(set(found) | set(listed)):
        d = found.get(w2, {"kb": 0, "procs": 0})
        leads[w2] = {"mb": d["kb"] // 1024, "kb": d["kb"], "procs": d["procs"], "in_status": w2 in listed}
    avail = mem_available_kb()
    return {"at": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(now if now is not None else time.time())),
            "avail_mb": None if avail is None else avail // 1024, "leads": leads}


def append(path, row, max_bytes):
    """One line; the file moves to <path>.1 first when it has reached max_bytes (the older .1 is replaced)."""
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    try:
        if os.path.getsize(path) >= max_bytes:
            os.replace(path, path + ".1")
    except OSError:
        pass
    with open(path, "a") as f:
        f.write(json.dumps(row) + "\n")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--every", type=float, default=60.0)
    ap.add_argument("--count", type=int, default=0, help="stop after N samples (0 = until stopped)")
    ap.add_argument("--out", default=f"{ORCH}/log/lead-mem-watch.jsonl")
    ap.add_argument("--max-bytes", type=int, default=20 * 1024 * 1024)
    ap.add_argument("--status-json", default=f"{ORCH}/dispatch/status.json")
    ap.add_argument("--wt", default=WT)
    ap.add_argument("--pidfile", default=None)
    a = ap.parse_args(argv)
    if a.pidfile:
        with open(a.pidfile, "w") as f:
            f.write(str(os.getpid()))
    n = 0
    try:
        while True:
            append(a.out, make_row(a.wt, a.status_json), a.max_bytes)
            n += 1
            if a.count and n >= a.count:
                break
            time.sleep(a.every)
    finally:
        if a.pidfile:
            try:
                if open(a.pidfile).read().strip() == str(os.getpid()):
                    os.remove(a.pidfile)
            except OSError:
                pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
