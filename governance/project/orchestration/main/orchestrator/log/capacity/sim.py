"""CAPACITY-1, bigger machine: a list scheduler over Wave 2's remaining tickets.

Inputs: tickets.json (load_tickets.py), the measured run times (measure_runs.py) and the assumptions below.
For each scenario (machine capacity c x today's, leads at once N) it prints when EXAMIN's copy can start (W2-27
starts) and when Wave 2 closes (W2-47 done), the peak and mean leads in use, and the series that sets the pace.

Assumptions (each marked measured or estimated in the draft):
  run hours at today's load (measured, 2026-10-30/31 medians, gate waits trimmed): LITE 2.4, STANDARD 3.3, FULL 4.5;
  runs per ticket 2.5 (measured median to DONE); a lead run is ~55 % CPU-bound (tests, rebuilds) and ~45 % model time
  (estimated); the CPU-bound part slows with load as W2-108's eight measured runs show (f(u) below, u = load per
  processor); each running lead adds ~10 to the load and each running close ~10 (measured: ~6 leads + closes ~ 60);
  a close is ~3 h of CPU-bound work at today's load (measured 2.5 to 3 h without gate waits);
  between runs: 0.5 h of the CTO's turnaround; one owner decision per STANDARD or FULL ticket (measured ~0.3 per run),
  answered in ~0.5 h while the owner is awake (09:00 to 02:00) and otherwise at 09:30 (DEC-973's morning package);
  two tickets whose allowed_paths overlap never run at once (DEC-786, DEC-942).
"""
import heapq
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
T0 = datetime(2026, 10, 31, 14, 30)
RUN_H = {"LITE": 2.4, "STANDARD": 3.3, "FULL": 4.5, "": 3.3}
CPU_SHARE = 0.55
CLOSE_H = 3.0
LOAD_PER_JOB = 10.0
NPROC = 20
F_POINTS = [(0.5, 1.0), (1.0, 1.37), (1.8, 2.48), (2.4, 3.5), (3.17, 3.86), (5.0, 4.8)]
U_REF = 3.0  # today's load per processor, where the measured run hours were taken


def f(u):
    if u <= F_POINTS[0][0]:
        return F_POINTS[0][1]
    for (u0, f0), (u1, f1) in zip(F_POINTS, F_POINTS[1:]):
        if u <= u1:
            return f0 + (f1 - f0) * (u - u0) / (u1 - u0)
    return F_POINTS[-1][1] + 0.5 * (u - F_POINTS[-1][0])


def run_hours(base, u):
    return base * ((1 - CPU_SHARE) + CPU_SHARE * f(u) / f(U_REF))


def close_hours(u):
    return CLOSE_H * f(u) / f(U_REF)


def owner_ready(t):
    """When the owner's answer to a package sent at t arrives."""
    d = T0 + timedelta(hours=t)
    h = d.hour + d.minute / 60
    if h >= 9 or h < 2:
        return t + 0.5
    nxt = d.replace(hour=9, minute=30, second=0)
    return t + (nxt - d).total_seconds() / 3600


def pattern_base(p):
    p = p.strip()
    cut = len(p)
    for ch in "*?[{":
        i = p.find(ch)
        if i >= 0:
            cut = min(cut, i)
    return p[:cut], cut < len(p)


def sweep(base, glob):
    # a sweep across the whole package (src/gov/**/*.py) is split by file in practice (DEC-942 item 1)
    return glob and base.count("/") < 3


def overlap(pa, pb):
    acc = "tests/" + "acceptance/"
    for a in pa:
        ba, ga = pattern_base(a)
        if ba.startswith(acc) or sweep(ba, ga):
            continue
        for b in pb:
            bb, gb = pattern_base(b)
            if bb.startswith(acc) or sweep(bb, gb):
                continue
            if not ga and not gb and ba == bb:
                return True
            if ga and bb.startswith(ba.rsplit("/", 1)[0] + "/") and (ba.endswith("/") or bb.startswith(ba)):
                return True
            if gb and ba.startswith(bb.rsplit("/", 1)[0] + "/") and (bb.endswith("/") or ba.startswith(bb)):
                return True
    return False


def build():
    t = json.load(open(os.path.join(HERE, "tickets.json")))
    out_tags = ("wave-3", "deferred", "withdrawn", "parked")
    live = {k: v for k, v in t.items() if v["wbs"].startswith("W2-") and v["wbs"] != "W2-00"
            and not any(x in v["tags"] for x in out_tags)}
    merges = subprocess.run(["git", "-C", "/home/usain/Dynamic-Agentic-Engineering-OS", "log", "--merges",
                             "--first-parent", "w2/integrate", "--format=%s", "-900"],
                            capture_output=True, text=True).stdout
    running_now = {"W2-05", "W2-107", "W2-108", "W2-67", "W2-95", "W2-96"}
    queued_resume = {"W2-105", "W2-52"}
    nodes = {}
    for k, v in live.items():
        w = v["wbs"]
        if v["status"] == "closed":
            continue
        merged = (f"Merge w2/{w} " in merges or f"Merge w2/{w} (" in merges) and w not in running_now
        if merged:
            runs = 0.0
        elif w in running_now:
            runs = 1.0
        elif w in queued_resume:
            runs = 1.0
        elif w == "W2-60a":
            runs = 0.0
        elif w in ("W2-20", "W2-37", "W2-56", "W2-81"):
            runs = 2.0
        elif w in ("W2-46", "W2-24", "W2-28", "W2-30", "W2-47"):
            runs = 1.0
        else:
            runs = 2.5
        deps = []
        for d in v["deps"]:
            if d in live and live[d]["status"] != "closed":
                deps.append(live[d]["wbs"])
        nodes[w] = {"w": w, "profile": v["profile"], "runs": runs, "deps": set(deps), "paths": v["paths"],
                    "merged": merged, "owner": v["profile"] in ("STANDARD", "FULL") and runs >= 2,
                    "running_now": w in running_now}
    nodes["W2-60a"]["deps"].add("W2-11")
    # sequencing lines of PLAN-GROWTH-1 and the WBS that are not in depends_on
    for a, b in [("W2-13", "W2-108"), ("W2-33", "W2-11"), ("W2-23", "W2-52"), ("W2-83a", "W2-52"),
                 ("W2-60a", "W2-56"), ("W2-60b", "W2-60a"), ("W2-82", "W2-60b"), ("W2-21", "W2-82"),
                 ("W2-55", "W2-04"), ("W2-91", "W2-86")]:
        if a in nodes and b in nodes:
            nodes[a]["deps"].add(b)
    memory = ["W2-55", "W2-04", "W2-05", "W2-06", "W2-13", "W2-15a", "W2-32", "W2-61h", "W2-86", "W2-88", "W2-91",
              "W2-92", "W2-108"]
    roles = ["W2-11", "W2-33", "W2-60a", "W2-60b", "W2-83a", "W2-83b"]
    nodes["ACT2"] = {"w": "ACT2", "profile": "", "runs": 0, "deps": {x for x in memory + roles if x in nodes},
                     "paths": [], "merged": False, "owner": False, "milestone_h": 12.0, "owner_act": True}
    nodes["LAYERS"] = {"w": "LAYERS", "profile": "", "runs": 0, "deps": {"ACT2"}, "paths": [], "merged": False,
                       "owner": False, "milestone_h": 24.0}
    for w in ("W2-100", "W2-101"):
        if w in nodes:
            nodes[w]["deps"].add("ACT2")
    if "W2-27" in nodes:
        nodes["W2-27"]["deps"].add("LAYERS")
        nodes["W2-27"]["owner"] = True
    if "W2-47" in nodes:
        nodes["W2-47"]["owner"] = True
    for n in nodes.values():
        n["deps"] = {d for d in n["deps"] if d in nodes}
    return nodes


CTO_H = 0.25      # the CTO's turnaround per lead return (read, verify, brief, relaunch), one session: estimated
RB_QUIET_H = 300 / 3600  # one store rebuild on a quiet machine (W2-108's quickest run, measured)


def simulate(nodes, cap, N, trace=False, serial=True, runs_scale=1.0, hours_scale=1.0, reserve=False):
    cto = [0.0]
    rb_lock = [0.0]
    nodes = {k: dict(v, deps=set(v["deps"])) for k, v in nodes.items()}
    # the remaining chain length (by base hours), for priority
    memo = {}
    dependants = {k: [] for k in nodes}
    for k, v in nodes.items():
        for d in v["deps"]:
            dependants[d].append(k)

    def tail(k):
        if k in memo:
            return memo[k]
        v = nodes[k]
        own = v["runs"] * RUN_H.get(v["profile"], 3.3) + CLOSE_H + v.get("milestone_h", 0)
        memo[k] = own + max([tail(x) for x in dependants[k]] or [0])
        return memo[k]

    done_at, started_at, finished_runs_at = {}, {}, {}
    state = {k: "wait" for k in nodes}
    remaining = {k: (v["runs"] * runs_scale if v["runs"] >= 2 else v["runs"]) for k, v in nodes.items()}
    holding = set()   # tickets holding their paths (from first run to merge)
    running = {}      # ticket -> end time of its current run
    closing = {}      # ticket -> end time of its close
    events = []
    t = 0.0
    use_samples = []
    ready_samples = []
    for k, v in nodes.items():
        if v.get("merged") and v["runs"] == 0 and not v["deps"] and k != "W2-60a":
            state[k] = "closing"
            u = (LOAD_PER_JOB * (len(closing) + 1)) / (NPROC * cap)
            closing[k] = close_hours(u)
            heapq.heappush(events, (closing[k], "close_end", k))
    next_free = {k: 0.0 for k in nodes}  # earliest time a ticket's next run may start (gaps, owner)

    def deps_done(k):
        return all(state.get(d) == "done" or (nodes[d].get("merged") and state.get(d) in ("closing", "done"))
                   for d in nodes[k]["deps"])

    def can_hold(k):
        return all(not overlap(nodes[k]["paths"], nodes[h]["paths"]) for h in holding if h != k)

    def load_u():
        return LOAD_PER_JOB * (len(running) + len(closing)) / (NPROC * cap)

    def start_runs():
        nonlocal t
        cands = []
        for k, v in nodes.items():
            if state[k] in ("wait", "between") and deps_done(k) and next_free[k] <= t + 1e-9:
                if v.get("milestone_h") is not None and k in ("ACT2", "LAYERS"):
                    if state[k] == "wait":
                        state[k] = "milestone"
                        end = t + v["milestone_h"]
                        if v.get("owner_act"):
                            end = owner_ready(end)
                        heapq.heappush(events, (end, "ms_end", k))
                        started_at[k] = t
                    continue
                if remaining[k] <= 0:
                    if state[k] in ("wait", "between"):
                        state[k] = "closing"
                        started_at.setdefault(k, t)
                        holding.discard(k)
                        closing[k] = t + close_hours(load_u())
                        heapq.heappush(events, (closing[k], "close_end", k))
                    continue
                if k not in holding and not can_hold(k):
                    continue
                cands.append((-tail(k), k))
        cands.sort()
        for _, k in cands:
            if len(running) >= N:
                break
            if k not in holding and not can_hold(k):
                continue
            if reserve and k not in holding and any(
                    state[j] == "wait" and j.startswith("W2") and remaining[j] > 0 and tail(j) >= tail(k) + 12
                    and overlap(nodes[k]["paths"], nodes[j]["paths"]) for j in nodes):
                continue  # the critical path's files kept free for it
            holding.add(k)
            started_at.setdefault(k, t)
            state[k] = "running"
            base = RUN_H.get(nodes[k]["profile"], 3.3) * min(1.0, remaining[k]) * hours_scale
            if serial:
                # one store rebuild at a time on the machine (DEC-962, until W2-76's lock is measured)
                rb = RB_QUIET_H * f(load_u()) / f(0.5)
                rb_start = max(rb_lock[0], t)
                rb_lock[0] = rb_start + rb
                end = rb_lock[0] + run_hours(base, load_u()) - rb
            else:
                end = t + run_hours(base, load_u())
            running[k] = end
            heapq.heappush(events, (end, "run_end", k))

    start_runs()
    while events:
        t, kind, k = heapq.heappop(events)
        if kind == "run_end":
            running.pop(k, None)
            remaining[k] -= 1.0
            if remaining[k] <= 1e-9:
                remaining[k] = 0
                holding.discard(k)
                state[k] = "closing"
                closing[k] = t + close_hours(load_u())
                heapq.heappush(events, (closing[k], "close_end", k))
            else:
                state[k] = "between"
                if serial:
                    cto[0] = max(cto[0], t) + CTO_H
                    gap = cto[0] + 0.25
                else:
                    gap = t + 0.5
                if nodes[k]["owner"] and not nodes[k].get("owner_used"):
                    nodes[k]["owner_used"] = True
                    gap = owner_ready(t) + 0.25
                next_free[k] = gap
                heapq.heappush(events, (gap, "wake", k))
        elif kind == "close_end":
            closing.pop(k, None)
            if nodes[k]["owner"] and k in ("W2-47",) and not nodes[k].get("owner_used"):
                nodes[k]["owner_used"] = True
                heapq.heappush(events, (owner_ready(t), "ms_end", k))
                continue
            state[k] = "done"
            done_at[k] = t
        elif kind == "ms_end":
            state[k] = "done"
            done_at[k] = t
        start_runs()
        use_samples.append((t, len(running)))
        ready_samples.append((t, sum(1 for kk, vv in nodes.items() if kk.startswith("W2") and state[kk] in ("wait", "between", "running")
                                     and remaining[kk] > 0 and deps_done(kk))))
    # metrics
    end = max(done_at.values()) if done_at else 0
    busy = 0.0
    for (t1, n1), (t2, _) in zip(use_samples, use_samples[1:]):
        busy += n1 * (t2 - t1)
    mean_use = busy / end if end else 0
    peak = max(n for _, n in use_samples) if use_samples else 0
    copy_start = started_at.get("W2-27")
    ready_peak = max(n for _, n in ready_samples) if ready_samples else 0
    daily = {}
    for (t1, n1), (t2, _) in zip(use_samples, use_samples[1:]):
        d = (T0 + timedelta(hours=t1)).strftime("%m-%d")
        daily[d] = daily.get(d, 0) + n1 * (t2 - t1)
    w2_close = done_at.get("W2-47")
    left = [k for k, s in state.items() if s != "done"]
    return {"copy_start": copy_start, "w2_close": w2_close, "peak": peak, "mean": round(mean_use, 1),
            "done_at": done_at, "started_at": started_at, "left": left,
            "ready_peak": ready_peak, "daily_lead_h": {k: round(v, 1) for k, v in daily.items()}}


def critical(nodes, res):
    """The chain into W2-47: each step's latest-finishing dependency."""
    done = res["done_at"]
    chain, k = [], "W2-47"
    while k in nodes:
        chain.append(k)
        deps = [d for d in nodes[k]["deps"] if d in done]
        if not deps:
            break
        k = max(deps, key=lambda d: done[d])
    return list(reversed(chain))


def when(h):
    return (T0 + timedelta(hours=h)).strftime("%m-%d %H:%M") if h is not None else "never"


if __name__ == "__main__":
    nodes = build()
    scen = [("1x, 6 leads (today)", 1, 6), ("4x, 24 leads", 4, 24), ("6x, 36 leads", 6, 36), ("10x, 60 leads", 10, 60),
            ("4x, 6 leads (no overload)", 4, 6), ("4x, 12 leads", 4, 12), ("unlimited", 1000, 1000)]
    mode = sys.argv[1] if len(sys.argv) > 1 else "serial"
    kw = {"serial": dict(serial=True), "plain": dict(serial=False),
          "slow": dict(serial=True, runs_scale=1.4, hours_scale=1.3),
          "reserve": dict(serial=True, reserve=True),
          "slow-reserve": dict(serial=True, runs_scale=1.4, hours_scale=1.3, reserve=True)}[mode]
    print("mode", mode, kw)
    out = {}
    for name, cap, N in scen:
        r = simulate(nodes, cap, N, **kw)
        out[name] = r
        print(f"{name:28s} copy start {when(r['copy_start'])}  W2 close {when(r['w2_close'])}  peak {r['peak']:3d}"
              f"  mean {r['mean']:5.1f}  ready-peak {r['ready_peak']}  left {r['left'][:5]}")
        print("    lead-hours per day:", r["daily_lead_h"])
    r = out["unlimited"]
    print("critical chain (unlimited):", " > ".join(critical(nodes, r)))
    r = out["1x, 6 leads (today)"]
    print("critical chain (1x):", " > ".join(critical(nodes, r)))
    json.dump({k: {kk: vv for kk, vv in v.items() if kk in ("copy_start", "w2_close", "peak", "mean", "ready_peak", "daily_lead_h")}
               for k, v in out.items()}, open(os.path.join(HERE, f"sim_result_{mode}.json"), "w"), indent=1)
    print("nodes", len(nodes))
