"""CAPACITY-1: measured lead runs (log/*-A5-*.json): wall hours by the ticket's profile, the DONE/PACKAGES share,
runs per ticket, and cost. Writes runs.json."""
import glob
import json
import os
import re
import statistics as st

O = "/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator"
HERE = os.path.dirname(os.path.abspath(__file__))
tickets = json.load(open(os.path.join(HERE, "tickets.json")))
by_wbs = {t["wbs"]: t for t in tickets.values()}

runs = []
for p in glob.glob(O + "/log/*-A5-*.json"):
    name = os.path.basename(p)
    m = re.match(r"(W2-\d+[a-z]?)-A5-", name)
    if not m:
        continue
    try:
        d = json.load(open(p))
    except (ValueError, OSError):
        continue
    if not isinstance(d, dict) or not d.get("duration_ms"):
        continue
    res = d.get("result") or ""
    st_m = re.search(r"^status:\s*\**\s*([A-Z_]+)", res, re.M)
    status = st_m.group(1) if st_m else "?"
    w2 = m.group(1)
    prof = by_wbs.get(w2, {}).get("profile", "?")
    runs.append({"w2": w2, "file": name, "hours": d["duration_ms"] / 3.6e6, "cost": d.get("total_cost_usd") or 0,
                 "status": status, "profile": prof, "mtime": os.path.getmtime(p)})

out = {"n": len(runs)}
for prof in ("LITE", "STANDARD", "FULL"):
    hs = [r["hours"] for r in runs if r["profile"] == prof]
    if hs:
        out[prof] = {"runs": len(hs), "median_h": round(st.median(hs), 2), "mean_h": round(st.mean(hs), 2),
                     "p75_h": round(sorted(hs)[int(0.75 * (len(hs) - 1))], 2)}
per_ticket = {}
for r in runs:
    per_ticket.setdefault(r["w2"], []).append(r)
done = [w for w, rs in per_ticket.items() if any(x["status"] == "DONE" for x in rs)]
runs_to_done = [len(per_ticket[w]) for w in done]
out["status_counts"] = {s: sum(1 for r in runs if r["status"] == s) for s in set(r["status"] for r in runs)}
out["tickets_with_runs"] = len(per_ticket)
out["tickets_done"] = len(done)
out["runs_per_done_ticket_mean"] = round(st.mean(runs_to_done), 2) if runs_to_done else None
out["runs_per_done_ticket_median"] = st.median(runs_to_done) if runs_to_done else None
recent = [r for r in runs if r["mtime"] > 1793318400]  # since 2026-10-30 00:00 UTC
out["recent"] = {"runs": len(recent), "hours": round(sum(r["hours"] for r in recent), 1),
                 "cost": round(sum(r["cost"] for r in recent), 1),
                 "status_counts": {s: sum(1 for r in recent if r["status"] == s) for s in set(r["status"] for r in recent)}}
for prof in ("LITE", "STANDARD", "FULL"):
    hs = [r["hours"] for r in recent if r["profile"] == prof]
    if hs:
        out["recent"][prof] = {"runs": len(hs), "median_h": round(st.median(hs), 2)}
json.dump({"summary": out, "runs": runs}, open(os.path.join(HERE, "runs.json"), "w"), indent=1)
print(json.dumps(out, indent=1))
