#!/usr/bin/env python3
"""USAGE-1: tables from calls.jsonl, sessions.json and results.json (run collect.py and workers.py first).

    python3 -I analyze.py [top|sources|tickets|days|meter|check]   (default: all) -> stdout; also units.json
"""
import json
import re
import statistics
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
S = json.loads((HERE / "sessions.json").read_text())
C = [json.loads(l) for l in open(HERE / "calls.jsonl")]
R = json.loads((HERE / "results.json").read_text())
USAGE = Path("/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/log/usage.txt")
# experiments run with --no-session-persistence: cost from their own records (M, FRESH-80-RESULT.md "Cost")
EXTERNAL = [dict(source="experiments", ticket="W2-88/K9 fresh 80", day="2026-11-08", cost=109.05,
                 start="2026-11-08T19:32", end="2026-11-08T21:46", note="FRESH-80-RESULT.md cost table")]

res_by_sid = {}
for r in R:
    if r["session_id"] and r["session_id"] not in res_by_sid:
        res_by_sid[r["session_id"]] = r


def source(s):
    k = s["kind"]
    if k == "cto":
        return "1 CTO session"
    if k == "cto-helper":
        return "2 CTO helpers"
    if k == "worktree":
        return "3 launched workers"
    if k in ("sentinel", "sentinel-helper"):
        return "5 sentinel"
    if k == "tmp":
        return "6 dead-man pushes"
    if k == "main-other":
        return "7 usage recorder"
    if "gov-os-operator" in s["folder"]:
        return "8 operator folder session"
    if k == "writer":
        return "4 experiments (writer)"
    return "9 live tests (pytest)"


def ticket(s):
    f = s["folder"]
    m = re.match(r"-home-usain-gov-os-worktrees-(W2-\d+|D6)", f)
    if m:
        return m.group(1).replace("D6", "D-6")
    if s["kind"] == "cto-helper":
        desc = (s["meta"] or {}).get("description") or ""
        m = re.search(r"\b(W[12]-\d+|ACT-[A-Z0-9-]+|D-?\d{1,2})\b", desc)
        if m:
            return m.group(1)
        if s["ids"]:
            w = [i for i in s["ids"] if i.startswith("W2-")]
            return (w or s["ids"])[0]
        return "(helper, no id)"
    if s["kind"] == "cto":
        return "(CTO)"
    if "gov-os-lead-W2-56" in f or "w56" in f:
        return "W2-56"
    if "w1-46" in f:
        return "W1-46/W2-153"
    return "(" + source(s)[2:] + ")"


def role(s):
    sid = s["session_id"]
    r = res_by_sid.get(sid)
    name = Path(r["file"]).stem if r else ""
    if s["kind"] == "cto-helper":
        return (s["meta"] or {}).get("agentType") or "helper"
    if s["kind"] != "worktree":
        return ""
    if "/subagents/" in s["rel"]:
        return "worker's helper"
    low = name.lower()
    if "review" in low or "audit" in low:
        return "independent-auditor"
    if s["folder"].endswith("-tests") or "test" in low or "designer" in low:
        return "test designer"
    return "engineer/other"


def agg_new():
    return dict(calls=0, inp=0, out=0, cr=0, cw=0, cost=0.0)


def add(a, c):
    a["calls"] += 1
    a["inp"] += c["inp"]
    a["out"] += c["out"]
    a["cr"] += c["cr"]
    a["cw"] += c["w5"] + c["w1"]
    a["cost"] += c["cost"] or 0


def M(x):
    return f"{x / 1e6:,.1f}"


def table(rows, title):
    print(f"\n## {title}")
    print("| key | calls | input | output | cache read | cache write | $ list |")
    print("|---|---|---|---|---|---|---|")
    tot = agg_new()
    for k, a in rows:
        print(f"| {k} | {a['calls']:,} | {a['inp']:,} | {M(a['out'])} M | {M(a['cr'])} M | {M(a['cw'])} M | {a['cost']:,.2f} |")
        for f in tot:
            tot[f] += a[f]
    print(f"| total | {tot['calls']:,} | {tot['inp']:,} | {M(tot['out'])} M | {M(tot['cr'])} M | {M(tot['cw'])} M | {tot['cost']:,.2f} |")


def sources():
    by = defaultdict(agg_new)
    bym = defaultdict(agg_new)
    for c in C:
        s = S[c["key"]]
        add(by[source(s)], c)
        add(bym[(source(s), c["model"].replace("claude-", ""))], c)
    table(sorted(by.items()), "by source (transcripts)")
    table(sorted(bym.items()), "by source and model")
    for e in EXTERNAL:
        print(f"external: {e}")


def tickets():
    by = defaultdict(agg_new)
    for c in C:
        s = S[c["key"]]
        by[ticket(s)][c["model"]] = 1
        add(by[ticket(s)], c)
    rows = sorted(by.items(), key=lambda x: -x[1]["cost"])
    print("\n## by ticket")
    print("| ticket | calls | $ | sources |")
    srcs = defaultdict(lambda: defaultdict(float))
    for c in C:
        s = S[c["key"]]
        srcs[ticket(s)][source(s)[2:]] += c["cost"] or 0
    for k, a in rows:
        sp = ", ".join(f"{n} {v:.0f}" for n, v in sorted(srcs[k].items(), key=lambda x: -x[1]))
        print(f"| {k} | {a['calls']} | {a['cost']:.2f} | {sp} |")


def days():
    by = defaultdict(agg_new)
    byd = defaultdict(lambda: defaultdict(float))
    for c in C:
        d = c["ts"][:10]
        add(by[d], c)
        byd[d][source(S[c["key"]])] += c["cost"] or 0
    table(sorted(by.items()), "by day (UTC)")
    for d in sorted(byd):
        print(d, {k: round(v, 2) for k, v in sorted(byd[d].items())})


def meter():
    pts = []
    for line in USAGE.read_text().splitlines():
        m = re.match(r"(\S+ \S+) week \(all models\)=(\d+)%", line)
        if m and m.group(1) >= "2026-11-08 09:00":
            pts.append((m.group(1).replace(" ", "T"), int(m.group(2))))
    # interval sums: dollars, output tokens, cache-read, "weighted tokens" (input+cw+out), calls
    ext = []
    for e in EXTERNAL:  # spread evenly over its window
        ext.append(e)
    print("\n## meter intervals")
    print("| from | to | pct | $ | $ incl. exp | out M | cr M | cw M | calls | $/pt |")
    rows = []
    prev = None
    anchors = [p for p in pts]
    for i in range(1, len(anchors)):
        a, b = anchors[i - 1], anchors[i]
        rows.append((a, b))
    # coarse windows between distinct readings
    marks = [pts[0]]
    for p in pts[1:]:
        if p[1] != marks[-1][1]:
            marks.append(p)
    if marks[-1] != pts[-1]:
        marks.append(pts[-1])
    out = []
    t0 = "2026-11-08T09:00:00"
    windows = [(t0, 0)] + marks
    for i in range(1, len(windows)):
        (ta, pa), (tb, pb) = windows[i - 1], windows[i]
        a = agg_new()
        for c in C:
            if ta <= c["ts"][:19] < tb:
                add(a, c)
        extc = 0.0
        for e in EXTERNAL:
            s0, s1 = e["start"], e["end"]
            ov0, ov1 = max(s0, ta[:16]), min(s1, tb[:16])
            if ov0 < ov1:
                span = (datetime.fromisoformat(s1) - datetime.fromisoformat(s0)).total_seconds()
                ov = (datetime.fromisoformat(ov1) - datetime.fromisoformat(ov0)).total_seconds()
                extc += e["cost"] * ov / span
        dp = pb - pa
        out.append(dict(ta=ta, tb=tb, pa=pa, pb=pb, dp=dp, cost=a["cost"], ext=extc, out=a["out"], cr=a["cr"],
                        cw=a["cw"], inp=a["inp"], calls=a["calls"]))
        print(f"| {ta[5:16]} | {tb[5:16]} | {pa}->{pb} | {a['cost']:.0f} | {a['cost'] + extc:.0f} | {M(a['out'])} | "
              f"{M(a['cr'])} | {M(a['cw'])} | {a['calls']} | {((a['cost'] + extc) / dp) if dp else float('nan'):.1f} |")
    (HERE / "meter.json").write_text(json.dumps(dict(points=pts, windows=out), indent=0))


def top(n=25):
    cost = defaultdict(float)
    per = defaultdict(list)
    for c in C:
        cost[c["key"]] += c["cost"] or 0
        per[c["key"]].append(c)
    # fold a session's own subagents into it for "a session, helper or worker each"? keep separate, but show both.
    print("\n## top transcripts")
    print("| # | source | ticket | role | label | calls | turns | ctx med/max k | cr M | out k | cw M | effort | compact | reads/distinct | $ |")
    for i, (k, v) in enumerate(sorted(cost.items(), key=lambda x: -x[1])[:n], 1):
        s = S[k]
        ctx = s["ctx"]
        cr = sum(c["cr"] for c in per[k])
        out = sum(c["out"] for c in per[k])
        cw = sum(c["w5"] + c["w1"] for c in per[k])
        r = res_by_sid.get(s["session_id"])
        label = Path(r["file"]).stem if (r and s["kind"] == "worktree" and "/subagents/" not in s["rel"]) else (
            (s["meta"] or {}).get("description") or "")
        eff = ",".join(f"{e}:{n}" for e, n in s["efforts"].items())
        print(f"| {i} | {source(s)[2:]} | {ticket(s)} | {role(s)} | {label[:50]} | {s['calls']} | {s['human_turns']} | "
              f"{statistics.median(ctx) / 1e3:.0f}/{max(ctx) / 1e3:.0f} | {cr / 1e6:.1f} | {out / 1e3:.0f} | "
              f"{cw / 1e6:.2f} | {eff} | {s['compactions']} | {s['reads']}/{s['read_distinct']} | {v:.2f} |")


def check():
    """the workers' own total_cost_usd against the transcript-priced cost (session + its subagents)."""
    by_sid = defaultdict(float)
    for c in C:
        by_sid[S[c["key"]]["session_id"]] += c["cost"] or 0
    pairs = [(res_by_sid[sid]["cost"], v) for sid, v in by_sid.items() if sid in res_by_sid]
    a = sum(p[0] for p in pairs)
    b = sum(p[1] for p in pairs)
    print(f"\n## check: {len(pairs)} sessions with own result: total_cost_usd {a:.2f} vs priced here {b:.2f} "
          f"(ratio {b / a:.3f})")


def tools():
    tc = defaultdict(int)
    rc = defaultdict(int)
    bysrc = defaultdict(lambda: defaultdict(int))
    for s in S.values():
        for t, n in s["tools"].items():
            tc[t] += n
        for t, n in s["result_chars"].items():
            rc[t] += n
            bysrc[source(s)][t] += n
    print("\n## tool calls / result chars")
    for t, n in sorted(rc.items(), key=lambda x: -x[1])[:10]:
        print(t, tc.get(t), f"{n / 1e6:.1f} M chars")
    for src, d in sorted(bysrc.items()):
        print(src, {t: f"{n / 1e6:.1f}M" for t, n in sorted(d.items(), key=lambda x: -x[1])[:4]})


if __name__ == "__main__":
    what = sys.argv[1:] or ["sources", "tickets", "days", "meter", "top", "check", "tools"]
    for w in what:
        globals()[w]()
