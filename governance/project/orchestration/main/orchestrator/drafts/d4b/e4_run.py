#!/usr/bin/env python3
"""E4's reader runs (E3-E5-DESIGN §1, DEC-1092): one reader call per question on today's bundle as M3 (zerank + gte)
and M1 (the 0.6B + gte) build it (E4's replays: measure.txt in ~/gov-os-runs/D4B/e4/<cell>/<set>/, kept first calls
in ~/gov-os-eval/runs/e4/<cell>-<set>/), E3's reader and graders, each compared with E3's run on the 0.6B's bundle
(E3's "today's bundle", shared). Counts and ids only. The runaway brake at twice the projection. The pin's python.
Usage: <pin python> e4_run.py <run folder> <projection usd>"""
import json, sys, time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

src = Path(__file__).with_name("e3_run.py").read_text().replace("\nmain()\n", "\n")
E3 = type(sys)("e3"); exec(compile(src, "e3_run.py", "exec"), E3.__dict__)
HOME = Path.home()
E3RUN = HOME / "gov-os-runs/D4B/e3"
CELLS = ("m3", "m1")


def load_cell(cell):
    """E3's questions, with each question's first call taken from the cell's replay outputs."""
    E3.E0 = HOME / f"gov-os-runs/D4B/e4/{cell}"
    qs = E3.load()  # reads E0/<r80|r60>/measure.txt for the call numbers
    for q in qs:
        kept = "r60" if q["kind"] == "spent" else "r80"
        n = int(Path(q["first"]).stem)
        q["first"] = HOME / f"gov-os-eval/runs/e4/{cell}-{kept}" / f"{n:05d}.json"
    return qs


def main():
    run, projection = Path(sys.argv[1]), float(sys.argv[2]); brake = 2 * projection; run.mkdir(parents=True, exist_ok=True)
    t0 = time.time(); jobs = []
    for cell in CELLS:
        for q in load_cell(cell):
            items = [E3.sent(e) for e in json.loads(Path(q["first"]).read_text())["result"]["evidence"]]
            jobs.append((q, cell, items))
    with ThreadPoolExecutor(E3.WORKERS) as pool:
        rows = [r for r in pool.map(lambda j: E3.one(*j, run, brake), jobs) if r]
    base = {}
    for f in E3RUN.glob("*.bundle.json"):
        r = json.loads(f.read_text()); base[r["id"]] = r
    rep = {"jobs": len(rows), "stopped": E3.stop_reason[0], "projection_usd": projection, "brake_usd": brake,
           "spent_usd": round(E3.spent[0], 2), "wall_min": round((time.time() - t0) / 60, 1),
           "errors": sum(1 for r in rows if r["verdict"] == "error")}
    for cell in CELLS:
        by = {r["id"]: r for r in rows if r["condition"] == cell}
        ids = [i for i in by if not by[i]["apart"] and i in base]
        for kind in ("visible", "hidden", "spent", "the 138"):
            rep[f"{cell} {kind}"] = sum(E3.right(by[i]) for i in ids if kind == "the 138" or by[i]["kind"] == kind)
        rep[f"{cell} correct"] = sum(1 for i in ids if by[i]["verdict"] == "answer" and (by[i]["grades"].get("grader") or {}).get("grade") == "correct")
        rep[f"{cell} wrong claims"] = sum(1 for i in ids if by[i]["verdict"] == "answer" and (by[i]["grades"].get("grader") or {}).get("grade") != "correct")
        rep[f"{cell} gold in bundle"] = sum(by[i]["gold_in_bundle"] for i in ids)
        rep[f"{cell} nonexistent-id right"] = sum(E3.right(by[i]) for i in by if by[i]["apart"])
        rep[f"{cell} vs 0.6B bundle (E3) (gains, losses, p)"] = E3.mcnemar([E3.right(base[i]) for i in ids], [E3.right(by[i]) for i in ids])
    rep["0.6B bundle (E3) the 138"] = sum(E3.right(base[i]) for i in base if not base[i]["apart"])
    (run / "summary.json").write_text(json.dumps(rep, indent=1))
    print(json.dumps(rep, indent=1))


main()
