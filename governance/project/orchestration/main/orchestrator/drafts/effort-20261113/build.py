#!/usr/bin/env python3
"""Where the effort went (owner's question, 2026-11-13): builds units.jsonl (one row per session / run / land / wait slice)
from the records that exist. Read-only on everything but its own output. Usage: python3 -I build.py [--W minutes]
Every unit carries q: 'M' measured (a cost or a time from a record) or 'E' estimated (a rule applied; see METHOD in REPORT.md)."""
import json, os, re, glob, sys, subprocess, collections, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("common", HERE + "/common.py"); C = importlib.util.module_from_spec(spec); spec.loader.exec_module(C)
ORCH, REPO, PROJ = C.ORCH, C.REPO, C.PROJ
WMIN = 30.0
for i, a in enumerate(sys.argv):
    if a == "--W": WMIN = float(sys.argv[i + 1])
OUTNAME = "units.jsonl" if WMIN == 30.0 else f"units-W{int(WMIN)}.jsonl"
START, END = C.LIFT - 86400, C.NOW   # collect from a day before the lift, clip later

units = []
def add(**k):
    k.setdefault("usd", 0.0); k.setdefault("lead_h", 0.0); k.setdefault("sess_h", 0.0); k.setdefault("q", "M"); k.setdefault("usd_q", "M")
    units.append(k)
def jl(p):
    out = []
    for l in open(p, errors="replace"):
        l = l.strip()
        if l:
            try: out.append(json.loads(l))
            except ValueError: pass
    return out
def rd_result(p):
    try: t = open(p, errors="replace").read()
    except OSError: return None
    if "total_cost_usd" not in t: return None
    dec = json.JSONDecoder(); i = 0; last = None
    while True:
        j = t.find("{", i)
        if j < 0: break
        try: o, e = dec.raw_decode(t, j)
        except ValueError: i = j + 1; continue
        if isinstance(o, dict) and "total_cost_usd" in o: last = o
        i = e if isinstance(o, dict) else j + 1
    return last

# ---------------------------------------------------------------- the lead ledger (143 runs) -> intervals per ticket
LED = jl(C.OUT + "/lead-ledger-window.jsonl")
runs_by_w2 = collections.defaultdict(list)
for r in LED:
    s = C.epoch(r["start"]); e = C.epoch(r["end"]) if r["end"] else (C.NOW if r["running"] else None)
    if e is None and r["wall_minutes"]: e = s + r["wall_minutes"] * 60
    r["_s"], r["_e"] = s, (e if e is not None else s)
    runs_by_w2[r["W2"]].append(r)

# ---------------------------------------------------------------- git: events for the CTO's turns, and what was produced
def git(*a):
    return subprocess.run(["git", "-C", REPO] + list(a), capture_output=True, text=True).stdout
def cls_files(files, subject):
    if re.match(r"ACT-", subject): return (3, "CTO: ACTs (artefact timing)")
    cnt = collections.Counter()
    for f in files:
        if f.startswith("governance/project/orchestration/packages/"): cnt[(4, "CTO: packages and CIT-Ps")] += 1
        elif f.startswith("governance/project/orchestration/closes/"): cnt[(4, "CTO: close records")] += 1
        elif f.startswith("governance/project/orchestration/reviews/") or f.startswith("docs/probes"): cnt[(2, "CTO: narrow checks and review records")] += 1
        elif f in ("docs/DECISION_REGISTER.md", "governance/project/orchestration/DECISIONS-IN-FORCE.md"): cnt[(5, "CTO: decisions (register)")] += 1
        elif f.startswith("governance/project/orchestration/nightly/"): cnt[(7, "CTO: nightly record")] += 1
        else: cnt[(5, "CTO: orchestration (tickets, tools, notes, briefs)")] += 1
    if not cnt: return (5, "CTO: orchestration (tickets, tools, notes, briefs)")
    order = [(4, "CTO: packages and CIT-Ps"), (4, "CTO: close records"), (2, "CTO: narrow checks and review records"), (5, "CTO: decisions (register)"), (7, "CTO: nightly record"), (5, "CTO: orchestration (tickets, tools, notes, briefs)")]
    top = max(cnt.values())
    for k in order:
        if cnt.get(k) == top: return k
raw = git("log", "--first-parent", f"--since=@{int(START)}", "--name-only", "--format=%x1e%H%x1f%ct%x1f%P%x1f%s")
events = []; commits = []
for rec in raw.split("\x1e"):
    if not rec.strip(): continue
    head, _, files = rec.partition("\n")
    h, ct, p, s = head.split("\x1f")
    merge = len(p.split()) > 1
    fl = [f for f in files.split("\n") if f]
    k = (7, "CTO: merges and lands (hand merges)") if merge else cls_files(fl, s)
    events.append((int(ct), k)); commits.append((int(ct), h, s, merge, fl))
for p in glob.glob(ORCH + "/acts/**", recursive=True):
    if os.path.isfile(p):
        m = os.path.getmtime(p)
        if m >= START: events.append((m, (3, "CTO: ACTs (artefact timing)")))
for p in glob.glob(ORCH + "/briefs/*"):
    m = os.path.getmtime(p)
    if m >= START: events.append((m, (5, "CTO: orchestration (tickets, tools, notes, briefs)")))
events.sort(key=lambda x: x[0])
ev_t = [e[0] for e in events]
import bisect
def event_class(t):
    i = bisect.bisect_left(ev_t, t)
    if i < len(events) and ev_t[i] - t <= WMIN * 60: return events[i][1]
    return (5, "CTO: orchestration (no artefact within the window)")

# ---------------------------------------------------------------- CTO sessions (main transcripts)
CTO = ["8ddb8b14-0dce-4faa-9cb0-7150fcce200d", "b40cba91-6c08-4f82-b30e-591a4b93fb70", "b2f0511f-891b-4874-8930-6d34ca5972ea", "f3886235-4854-4c91-9cf3-1a1dd009cb50"]
GAP = 600.0
cto_msgs = 0
for sid in CTO:
    msgs = C.read_transcript(f"{PROJ}/{sid}.jsonl")
    prev = None
    for (t, model, usd, outt) in msgs:
        if t < START or t > END: prev = t; continue
        b, sub = event_class(t)
        hrs = (t - prev) / 3600 if (prev is not None and t - prev <= GAP) else 0.0
        prev = t
        add(kind="cto", id=sid[:8], label=f"CTO session {sid[:8]}", bucket=b, sub=sub, t0=t, t1=t, usd=usd, sess_h=hrs, q="E", usd_q="M", model=C.tier(model))
        cto_msgs += 1

# ---------------------------------------------------------------- CTO helpers (subagent transcripts)
def helper_class(atype, desc):
    d = desc or ""
    if re.search(r"\bACT\b|ACT-|COPIES|\bACTs\b", d):
        if atype == "independent-auditor" or re.search(r"[Rr]eview", d): return (3, "ACTs: reviewing")
        if re.search(r"[Rr]ehears|[Dd]ry-run", d): return (3, "ACTs: rehearsing")
        return (3, "ACTs: building")
    if atype == "independent-auditor": return (2, "helper reviews and narrow checks")
    if re.search(r"CIT-P|package|DIF |supersede|records|Ticket lines|decision", d): return (4, "helper: CIT-Ps, records, packages")
    return (6, "helpers (research, briefs, tools, sweeps)")
helper_files = []
for sid in CTO:
    for mp in glob.glob(f"{PROJ}/{sid}/subagents/**/*.meta.json", recursive=True):
        try: meta = json.load(open(mp))
        except ValueError: meta = {}
        jp = mp[:-len(".meta.json")] + ".jsonl"
        if not os.path.exists(jp): continue
        msgs = [m for m in C.read_transcript(jp) if START <= m[0] <= END]
        if not msgs: continue
        b, sub = helper_class(meta.get("agentType"), meta.get("description"))
        span = (msgs[-1][0] - msgs[0][0]) / 3600
        usd_tot = sum(m[2] for m in msgs)
        helper_files.append((usd_tot, sid[:8], os.path.basename(jp)[:14], meta.get("agentType"), b, sub, span))
        n = len(msgs)
        for (t, model, usd, outt) in msgs:
            add(kind="helper", id=f"{sid[:8]}/{os.path.basename(jp)[6:14]}", label=f"helper {meta.get('agentType')} {os.path.basename(jp)[6:14]} (of {sid[:8]})", bucket=b, sub=sub,
                t0=t, t1=t, usd=usd, sess_h=span / n, q="E", hours_q="M", usd_q="M", model=C.tier(model), unit=f"{sid[:8]}/{os.path.basename(jp)[6:14]}", atype=meta.get("agentType"), desc_tok=(re.search(r"(ACT-[A-Z0-9-]+|W2-\d+[a-z]?)", meta.get("description") or "") or [None])[0])

# ---------------------------------------------------------------- ambient sessions in the project folder (not CTO, not helpers)
amb = collections.Counter()
for p in glob.glob(PROJ + "/*.jsonl"):
    sid = os.path.basename(p)[:-6]
    if sid in CTO or os.path.getmtime(p) < START: continue
    msgs = [m for m in C.read_transcript(p) if START <= m[0] <= END]
    for (t, model, usd, outt) in msgs:
        add(kind="ambient", id=sid[:8], label=f"ambient session {sid[:8]} ({C.tier(model)})", bucket="U", sub="unplaced: usage recorder, sentinel, dead-man, side sessions", t0=t, t1=t, usd=usd, sess_h=0.0, q="M", usd_q="M", model=C.tier(model), unit=sid[:8])
        amb[sid[:8]] += usd

# ---------------------------------------------------------------- launched workers
sp = jl(ORCH + "/log/spend.jsonl")
seen = set(); wk = []
for d in sp:
    if d.get("kind") != "launched": continue
    ex = d.get("extra") or {}
    lg = ex.get("log"); sid = ex.get("session_id")
    res = rd_result(lg) if lg and os.path.exists(lg) else None
    key = sid or (res or {}).get("session_id") or (lg, d.get("at"))
    if key in seen and res is not None: continue
    seen.add(key)
    at = C.epoch(d["at"])
    usd = (res or {}).get("total_cost_usd", d.get("cost_usd"))
    wk.append(dict(d=d, ex=ex, lg=lg, res=res, at=at, usd=usd))
def inside_lead(w2, s, e):
    for r in runs_by_w2.get(w2, []):
        if r["_s"] - 180 <= s and e <= r["_e"] + 180: return True
    return False
import statistics
_spd = collections.defaultdict(list)
for w in wk:
    if w["res"] and w["usd"] and (w["res"].get("duration_ms") or 0) > 0:
        _spd[w["d"].get("role")].append(w["res"]["duration_ms"] / 1000.0 / w["usd"])
SPD = {k: statistics.median(v) for k, v in _spd.items()}
nrefused = 0; failed_w = []; nolog = 0
win_lo = START
for w in wk:
    d, res, lg = w["d"], w["res"], w["lg"]
    role = d.get("role"); wbs = d.get("wbs"); n = os.path.basename(lg or "")[:-5] if lg else ""
    if w["usd"] is None:
        if w["at"] >= START: nrefused += 1
        continue
    hq = "M"
    if res is None:   # the worktree's log is gone: the spend row's cost (measured), its minute as the end, the duration est. from the role's median seconds per dollar
        end = w["at"] + 30; dur = w["usd"] * SPD.get(role, 600.0); hq = "E"; nolog += 1
        res = {"is_error": (d.get("extra") or {}).get("is_error")}
    else:
        end = os.path.getmtime(lg)
        dur = (res.get("duration_ms") or 0) / 1000.0
    start = end - dur
    bad = bool(res.get("is_error")) or str((w["ex"] or {}).get("exit", "0")) not in ("0", "None")
    m = re.match(r"^(td|eng)-r?(\d+)", n)
    rnd = int(m.group(2)) if m else None
    if "ACT-" in n:
        b, sub = (3, "ACTs: reviewing") if role == "independent-auditor" else (3, "ACTs: building")
    elif re.search(r"merge|premerge", n): b, sub = 1, "land: merge and premerge workers"
    elif role == "independent-auditor":
        b, sub = (2, "narrow checks and probes") if re.search(r"probe|check|default", n) else (2, "independent reviews (ticket review rounds)")
    elif role == "independent-test-designer": b, sub = 1, "tests (designers)"
    else: b, sub = 1, "build (engineers, product-spec, research)"
    q = "M"
    if bad: b, sub = 8, "8a failed or errored worker (measured)"
    elif rnd and rnd >= 2 and b == 1 and sub.startswith(("tests", "build")):
        sub = "8b redo rounds: " + ("tests" if sub.startswith("tests") else "build") + " round >= 2 (est.)"; b = 8; q = "E"
    add(kind="worker", id=f"{wbs}/{n}", label=f"{wbs} {role} {n}", bucket=b, sub=sub, t0=start, t1=end, usd=w["usd"], sess_h=dur / 3600,
        q=q, usd_q="M", hours_q=hq, model=C.tier(d.get("model")), w2=wbs, inside_lead=inside_lead(wbs, start, end), role=role, rnd=rnd, unit=f"{wbs}/{n}")

# ---------------------------------------------------------------- lead runs, split by what its workers were doing
def phase_bucket(wk_):
    nm, ph = wk_["name"], wk_["phase"]
    if not wk_.get("worker"): return (1, "lead own time: verify, accept, merge, reading returns (no worker running)")
    if ph == "tests": return (1, "tests (designers)")
    if ph == "build": return (1, "build (engineers, product-spec, research)")
    if ph == "review": return (2, "independent reviews (ticket review rounds)")
    if re.match(r"^(au|rev|rv|probe)", nm): return (2, "independent reviews (ticket review rounds)")
    return (1, "build (engineers, product-spec, research)")
BAD = ("ERROR", "NO_STATUS", "LAUNCH_BLOCKED", "REFUSED")
for r in LED:
    s, e = r["_s"], r["_e"]
    if e <= s: continue
    usd = r["cost"]["lead_usd"]
    if r["status"] in BAD: parts = {(8, "8a failed or errored lead run (measured)"): 1.0}; q = "M"
    else:
        # sweep: partition [s,e] by the workers' intervals (LLM workers by phase; tool steps as lead's own)
        pts = {s, e}
        ivs = []
        for w in r["workers"]:
            ws = C.epoch(w["start"]); we = C.epoch(w["end"]) if w["end"] else (C.NOW if w["running"] else None)
            if ws is None or we is None: continue
            ws, we = max(ws, s), min(we, e)
            if we > ws: ivs.append((ws, we, phase_bucket(w))); pts.update((ws, we))
        P = sorted(pts); parts = collections.Counter()
        for a, b2 in zip(P, P[1:]):
            act = [iv[2] for iv in ivs if iv[0] <= a and iv[1] >= b2]
            llm = [k for k in act if not k[1].startswith("land and verify")]
            use = llm or act
            if not use: parts[(1, "lead own time: verify, accept, merge, reading returns (no worker running)")] += b2 - a
            else:
                for k in use: parts[k] += (b2 - a) / len(use)
        tot = sum(parts.values()) or 1
        parts = {k: v / tot for k, v in parts.items()}; q = "E"
    # hours: one piece per bucket by time share (est.); cost: the lead's own measured total, whole, in one piece (bucket 1, or 8 when the run failed)
    for k, share in parts.items():
        add(kind="lead", id=f"{r['W2']}/{r['run']}", label=f"lead {r['W2']} {r['run']} ({r['status']})", bucket=k[0], sub=k[1], t0=s, t1=e,
            usd=0.0, lead_h=(e - s) / 3600 * share, q=q, usd_q="M", model="opus", w2=r["W2"], unit=f"{r['W2']}/{r['run']}", status=r["status"])
    if usd:
        bk = (8, "8a failed or errored lead run (measured)") if r["status"] in BAD else (1, "lead's own session cost (orchestration, verify, accept, land; all phases)")
        add(kind="lead", id=f"{r['W2']}/{r['run']}", label=f"lead {r['W2']} {r['run']} ({r['status']})", bucket=bk[0], sub=bk[1], t0=s, t1=e,
            usd=usd, lead_h=0.0, q="M", usd_q="M", model="opus", w2=r["W2"], unit=f"{r['W2']}/{r['run']}", status=r["status"])

# ---------------------------------------------------------------- landing queue (machine hours, no LLM) and the nightly
dl = open(ORCH + "/dispatch/dispatch.log", errors="replace").read().split("\n")
starts = []
lands = []
for l in dl:
    m = re.match(r"^(\d{4}-\d\d-\d\d \d\d:\d\d:\d\d) land started: \[(.*?)\] -> (\S+)", l)
    if m: starts.append([C.epoch(m.group(1)), m.group(2), m.group(3), None, None]); continue
    m = re.match(r"^(\d{4}-\d\d-\d\d \d\d:\d\d:\d\d) land finished: (\{.*\})", l)
    if m and starts and starts[-1][3] is None:
        starts[-1][3] = C.epoch(m.group(1)); starts[-1][4] = m.group(2)
for s_, tk, out, e_, res in starts:
    if s_ is None or (e_ or C.NOW) < START: continue
    e_ = e_ or C.NOW
    outcomes = re.findall(r"'([^']+)': '([^']*)'", res or "")
    n = max(len(outcomes), 1)
    bad = [o for o in outcomes if o[1] != "CLOSED"]
    lands.append((s_, e_, out, outcomes))
    nb = len(bad) if res else 0
    if res is None: share_bad = 0.0
    else: share_bad = nb / n
    hrs = (e_ - s_) / 3600
    if hrs <= 0: continue
    if share_bad < 1: add(kind="land", id=out, label=f"landing run {out[14:-4]} ({n} ticket(s))", bucket=7, sub="landing queue (machine hours, no LLM)", t0=s_, t1=e_, sess_h=hrs * (1 - share_bad), q="M", running=(res is None))
    if share_bad > 0: add(kind="land", id=out, label=f"landing run {out[14:-4]} ejections", bucket=8, sub="8a ejected or refused landing (measured outcome; hours share est.)", t0=s_, t1=e_, sess_h=hrs * share_bad, q="E")
hist = jl(ORCH + "/log/nightly/history.jsonl")
for h in hist:
    t1 = h.get("when"); a = h.get("actual_s")
    if t1 and a and t1 >= START:
        add(kind="nightly", id=f"nightly {C.fmt(t1)}", label=f"nightly run ending {C.fmt(t1)}", bucket=7, sub="nightly (machine hours, no LLM)", t0=t1 - a, t1=t1, sess_h=a / 3600, q="M")

# ---------------------------------------------------------------- waiting (ticket-hours, owner stand-by, gate, slot)
for r in LED:
    for w in r["waits"]:
        if w["kind"] in ("waiting on the CTO or the owner", "launch refusal", "brake"):
            a, b = C.epoch(w["from"]), (C.epoch(w["to"]) if w["to"] else (C.NOW if w.get("open") else None))
            if a and b and b > a:
                add(kind="wait", id=f"{r['W2']}/{r['run']}", label=f"ticket {r['W2']} waits ({w['kind']})", bucket=9, sub="ticket waits: " + ("on the CTO or the owner (between lead runs)" if w["kind"].startswith("waiting") else "on the gate or a launch refusal"), t0=a, t1=b, sess_h=(b - a) / 3600, q="M", ticket_h=True)
for h in jl(ORCH + "/log/heavy-slot-waits.jsonl"):
    t = C.epoch(h["t"])
    if t and t >= START:
        add(kind="wait", id="slot", label="heavy-slot wait", bucket=9, sub="slot waits for a test run (carved out of lead or worker hours)", t0=t - h["waited_s"], t1=t, sess_h=h["waited_s"] / 3600, q="M", slot=True)
for p in sorted(glob.glob(ORCH + "/log/cto-standby.ended-*.txt")):
    nm = os.path.basename(p)
    me = re.search(r"ended-(\d{8})T(\d\d)(\d\d)(\d\d)", nm) or re.search(r"ended-(\d{8})-(\d\d)(\d\d)()", nm)
    if not me: continue
    d8 = me.group(1); en = C.epoch(f"{d8[:4]}-{d8[4:6]}-{d8[6:]} {me.group(2)}:{me.group(3)}:{me.group(4) or '00'}")
    txt = open(p, errors="replace").read(400)
    mm = re.search(r"since (\d{4}-\d\d-\d\d \d\d:\d\d)", txt) or re.match(r"^(\d{4}-\d\d-\d\d \d\d:\d\d)", txt)
    st = C.epoch(mm.group(1)) if mm else None
    if st and en and en > st and en >= START:
        add(kind="wait", id=nm, label="CTO stand-by (waiting on the owner or session switch)", bucket=9, sub="memo: CTO stand-by files (inside the CTO idle gaps)", t0=st, t1=en, sess_h=(en - st) / 3600, q="M", memo=True)
# CTO idle: gaps between the CTO's own turns, over 10 min and under 12 h (a longer gap is a session break); cause is not recorded
for sid in CTO:
    ts = [m[0] for m in C.read_transcript(f"{PROJ}/{sid}.jsonl")]
    for a_, b_ in zip(ts, ts[1:]):
        if 600 < b_ - a_ < 43200 and b_ >= START and a_ <= END:
            add(kind="wait", id=f"cto-idle {sid[:8]}", label=f"CTO idle {sid[:8]}", bucket=9, sub="CTO idle between turns (>10 min; owner, leads or queue: cause not recorded)", t0=a_, t1=b_, sess_h=(b_ - a_) / 3600, q="E", cto_idle=True)

json.dump(dict(nolog=nolog, WMIN=WMIN, NOW=C.NOW, LIFT=C.LIFT, cto_msgs=cto_msgs, nrefused=nrefused, amb=dict(amb)), open(C.OUT + "/build-meta.json", "w"))
with open(C.OUT + "/" + OUTNAME, "w") as f:
    for u in units: f.write(json.dumps(u) + "\n")
json.dump([x for x in helper_files], open(C.OUT + "/helpers.json", "w"))
json.dump([(a, b, c_, d_) for a, b, c_, d_ in lands], open(C.OUT + "/lands.json", "w"), default=str)
json.dump([[c0, h, s, m, fl[:6]] for c0, h, s, m, fl in commits], open(C.OUT + "/commits.json", "w"))
print("workers with no log, duration est.:", nolog, ";", len(units), "units;", cto_msgs, "CTO messages; refused/no-cost worker rows:", nrefused, "; lands:", len(lands), "ambient total", round(sum(amb.values()), 2))
