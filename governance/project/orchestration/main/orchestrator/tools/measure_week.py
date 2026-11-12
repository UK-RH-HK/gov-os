#!/usr/bin/env python3
"""measure_week.py - usage, spend and speed of work per UTC day, and a usage forecast.

Subcommands
  daily    one row per UTC day: usage points gained (week percent, reset-aware), spend (spend.jsonl),
           speed (tickets closed, close records, merges, lead runs, lead-hours) and derived ratios.
  forecast points per hour at N leads from the last 72 h (least-squares fit), time to 100 % and 97 %.
  record   append today's daily rows and the forecast inputs to log/measure/week.jsonl.

Sources (all times are read as UTC; London is UTC in November):
  usage        log/usage.txt  (new form: "week (all models)=NN%"; old form: "session N|... week NN|...")
               and log/usage-lines.log ("YYYY-MM-DD HH:MM:SS NN")
  spend        log/spend.jsonl (cost_usd summed by the day of "at"; rows without cost_usd are counted, never summed)
  closes       .tickets/*.md with "status: closed" (newest commit adding that line), minus tickets tagged withdrawn;
               governance/project/orchestration/closes/*.md (the "Closed:" line, else the git first-add date)
  merges       git log --first-parent --merges <branch>
  lead runs    log/lead-ledger.jsonl (runs started that day) and the distinct lead trees seen in the samples
  lead-hours   log/lead-mem-watch.jsonl (leads with in_status) where it exists, else log/lead-mem.jsonl
               (every lead tree present in a sample); each sample counts for its real interval, at most 150 s.
A day or span with no readings is marked as a gap ("gap"), never shown as zero.

Paths: --root (repo, env MEASURE_ROOT), --log (env MEASURE_LOG), --out (env MEASURE_OUT).
"""
import argparse
import collections
import datetime as dt
import json
import math
import os
import re
import subprocess
import sys
from pathlib import Path

UTC = dt.timezone.utc
USAGE_GAP_H = 2.0       # readings further apart than this are a gap, not a rate
LEAD_MAX_DT = 150.0     # seconds one lead sample may stand for
FORECAST_WINDOW_H = 72
BULK_CLOSES = 10        # tickets closed by one commit at or above this count are a bulk (administrative) close
MIN_BUCKET_LEAD_COVER = 2400.0  # seconds of lead samples an hourly bucket needs


# ----------------------------------------------------------------------------- paths

class Paths:
    def __init__(self, root=None, log=None, out=None, branch="w2/integrate"):
        here = Path(__file__).resolve()
        default_root = here.parents[4] if len(here.parents) > 4 else Path.cwd()
        self.root = Path(root or os.environ.get("MEASURE_ROOT") or default_root)
        self.log = Path(log or os.environ.get("MEASURE_LOG")
                        or self.root / ".gov-runtime/scratch/orchestrator/log")
        self.out = Path(out or os.environ.get("MEASURE_OUT") or self.log / "measure")
        self.branch = branch

    @property
    def tickets(self):
        return self.root / ".tickets"

    @property
    def closes(self):
        return self.root / "governance/project/orchestration/closes"


def p_ts(s):
    s = s.strip().replace("T", " ")
    if len(s) == 16:
        s += ":00"
    return dt.datetime.strptime(s[:19], "%Y-%m-%d %H:%M:%S").replace(tzinfo=UTC)


def p_iso_utc(s):
    return dt.datetime.fromisoformat(s.strip()).astimezone(UTC)


def day_of(t):
    return t.astimezone(UTC).date()


def spread(t1, t2, value=1.0):
    """Split value over the UTC days between t1 and t2, in proportion to time. Yields (date, share, seconds)."""
    total = (t2 - t1).total_seconds()
    if total <= 0:
        return
    cur = t1
    while cur < t2:
        nxt = min(t2, dt.datetime.combine(cur.date() + dt.timedelta(days=1), dt.time(0), tzinfo=UTC))
        sec = (nxt - cur).total_seconds()
        yield cur.date(), value * sec / total, sec
        cur = nxt


# ----------------------------------------------------------------------------- usage

NEW_RE = re.compile(r"^(\d{4}-\d\d-\d\d \d\d:\d\d:\d\d)\s+week \(all models\)=(\d+)%")
OLD_RE = re.compile(r"^(\d{4}-\d\d-\d\d \d\d:\d\d:\d\d)\s+session (?:\d+\|.*?|unread)\s+week (\d+)\|")
LINES_RE = re.compile(r"^(\d{4}-\d\d-\d\d \d\d:\d\d:\d\d)\s+(\d+)\s*$")
RESETS_RE = re.compile(r"week \(all models\)=\d+% \(resets ([A-Z][a-z]{2}) (\d+), (\d+):(\d\d)(am|pm)")
OLD_RESETS_RE = re.compile(r"\bweek \d+\|([A-Z][a-z]{2}) (\d+), (\d+):(\d\d)(am|pm)")


def read_usage(log):
    """Return (readings sorted [(t, pct)], skipped line count, last reset text or None)."""
    seen = {}
    skipped = 0
    last_reset = None
    for name in ("usage.txt", "usage-lines.log"):
        f = Path(log) / name
        if not f.exists():
            continue
        for line in f.read_text(errors="replace").splitlines():
            if not line.strip():
                continue
            m = NEW_RE.match(line) or OLD_RE.match(line) or LINES_RE.match(line)
            if not m:
                skipped += 1
                continue
            t = p_ts(m.group(1))
            seen[t] = int(m.group(2))
            r = RESETS_RE.search(line) or OLD_RESETS_RE.search(line)
            if r:
                last_reset = (t, r.groups())
    return sorted(seen.items()), skipped, last_reset


def reset_time_from(last_reset):
    """The UTC time named by the newest reading's 'resets Nov 15, 8:59am' text (London = UTC in winter)."""
    if not last_reset:
        return None
    t, (mon, d, hh, mm, ap) = last_reset
    hh = int(hh) % 12 + (12 if ap == "pm" else 0)
    try:
        r = dt.datetime.strptime(f"{t.year} {mon} {int(d)} {hh}:{mm}", "%Y %b %d %H:%M").replace(tzinfo=UTC)
    except ValueError:
        return None
    if r < t:
        r = r.replace(year=t.year + 1)
    # an 8:59 reading is the 09:00 reset
    if r.minute == 59:
        r += dt.timedelta(minutes=1)
    return r


def usage_segments(readings, gap_h=USAGE_GAP_H):
    """Consecutive pairs -> list of dicts {t1,t2,v1,v2,kind,gain}. kind: rise | flat | reset | gap."""
    segs = []
    for (t1, v1), (t2, v2) in zip(readings, readings[1:]):
        hrs = (t2 - t1).total_seconds() / 3600
        if hrs > gap_h:
            segs.append(dict(t1=t1, t2=t2, v1=v1, v2=v2, kind="gap", gain=None))
        elif v2 < v1:
            segs.append(dict(t1=t1, t2=t2, v1=v1, v2=v2, kind="reset", gain=v2))
        else:
            segs.append(dict(t1=t1, t2=t2, v1=v1, v2=v2, kind="rise" if v2 > v1 else "flat", gain=v2 - v1))
    return segs


def usage_by_day(readings):
    days = collections.defaultdict(lambda: dict(gain=0.0, hours=0.0, resets=0, readings=0,
                                                first=None, last=None, gaps=[]))
    for t, v in readings:
        d = days[day_of(t)]
        d["readings"] += 1
        d["first"] = v if d["first"] is None else d["first"]
        d["last"] = v
    for s in usage_segments(readings):
        if s["kind"] == "gap":
            for dd, _, sec in spread(s["t1"], s["t2"]):
                days[dd]["gaps"].append((s["t1"], s["t2"], s["v1"], s["v2"]))
            continue
        for dd, share, sec in spread(s["t1"], s["t2"], s["gain"]):
            days[dd]["gain"] += share
            days[dd]["hours"] += sec / 3600
        if s["kind"] == "reset":
            days[day_of(s["t2"])]["resets"] += 1
    return days


# ----------------------------------------------------------------------------- spend

def read_spend(log):
    f = Path(log) / "spend.jsonl"
    rows = []
    bad = 0
    if f.exists():
        for line in f.read_text(errors="replace").splitlines():
            if not line.strip():
                continue
            try:
                rows.append(json.loads(line))
            except ValueError:
                bad += 1
    return rows, bad


PRICED_KINDS_SKIP = {"brake", "brake-clear", "note"}
TIER_RE = re.compile(r"\b(opus|sonnet|haiku|fable)\b", re.I)


def tier_of(r):
    """The row's tier; else the tier named in its model or its text; else '?' (not recorded)."""
    if r.get("tier"):
        return r["tier"]
    for text in (r.get("model") or "", r.get("what") or ""):
        m = TIER_RE.search(text)
        if m:
            return m.group(1).lower()
    return "?"


def spend_by_day(rows):
    days = collections.defaultdict(lambda: dict(usd=0.0, n=0, unpriced=0, tier=collections.Counter(),
                                                role=collections.Counter(), model=collections.Counter(),
                                                out_tok=0, cache_read=0, cache_create=0))
    for r in rows:
        at = r.get("at")
        if not at:
            continue
        d = days[p_ts(at).date()]
        c = r.get("cost_usd")
        if c is None:
            if r.get("kind") not in PRICED_KINDS_SKIP:
                d["unpriced"] += 1
            continue
        d["usd"] += float(c)
        d["n"] += 1
        d["tier"][tier_of(r)] += float(c)
        d["role"][r.get("role") or f"({r.get('kind') or 'none'}, no role recorded)"] += float(c)
        d["model"][r.get("model") or "?"] += float(c)
        d["out_tok"] += r.get("output_tokens") or 0
        d["cache_read"] += r.get("cache_read_tokens") or 0
        d["cache_create"] += r.get("cache_creation_tokens") or 0
    return days


# ----------------------------------------------------------------------------- leads

def read_leads(log):
    """Timeline [(t, n_leads)] sorted, plus info. Watch file (in_status) wins from its first sample on."""
    log = Path(log)
    watch = []
    f = log / "lead-mem-watch.jsonl"
    if f.exists():
        for line in f.read_text(errors="replace").splitlines():
            try:
                r = json.loads(line)
                leads = r.get("leads") or {}
                watch.append((p_ts(r["at"]), sum(1 for v in leads.values() if v.get("in_status")),
                              sorted(k for k, v in leads.items() if v.get("in_status"))))
            except (ValueError, KeyError, AttributeError):
                continue
    first_watch = watch[0][0] if watch else None
    mem = []
    f = log / "lead-mem.jsonl"
    if f.exists():
        for line in f.read_text(errors="replace").splitlines():
            try:
                r = json.loads(line)
                t = p_ts(r.get("t") or r["at"])
                if first_watch and t >= first_watch:
                    continue
                keys = sorted((r.get("leads_kb") or {}).keys())
                mem.append((t, len(keys), keys))
            except (ValueError, KeyError, AttributeError):
                continue
    samples = sorted(mem + watch, key=lambda x: x[0])
    return samples, dict(first_watch=first_watch, n_watch=len(watch), n_mem=len(mem))


def leads_by_day(samples, max_dt=LEAD_MAX_DT):
    days = collections.defaultdict(lambda: dict(lead_s=0.0, cover_s=0.0, seen=set()))
    for (t1, n1, k1), (t2, _, _) in zip(samples, samples[1:]):
        dtv = min((t2 - t1).total_seconds(), max_dt)
        if dtv <= 0:
            continue
        for dd, _, sec in spread(t1, t1 + dt.timedelta(seconds=dtv)):
            days[dd]["lead_s"] += n1 * sec
            days[dd]["cover_s"] += sec
        days[day_of(t1)]["seen"].update(k1)
    return days


def lead_avg_in(samples, a, b, max_dt=LEAD_MAX_DT):
    """Time-weighted average lead count in [a, b) and the seconds covered."""
    lead_s = cover = 0.0
    for (t1, n1, _), (t2, _, _) in zip(samples, samples[1:]):
        if t2 <= a or t1 >= b:
            continue
        end = min(t2, t1 + dt.timedelta(seconds=max_dt))
        lo, hi = max(t1, a), min(end, b)
        sec = (hi - lo).total_seconds()
        if sec > 0:
            lead_s += n1 * sec
            cover += sec
    return (lead_s / cover if cover else None), cover


def read_ledger(log):
    f = Path(log) / "lead-ledger.jsonl"
    days = collections.defaultdict(lambda: dict(runs=0, refused=0, wall_min=0.0))
    if f.exists():
        for line in f.read_text(errors="replace").splitlines():
            try:
                r = json.loads(line)
                d = days[p_ts(r["start"]).date()]
            except (ValueError, KeyError):
                continue
            if r.get("status") == "REFUSED":
                d["refused"] += 1
            else:
                d["runs"] += 1
                d["wall_min"] += float(r.get("wall_minutes") or 0)
    return days


# ----------------------------------------------------------------------------- git (closes, merges)

def git(root, *args):
    r = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ""


def ticket_closes(paths):
    """{date: [ticket ids]} for tickets whose file says closed and is not tagged withdrawn; plus counts."""
    closed = {}
    withdrawn = 0
    if paths.tickets.is_dir():
        for f in sorted(paths.tickets.glob("*.md")):
            head = f.read_text(errors="replace").split("\n---", 2)[0]
            if re.search(r"^status:\s*closed\s*$", head, re.M):
                if re.search(r"^tags:.*\bwithdrawn\b", head, re.M):
                    withdrawn += 1
                    continue
                closed[f"{paths.tickets.name}/{f.name}"] = None
    out = git(paths.root, "log", paths.branch, "-G^status: closed", "-p", "--abbrev=12",
              "--format=@@C%cI|%h|%s", "--", paths.tickets.name)
    cur = None
    fname = None
    commit_of = {}
    subject = {}
    for line in out.splitlines():
        if line.startswith("@@C"):
            iso, h, subj = line[3:].split("|", 2)
            cur = (p_iso_utc(iso), h)
            subject[h] = subj
        elif line.startswith("+++ b/"):
            fname = line[6:]
        elif line.strip() == "+status: closed" and fname in closed and closed[fname] is None:
            closed[fname] = cur[0]
            commit_of[fname] = cur[1]
    per_commit = collections.Counter(commit_of.values())
    bulk = {h for h, n in per_commit.items() if n >= BULK_CLOSES}
    days = collections.defaultdict(list)
    bulk_days = collections.defaultdict(list)
    undated = [k for k, v in closed.items() if v is None]
    for k, v in closed.items():
        if v is None:
            continue
        if commit_of[k] in bulk:
            bulk_days[v.date()].append(Path(k).stem)
        else:
            days[v.date()].append(Path(k).stem)
    bulk_info = [dict(day=str(min(d for d, ids in bulk_days.items() if commit_of[f".tickets/{ids[0]}.md"] == h)),
                      commit=h, n=per_commit[h], subject=subject[h][:90])
                 for h in sorted(bulk)] if bulk_days else []
    return (days, bulk_days), dict(undated=len(undated), withdrawn=withdrawn, total=len(closed), bulk=bulk_info)


CLOSED_LINE = re.compile(r"^- Closed:\s*(\d{4}-\d\d-\d\d \d\d:\d\d:\d\d)", re.M)


def close_records(paths):
    days = collections.defaultdict(list)
    n_git = 0
    if not paths.closes.is_dir():
        return days, dict(total=0, from_git=0)
    adds = {}
    out = git(paths.root, "log", paths.branch, "--diff-filter=A", "--name-only", "--format=@@C%cI",
              "--", str(paths.closes.relative_to(paths.root)))
    cur = None
    for line in out.splitlines():
        if line.startswith("@@C"):
            cur = p_iso_utc(line[3:])
        elif line.strip():
            adds[Path(line.strip()).name] = cur  # the oldest add wins (log is newest first)
    total = 0
    for f in sorted(paths.closes.glob("*.md")):
        total += 1
        m = CLOSED_LINE.search(f.read_text(errors="replace"))
        if m:
            t = p_ts(m.group(1))
        elif f.name in adds:
            t = adds[f.name]
            n_git += 1
        else:
            continue
        days[t.date()].append(f.stem)
    return days, dict(total=total, from_git=n_git)


def merges_by_day(paths):
    out = git(paths.root, "log", "--first-parent", "--merges", "--format=%cI", paths.branch)
    days = collections.Counter()
    for line in out.splitlines():
        if line.strip():
            days[p_iso_utc(line).date()] += 1
    return days


# ----------------------------------------------------------------------------- daily

def build_daily(paths, since, now=None):
    now = now or dt.datetime.now(UTC)
    readings, skipped, _ = read_usage(paths.log)
    udays = usage_by_day(readings)
    srows, sbad = read_spend(paths.log)
    sdays = spend_by_day(srows)
    spend_first = min(sdays) if sdays else None
    spend_last = max(sdays) if sdays else None
    samples, linfo = read_leads(paths.log)
    ldays = leads_by_day(samples)
    ledger = read_ledger(paths.log)
    (tdays, bdays), tinfo = ticket_closes(paths)
    rdays, rinfo = close_records(paths)
    mdays = merges_by_day(paths)

    today = now.date()
    since_d = since if isinstance(since, dt.date) else dt.date.fromisoformat(since)
    rows = []
    d = since_d
    while d <= today:
        r = dict(day=d.isoformat(), partial=(d == today))
        u = udays.get(d)
        if u and u["hours"] > 0:
            r["pts"] = round(u["gain"], 2)
            r["usage_h"] = round(u["hours"], 2)
            r["pts_h"] = round(u["gain"] / u["hours"], 3) if u["hours"] >= 1 else None
            r["resets"] = u["resets"]
            r["first_pct"], r["last_pct"] = u["first"], u["last"]
            r["usage_gaps"] = len(u["gaps"])
        else:
            r.update(pts=None, usage_h=0.0, pts_h=None, resets=0, first_pct=None, last_pct=None,
                     usage_gaps=len(u["gaps"]) if u else 0)
        s = sdays.get(d)
        if spend_first is None or d < spend_first:
            r.update(usd=None, spend_rows=None, unpriced=None, tiers={}, roles={}, models={})
        else:
            s = s or dict(usd=0.0, n=0, unpriced=0, tier={}, role={}, model={})
            r.update(usd=round(s["usd"], 4), spend_rows=s["n"], unpriced=s["unpriced"],
                     tiers={k: round(v, 3) for k, v in sorted(dict(s["tier"]).items(), key=lambda x: -x[1])},
                     roles={k: round(v, 3) for k, v in sorted(dict(s["role"]).items(), key=lambda x: -x[1])},
                     models={k: round(v, 3) for k, v in sorted(dict(s["model"]).items(), key=lambda x: -x[1])})
        r["closes"] = len(tdays.get(d, []))
        r["closes_bulk"] = len(bdays.get(d, []))
        r["close_records"] = len(rdays.get(d, []))
        r["merges"] = mdays.get(d, 0)
        lg = ledger.get(d)
        r["lead_runs"] = lg["runs"] if lg else None
        r["lead_refused"] = lg["refused"] if lg else None
        L = ldays.get(d)
        if L and L["cover_s"] > 0:
            r["lead_h"] = round(L["lead_s"] / 3600, 3)
            r["lead_cover_h"] = round(L["cover_s"] / 3600, 2)
            r["leads_seen"] = len(L["seen"])
        else:
            r.update(lead_h=None, lead_cover_h=0.0, leads_seen=None)
        expected_h = ((now - dt.datetime.combine(d, dt.time(0), tzinfo=UTC)).total_seconds() / 3600
                      if d == today else 24.0)
        r["lead_partial"] = bool(r["lead_h"] is not None and r["lead_cover_h"] < 0.85 * expected_h)
        # derived
        r["usd_per_close"] = round(r["usd"] / r["closes"], 3) if r["usd"] is not None and r["closes"] else None
        r["pts_per_lead_h"] = (round(r["pts"] / r["lead_h"], 3)
                               if r["pts"] is not None and r["lead_h"] and r["lead_h"] >= 0.25 else None)
        r["pts_per_close"] = round(r["pts"] / r["closes"], 3) if r["pts"] is not None and r["closes"] else None
        rows.append(r)
        d += dt.timedelta(days=1)
    meta = dict(usage_readings=len(readings), usage_skipped_lines=skipped, spend_rows=len(srows),
                spend_bad_lines=sbad, spend_first=str(spend_first) if spend_first else None,
                spend_last=str(spend_last) if spend_last else None, lead_info={
                    k: (str(v) if v is not None else None) for k, v in linfo.items()},
                tickets=tinfo, close_records=rinfo, usage_spans=gap_spans(readings))
    return rows, meta


def gap_spans(readings):
    out = []
    for s in usage_segments(readings):
        if s["kind"] == "gap":
            out.append(dict(from_=s["t1"].strftime("%Y-%m-%d %H:%M"), to=s["t2"].strftime("%Y-%m-%d %H:%M"),
                            pct_from=s["v1"], pct_to=s["v2"],
                            hours=round((s["t2"] - s["t1"]).total_seconds() / 3600, 1)))
    return out


def f_num(v, nd=1, gap="gap"):
    return gap if v is None else f"{v:.{nd}f}"


def tiers_str(r):
    if r["usd"] is None:
        return "gap"
    if not r["tiers"]:
        return "-"
    return ", ".join(f"{k} {v:.1f}" for k, v in list(r["tiers"].items())[:3])


COLS = [("day", lambda r: r["day"] + ("*" if r["partial"] else "")),
        ("pts", lambda r: f_num(r["pts"], 1)),
        ("rd_h", lambda r: f_num(r["usage_h"] or None, 1)),
        ("pts/h", lambda r: f_num(r["pts_h"], 2, "-" if r["pts"] is not None else "gap")),
        ("usd", lambda r: f_num(r["usd"], 2) + ("" if not r["unpriced"] else f" (+{r['unpriced']}u)")),
        ("tiers", tiers_str),
        ("closed", lambda r: str(r["closes"]) + (f" (+{r['closes_bulk']}b)" if r["closes_bulk"] else "")),
        ("recs", lambda r: str(r["close_records"])),
        ("merges", lambda r: str(r["merges"])),
        ("runs", lambda r: "gap" if r["lead_runs"] is None else str(r["lead_runs"])
         + (f"+{r['lead_refused']}R" if r["lead_refused"] else "")),
        ("seen", lambda r: "gap" if r["leads_seen"] is None else str(r["leads_seen"])),
        ("lead_h", lambda r: f_num(r["lead_h"], 2) + ("~" if r["lead_h"] is not None and r["lead_partial"] else "")),
        ("usd/cl", lambda r: f_num(r["usd_per_close"], 2, "-" if r["usd"] is not None else "gap")),
        ("pts/ldh", lambda r: f_num(r["pts_per_lead_h"], 2, "-") + ("~" if r["pts_per_lead_h"] is not None and r["lead_partial"] else "")),
        ("pts/cl", lambda r: f_num(r["pts_per_close"], 2, "-"))]


def table(rows, md):
    cells = [[c[1](r) for c in COLS] for r in rows]
    head = [c[0] for c in COLS]
    if md:
        out = ["| " + " | ".join(head) + " |", "|" + "|".join("---" for _ in head) + "|"]
        out += ["| " + " | ".join(row) + " |" for row in cells]
        return "\n".join(out)
    w = [max(len(h), *(len(row[i]) for row in cells)) if cells else len(h) for i, h in enumerate(head)]
    out = ["  ".join(h.ljust(w[i]) for i, h in enumerate(head))]
    out += ["  ".join(c.ljust(w[i]) for i, c in enumerate(row)) for row in cells]
    return "\n".join(out)


def window_stats(rows):
    """Pooled figures for a list of rows; a metric lists only the days that have its source (n)."""
    def pool(num, den, cond):
        use = [r for r in rows if cond(r)]
        a = sum(num(r) for r in use)
        b = sum(den(r) for r in use)
        return (a / b if b else None), len(use)
    return {
        "pts/h": pool(lambda r: r["pts"], lambda r: r["usage_h"], lambda r: r["pts"] is not None and r["usage_h"] >= 1),
        "usd/day": pool(lambda r: r["usd"], lambda r: 1, lambda r: r["usd"] is not None and not r["partial"]),
        "closed/day": pool(lambda r: r["closes"], lambda r: 1, lambda r: not r["partial"]),
        "merges/day": pool(lambda r: r["merges"], lambda r: 1, lambda r: not r["partial"]),
        "lead_h/day": pool(lambda r: r["lead_h"], lambda r: 1,
                           lambda r: r["lead_h"] is not None and not r["lead_partial"] and not r["partial"]),
        "usd/close": pool(lambda r: r["usd"], lambda r: r["closes"],
                          lambda r: r["usd"] is not None and not r["partial"] and r["closes"] > 0),
        "pts/close": pool(lambda r: r["pts"], lambda r: r["closes"],
                          lambda r: r["pts"] is not None and r["closes"] > 0 and r["usage_h"] >= 20),
    }


def change_block(rows):
    full = [r for r in rows if not r["partial"]]
    if len(full) < 4:
        return []
    a, b = full[:3], full[-3:]
    sa, sb = window_stats(a), window_stats(b)
    out = [f"Change, first 3 days ({a[0]['day']}..{a[-1]['day']}) vs last 3 full days ({b[0]['day']}..{b[-1]['day']}); "
           "n = days having the source:"]
    for k in sa:
        va, na = sa[k]
        vb, nb = sb[k]
        if va is None or vb is None:
            out.append(f"  {k:<11} first {f_num(va, 2)} (n={na})  last {f_num(vb, 2)} (n={nb})  change: gap in one window")
        else:
            ch = f"{(vb - va) / va * 100:+.0f}%" if va else "n/a"
            out.append(f"  {k:<11} first {va:.2f} (n={na})  last {vb:.2f} (n={nb})  change {ch}")
    return out


def pooled_line(rows):
    use = [r for r in rows if r["pts"] is not None and r["usd"] is not None and r["usage_h"] >= 20 and not r["partial"]]
    if not use:
        return []
    pts = sum(r["pts"] for r in use)
    usd = sum(r["usd"] for r in use)
    cl = sum(r["closes"] for r in use)
    mg = sum(r["merges"] for r in use)
    days = len(use)
    bits = [f"{use[0]['day']}..{use[-1]['day']} ({days} full days with usage and spend): {pts:.1f} pts, usd {usd:.1f}, "
            f"closed {cl}, merges {mg}"]
    bits.append(f"usd/pt {usd / pts:.2f}" if pts else "usd/pt n/a")
    bits.append(f"usd/merge {usd / mg:.2f}" if mg else "usd/merge n/a")
    bits.append(f"usd/close {usd / cl:.2f}" if cl else "usd/close n/a (no close in the span)")
    bits.append(f"pts/merge {pts / mg:.2f}" if mg else "pts/merge n/a")
    return ["Pooled, " + "; ".join(bits) + " (closes arrive in batches through the close queue, so per-close figures lag the work)."]


def notes_block(rows, meta):
    out = ["Sources and gaps:"]
    out.append(f"  usage: usage.txt + usage-lines.log, {meta['usage_readings']} readings "
               f"({meta['usage_skipped_lines']} lines not readable as a week percent); pts = points gained "
               "(a drop = reset: gain = new value); rd_h = hours covered by readings; * = current partial day.")
    for g in meta["usage_spans"]:
        avg = (f"; {(g['pct_to'] - g['pct_from']) / g['hours']:.2f} pts/h on average over the gap"
               if g["pct_to"] >= g["pct_from"] else "; a reset lies inside it")
        out.append(f"  usage gap: {g['from_']} .. {g['to']} UTC ({g['hours']} h, {g['pct_from']}% -> {g['pct_to']}%): "
                   f"points not split by day{avg}")
    out.append(f"  spend: spend.jsonl {meta['spend_first']}..{meta['spend_last']} ({meta['spend_rows']} rows); days before the "
               "first row are a gap; (+Nu) = rows with no cost_usd (not summed, so usd is a floor); the CTO's own session "
               "and unpriced agents are not in it; tier ? = no tier, model or tier word in the row's text.")
    out.append(f"  closed = tickets closed (status closed, not withdrawn; closing commit date; "
               f"{meta['tickets']['undated']} undated, {meta['tickets']['withdrawn']} withdrawn skipped); "
               f"recs = close records ({meta['close_records']['total']} files; 'Closed:' line, "
               f"{meta['close_records']['from_git']} by git first-add); merges = first-parent merges into the branch.")
    li = meta["lead_info"]
    out.append(f"  leads: runs = lead-ledger runs started (+R = refused); seen = distinct lead trees in the samples; "
               f"lead_h = lead-hours (lead-mem.jsonl before {li.get('first_watch')}, lead-mem-watch in_status after); "
               "samples are about a minute apart.")
    cov = [r for r in rows if r["lead_h"] is not None and r["lead_partial"]]
    if cov:
        out.append("  ~ = lead samples cover under 85% of the day's hours (lead_h under-counted, pts/lead_h over-stated): "
                   + ", ".join(f"{r['day']} ({r['lead_cover_h']} h)" for r in cov))
    for b in meta["tickets"]["bulk"]:
        out.append(f"  bulk close: {b['n']} tickets closed by one commit {b['commit']} on {b['day']} ({b['subject']}); shown "
                   "as (+Nb) and left out of every ratio.")
    return out


def cmd_daily(a, paths):
    rows, meta = build_daily(paths, a.since)
    if a.md:
        print(table(rows, True))
        print()
        for ln in pooled_line(rows) + change_block(rows) + [""] + notes_block(rows, meta):
            print(ln if not ln.startswith("  ") else "- " + ln.strip())
    else:
        print(table(rows, False))
        print()
        print("\n".join(pooled_line(rows) + change_block(rows)))
        print()
        print("\n".join(notes_block(rows, meta)))
    role = collections.Counter()
    for r in rows:
        role.update(r["roles"])
    if role:
        tot = sum(role.values())
        top = ", ".join(f"{k} {v:.1f}" for k, v in role.most_common(6))
        print(("- " if a.md else "") + f"spend by role over the range (usd {tot:.1f}): {top}")
        tiers = collections.Counter()
        for r in rows:
            tiers.update(r["tiers"])
        print(("- " if a.md else "") + "spend by tier: " + ", ".join(f"{k} {v:.1f}" for k, v in tiers.most_common()))
        models = collections.Counter()
        for r in rows:
            models.update(r["models"])
        print(("- " if a.md else "") + "spend by model: " + ", ".join(f"{k} {v:.1f}" for k, v in models.most_common()))
    return 0


# ----------------------------------------------------------------------------- forecast

def cum_series(readings):
    """Reset-aware cumulative points [(t, cum)] and the spans that are not usable (gaps and resets)."""
    cum = float(readings[0][1]) if readings else 0.0
    pts = [(readings[0][0], cum)] if readings else []
    bad = []
    for s in usage_segments(readings):
        if s["kind"] == "gap":
            bad.append((s["t1"], s["t2"]))
            cum += 0  # unknown; no cum step: the series is not used across this span
            pts.append((s["t2"], cum))
            continue
        if s["kind"] == "reset":
            bad.append((s["t1"], s["t2"]))
        cum += s["gain"]
        pts.append((s["t2"], cum))
    return pts, bad


def interp(pts, t):
    for (t1, c1), (t2, c2) in zip(pts, pts[1:]):
        if t1 <= t <= t2:
            if t2 == t1:
                return c2
            return c1 + (c2 - c1) * (t - t1).total_seconds() / (t2 - t1).total_seconds()
    return None


def hourly_buckets(readings, samples, end, window_h=FORECAST_WINDOW_H):
    pts, bad = cum_series(readings)
    out = []
    start = end - dt.timedelta(hours=window_h)
    b0 = start
    while b0 + dt.timedelta(hours=1) <= end:
        b1 = b0 + dt.timedelta(hours=1)
        if any(x < b1 and y > b0 for x, y in bad):
            b0 = b1
            continue
        c0, c1 = interp(pts, b0), interp(pts, b1)
        avg, cover = lead_avg_in(samples, b0, b1)
        if c0 is None or c1 is None or avg is None or cover < MIN_BUCKET_LEAD_COVER:
            b0 = b1
            continue
        out.append(dict(t=b0, y=c1 - c0, x=avg))
        b0 = b1
    return out


def ols(buckets):
    n = len(buckets)
    xs = [b["x"] for b in buckets]
    ys = [b["y"] for b in buckets]
    ybar = sum(ys) / n if n else None
    res = dict(n=n, xbar=(sum(xs) / n if n else None), ybar=ybar, a=ybar, b=None, s=None, se_a=None, se_b=None,
               r2=None, sxx=0.0, identified=False, xmin=min(xs) if xs else None, xmax=max(xs) if xs else None)
    if n < 3:
        return res
    xbar = res["xbar"]
    sxx = sum((x - xbar) ** 2 for x in xs)
    res["sxx"] = sxx
    if sxx < 1e-9:
        res["s"] = math.sqrt(sum((y - ybar) ** 2 for y in ys) / (n - 1))
        return res
    b = sum((x - xbar) * (y - ybar) for x, y in zip(xs, ys)) / sxx
    a = ybar - b * xbar
    sse = sum((y - a - b * x) ** 2 for x, y in zip(xs, ys))
    s = math.sqrt(sse / (n - 2))
    sst = sum((y - ybar) ** 2 for y in ys)
    res.update(a=a, b=b, s=s, se_b=s / math.sqrt(sxx), se_a=s * math.sqrt(1 / n + xbar ** 2 / sxx),
               r2=(1 - sse / sst if sst else None), identified=True)
    return res


def rate_at(fit, n_leads):
    if fit["a"] is None:
        return None, None
    if not fit["identified"]:
        return fit["ybar"], (fit["s"] / math.sqrt(fit["n"]) if fit["s"] else None)
    rate = fit["a"] + fit["b"] * n_leads
    se = fit["s"] * math.sqrt(1 / fit["n"] + (n_leads - fit["xbar"]) ** 2 / fit["sxx"])
    return rate, se


def hrs_to(target, pct, rate):
    if rate is None or rate <= 1e-9:
        return None
    return max(0.0, (target - pct) / rate)


def forecast(pct, at, reset, leads, readings, samples, window_h=FORECAST_WINDOW_H):
    # the fit window ends at --at, or at the newest reading when --at lies beyond the data (a post-reset forecast)
    wend = min(at, readings[-1][0]) if readings else at
    buckets = hourly_buckets(readings, samples, wend, window_h)
    fit = ols(buckets)
    horizon = (reset - at).total_seconds() / 3600
    rows = []
    for n in leads:
        rate, se = rate_at(fit, n)
        row = dict(leads=n, rate=rate, se=se, extrapolated=bool(fit["xmax"] is not None and n > fit["xmax"] + 1e-9))
        for target in (100, 97):
            h = hrs_to(target, pct, rate)
            row[f"h{target}"] = h
            row[f"t{target}"] = at + dt.timedelta(hours=h) if h is not None else None
            if rate is not None and se is not None:
                lo = hrs_to(target, pct, rate + se)   # faster rate: earlier
                hi = hrs_to(target, pct, rate - se)
                row[f"h{target}_lo"], row[f"h{target}_hi"] = lo, hi
        reach = row["h100"] is not None and row["h100"] < horizon
        row["runs_out_before_reset"] = bool(reach)
        row["margin_h"] = (horizon - row["h100"]) if row["h100"] is not None else None
        rows.append(row)
    # largest steady lead count that does not reach the target before the reset
    steady = {}
    for target in (100, 97):
        budget = (target - pct) / horizon if horizon > 0 else None
        if budget is None or fit["a"] is None:
            steady[target] = None
        elif not fit["identified"] or fit["b"] <= 1e-9:
            steady[target] = "unbounded" if fit["a"] <= budget else "none"
        else:
            n_star = (budget - fit["a"]) / fit["b"]
            steady[target] = n_star
    return dict(pct=pct, at=at, reset=reset, horizon_h=horizon, fit=fit, window_end=wend, buckets=len(buckets), rows=rows,
                steady=steady, window_h=window_h)


def fmt_t(t):
    return t.strftime("%Y-%m-%d %H:%M") if t else "never"


def fmt_forecast(fc, md=False):
    f = fc["fit"]
    out = []
    out.append(f"Forecast from {fc['pct']}% at {fmt_t(fc['at'])} UTC; reset {fmt_t(fc['reset'])} UTC "
               f"({fc['horizon_h']:.1f} h away); window {fc['window_h']} h ending {fmt_t(fc['window_end'])}, {fc['buckets']} hourly buckets used "
               "(buckets with a gap, a reset or under 40 min of lead samples are dropped).")
    if f["n"] < 3:
        out.append("Fit: too few buckets for a fit; no forecast.")
        return out
    if f["identified"]:
        out.append(f"Fit: pts/h = {f['a']:.3f} (+-{f['se_a']:.3f}) + {f['b']:.3f} (+-{f['se_b']:.3f}) x leads; "
                   f"residual sd {f['s']:.3f} pts/h; R^2 {f['r2']:.2f}; leads seen {f['xmin']:.2f}..{f['xmax']:.2f} "
                   f"(mean {f['xbar']:.2f}); n={f['n']}.")
    else:
        out.append(f"Fit: lead count did not vary (all about {f['xbar']:.2f}); per-lead rate not identifiable, "
                   f"mean {f['ybar']:.3f} pts/h used for every N (sd {f['s']:.3f}, n={f['n']}).")
    head = ["leads", "pts/h", "+-se", "to 100% (h)", "100% at", "to 97% (h)", "97% at", "vs reset", "note"]
    body = []
    for r in fc["rows"]:
        if r["rate"] is None:
            body.append([str(r["leads"])] + ["-"] * 7 + ["no rate"])
            continue
        if r["h100"] is None:
            vs = "no rise: reaches the reset"
        elif r["runs_out_before_reset"]:
            vs = f"RUNS OUT {r['margin_h']:.1f} h before"
        else:
            vs = f"ok, {-r['margin_h']:.1f} h of margin"
        rng = ""
        if r.get("h100_lo") is not None and r.get("h100_hi") is not None:
            rng = f"100%: {r['h100_lo']:.0f}..{r['h100_hi']:.0f} h at +-1 se"
        elif r.get("h100_lo") is not None:
            rng = f"100%: from {r['h100_lo']:.0f} h"
        note = ("extrapolated beyond leads seen; " if r["extrapolated"] else "") + rng
        body.append([str(r["leads"]), f"{r['rate']:.2f}", f"{r['se']:.2f}" if r["se"] is not None else "-",
                     f_num(r["h100"], 1, "never"), fmt_t(r["t100"]), f_num(r["h97"], 1, "never"), fmt_t(r["t97"]),
                     vs, note])
    if md:
        out.append("| " + " | ".join(head) + " |")
        out.append("|" + "|".join("---" for _ in head) + "|")
        out += ["| " + " | ".join(b) + " |" for b in body]
    else:
        w = [max(len(h), *(len(b[i]) for b in body)) for i, h in enumerate(head)]
        out.append("  ".join(h.ljust(w[i]) for i, h in enumerate(head)))
        out += ["  ".join(c.ljust(w[i]) for i, c in enumerate(b)) for b in body]
    for target in (100, 97):
        s = fc["steady"][target]
        if s is None:
            txt = "no estimate"
        elif isinstance(s, str):
            txt = s
        elif s < 0:
            txt = f"none: even 0 leads reaches {target}% before the reset (base {f['a']:.2f} pts/h)"
        else:
            txt = f"{s:.2f} leads (floor {int(math.floor(s))})" + ("; beyond the leads seen" if f["xmax"] is not None
                                                                     and s > f["xmax"] else "")
        out.append(f"Largest steady lead count that stays under {target}% until the reset: {txt}.")
    return out


def parse_utc(s):
    return p_ts(s)


def cmd_forecast(a, paths):
    readings, _, _ = read_usage(paths.log)
    samples, _ = read_leads(paths.log)
    leads = [float(x) if "." in x else int(x) for x in a.leads.split(",") if x.strip()]
    fc = forecast(a.pct, parse_utc(a.at), parse_utc(a.reset), leads, readings, samples, a.window)
    lines = fmt_forecast(fc, a.md)
    print("\n".join(lines))
    return 0


# ----------------------------------------------------------------------------- record

def cmd_record(a, paths):
    now = dt.datetime.now(UTC)
    since = a.since or (now.date() - dt.timedelta(days=1)).isoformat()
    rows, meta = build_daily(paths, since, now)
    readings, _, last_reset = read_usage(paths.log)
    samples, _ = read_leads(paths.log)
    at = parse_utc(a.at) if a.at else (readings[-1][0] if readings else now)
    pct = a.pct if a.pct is not None else (readings[-1][1] if readings else None)
    reset = parse_utc(a.reset) if a.reset else reset_time_from(last_reset)
    leads = [int(x) for x in a.leads.split(",") if x.strip()]
    rec = dict(at=now.strftime("%Y-%m-%d %H:%M:%S"), daily=rows, meta=meta, forecast_inputs=None, forecast=None)
    if pct is not None and reset is not None:
        fc = forecast(pct, at, reset, leads, readings, samples, a.window)
        f = fc["fit"]
        rec["forecast_inputs"] = dict(pct=pct, at=fmt_t(at), reset=fmt_t(reset), leads=leads, window_h=a.window,
                                      buckets=fc["buckets"])
        rec["forecast"] = dict(
            fit={k: (round(v, 4) if isinstance(v, float) else v) for k, v in f.items()},
            rows=[{k: (fmt_t(v) if isinstance(v, dt.datetime) else (round(v, 3) if isinstance(v, float) else v))
                   for k, v in r.items()} for r in fc["rows"]],
            steady={str(k): (round(v, 3) if isinstance(v, float) else v) for k, v in fc["steady"].items()})
    paths.out.mkdir(parents=True, exist_ok=True)
    target = paths.out / "week.jsonl"
    with target.open("a") as fh:
        fh.write(json.dumps(rec, default=str) + "\n")
    print(f"recorded {len(rows)} daily rows and "
          f"{'the forecast inputs' if rec['forecast_inputs'] else 'no forecast (no reading or reset)'} to {target}")
    return 0


# ----------------------------------------------------------------------------- main

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root")
    ap.add_argument("--log")
    ap.add_argument("--out")
    ap.add_argument("--branch", default="w2/integrate")
    sub = ap.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("daily")
    d.add_argument("--since", default="2026-11-02")
    d.add_argument("--md", action="store_true")
    f = sub.add_parser("forecast")
    f.add_argument("--pct", type=float, required=True)
    f.add_argument("--at", required=True)
    f.add_argument("--reset", required=True)
    f.add_argument("--leads", default="1,3,5")
    f.add_argument("--window", type=int, default=FORECAST_WINDOW_H)
    f.add_argument("--md", action="store_true")
    r = sub.add_parser("record")
    r.add_argument("--since")
    r.add_argument("--pct", type=float)
    r.add_argument("--at")
    r.add_argument("--reset")
    r.add_argument("--leads", default="1,3,5")
    r.add_argument("--window", type=int, default=FORECAST_WINDOW_H)
    a = ap.parse_args(argv)
    paths = Paths(a.root, a.log, a.out, a.branch)
    return {"daily": cmd_daily, "forecast": cmd_forecast, "record": cmd_record}[a.cmd](a, paths)


if __name__ == "__main__":
    sys.exit(main())
