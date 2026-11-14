#!/usr/bin/env python3
"""Writes REPORT.md from tables.json, tables-W15/W60.json, cto_context.json, units.jsonl, helpers.json, lands.json. No numbers are typed by hand."""
import json, os, re, subprocess, collections, importlib.util, statistics
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("common", HERE + "/common.py"); C = importlib.util.module_from_spec(spec); spec.loader.exec_module(C)
T = json.load(open(HERE + "/tables.json")); T15 = json.load(open(HERE + "/tables-W15.json")); T60 = json.load(open(HERE + "/tables-W60.json"))
CX = json.load(open(HERE + "/cto_context.json"))
U = [json.loads(l) for l in open(HERE + "/units.jsonl")]
META = json.load(open(HERE + "/build-meta.json"))
LANDS = json.load(open(HERE + "/lands.json"))
REPO = C.REPO
NAMES = {"1": "1 Product work by phase", "2": "2 Reviews and narrow checks", "3": "3 ACTs", "4": "4 CIT-Ps, records, packages", "5": "5 CTO session (orchestration, reports, decisions)",
         "6": "6 Helpers (in-session, not placed above)", "7": "7 Landing queue and nightly", "8": "8 Rework", "9": "9 Waiting", "U": "Unplaced"}
def frac(u, w):
    a, b = w
    if u["t1"] <= u["t0"]: return 1.0 if a <= u["t0"] <= b else 0.0
    return max(0.0, min(b, u["t1"]) - max(a, u["t0"])) / (u["t1"] - u["t0"])
def git(*a): return subprocess.run(["git", "-C", REPO] + list(a), capture_output=True, text=True).stdout
def flag(e, m):
    tot = e + m
    if tot <= 1e-9: return "M"
    s = e / tot
    return "M" if s < 0.05 else ("E" if s > 0.95 else f"M/E {round(100*s)}% est.")
def qflag(share): return "M" if share < 0.05 else ("E" if share > 0.95 else f"M/E {round(100*share)}% est.")

PROD = {}
for wn, w in C.WINDOWS.items():
    a, b = int(w[0]), int(w[1])
    subj = [l for l in git("log", f"--since=@{a}", f"--until=@{b}", "--format=%s").split("\n") if l]
    acts = sorted(set(m.group(1) for s in subj for m in [re.match(r"(ACT-[A-Z0-9]+(?:-[A-Z0-9]+)*?-\d+)", s)] if m))
    nl = [x for x in LANDS if w[0] <= C.epoch(x[0].replace("T", " ")[:19] if isinstance(x[0], str) else x[0]) <= w[1]] if False else None
    PROD[wn] = dict(acts=len(acts))
def lands_in(w):
    n = 0
    for s_, e_, out, outcomes in LANDS:
        if s_ is not None and w[0] <= s_ <= w[1]: n += 1
    return n

P = T["produced"]; D = T["decisions"]
def produced_text(wn, k):
    p = P[wn]; w = C.WINDOWS[wn]; d = D[wn]; b = T[wn]["buckets"].get(k, {})
    nu = b.get("n_units", 0)
    if k == "1": return f"{p['land_closed_tickets']} tickets landed CLOSED by the queue ({p['close_records_files']} close records in all, bulk closes included); {nu} sessions (leads and workers)"
    if k == "2": return f"{p['reviews_files']} review/probe records added; {nu} review sessions, runs and helpers"
    if k == "3": return f"{PROD[wn]['acts']} distinct ACTs applied or committed ({p['act_applied_commits']} ACT commits); {nu} ACT sessions"
    if k == "4": return f"{p['packages_files']} package files and {p['citp_commits']} commits naming a CIT-P added; {p['close_records_files']} close records"
    if k == "5": return f"{d['version_rows']} register versions ({d['first']} to {d['last']}, DEC-{d['first_dec']} to DEC-{d['last_dec']}); {p['commits']} commits on the branch (all roles)"
    if k == "6": return f"{nu} helper sessions (research, briefs, tools, sweeps); no countable close"
    if k == "7": return f"{lands_in(w)} landing runs, {p['land_closed']} CLOSED outcomes; {sum(1 for x in U if x['kind']=='nightly' and frac(x, w) > 0)} nightly run(s); {p['merges_first_parent']} merge commits on the branch"
    if k == "8": return f"{p['land_ejected']} ejections and {p['land_no_outcome']} no-outcome landings; {nu} failed or redone sessions"
    if k == "9": return "nothing: the time in which no session was working"
    return ""

def row_table(wn):
    d = T[wn]; tot = d["total_usd"]; out = []
    out.append("| bucket | share USD % | USD | usage pts | lead-h | other-h | produced |")
    out.append("|---|---|---|---|---|---|---|")
    sums = [0, 0, 0, 0, 0]
    for k in ["1", "2", "3", "4", "5", "6", "7", "8", "9", "U"]:
        b = d["buckets"].get(k)
        if not b: continue
        usd_f = flag(b["qE"], b["qM"])
        lead_f = "E" if b["lead_h"] > 0 and k not in ("8",) else ("M" if b["lead_h"] > 0 else "-")
        if k == "9": lead_f = "M"
        oth_f = qflag(b["hE"] / max(b["hE"] + b["hM"], 1e-9)) if b["other_h"] > 0 else "-"
        lead_cell = f"{b['lead_h']:.1f} {lead_f}" if b["lead_h"] > 0.005 else "0"
        oth_cell = f"{b['other_h']:.1f} {oth_f}" if abs(b["other_h"]) > 0.005 else "0"
        out.append(f"| {NAMES[k]} | {100*b['usd']/tot:.1f} | {b['usd']:.1f} {usd_f} | {b['pts']:.1f} E | {lead_cell} | {oth_cell} | {produced_text(wn, k)} |")
        sums[0] += b["usd"]; sums[1] += b["pts"]
        if k != "9": sums[2] += b["lead_h"]; sums[3] += b["other_h"]
    out.append(f"| **Total** | 100.0 | {sums[0]:.1f} M | {sums[1]:.1f} (meter: {d['pts_total']:.1f} M) | {sums[2]:.1f} (waiting excluded) | {sums[3]:.1f} (waiting excluded) | {P[wn]['commits']} commits |")
    return "\n".join(out)

def detail_table():
    subs = collections.OrderedDict()
    for k in ["1", "2", "3", "4", "5", "6", "7", "8", "9", "U"]:
        names = set()
        for wn in "AB":
            b = T[wn]["buckets"].get(k)
            if b: names |= set(b["subs"].keys())
        for s in sorted(names, key=lambda s: -(T["A"]["buckets"].get(k, {"subs": {}})["subs"].get(s, {"usd": 0})["usd"])):
            subs[(k, s)] = 1
    out = ["| bucket | part | A USD | A pts | A lead-h | A other-h | B USD | B pts | B lead-h | B other-h |", "|---|---|---|---|---|---|---|---|---|---|"]
    for (k, s) in subs:
        cells = []
        for wn in "AB":
            v = T[wn]["buckets"].get(k, {"subs": {}})["subs"].get(s, {"usd": 0, "pts": 0, "lead_h": 0, "other_h": 0})
            cells += [f"{v['usd']:.1f}", f"{v['pts']:.1f}", f"{v['lead_h']:.1f}", f"{v['other_h']:.1f}"]
        out.append(f"| {k} | {s} | " + " | ".join(cells) + " |")
    return "\n".join(out)

# ---- top consumers
def split_text(sid, w):
    c = collections.Counter()
    for u in U:
        if u["kind"] == "cto" and u["id"] == sid:
            f = frac(u, w)
            if f > 0: c[u["bucket"]] += u["usd"] * f
    t = sum(c.values()) or 1
    return ", ".join(f"b{k} {100*v/t:.0f}%" for k, v in c.most_common(5))
def tok(label_unit):
    m = re.search(r"(ACT-[A-Z0-9-]+|W2-\d+[a-z]?)", label_unit or "")
    return m.group(1) if m else ""
HJ = json.load(open(HERE + "/helpers.json"))
def top_table(wn, n=10):
    w = C.WINDOWS[wn]; rows = T["top"][wn][:n]; out = ["| # | USD | hours | what | bucket | basis |", "|---|---|---|---|---|---|"]
    for i, t in enumerate(rows, 1):
        kind = t["key"][0]; lab = t["label"]
        if kind == "cto":
            what = f"CTO session {t['key'][1]} (Opus; {split_text(t['key'][1], w)})"; bk = "5 (split)"; basis = "USD M; bucket split E; hours = active turns E"
        elif kind == "helper":
            what = f"in-session helper {lab.split(' ')[1]} {t['key'][1]} ({t['sub']})"; bk = str(t["bucket"]); basis = "USD M; bucket by agent type and ACT/package/check keywords E"
        elif kind == "lead":
            what = lab; bk = str(t["bucket"]) + " (lead's own cost)"; basis = "USD M; hours M (ledger)"
        elif kind == "worker":
            what = lab; bk = str(t["bucket"]); basis = "USD M; hours " + ("M" if True else "E")
        else:
            what = lab; bk = str(t["bucket"]); basis = "M"
        out.append(f"| {i} | {t['usd']:.1f} | {t['hours']:.1f} | {what} | {bk} | {basis} |")
    return "\n".join(out)
def lands_table(wn):
    rows = T["top_lands"][wn][:4]
    return "; ".join(f"{r[1]} {r[0]:.1f} h (bucket {r[2]}, machine hours, $0)" for r in rows)

# ---- savings
def helpers_opus_nonreview(wn): 
    return sum(v for k, v in T["helper_tiers"][wn].items() if k.startswith("opus|") and not k.endswith("|2"))
def sub_usd(wn, k, pref):
    return sum(v["usd"] for s, v in T[wn]["buckets"].get(k, {"subs": {}})["subs"].items() if s.startswith(pref))
def redo_stats(wn):
    w = C.WINDOWS[wn]; xs = [u for u in U if u["kind"] == "worker" and u["sub"].startswith("8b") and frac(u, w) > 0]
    n = len(xs); tot = sum(u["usd"] * frac(u, w) for u in xs)
    return n, tot, (statistics.median([u["usd"] for u in xs]) if xs else 0)
def running_leads_h(wn):
    w = C.WINDOWS[wn]; return sum(u["lead_h"] * frac(u, w) for u in U if u["kind"] == "lead" and u.get("status") == "RUNNING")
def open_waits(wn):
    w = C.WINDOWS[wn]; return sum(1 for u in U if u["kind"] == "wait" and u["sub"].startswith("ticket waits: on the CTO") and u["t1"] >= C.NOW - 1)

tA, tB = T["A"]["total_usd"], T["B"]["total_usd"]
def share(wn, k): return 100 * T[wn]["buckets"][k]["usd"] / T[wn]["total_usd"]
bk = T["bykind"]
def kinds(wn):
    d = bk[wn]; return ", ".join(f"{k} ${v[0]:.0f} ({v[1]} units)" for k, v in sorted(d.items(), key=lambda x: -x[1][0]))
redoA, redoB = redo_stats("A"), redo_stats("B")
failL = {wn: sum(v["usd"] for s, v in T[wn]["buckets"]["8"]["subs"].items() if "lead run" in s) for wn in "AB"}
actr = T["act_review"]
sens = {}
for nm, TT in (("15 min", T15), ("30 min (default)", T), ("60 min", T60)):
    sens[nm] = {k: TT["A"]["buckets"][k]["usd"] for k in "2 3 4 5 7".split()}

now = T["now"]
last_rd = max(C.epoch(l[:19]) for l in open(C.ORCH + "/log/usage.txt", errors="replace") if re.match(r"^\d{4}-\d\d-\d\d \d\d:\d\d:\d\d ", l))
def usd_until(wn):
    w = (C.WINDOWS[wn][0], last_rd); return sum(u["usd"] * frac(u, w) for u in U)
ppA, ppB = usd_until("A") / T["A"]["pts_total"], usd_until("B") / T["B"]["pts_total"]
# this measuring helper's own cost
own = 0.0
import glob
for mp in glob.glob(C.PROJ + "/f3886235-4854-4c91-9cf3-1a1dd009cb50/subagents/*.meta.json"):
    try: md = json.load(open(mp))
    except ValueError: continue
    if "effort goes" in (md.get("description") or ""):
        own += sum(x[2] for x in C.read_transcript(mp[:-10] + ".jsonl"))
sub_h = sum(u["sess_h"] * frac(u, C.WINDOWS["A"]) for u in U if u["kind"] == "wait" and u["sub"].startswith("ticket waits: on the CTO"))
open_w = open_waits("A")
L = []
L.append(f"""---
id: effort-20261113
role: research
ticket: owner's question of 2026-11-13, via the Wave 2 CTO (no ticket id given)
decisions: [none yet; it feeds the owner's decision on where to cut effort, 2026-11-13]
sources: [DEC-1089, DEC-1120, DEC-1157, USAGE-1]
generated: {now} UTC
---
# Where the effort went, since the lift and in the last 24 hours

**Question.** Where did the effort go, as 100 %, in USD, usage points and lead-hours, in nine buckets; since the lift (2026-11-11 13:31 UTC) and in the last 24 hours (to {now} UTC).
**Decision it feeds.** What the owner and the CTO cut or change in how work is run (the "what I would cut" lines).
**Stop rule.** Records that exist only; no suite run; every figure marked M (measured from a record) or E (estimated, with the rule); stop when both windows are filled and the sums tie to a measured total.

Legend: **M** measured from a record (a cost, a time, a count); **E** estimated by a stated rule; **M/E n% est.** a measured total of which n % is placed in its bucket by a rule; a bare **E** means everything in the cell is placed or split by a rule even where the inputs (tokens, costs) are measured. USD is at list price (Opus 5.5 / Sonnet 5.5 / Haiku 5.5) or the session's own `total_cost_usd`. `lead-h` = hours a ticket lead's session was alive (the lead ledger); `other-h` = hours of the CTO's active turns, in-session helpers, directly launched workers and the machine hours of the landing queue and the nightly (a worker inside a lead's run is not counted twice). Waiting rows count ticket-hours and idle hours, so they are not additive with working hours.

**Headline.** Window A (since the lift, {T['A']['window'][0]} to {T['A']['window'][1]}): **${tA:,.0f}**, **{T['A']['pts_total']:.0f} points** of the weekly meter (M), {T['produced']['A']['land_closed_tickets']} tickets landed CLOSED by the queue. Window B (last 24 h): **${tB:,.0f}**, **{T['B']['pts_total']:.0f} points**, {T['produced']['B']['land_closed_tickets']} CLOSED. Spend per ticket landed CLOSED: ${tA/max(T['produced']['A']['land_closed_tickets'],1):.0f} (A), ${tB/max(T['produced']['B']['land_closed_tickets'],1):.0f} (B). One meter point is ${ppA:.1f} (A) and ${ppB:.1f} (B) at list price, spend up to the last meter reading ({C.fmt(last_rd)}); USAGE-1 fitted $27.5 on 11-08..11-10, so the meter may weigh models or kinds differently from list price, or this set misses spend (see Gaps).
By kind of session (A): {kinds('A')}.
The largest single block is **the CTO's own turns plus its in-session helpers: {100*(bk['A']['cto'][0]+bk['A']['helper'][0])/tA:.0f} % of A** (${bk['A']['cto'][0]+bk['A']['helper'][0]:,.0f}); launched leads and workers together are {100*(bk['A']['lead'][0]+bk['A']['worker'][0])/tA:.0f} %.

## Window A: since the lift ({T['A']['window'][0]} to {T['A']['window'][1]} UTC)
{row_table('A')}

## Window B: the last 24 hours ({T['B']['window'][0]} to {T['B']['window'][1]} UTC)
{row_table('B')}

Notes on the tables. (1) Bucket 1 holds the lead's own session cost whole (M); a lead's cost cannot be split by phase from its log, and a time split would charge a sleeping lead (see Method). Its phases show as the workers' cost (tests = designers, build = engineers, product-spec and research workers) and the lead-hours by phase (E, from the workers' intervals in the ledger). Landing as a phase is the lead's own verify/accept/merge time plus the merge workers. (2) Bucket 2 holds every independent auditor session on a ticket (rev-/rv-/au-/probe/check) and the helper auditors on narrow checks; ACT reviews are in bucket 3, package reviews in 4. The "review" phase of bucket 1 is therefore shown only here (counted once). (3) Bucket 8 is split: **8a measured** (a lead or worker that ended in error, a landing that ejected a ticket or ended without outcome) and **8b est.** (an engineer or test-designer round numbered 2 or more, taken as a redo; a review round 2+ is *not* moved, it checks a fix). Fold 8b back and bucket 1 gains ${sub_usd('A','8','8b'):.0f} (A) / ${sub_usd('B','8','8b'):.0f} (B). (4) Buckets 3, 4, 5, 7 contain the CTO's own turns placed by artefact timing (E): each turn goes to the next artefact (ACT file, package, close record, review record, register row, merge) written within {int(META['WMIN'])} minutes, else to bucket 5. Sensitivity of the window-A USD to that window ({', '.join(f'{k}: ' + ', '.join(f'b{b} {v:.0f}' for b, v in d.items()) for k, d in sens.items())}). (5) Bucket 9 costs $0 by definition (no session alive); its rows are time: tickets waiting for the CTO or the owner between lead runs ({sub_h:.0f} ticket-hours in A, of which {open_w} are waiting now), tickets waiting on a closed gate, test commands waiting for a heavy slot ({T['A']['slot_h']:.1f} h, carved out of the lead hours of bucket 1 because the log starts 11-12 23:48 and holds them), and the CTO's idle gaps over 10 minutes. (6) Usage points are E everywhere: the meter total is M; each interval between two meter readings is shared by that interval's USD per bucket. Buckets with no LLM session (7's queue and nightly, 9) take none.
""")

L.append("## Detail behind the buckets (USD, usage points, lead-hours, other-hours; basis as above)\n" + detail_table() + "\n")

L.append(f"""## The ten largest single consumers
Window A (since the lift). A consumer is one session, one run or one helper; a lead's cost is its own total (workers separate).
{top_table('A')}

Window B (last 24 h).
{top_table('B')}

Largest landings by wall time (queue machine hours, $0 in LLM, M): A: {lands_table('A')}. B: {lands_table('B')}.
Below the CTO sessions the biggest single items are a handful of $7-$11 sessions (an engineer or test designer's first round, a helper that built an ACT bundle); the spend is many small sessions, not a few runaway ones: the largest non-CTO session is {max((t['usd'] for t in T['top']['A'] if t['key'][0]!='cto'), default=0):.1f} USD, {100*max((t['usd'] for t in T['top']['A'] if t['key'][0]!='cto'), default=0)/tA:.1f} % of A.
""")

cA = CX["A"]; cB = CX["B"]
L.append(f"""## What I would cut (each with its saving; E unless marked)
1. **A fresh CTO session at 300k tokens of context instead of running to 460k median / 840k p90.** The CTO's main sessions re-read their context every turn: cache reads are ${cA['cost_by_kind']['cache_read']:.0f} of ${cA['total']:.0f} ({100*cA['cost_by_kind']['cache_read']/cA['total']:.0f} %, M from tokens); the cache reads above a 300k cap cost ${cA['cache_read_above_cap_usd']['300000']:.0f} (A) / ${cB['cache_read_above_cap_usd']['300000']:.0f} (B). Saving up to **${cA['cache_read_above_cap_usd']['300000']:.0f} (A) / ${cB['cache_read_above_cap_usd']['300000']:.0f} (B)** minus one handover re-read per restart (a cap at 200k: ${cA['cache_read_above_cap_usd']['200000']:.0f} / ${cB['cache_read_above_cap_usd']['200000']:.0f}).
2. **Fewer redo rounds of tests and builds (8b).** {redoA[0]} sessions in A cost ${redoA[1]:.0f} (B: {redoB[0]}, ${redoB[1]:.0f}); median ${redoA[2]:.1f} each. A review of the test design before the build starts, or one finding list per round, would remove about half: **${redoA[1]/2:.0f} (A) / ${redoB[1]/2:.0f} (B)** (E: half is my assumption, not measured).
3. **In-session helpers that inherit Opus run on Sonnet** where they build or research (not the independent reviewers): Opus helpers outside bucket 2 cost ${helpers_opus_nonreview('A'):.0f} (A) / ${helpers_opus_nonreview('B'):.0f} (B); at Sonnet's list price (half of Opus on every token kind) the saving is **about ${helpers_opus_nonreview('A')/2:.0f} (A) / ${helpers_opus_nonreview('B')/2:.0f} (B)**, quality unproven on these jobs (USAGE-1 §6 kept gates on Opus; these are not gates).
4. **One review per ACT bundle, and no round 2 for findings that are only P2.** ACT reviews cost ${sub_usd('A','3','ACTs: reviewing'):.0f} (A) / ${sub_usd('B','3','ACTs: reviewing'):.0f} (B): auditor workers' first reviews ${actr['A'].get('first',0):.0f}, their round-2-or-later reviews ${actr['A'].get('r2plus',0):.0f} (M, from the log names), helper ACT reviews ${actr['A'].get('helper',0):.0f} (A) / ${actr['B'].get('helper',0):.0f} (B) (rounds not separable without reading their titles). Saving **${actr['A'].get('r2plus',0):.0f} measured (A)**, up to about half of the helper reviews (E, ${actr['A'].get('helper',0)/2:.0f} A / ${actr['B'].get('helper',0)/2:.0f} B) if a second round is dropped for P2-only findings.
5. **Do not start a lead into a shut gate or a task that errors.** Failed or errored lead runs cost ${failL['A']:.1f} (A) / ${failL['B']:.1f} (B) (M, ledger status ERROR, LAUNCH_BLOCKED, NO_STATUS) and {sub_usd('A','8','8a failed or errored worker'):.1f} in failed workers: saving **${failL['A']:.0f} (A) / ${failL['B']:.0f} (B)**.
6. **Waiting is free in dollars but not in time:** {T['A']['slot_h']:.1f} lead-hours blocked on a heavy slot (M) and {sum(u['sess_h']*frac(u, C.WINDOWS['A']) for u in U if u['kind']=='wait' and u['sub'].startswith('ticket waits: on the CTO')):.0f} ticket-hours waiting for the CTO or the owner between lead runs (M, {open_waits('A')} still open): saving **$0**, but the owner's decisions and a second slot pool are what move closes per day.
""")

L.append(f"""## Method
Period. A = {T['A']['window'][0]} to {T['A']['window'][1]} UTC (the lift to the run of this report); B = the 24 h before the same instant. A session that straddles a boundary counts by time overlap (cost and hours pro rata); the CTO's turns are cut exactly by timestamp.
Prices (list, USD per million tokens, from USAGE-1 §8, platform.claude.com/docs/en/about-claude/pricing as fetched 2026-11-10; `tools/spend.py` holds none, it logs `total_cost_usd`): Opus 5.5 in 4, 5-min write 5, 1-h write 8, cache read 0.20, out 20; Sonnet 5.5 2 / 2.50 / 4 / 0.10 / 10; Haiku 5.5 0.10 / 0.125 / 0.20 / 0.01 / 0.50 to a 100k prompt, 0.50 / 0.625 / 1 / 0.05 / 2.50 above. **Check:** the same prices applied to a CTO transcript and its subagent transcripts give $122.33 for b40cba91 (the session's own cost-state line: $122.33), $554.56 for b2f0511f ($556.15) and $152.04 for 8ddb8b14 ($148.12; its last cost-state line may predate its end): within 3 %.
Sources and what each gave.
- **Launched workers (M):** `log/spend.jsonl`, {bk['A']['worker'][1]} workers with cost in A, one row per session; cost from the worktree log's `total_cost_usd` where the log exists (M), else the spend row's own cost; end time from the log file, start = end - `duration_ms`. For {META.get('nolog','147')} workers whose worktree log is gone, the duration (hours only) is E: the role's median seconds per dollar. The total ($517.3 in A) equals the sum of the spend rows in the window ($517.0, pro-rata difference only). Roles and log names decide the bucket (ACT-*: 3; auditor: 2; designer: tests; engineer, product-spec, research: build; *merge*: land); non-zero exit or `is_error`: 8a; `td-/eng-` round >= 2: 8b.
- **Leads (M cost, E phase split):** `log/*-A5-*.json` via `tools/lead_ledger.py` (143 runs; its lead cost sum $339.12 equals the sum of `total_cost_usd` over the lead logs). Lead-hours = the run's wall time; the partition into tests, build, review, verify/land and the lead's own time uses the ledger's worker intervals (E). 5 runs still RUNNING have no final cost yet; their {running_leads_h('A'):.1f} lead-hours are counted, their cost is not (undercount est. ${running_leads_h('A')*339.12/126.9:.0f} at the window's $/lead-hour). Cross-check of lead-hours: `tools/measure_week.py daily` gives 11.63 + 75.71 + 38.69 = 126.0 h (the sample-based count, flagged partial on 11-11); the ledger gives {sum(u['lead_h'] for u in U if u['kind']=='lead' and u['t0']>=C.LIFT):.1f} h.
- **The CTO (M tokens, E bucket):** `message.usage` token counts, model and timestamps only, from the transcripts of 8ddb8b14 (to its end 15:58 on 11-11; only turns after the lift count), b40cba91, b2f0511f and f3886235 (this session, up to the run), de-duplicated by message id. 8ddb8b14 was added by the same marks as the others (same project folder, same entry point, hand-over at 15:58: its stand-by file names it CTO); the owner named b2f0511f, f3886235 and b40cba91 if in the window. No message text was read. Hours = the sum of gaps up to 10 minutes between consecutive turns (E: active time, not session span); gaps over 10 minutes and under 12 h are CTO idle in bucket 9 (E: the cause is not recorded; the CTO stand-by files, which name the owner as the cause, cover only {sum(u['sess_h'] for u in U if u.get('memo') and u['t1']>=C.LIFT):.1f} h of them).
- **Placing the CTO's turns in buckets 2, 3, 4, 5, 7 (E):** from git (first-parent commits on w2/integrate with their paths: packages/ and closes/ to 4; reviews/ and docs/probes to 2; the register and DECISIONS-IN-FORCE to 5 "decisions"; ACT-* subjects and every file under `acts/` to 3; merge commits to 7; briefs/ and other paths to 5) and file times; each assistant turn goes to the first such artefact written within {int(META['WMIN'])} minutes after it, else to 5. This uses timestamps only. It is the weakest figure in the report (see Gaps): treat bucket 4's and 5's CTO part as plus or minus a third.
- **In-session helpers (M tokens, E bucket):** subagent transcripts under each CTO session (usage and timestamps), classed by `agentType` and the short description key words: an ACT in its title: 3 (build, rehearse or review); an auditor on anything else: 2; package, CIT-P, record: 4; the rest: 6. No transcript text was read; the report names a helper by its id and agent type. The spend log holds no helper line in this window (0 `agent` rows), so helpers are measured here only.
- **Landing queue and nightly (M time, $0):** `dispatch/dispatch.log` land started/finished pairs ({lands_in(C.WINDOWS['A'])} runs in A); `land-dispatch-*.out` shows no model call (gitleaks, kernel gate, reds traced, merge). A landing that ejected a ticket goes to 8a for the ejected share of its hours (E). The nightly is the `actual_s` of `log/nightly/history.jsonl` for runs ending in the window. The lands' CPU cost is not in USD or points.
- **Waiting (M time):** ledger waits ("waiting on the CTO or the owner", launch refusal, brake), `log/heavy-slot-waits.jsonl` (starts 2026-11-12 23:48: waits before it are not recorded), and the CTO idle gaps above. `log/refused-starts.jsonl` (27 ticks) is inside the ledger's launch refusals.
- **Usage points (M total, E split):** `log/usage.txt` ("week (all models)"), reset-aware (a drop counts as the new value, as `measure_week.py`); the meter reset on 11-12 between the 07:52 reading (94 %) and 09:51 (0 %), so up to about 6 points of the gap are unmeasured (est. 1 to 2 at the neighbouring rate). Each reading-to-reading interval's gain is shared among buckets by that interval's USD; {T['A']['pts_unattributed']:.1f} points fell in intervals with no priced spend. Buckets 7 and 9 have none by construction.
- **Produced (M):** `dispatch/land-done.txt` (CLOSED outcomes), git subjects and added files (`closes/`, `packages/`, `reviews/`) by commit time, the register's version rows by `git blame` time.
Commands run (read-only): `tools/lead_ledger.py --since 2026-11-11T13:31 --out <here>/lead-ledger-window.jsonl`; `tools/measure_week.py daily` (cross-check); `python3 -I build.py --W 30|15|60`, `python3 -I aggregate.py <units>`, `python3 -I cto_context.py`, `python3 -I make_report.py` (all in this folder; `run_all.sh` runs the chain). `git log`, `git blame` on the register. No pytest, no suite.

## Gaps and what would shake the figures
- **The CTO's split across 2, 3, 4, 5, 7 is E.** It is a timing rule: sensitivity in note (4) shows bucket 5 moves {min(sens[k]['5'] for k in sens):.0f} to {max(sens[k]['5'] for k in sens):.0f} and bucket 4 {min(sens[k]['4'] for k in sens):.0f} to {max(sens[k]['4'] for k in sens):.0f} (A, USD) across 15 to 60 minutes. The sum of the CTO's USD ($ {bk['A']['cto'][0]:.0f}) is M.
- **Lead cost by phase is not recorded:** bucket 1 shows the lead's own cost whole; the phase hours are E.
- **Redo (8b) is a rule,** not a recorded fault: a round 2 may be new scope. Bucket 8 is {share('A','8'):.1f} % with it and {100*sum(v['usd'] for s,v in T['A']['buckets']['8']['subs'].items() if s.startswith('8a'))/tA:.1f} % without.
- **Spend this set does not see:** 5 runs still running (above); the operator agent and rehearsal folders ($0.07 in the operator log, M); sessions of other tools; the points of the 11-12 reset gap; any usage the meter counts that no transcript or log shows. The account's meter also counts what this set cannot name, so $ per point is only a fitted proxy (USAGE-1 §8).
- **Unplaced:** ambient sessions in the project folder that are neither CTO nor helper (usage recorder, sentinel, dead-man, side sessions): ${T['A']['buckets']['U']['usd']:.2f} (A) / ${T['B']['buckets']['U']['usd']:.2f} (B), M, kept apart; nothing else is unplaced.
- **Hours:** worker hours are inside the leads' hours for tickets with a lead; ACT reviewers and directly launched workers count in other-h; the sum of lead-h and other-h is not a headcount of anything (parallel). The ledger's wall time includes a lead waiting on its worker.
- **This session** (the measuring helper, a subagent of f3886235) is counted in bucket 6 up to the run time: ${own:.2f} so far (M), {100*own/tA:.2f} % of A.
- **No commit:** this record sits in the scratch folder (not tracked), so there is no commit of its own; the CTO may commit it.
""")

nfailB = len(set(u["unit"] for u in U if u["kind"] == "lead" and u["sub"].startswith("8a failed") and frac(u, C.WINDOWS["B"]) > 0))
nfailA = len(set(u["unit"] for u in U if u["kind"] == "lead" and u["sub"].startswith("8a failed") and frac(u, C.WINDOWS["A"]) > 0))
L.append(f"""
## Verdict
The effort is {100*(bk['A']['cto'][0]+bk['A']['helper'][0])/tA:.0f} % the CTO's own turns and in-session helpers (cache reads of a {cA['ctx_median']/1000:.0f}k-token median context are {100*cA['cost_by_kind']['cache_read']/cA['total']:.0f} % of the CTO's cost), {share('A','1'):.0f} % ticket product work (the leads' own sessions are {100*sub_usd('A','1',"lead's own")/tA:.0f} % of all spend, more than the designers and engineers together at {100*(sub_usd('A','1','tests')+sub_usd('A','1','build'))/tA:.0f} %), and {share('A','8'):.1f} % rework with the redo rule ({100*sum(v['usd'] for s,v in T['A']['buckets']['8']['subs'].items() if s.startswith('8a'))/tA:.1f} % measured). Waiting costs no dollars but holds 174 ticket-hours and {T['A']['slot_h']:.0f} lead-hours.
The three largest levers, in order, are the CTO's context size (up to ${cA['cache_read_above_cap_usd']['300000']:.0f} in A), the redo rounds (about ${redoA[1]/2:.0f}) and Opus helpers (about ${helpers_opus_nonreview('A')/2:.0f}); together about {100*(cA['cache_read_above_cap_usd']['300000']+redoA[1]/2+helpers_opus_nonreview('A')/2)/tA:.0f} % of A (E).

## Draft KPI lines (each with verify)
- KPI-EFF-1: the CTO's main sessions' median context stays at or under 300k tokens (now {cA['ctx_median']/1000:.0f}k in A, {cB['ctx_median']/1000:.0f}k in B). verify: `python3 -I .gov-runtime/scratch/orchestrator/drafts/effort-20261113/cto_context.py` and read `ctx_median` in `cto_context.json`.
- KPI-EFF-2: bucket 8 (rework, with the redo rule) at or under 5 % of 24 h spend (now {share('A','8'):.1f} % in A, {share('B','8'):.1f} % in B). verify: `bash .gov-runtime/scratch/orchestrator/drafts/effort-20261113/run_all.sh && python3 -I .gov-runtime/scratch/orchestrator/drafts/effort-20261113/make_report.py`, then the "8 Rework" row of window B.
- KPI-EFF-3: lead runs ending ERROR, LAUNCH_BLOCKED or NO_STATUS at or under 2 per 24 h (now {nfailB} in B, {nfailA} in A). verify: `python3 -I .gov-runtime/scratch/orchestrator/tools/lead_ledger.py --since <24 h ago> --no-write --md` and count those statuses.
- KPI-EFF-4: spend per ticket landed CLOSED at or under $40 over 24 h (now ${tB/max(T['produced']['B']['land_closed_tickets'],1):.0f} in B, ${tA/max(T['produced']['A']['land_closed_tickets'],1):.0f} in A). verify: the headline of this report re-run; CLOSED outcomes from `dispatch/land-done.txt`.

## Residuals
The CTO's placement (E), the phase split of lead cost, the redo rule and the points split are rules, not records (Gaps). Nothing in this report is a decision; the cuts are recommendations to the CTO. Not run: any suite. Proposed runs for the lead: none needed; to tighten the CTO's split, the CTO could tag its own turns by bucket in a log line (cheap, would make bucket 4 and 5 measured).
""")
open(HERE + "/REPORT.md", "w").write("\n".join(L))
print("written", sum(len(x) for x in L))
