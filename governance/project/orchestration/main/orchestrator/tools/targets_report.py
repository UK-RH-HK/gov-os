"""The standing targets' report for the morning package (owner, DEC-1038 (4); the dispatcher's targets, DEC-1039).

    python3 targets_report.py [--since YYYY-MM-DD[THH:MM]] [--hours 07:30-02:00] [--json]
                              [--balance <balance.jsonl>] [--incidents <folder>]

Reads (read only) the dispatcher's balance rows, log/capacity/balance.jsonl (and its rotated balance-*.jsonl beside
it), one a pass, each with the targets it judged: True breached, False met, null not measured; and the incident
records in log/incidents/<date>-<HHMM>-<target>.md. For each target over the working hours (--hours, a span that
may cross midnight; default 07:30-02:00) since --since (default: the last 24 hours):
  - T1 (busy cores within the band, or below it with no work waiting): the share of passes met, target at least 80 %;
  - T2 (memory available above the floor), T3 (GPU used at most total minus headroom), outside-slot (no heavy step
    outside a slot for over 15 minutes counts as an incident): target 100 %;
  - T4 (no timed-out embedding), T5 (no cold rebuild): the passes with events, target zero;
then the incidents with their causes (the record's Cause field, as the CTO filled it) and whether each closed, and the
worst hour (the clock hour with the most breached passes). Exit 0; 2 when the balance rows cannot be read.
"""
import argparse
import json
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

ORCH = Path(__file__).resolve().parents[1]
BALANCE = ORCH / "log/capacity/balance.jsonl"
INCIDENTS = ORCH / "log/incidents"
TARGETS = {"T1": ("busy cores within the band", 80.0), "T2": ("memory available above the floor", 100.0),
           "T3": ("GPU used at most total minus headroom", 100.0), "T4": ("no timed-out embedding", None),
           "T5": ("no cold rebuild", None), "outside-slot": ("no heavy step outside a slot", 100.0)}


def hours_span(text):
    """'07:30-02:00' -> (450, 120) in minutes of the day."""
    m = re.fullmatch(r"(\d{1,2}):(\d{2})-(\d{1,2}):(\d{2})", text.strip())
    if not m:
        raise ValueError(f"--hours wants HH:MM-HH:MM, not {text!r}")
    a, b, c, d = (int(x) for x in m.groups())
    return a * 60 + b, c * 60 + d


def in_hours(t, span):
    lo, hi = span
    m = t.hour * 60 + t.minute
    return lo <= m < hi if lo < hi else (m >= lo or m < hi)


def read_rows(path, since, until):
    files = sorted(path.parent.glob("balance-*.jsonl")) + [path]
    rows = []
    for f in files:
        try:
            text = f.read_text()
        except OSError:
            continue
        for line in text.splitlines():
            try:
                r = json.loads(line)
                t = datetime.strptime(r["t"], "%Y-%m-%dT%H:%M:%S")
            except (ValueError, KeyError, TypeError):
                continue
            if since <= t <= until:
                rows.append((t, r))
    return sorted(rows, key=lambda x: x[0])


def read_incidents(folder, since):
    out = []
    for p in sorted(folder.glob("*.md")) if folder.is_dir() else []:
        m = re.match(r"(\d{4}-\d{2}-\d{2})-(\d{2})(\d{2})-(.+?)(?:-\d+)?\.md$", p.name)
        if not m:
            continue
        at = datetime.strptime(f"{m.group(1)} {m.group(2)}:{m.group(3)}", "%Y-%m-%d %H:%M")
        if at < since:
            continue
        text = p.read_text(errors="replace")
        cause = re.search(r"^- \*\*Cause:\*\*[ \t]*(.*)$", text, re.M)
        closed = re.search(r"^- \*\*Closed:\*\*[ \t]*(.*)$", text, re.M)
        target = m.group(4).split("-")[0] if m.group(4).startswith("T") else m.group(4)
        out.append({"at": at.strftime("%Y-%m-%d %H:%M"), "target": target, "record": p.name,
                    "cause": (cause.group(1).strip() if cause else "") or "(not filled)",
                    "closed": closed.group(1).strip() if closed else None})
    return out


def report(rows, span, incidents):
    per = {}
    hours = {}
    working = [(t, r) for t, r in rows if in_hours(t, span)]
    for k, (name, want) in TARGETS.items():
        vals = [(t, (r.get("targets") or {}).get(k)) for t, r in working]
        vals = [(t, v) for t, v in vals if v is not None]
        met = sum(1 for _, v in vals if v is False)
        breached = len(vals) - met
        share = round(100.0 * met / len(vals), 1) if vals else None
        if want is None:
            ok = breached == 0
        else:
            ok = share is not None and share >= want
        by_hour = {}
        for t, v in vals:
            h = t.strftime("%Y-%m-%d %H:00")
            by_hour.setdefault(h, [0, 0])
            by_hour[h][0] += 1
            by_hour[h][1] += 1 if v else 0
            if v:
                hours[h] = hours.get(h, 0) + 1
        worst = min(by_hour.items(), key=lambda kv: (-kv[1][1] / kv[1][0], -kv[1][1], kv[0]),
                    default=None)  # the lowest share met, the earliest of equals
        per[k] = {"name": name, "passes": len(vals), "met": met, "breached": breached, "share": share,
                  "target": want, "ok": ok if vals else None,
                  "worst_hour": (None if not worst or not worst[1][1] else
                                 {"hour": worst[0], "share": round(100.0 * (1 - worst[1][1] / worst[1][0]), 1)})}
    worst = min(hours.items(), key=lambda kv: (-kv[1], kv[0]), default=None)  # the earliest of the worst
    return {"passes": len(working), "targets": per, "incidents": incidents,
            "worst_hour": {"hour": worst[0], "breached_passes": worst[1]} if worst else None}


def text_of(rep, since, until, hours):
    out = [f"Targets {since:%Y-%m-%d %H:%M} to {until:%Y-%m-%d %H:%M}, working hours {hours} ({rep['passes']} passes)"]
    for k, v in rep["targets"].items():
        verdict = "not measured" if v["ok"] is None else ("MET" if v["ok"] else "MISSED")
        if v["target"] is None:
            body = f"{v['breached']} passes with events (target 0)"
        else:
            body = (f"met {v['share']} % of {v['passes']} passes (target "
                    f"{'at least ' if v['target'] < 100 else ''}{v['target']:g} %)")
        w = v["worst_hour"]
        out.append(f"{k} {v['name']}: {body}: {verdict}" + (f"; worst hour {w['hour']} ({w['share']} % met)" if w else ""))
    out.append(f"Incidents: {len(rep['incidents'])}")
    for i in rep["incidents"]:
        out.append(f"  {i['at']} {i['target']}: cause: {i['cause']}; " + (f"closed {i['closed']}" if i["closed"]
                                                                          else "open") + f" ({i['record']})")
    w = rep["worst_hour"]
    out.append("Worst hour: " + (f"{w['hour']} ({w['breached_passes']} breached target-passes)" if w else "none"))
    return "\n".join(out)


def main(argv=None, now=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--since", help="YYYY-MM-DD or YYYY-MM-DDTHH:MM (default: 24 hours ago)")
    ap.add_argument("--hours", default="07:30-02:00")
    ap.add_argument("--balance", default=str(BALANCE))
    ap.add_argument("--incidents", default=str(INCIDENTS))
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    until = now or datetime.now()
    try:
        span = hours_span(a.hours)
        since = (datetime.fromisoformat(a.since) if a.since else until - timedelta(hours=24))
    except ValueError as exc:
        print(f"targets_report: {exc}", file=sys.stderr)
        return 2
    bal = Path(a.balance)
    if not bal.exists() and not list(bal.parent.glob("balance-*.jsonl")):
        print(f"targets_report: no balance rows at {bal}", file=sys.stderr)
        return 2
    rep = report(read_rows(bal, since, until), span, read_incidents(Path(a.incidents), since))
    print(json.dumps(rep, indent=1) if a.json else text_of(rep, since, until, a.hours))
    return 0


if __name__ == "__main__":
    sys.exit(main())
