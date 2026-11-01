#!/usr/bin/env python3
"""CAPACITY-1 (owner, 2026-10-31): what uses the machine, by kind, every minute. Appends one JSON line per sample to
log/capacity/kinds.jsonl: the time, load, MemTotal/MemAvailable, and per kind: processes, CPU (cores used over the
interval, from utime+stime deltas) and RSS (kB).
A process's CPU includes its reaped children's (cutime, cstime), so short-lived work (one gitleaks per file, a test's
`gov` calls) counts under the kind that started it; "machine.short_lived" is what is still left unattributed.
Kinds, judged per process:
  - by its own command first: embedding (ollama, llama-server), reranker (rerank_worker), gitleaks, codegraph
    (codebase-memory-mcp), claude (a Claude Code session's node process);
  - else by its nearest ancestor: a test run (pytest) or a rebuild (gov rebuild); a git command; else other.
Run detached:  python3 kind_sampler.py [--until HH:MM] [--every 60]"""
import json
import os
import sys
import time

OUT = "/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/log/capacity/kinds.jsonl"
TICK = os.sysconf("SC_CLK_TCK")
PAGE_KB = os.sysconf("SC_PAGE_SIZE") // 1024


def procs():
    out = {}
    for pid in os.listdir("/proc"):
        if not pid.isdigit():
            continue
        try:
            with open(f"/proc/{pid}/stat") as f:
                st = f.read()
            rest = st.rsplit(")", 1)[1].split()
            ppid, ut, stt, rss = int(rest[1]), int(rest[11]) + int(rest[13]), int(rest[12]) + int(rest[14]), int(rest[21]) * PAGE_KB  # own + reaped children (short-lived work counts under its parent)
            with open(f"/proc/{pid}/cmdline", "rb") as f:
                cmd = f.read().replace(b"\0", b" ").decode("utf-8", "replace")
            out[int(pid)] = (ppid, ut + stt, rss, cmd)
        except (OSError, IndexError, ValueError):
            continue
    return out


def own_kind(cmd):
    if "ollama" in cmd or "llama-server" in cmd:
        return "embedding"
    if "rerank_worker" in cmd:
        return "reranker"
    if cmd.startswith("gitleaks") or "/gitleaks " in cmd or " gitleaks " in cmd[:40]:
        return "gitleaks"
    if "codebase-memory-mcp" in cmd:
        return "codegraph"
    if "/.local/bin/claude" in cmd or "/claude-code/" in cmd or cmd.startswith("claude "):
        return "claude"
    return None


def kind_of(pid, ps, memo):
    if pid in memo:
        return memo[pid]
    ppid, _, _, cmd = ps[pid]
    k = own_kind(cmd)
    if k is None:
        q, seen = ppid, 0
        while q in ps and seen < 40:
            c = ps[q][3]
            if "pytest" in c:
                k = "test_run"
                break
            if "gov.cli.main rebuild" in c or "gov rebuild" in c:
                k = "rebuild"
                break
            q, seen = ps[q][0], seen + 1
        if k is None:
            k = "pytest_controller" if "pytest" in cmd else ("rebuild" if "rebuild" in cmd and "gov" in cmd else
                                                            ("git" if cmd.startswith("git ") else "other"))
            if k == "pytest_controller":
                k = "test_run"
    memo[pid] = k
    return k


def cpustat():
    with open("/proc/stat") as f:
        v = [int(x) for x in f.readline().split()[1:]]
    user, nice, system, idle, iowait, irq, softirq, steal = (v + [0] * 8)[:8]
    return {"busy": user + nice + system + irq + softirq + steal, "idle": idle, "iowait": iowait}


def meminfo():
    v = {}
    with open("/proc/meminfo") as f:
        for line in f:
            a, b = line.split(":", 1)
            v[a] = int(b.split()[0])
    return v


def main():
    until = sys.argv[sys.argv.index("--until") + 1] if "--until" in sys.argv else None
    every = int(sys.argv[sys.argv.index("--every") + 1]) if "--every" in sys.argv else 60
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    prev, t_prev, cs_prev = procs(), time.time(), cpustat()
    while True:
        time.sleep(every)
        cur, t, cs = procs(), time.time(), cpustat()
        dt = t - t_prev
        memo, kinds = {}, {}
        # a child seen before and ended in this interval: its parent's reaped-children time now holds the child's whole
        # life, part of which was already counted under the child; take that part back from the parent
        seen_ended = {}
        for pid, (ppid, cpu, rss, cmd) in prev.items():
            if pid not in cur:
                seen_ended[ppid] = seen_ended.get(ppid, 0) + cpu
        for pid, (ppid, cpu, rss, cmd) in cur.items():
            k = kind_of(pid, cur, memo)
            d = kinds.setdefault(k, {"n": 0, "cpu": 0.0, "rss_kb": 0})
            d["n"] += 1
            d["rss_kb"] += rss
            before = prev.get(pid)
            used = cpu - before[1] if before and before[3] == cmd else cpu  # new process: all its time is new
            used -= seen_ended.get(pid, 0)
            d["cpu"] += max(0, used) / TICK / dt
        for d in kinds.values():
            d["cpu"] = round(d["cpu"], 2)
        mi = meminfo()
        with open("/proc/loadavg") as f:
            load = [float(x) for x in f.read().split()[:3]]
        machine = {k: round((cs[k] - cs_prev[k]) / TICK / dt, 2) for k in cs}  # cores busy, idle, waiting on I/O
        machine["attributed"] = round(sum(d["cpu"] for d in kinds.values()), 2)
        machine["short_lived"] = round(max(0.0, machine["busy"] - machine["attributed"]), 2)
        rec = {"t": time.strftime("%Y-%m-%dT%H:%M:%S"), "load": load, "nproc": os.cpu_count(), "machine": machine,
               "mem_total_kb": mi["MemTotal"], "mem_available_kb": mi["MemAvailable"], "kinds": kinds}
        with open(OUT, "a") as f:
            f.write(json.dumps(rec) + "\n")
        prev, t_prev, cs_prev = cur, t, cs
        if until and time.strftime("%H:%M") >= until and time.strftime("%H:%M") < "23:59":
            break


if __name__ == "__main__":
    main()
