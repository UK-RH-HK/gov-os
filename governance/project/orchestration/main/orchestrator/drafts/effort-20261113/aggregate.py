#!/usr/bin/env python3
"""Aggregates units.jsonl into the two windows' tables, the usage-point allocation, what was produced and the top 10.
Usage: python3 -I aggregate.py [units file]   -> writes tables.json and tables.md in this folder."""
import json, os, re, sys, collections, subprocess, importlib.util, bisect
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("common", HERE + "/common.py"); C = importlib.util.module_from_spec(spec); spec.loader.exec_module(C)
UF = sys.argv[1] if len(sys.argv) > 1 else "units.jsonl"
U = [json.loads(l) for l in open(HERE + "/" + UF)]
REPO = C.REPO

def frac(u, w):
    a, b = w
    if u["t1"] <= u["t0"]: return 1.0 if a <= u["t0"] <= b else 0.0
    ov = min(b, u["t1"]) - max(a, u["t0"])
    return max(0.0, ov) / (u["t1"] - u["t0"])

# ---- usage points: reset-aware gains between readings (as measure_week.py), allocated by each interval's USD share
rd = []
for l in open(C.ORCH + "/log/usage.txt", errors="replace"):
    m = re.match(r"^(\d{4}-\d\d-\d\d \d\d:\d\d:\d\d) .*?week \(all models\)=(\d+)%", l)
    if m: rd.append((C.epoch(m.group(1)), int(m.group(2))))
rd.sort()
segs = []   # (ta, tb, gain, kind)
GAPH = 2.0
for (ta, pa), (tb, pb) in zip(rd, rd[1:]):
    if tb <= ta: continue
    if tb - ta > GAPH * 3600: segs.append((ta, tb, None, "gap")); continue
    if pb >= pa: segs.append((ta, tb, pb - pa, "gain"))
    else: segs.append((ta, tb, pb, "reset"))
def seg_points_total(w):
    tot = 0.0; gap = 0.0
    for ta, tb, g, k in segs:
        ov = min(w[1], tb) - max(w[0], ta)
        if ov <= 0: continue
        f = ov / (tb - ta)
        if g is None: gap += (tb - ta) * f / 3600
        else: tot += g * f
    return tot, gap
# atoms for allocation: the in-window units, time-spread over their span
def points_by(key, w):
    atoms = []
    for u in U:
        if u["usd"] <= 0: continue
        f = frac(u, w)
        if f <= 0: continue
        atoms.append((u["t0"], u["t1"], u["usd"] * f, u, f))
    # clip atom span to the window as well
    res = collections.Counter(); un = 0.0; tot = 0.0
    for ta, tb, g, k in segs:
        if g is None: continue
        a0, b0 = max(ta, w[0]), min(tb, w[1])
        if b0 <= a0: continue
        gs = g * (b0 - a0) / (tb - ta)
        part = collections.Counter(); den = 0.0
        for (t0, t1, usd, u, f) in atoms:
            if t1 <= t0:
                x = usd if a0 <= t0 < b0 else 0.0
            else:
                lo, hi = max(t0, w[0]), min(t1, w[1])
                if hi <= lo: continue
                ov = min(b0, hi) - max(a0, lo)
                x = usd * max(0.0, ov) / (hi - lo)
            if x > 0: part[key(u)] += x; den += x
        if den <= 0: un += gs; continue
        for k_, x in part.items(): res[k_] += gs * x / den
        tot += gs
    return res, un

def table(w, keyf):
    t = collections.defaultdict(lambda: dict(usd=0.0, lead_h=0.0, other_h=0.0, n=0, qE=0.0, qM=0.0, hE=0.0, hM=0.0, units=set(), subs=collections.defaultdict(lambda: dict(usd=0.0, lead_h=0.0, other_h=0.0))))
    for u in U:
        f = frac(u, w)
        if f <= 0 or u.get("memo"): continue
        k = keyf(u); r = t[k]
        usd = u["usd"] * f
        r["usd"] += usd
        if u["q"] == "E": r["qE"] += usd
        else: r["qM"] += usd
        lead = u["lead_h"] * f
        other = 0.0 if u.get("inside_lead") else u["sess_h"] * f
        r["lead_h"] += lead; r["other_h"] += other
        hh = lead + other
        if (u.get("hours_q") or u["q"]) == "E" or u.get("cto_idle"): r["hE"] += hh
        else: r["hM"] += hh
        r["units"].add(u.get("unit") or u["id"])
        s = r["subs"][u["sub"]]; s["usd"] += usd; s["lead_h"] += lead; s["other_h"] += other
        r["n"] += 1
    return t

OUTJ = {}
for wn, w in C.WINDOWS.items():
    t = table(w, lambda u: str(u["bucket"]))
    # slot waits carved out of lead hours of "land and verify": move to bucket 9 lead-hours
    slot = sum(u["sess_h"] * frac(u, w) for u in U if u.get("slot"))
    lv = t["1"]["subs"].get("lead own time: verify, accept, merge, reading returns (no worker running)")
    moved = 0.0
    if lv:
        moved = min(slot, lv["lead_h"]); lv["lead_h"] -= moved; t["1"]["lead_h"] -= moved
        t["9"]["lead_h"] += moved
        t["9"]["subs"]["slot waits for a test run (carved out of lead or worker hours)"]["lead_h"] += moved
        # the slot waits row's own "other_h" was counted as other hours: zero it (carved, not additional)
        t["9"]["other_h"] -= slot; t["9"]["subs"]["slot waits for a test run (carved out of lead or worker hours)"]["other_h"] -= slot
    pts_b, un = points_by(lambda u: str(u["bucket"]), w)
    pts_s, _ = points_by(lambda u: (str(u["bucket"]), u["sub"]), w)
    tot_pts, gap_h = seg_points_total(w)
    OUTJ[wn] = dict(window=[C.fmt(w[0]), C.fmt(w[1])], total_usd=sum(r["usd"] for r in t.values()), pts_total=tot_pts, pts_unattributed=un, gap_h=gap_h, slot_h=slot, slot_moved=moved,
                    buckets={k: dict(usd=r["usd"], lead_h=r["lead_h"], other_h=r["other_h"], qE=r["qE"], qM=r["qM"], hE=r["hE"], hM=r["hM"], n_units=len(r["units"]), pts=pts_b.get(k, 0.0),
                                      subs={s: dict(usd=v["usd"], lead_h=v["lead_h"], other_h=v["other_h"], pts=pts_s.get((k, s), 0.0)) for s, v in r["subs"].items()}) for k, r in t.items()})

# ---- top single consumers (per session / run / helper / land), whole window A
def top(w, n=14):
    agg = collections.defaultdict(lambda: dict(usd=0.0, h=0.0, kind=None, label=None, b=collections.Counter()))
    for u in U:
        f = frac(u, w)
        if f <= 0: continue
        if u["kind"] in ("cto",): key = ("cto", u["id"])
        elif u["kind"] == "helper": key = ("helper", u["unit"])
        elif u["kind"] in ("lead", "worker", "ambient"): key = (u["kind"], u["unit"])
        elif u["kind"] in ("land", "nightly"): key = (u["kind"], u["id"] + "|" + str(u["bucket"]))
        else: continue
        a = agg[key]; a["usd"] += u["usd"] * f; a["h"] += (u["lead_h"] + u["sess_h"]) * f if u["kind"] != "worker" else u["sess_h"] * f
        a["kind"] = u["kind"]; a["label"] = u["label"]; a["b"][u["bucket"]] += u["usd"] * f + 1e-9; a["sub"] = u["sub"]
    rows = [(k, v) for k, v in agg.items() if v["usd"] > 0]
    rows.sort(key=lambda x: -x[1]["usd"])
    return [dict(key=list(k), usd=v["usd"], hours=v["h"], label=v["label"], bucket=v["b"].most_common(1)[0][0], sub=v.get("sub")) for k, v in rows[:n]]
def top_lands(w, n=6):
    rows = []
    for u in U:
        if u["kind"] == "land" and frac(u, w) > 0: rows.append((u["sess_h"] * frac(u, w), u["label"], u["bucket"]))
    rows.sort(reverse=True); return rows[:n]
def bykind(w):
    c = collections.defaultdict(lambda: [0.0, 0])
    seen = collections.defaultdict(set)
    for u in U:
        f = frac(u, w)
        if f <= 0 or u["usd"] <= 0: continue
        c[u["kind"]][0] += u["usd"] * f; seen[u["kind"]].add(u.get("unit") or u["id"])
    return {k: [v[0], len(seen[k])] for k, v in c.items()}
OUTJ["bykind"] = {wn: bykind(w) for wn, w in C.WINDOWS.items()}
def helper_tiers(w):
    c = collections.Counter()
    for u in U:
        f = frac(u, w)
        if f > 0 and u["kind"] == "helper": c[(u.get("model"), u["bucket"])] += u["usd"] * f
    return {f"{k[0]}|{k[1]}": v for k, v in c.items()}
OUTJ["helper_tiers"] = {wn: helper_tiers(w) for wn, w in C.WINDOWS.items()}
def act_review_rounds(w):
    c = collections.Counter()
    for u in U:
        f = frac(u, w)
        if f > 0 and u["kind"] == "worker" and u["sub"] == "ACTs: reviewing":
            c["r2plus" if re.search(r"-r\d", u["id"]) else "first"] += u["usd"] * f
    for u in U:
        f = frac(u, w)
        if f > 0 and u["kind"] == "helper" and u["sub"] == "ACTs: reviewing": c["helper"] += u["usd"] * f
    return dict(c)
OUTJ["act_review"] = {wn: act_review_rounds(w) for wn, w in C.WINDOWS.items()}
OUTJ["top"] = {wn: top(w) for wn, w in C.WINDOWS.items()}
OUTJ["top_lands"] = {wn: top_lands(w) for wn, w in C.WINDOWS.items()}

# ---- produced (from git, land-done, the register)
def git(*a): return subprocess.run(["git", "-C", REPO] + list(a), capture_output=True, text=True).stdout
def produced(w):
    a, b = int(w[0]), int(w[1])
    subj = [l.split("\x1f") for l in git("log", f"--since=@{a}", f"--until=@{b}", "--format=%H\x1f%s").split("\n") if l]
    first = [l.split("\x1f") for l in git("log", "--first-parent", f"--since=@{a}", f"--until=@{b}", "--format=%H\x1f%P\x1f%s").split("\n") if l]
    out = {}
    out["commits"] = len(subj)
    out["merges_first_parent"] = sum(1 for h, p, s in first if len(p.split()) > 1)
    out["subjects_naming_closed"] = sum(1 for h, s in subj if re.search(r"\bclosed\b", s, re.I))
    out["act_applied_commits"] = sum(1 for h, s in subj if re.match(r"ACT-", s))
    out["citp_commits"] = sum(1 for h, s in subj if re.search(r"CIT-P", s))
    def added(path):
        o = git("log", f"--since=@{a}", f"--until=@{b}", "--diff-filter=A", "--name-only", "--format=", "--", path)
        return len(set(x for x in o.split("\n") if x))
    out["reviews_files"] = added("governance/project/orchestration/reviews")
    out["packages_files"] = added("governance/project/orchestration/packages")
    out["close_records_files"] = added("governance/project/orchestration/closes")
    closed = []
    for l in open(C.ORCH + "/dispatch/land-done.txt", errors="replace"):
        m = re.match(r"^(\d{4}-\d\d-\d\d \d\d:\d\d:\d\d) (\S+)=\S+ (.*)$", l)
        if m and a <= C.epoch(m.group(1)) <= b: closed.append((m.group(2), m.group(3)))
    out["land_closed"] = sum(1 for t, o in closed if o.startswith("CLOSED"))
    out["land_closed_tickets"] = len(set(t for t, o in closed if o.startswith("CLOSED")))
    out["land_ejected"] = sum(1 for t, o in closed if "ejected" in o)
    out["land_no_outcome"] = sum(1 for t, o in closed if o.startswith("no outcome"))
    out["land_not_landed_still_approved"] = sum(1 for t, o in closed if "still approved" in o)
    return out
OUTJ["produced"] = {wn: produced(w) for wn, w in C.WINDOWS.items()}
# register version rows with blame time (uncommitted rows: today)
reg = REPO + "/docs/DECISION_REGISTER.md"
lines = open(reg, errors="replace").read().split("\n")
rows = [(i + 1, l) for i, l in enumerate(lines) if re.match(r"^\| 0\.5\d\d \|", l)]
bl = subprocess.run(["git", "-C", REPO, "blame", "--line-porcelain"] + sum([["-L", f"{n},{n}"] for n, _ in rows], []) + ["--", "docs/DECISION_REGISTER.md"], capture_output=True, text=True).stdout
times = []; cur = None
for l in bl.split("\n"):
    m = re.match(r"^([0-9a-f]{40}) \d+ \d+", l)
    if m: cur = m.group(1)
    if l.startswith("committer-time "):
        t = int(l.split()[1]); times.append(t if cur and not set(cur) == {"0"} else None)
dec = []
for (n, l), t in zip(rows, times):
    ver = re.match(r"^\| (0\.5\d\d) \|", l).group(1)
    ids = re.findall(r"DEC-861\)[:;] DEC-(\d+)", l) or re.findall(r"DEC-(\d+)", l)
    dt_ = re.match(r"^\| 0\.5\d\d \| (\d{4}-\d\d-\d\d)", l).group(1)
    uncommitted = t is None
    te = C.NOW if uncommitted else t
    dec.append((ver, dt_, te, ids[0] if ids else None, uncommitted))
def decs(w): 
    r = [d for d in dec if w[0] <= d[2] <= w[1]]
    return dict(version_rows=len(r), first=r[0][0] if r else None, last=r[-1][0] if r else None, uncommitted_rows=sum(1 for d in r if d[4]),
                first_dec=r[0][3] if r else None, last_dec=r[-1][3] if r else None)
OUTJ["decisions"] = {wn: decs(w) for wn, w in C.WINDOWS.items()}
OUTJ["now"] = C.fmt(C.NOW)
json.dump(OUTJ, open(HERE + ("/tables.json" if UF == "units.jsonl" else "/tables-" + UF.replace("units-", "").replace(".jsonl", "") + ".json"), "w"), indent=1)
print("ok", {wn: (round(OUTJ[wn]["total_usd"], 1), round(OUTJ[wn]["pts_total"], 1), round(OUTJ[wn]["pts_unattributed"], 1)) for wn in "AB"})
