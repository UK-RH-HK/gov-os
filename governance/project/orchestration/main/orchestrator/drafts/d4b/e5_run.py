#!/usr/bin/env python3
"""E5's reader run (E3-E5-DESIGN §1, DEC-1092): one reader call per question on the 12,000-token bundle (a page of 40,
E5's live run: ~/gov-os-eval/runs/w4-e5/), E3's reader and graders, compared with E3's run on today's 6,000-token
bundle (its run folder). Counts and ids only. The runaway brake at twice the projection. Run with the pin's python.
Usage: <pin python> e5_run.py <run folder> <projection usd>"""
import json, sys, time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

src = Path(__file__).with_name("e3_run.py").read_text().replace("\nmain()\n", "\n")
E3 = type(sys)("e3"); exec(compile(src, "e3_run.py", "exec"), E3.__dict__)
HOME = Path.home()
E3.E0 = HOME / "gov-os-runs/D4B/w4-e5"           # its measure.txt files (r80/, r60/)
E3.KEPT = HOME / "gov-os-eval/runs/w4-e5"        # its kept first calls
E3RUN = HOME / "gov-os-runs/D4B/e3"


def main():
    run, projection = Path(sys.argv[1]), float(sys.argv[2]); brake = 2 * projection; run.mkdir(parents=True, exist_ok=True)
    qs = E3.load(); t0 = time.time()
    jobs = [(q, "bundle", [E3.sent(e) for e in json.loads(Path(q["first"]).read_text())["result"]["evidence"]]) for q in qs]
    with ThreadPoolExecutor(E3.WORKERS) as pool:
        rows = [r for r in pool.map(lambda j: E3.one(*j, run, brake), jobs) if r]
    by = {r["id"]: r for r in rows}
    base = {}
    for f in E3RUN.glob("*.bundle.json"):
        r = json.loads(f.read_text()); base[r["id"]] = r
    ids = [q["id"] for q in qs if not q["apart"] and q["id"] in by and q["id"] in base]
    rep = {"jobs": len(rows), "stopped": E3.stop_reason[0], "projection_usd": projection, "brake_usd": brake,
           "spent_usd": round(E3.spent[0], 2), "wall_min": round((time.time() - t0) / 60, 1),
           "errors": sum(1 for r in rows if r["verdict"] == "error")}
    for kind in ("visible", "hidden", "spent", "the 138"):
        rs = [by[i] for i in ids if kind == "the 138" or by[i]["kind"] == kind]
        bs = [base[i] for i in ids if kind == "the 138" or base[i]["kind"] == kind]
        rep[f"12000 {kind}"] = sum(map(E3.right, rs)); rep[f"6000 (E3) {kind}"] = sum(map(E3.right, bs))
    rs = [by[i] for i in ids]
    rep["12000 correct"] = sum(1 for r in rs if r["verdict"] == "answer" and (r["grades"].get("grader") or {}).get("grade") == "correct")
    rep["12000 wrong claims"] = sum(1 for r in rs if r["verdict"] == "answer" and (r["grades"].get("grader") or {}).get("grade") != "correct")
    rep["12000 gold in bundle"] = sum(r["gold_in_bundle"] for r in rs)
    rep["12000 bundle chars median"] = sorted(r["bundle_chars"] for r in rs)[len(rs) // 2]
    rep["12000 items median"] = sorted(r["items"] for r in rs)[len(rs) // 2]
    rep["nonexistent-id right"] = sum(E3.right(by[q["id"]]) for q in qs if q["apart"] and q["id"] in by)
    rep["mcnemar 12000 vs 6000 (gains, losses, p)"] = E3.mcnemar([E3.right(base[i]) for i in ids], [E3.right(by[i]) for i in ids])
    (run / "summary.json").write_text(json.dumps(rep, indent=1))
    print(json.dumps(rep, indent=1))


main()
