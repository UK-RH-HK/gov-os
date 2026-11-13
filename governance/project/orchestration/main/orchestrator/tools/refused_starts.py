"""Refused-starts log (DEC-1157 (13); CTO scratch tool, stdlib only; run forever, one look every 60 s).

Every minute: each live line of dispatch/ready.txt (not commented) whose log name is not yet in dispatch/started.txt is a
ready line not started. For each, one JSON line goes to log/refused-starts.jsonl with the time, the W2, the log name and
why, read from dispatch/status.json: the dispatcher's admission verdict (`admit`), the forecast's binding resource and
its text when the forecast refuses, the memory gate's line when it is shut, and whether a land is running. A line that
is waiting only for the dispatcher's next tick (written less than 90 s ago) is not logged. Read-only on the dispatcher's
files; writes only its own log.

    refused_starts.py [--every 60] [--once]
"""
import json
import sys
import time
from datetime import datetime
from pathlib import Path

ORCH = Path("/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator")
D = ORCH / "dispatch"
OUT = ORCH / "log" / "refused-starts.jsonl"


def live_lines():
    out = []
    try:
        for line in (D / "ready.txt").read_text().splitlines():
            parts = line.split()
            if len(parts) >= 4 and not line.lstrip().startswith("#"):
                out.append(parts[:4])
    except OSError:
        pass
    return out


def started_logs():
    try:
        return {l.split()[-1] for l in (D / "started.txt").read_text().splitlines() if l.split()}
    except OSError:
        return set()


def why(st):
    reasons = []
    if st.get("admit") is False:
        reasons.append("admission: refused")
    fc = (st.get("forecast") or {}).get("lead") or {}
    if fc and not fc.get("ok", True):
        res = fc.get("resources", {}).get((fc.get("binding") or "").lower(), {})
        reasons.append(f"forecast: {fc.get('binding')}: {res.get('text', '')}"[:300])
    if st.get("gate_open") is False:
        reasons.append(f"gate: {str(st.get('gate'))[:200]}")
    if st.get("disk_open") is False:
        reasons.append(f"disk: {str(st.get('disk'))[:120]}")
    if st.get("outside_slot"):
        reasons.append(f"heavy step outside a slot: {str(st['outside_slot'][0])[:120]}")
    if not reasons:
        reasons.append("no refusal in status.json (the dispatcher's own order or its next tick)")
    return reasons


def look():
    try:
        st = json.loads((D / "status.json").read_text())
    except (OSError, ValueError):
        st = {}
    started = started_logs()
    try:
        age = time.time() - (D / "ready.txt").stat().st_mtime
    except OSError:
        age = 999
    rows = []
    for w2, tid, brief, log in live_lines():
        if log in started or age < 90:
            continue
        rows.append({"t": datetime.now().strftime("%F %T"), "w2": w2, "ticket": tid, "log": log,
                     "leads_running": st.get("lead_count"), "land_running": st.get("land_running"),
                     "why": why(st)})
    if rows:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        with OUT.open("a") as f:
            for r in rows:
                f.write(json.dumps(r) + "\n")
    return rows


def main(argv):
    every = int(argv[argv.index("--every") + 1]) if "--every" in argv else 60
    if "--once" in argv:
        for r in look():
            print(json.dumps(r))
        return 0
    while True:
        try:
            look()
        except Exception as exc:  # noqa: BLE001 - keep watching; note the error
            with OUT.open("a") as f:
                f.write(json.dumps({"t": datetime.now().strftime("%F %T"), "error": repr(exc)[:200]}) + "\n")
        time.sleep(every)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
