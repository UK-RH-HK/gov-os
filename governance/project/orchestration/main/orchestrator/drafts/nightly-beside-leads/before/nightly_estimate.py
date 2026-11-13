"""The nightly's measured duration estimate (owner, standing, DEC-933 item 2).

    python3 nightly_estimate.py estimate            -> one JSON line: estimate_s and its parts
    python3 nightly_estimate.py record <parallel.xml> <serial.xml> <setup_s> <actual_s> <estimate_s> [<lock_wait_s>]

The estimate is measured from the per-test durations in the last full runs' JUnit files, never fixed:
  parallel = the newest run's parallel sum / the effective parallelism, and never less than its longest case.
             The effective parallelism is the lowest (sum / wall) of the last three full runs: on this machine about
             7.4 to 8.2, not the 20 workers (subprocess-heavy tests share the CPUs). sum / 20 would book about 45 %
             of the real time (measured 2026-10-28 on the nightly of 2026-10-25 and the full closes of W2-66, W2-70).
  serial   = the newest run's serial sum (one case at a time).
  setup    = the smallest recorded clone + rebuild + collection time of the last three runs (420 s until one is
             recorded). The time spent waiting for the verification lock is recorded apart (lock_wait_s) and is never
             setup (DEC-939 item 6); the smallest also drops a night whose setup was recorded before that split.
  estimate = (parallel + serial + setup) * 1.10.
Sources, newest first: `log/nightly/history.jsonl` (one line per nightly, written by `record`), then the JUnit files
of full runs still on disk (the nightly's, the ACT clone runs', and full closes' `*regression-parallel.xml`).
"""
import glob
import json
import os
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ORCH = Path("/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator")
HISTORY = ORCH / "log/nightly/history.jsonl"
FULL_CASES = 10000          # a parallel file with fewer cases is a scoped run, not a full one
MARGIN = 1.10
DEFAULT_SETUP_S = 420


def sums(path: str) -> dict:
    root = ET.parse(path).getroot()
    suites = [root] if root.tag == "testsuite" else list(root.iter("testsuite"))
    cases = [float(c.get("time") or 0) for c in root.iter("testcase")]
    return {"cases": len(cases), "sum": sum(cases), "longest": max(cases or [0]),
            "wall": sum(float(s.get("time") or 0) for s in suites)}


def junit_runs() -> list[dict]:
    """Full runs still on disk: (mtime, parallel sums, serial sums)."""
    pairs = []
    for par in glob.glob("/tmp/gov-os-nightly-junit/*/parallel.xml") + glob.glob("/tmp/gov-os-act-junit/*/parallel.xml"):
        ser = os.path.join(os.path.dirname(par), "serial.xml")
        if os.path.exists(ser):
            pairs.append((par, ser))
    for par in glob.glob(str(ORCH.parents[1] / "close/*/*/*regression-parallel.xml")):
        sers = glob.glob(os.path.join(os.path.dirname(par), "*regression-serial-afterwards.xml"))
        if sers:
            pairs.append((par, sers[0]))
    runs = []
    for par, ser in pairs:
        try:
            p, s = sums(par), sums(ser)
        except (ET.ParseError, OSError):
            continue
        if p["cases"] >= FULL_CASES and p["wall"] > 0:
            runs.append({"when": os.path.getmtime(par), "parallel": p, "serial": s, "source": par})
    return sorted(runs, key=lambda r: r["when"], reverse=True)


def history() -> list[dict]:
    if not HISTORY.exists():
        return []
    lines = [json.loads(line) for line in HISTORY.read_text().splitlines() if line.strip()]
    return sorted(lines, key=lambda r: r["when"], reverse=True)


def estimate() -> dict:
    runs = (history() + junit_runs())[:3]
    runs = sorted(runs, key=lambda r: r["when"], reverse=True)
    if not runs:
        return {"estimate_s": None, "why": "no full run measured"}
    newest = runs[0]
    effective = min(r["parallel"]["sum"] / r["parallel"]["wall"] for r in runs)
    parallel = max(newest["parallel"]["sum"] / effective, newest["parallel"]["longest"])
    serial = newest["serial"]["sum"]
    setups = [r["setup_s"] for r in runs if r.get("setup_s")]
    setup = min(setups) if setups else DEFAULT_SETUP_S
    total = (parallel + serial + setup) * MARGIN
    return {"estimate_s": round(total), "parallel_s": round(parallel), "serial_s": round(serial),
            "setup_s": round(setup), "effective_workers": round(effective, 2), "margin": MARGIN,
            "runs": [r.get("source", "history") for r in runs]}


def record(par: str, ser: str, setup_s: str, actual_s: str, estimate_s: str, lock_wait_s: str = "0") -> None:
    line = {"when": os.path.getmtime(par), "parallel": sums(par), "serial": sums(ser), "setup_s": float(setup_s),
            "actual_s": float(actual_s), "estimate_s": float(estimate_s) if estimate_s else None,
            "lock_wait_s": float(lock_wait_s or 0), "source": "history"}
    HISTORY.parent.mkdir(parents=True, exist_ok=True)
    with HISTORY.open("a") as out:
        out.write(json.dumps(line) + "\n")


if __name__ == "__main__":
    if sys.argv[1:2] == ["estimate"]:
        print(json.dumps(estimate()))
    elif sys.argv[1:2] == ["record"] and len(sys.argv) in (7, 8):
        record(*sys.argv[2:])
    else:
        sys.exit(__doc__)
