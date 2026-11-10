#!/usr/bin/env python3
"""USAGE-1: cost components, role/effort split, baselines, cache expiries, counterfactuals and the meter fit.

    python3 -I savings.py      (after collect.py, workers.py; reads analyze.py's helpers)
"""
import json
import re
import statistics
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import analyze as A  # noqa: E402

S, C = A.S, A.C
P = {"claude-opus-5-5": (4.0, 5.0, 8.0, 0.20, 20.0), "claude-sonnet-5-5": (2.0, 2.5, 4.0, 0.10, 10.0),
     "claude-haiku-5-5": (0.10, 0.125, 0.20, 0.01, 0.50)}


def t(ts):
    return datetime.fromisoformat(ts.replace("Z", "+00:00")).timestamp()


def comps():
    print("\n## cost components by source ($)")
    by = defaultdict(lambda: defaultdict(float))
    for c in C:
        p = P.get(c["model"])
        if not p or c["model"] == "claude-haiku-5-5":
            src = A.source(S[c["key"]])
            by[src]["haiku/all"] += c["cost"] or 0
            continue
        src = A.source(S[c["key"]])
        by[src]["read"] += c["cr"] * p[3] / 1e6
        by[src]["write5m"] += c["w5"] * p[1] / 1e6
        by[src]["write1h"] += c["w1"] * p[2] / 1e6
        by[src]["output"] += c["out"] * p[4] / 1e6
        by[src]["input"] += c["inp"] * p[0] / 1e6
        by[src]["think_tok"] += c.get("think", 0)
        by[src]["out_tok"] += c["out"]
    tot = defaultdict(float)
    for s, d in sorted(by.items()):
        print(s, {k: round(v, 1) if "tok" not in k else int(v) for k, v in d.items()})
        for k, v in d.items():
            tot[k] += v
    print("total", {k: round(v, 1) for k, v in tot.items()})


def roles():
    print("\n## by role and effort ($)")
    by = defaultdict(lambda: [0.0, 0, set()])
    eff = defaultdict(float)
    for c in C:
        s = S[c["key"]]
        src = A.source(s)[2:]
        r = A.role(s) or "-"
        k = (src, r)
        by[k][0] += c["cost"] or 0
        by[k][1] += 1
        by[k][2].add(c["key"])
        eff[(src, str(c["effort"]))] += c["cost"] or 0
    for k, v in sorted(by.items(), key=lambda x: -x[1][0]):
        print(k, round(v[0], 2), v[1], "calls", len(v[2]), "transcripts")
    for k, v in sorted(eff.items(), key=lambda x: -x[1]):
        print("effort", k, round(v, 2))


def baselines():
    print("\n## first-call context (k tokens) by source: median, p90; and calls per transcript median")
    per = defaultdict(list)
    for c in C:
        per[c["key"]].append(c)
    first = defaultdict(list)
    ncalls = defaultdict(list)
    for k, cs in per.items():
        src = A.source(S[k])
        if "/subagents/" in S[k]["rel"] and src.startswith("3"):
            src = "3w workers' helpers"
        first[src].append((cs[0]["inp"] + cs[0]["cr"] + cs[0]["w5"] + cs[0]["w1"]) / 1e3)
        ncalls[src].append(len(cs))
    for s in sorted(first):
        v = sorted(first[s])
        print(s, len(v), round(statistics.median(v)), round(v[int(0.9 * (len(v) - 1))]),
              "calls med", statistics.median(ncalls[s]))


def expiries():
    print("\n## cache expiries: calls whose cache write > 60k (a cold or near-cold prompt), by source")
    per = defaultdict(list)
    for c in C:
        per[c["key"]].append(c)
    out = defaultdict(lambda: [0, 0.0, 0.0])
    gaps = defaultdict(list)
    for k, cs in per.items():
        src = A.source(S[k])
        prev = None
        for i, c in enumerate(cs):
            cw = c["w5"] + c["w1"]
            p = P.get(c["model"], (0, 0, 0, 0, 0))
            if i > 0 and cw > 60_000:
                out[src][0] += 1
                out[src][1] += c["w5"] * p[1] / 1e6 + c["w1"] * p[2] / 1e6
                out[src][2] += (t(c["ts"]) - t(prev)) / 60
            if prev:
                gaps[src].append((t(c["ts"]) - t(prev)) / 60)
            prev = c["ts"]
    for s, v in sorted(out.items()):
        g = gaps[s]
        print(s, "cold calls", v[0], "their write $%.1f" % v[1], "mean gap before %.0f min" % (v[2] / max(v[0], 1)),
              "| gaps>5m: %d of %d, >60m: %d" % (sum(x > 5 for x in g), len(g), sum(x > 60 for x in g)))


def worker_5m():
    """workers (claude -p) write the 1h cache. If 5m: writes at 1.25x not 2x, but a gap > 5 min re-writes the
    whole prompt (cache read -> 5m write)."""
    per = defaultdict(list)
    for c in C:
        if A.source(S[c["key"]]).startswith("3") and c["model"] == "claude-opus-5-5":
            per[c["key"]].append(c)
    now = alt = 0.0
    for k, cs in per.items():
        prev = None
        for c in cs:
            now += c["cost"]
            gap = (t(c["ts"]) - t(prev)) / 60 if prev else 0
            cw = c["w5"] + c["w1"]
            if gap > 5:
                alt += (c["inp"] * 4 + (c["cr"] + cw) * 5 + c["out"] * 20) / 1e6
            else:
                alt += (c["inp"] * 4 + cw * 5 + c["cr"] * 0.2 + c["out"] * 20) / 1e6
            prev = c["ts"]
    print(f"\n## workers 1h->5m cache: now ${now:.2f}, with 5m ${alt:.2f}, saving ${now - alt:.2f}")


def cap(limit, handover):
    """restart a session (fresh, with a handover of `handover` tokens) whenever its context passes `limit`:
    later calls' cache reads drop by (context at restart - handover); the restart writes the handover (5m/1h as
    the session did). Opus sessions only. Returns saving by source."""
    per = defaultdict(list)
    for c in C:
        if c["model"] == "claude-opus-5-5":
            per[c["key"]].append(c)
    sav = defaultdict(float)
    restarts = defaultdict(int)
    for k, cs in per.items():
        src = A.source(S[k])
        shift = 0
        for c in cs:
            ctx = c["inp"] + c["cr"] + c["w5"] + c["w1"] - shift
            if ctx > limit:
                restarts[src] += 1
                shift += ctx - handover
                wrate = 8.0 if c["w1"] else 5.0
                sav[src] -= handover * wrate / 1e6
                ctx = handover
            red = min(shift, c["cr"])
            sav[src] += red * 0.20 / 1e6
    return sav, restarts


def caps():
    print("\n## context cap counterfactual (saving $, restarts)")
    for limit, ho in ((150_000, 60_000), (200_000, 60_000), (300_000, 80_000)):
        sav, rs = cap(limit, ho)
        print(f"limit {limit // 1000}k handover {ho // 1000}k: total ${sum(sav.values()):.0f}",
              {k[2:]: (round(v), rs[k]) for k, v in sorted(sav.items())})


def meter_fit():
    print("\n## the meter: cumulative fit pct = k * X (through the origin) at each reading since the reset")
    pts = json.loads((HERE / "meter.json").read_text())["points"]
    ext = A.EXTERNAL[0]
    e0, e1 = t(ext["start"] + ":00+00:00"), t(ext["end"] + ":00+00:00")
    cs = sorted(C, key=lambda c: c["ts"])
    measures = {
        "$ list incl. fresh-80": lambda c: c["cost"] or 0,
        "$ list, transcripts only": lambda c: c["cost"] or 0,
        "output tokens": lambda c: c["out"],
        "cache-read tokens": lambda c: c["cr"],
        "all tokens (in+out+cr+cw)": lambda c: c["inp"] + c["out"] + c["cr"] + c["w5"] + c["w1"],
        "in+out+cw (no cache read)": lambda c: c["inp"] + c["out"] + c["w5"] + c["w1"],
        "API calls": lambda c: 1,
    }
    for name, f in measures.items():
        xs, ys = [], []
        i, acc = 0, 0.0
        for ts, pct in pts:
            tt = t(ts + "+00:00")
            while i < len(cs) and t(cs[i]["ts"]) <= tt:
                acc += f(cs[i])
                i += 1
            x = acc
            if name.startswith("$ list incl"):
                x += ext["cost"] * min(max((tt - e0) / (e1 - e0), 0), 1)
            xs.append(x)
            ys.append(pct)
        k = sum(x * y for x, y in zip(xs, ys)) / sum(x * x for x in xs)
        res = [y - k * x for x, y in zip(xs, ys)]
        rmse = (sum(r * r for r in res) / len(res)) ** 0.5
        ybar = sum(ys) / len(ys)
        r2 = 1 - sum(r * r for r in res) / sum((y - ybar) ** 2 for y in ys)
        maxr = max(abs(r) for r in res)
        unit = 1 / k
        print(f"{name}: one point = {unit:,.3g}; RMSE {rmse:.2f} pt, max miss {maxr:.1f} pt, R2 {r2:.4f}")


def cto_wakes():
    s = S[f"{A.CTO_KEY}"] if hasattr(A, "CTO_KEY") else [v for v in S.values() if v["kind"] == "cto"][0]
    print("\n## CTO wakes:", s["wake_kinds"], "human turns", s["human_turns"], "compactions", s["compactions"],
          "tools", dict(sorted(s["tools"].items(), key=lambda x: -x[1])[:8]))
    sent = [v for v in S.values() if v["kind"] == "sentinel"][0]
    print("sentinel wakes:", sent["wake_kinds"], sent["calls"], "calls", sent["first_ts"], sent["last_ts"])


def top10():
    per = defaultdict(list)
    for c in C:
        per[c["key"]].append(c)
    cost = {k: sum(c["cost"] or 0 for c in v) for k, v in per.items()}
    print("\n## top 10 detail")
    for k, v in sorted(cost.items(), key=lambda x: -x[1])[:10]:
        cs = per[k]
        s = S[k]
        p = P[cs[0]["model"]]
        rd = sum(c["cr"] for c in cs) * p[3] / 1e6
        wr = sum(c["w5"] * p[1] + c["w1"] * p[2] for c in cs) / 1e6
        ou = sum(c["out"] for c in cs) * p[4] / 1e6
        th = sum(c.get("think", 0) for c in cs)
        ot = sum(c["out"] for c in cs)
        ctx = [c["inp"] + c["cr"] + c["w5"] + c["w1"] for c in cs]
        hrs = (t(cs[-1]["ts"]) - t(cs[0]["ts"])) / 3600
        bash = s["tools"].get("Bash", 0)
        rc = sum(s["result_chars"].values()) / 1e6
        print(f"{A.ticket(s)} {A.role(s)} ${v:.2f}: read ${rd:.1f} write ${wr:.1f} out ${ou:.1f} "
              f"(thinking {th / max(ot, 1):.0%}); calls {len(cs)}; ctx first {ctx[0] / 1e3:.0f}k med "
              f"{statistics.median(ctx) / 1e3:.0f}k last {ctx[-1] / 1e3:.0f}k max {max(ctx) / 1e3:.0f}k; "
              f"{hrs:.1f} h {cs[0]['ts'][5:16]}..{cs[-1]['ts'][5:16]}; Bash {bash}, tool-result {rc:.1f}M chars; "
              f"reads {s['reads']}/{s['read_distinct']}; tools {sum(s['tools'].values())}; "
              f"desc {((s['meta'] or {}).get('description') or '')[:40]}")


if __name__ == "__main__":
    for f in (comps, roles, baselines, expiries, worker_5m, caps, meter_fit, cto_wakes, top10):
        f()
