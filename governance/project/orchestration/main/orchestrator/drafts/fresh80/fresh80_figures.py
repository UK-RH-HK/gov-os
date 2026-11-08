#!/usr/bin/env python3
"""The fresh 80's figures (FRESH-80-1 §3.4, §4.3; DEC-1097 (1)(c), (d)). Counts only.

1. **The verdict line, from the judged condition only** (the reader run's A2), against K9's bar: right end to end at
   least 85 % and wrong claims at most 5 % of the 79 (at least 68 right, at most 3 wrong), target 95 % (76), on the
   observed figure; the exact (Clopper-Pearson) 95 % interval beside it, and Wilson's (the form of FRESH-80-1 §4.3's
   example) beside that. The denominator is every question but the nonexistent-id one: a question with no row (a
   brake stop) counts as not right and is named, never dropped.
2. **Beside it, as data:** hit@5 (and hit@10, hit@20, MRR, in the bundle, full evidence) from the counting attempt's
   measure; "answer correct, citation aside"; the stricter of the two grades; grader agreement; A1 and A3 and the
   McNemar A1 against A2; the nonexistent-id question apart (right or not, and whether the product stopped with
   UNRESOLVED_IDS naming its id, DEC-1071 (5)), or its drop when the pre-flight found its id now exists (item 6);
   the search failures (item 17), the citations outside every received item (item 18), the calls run again, the
   grades that never came, the spend.
3. **The data table, "data only, not judged"**: each data condition's summary (fresh80_data.py), apart from the
   verdict.

    python3 fresh80_figures.py --sets-root ~/gov-os-eval
"""
import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import f80lib as L  # noqa: E402

LINE = re.compile(r"(\S+) \((\w+)\): hit@5 (yes|no) \(first gold rank (\d+|-)\), in the bundle (yes|no); "
                  r"full evidence (yes|no)")
DATA = ("e3", "e3sa", "e5", "e4", "e2g")


def outcome(r, cut):
    """E2's cut, byte for byte (e2_run.py's outcome)."""
    return L.e2_parts()["outcome"](r, cut)


def strict_grade(r):
    g = r.get("grades") or {}
    a, b = (g.get("grader") or {}).get("grade"), (g.get("check") or {}).get("grade")
    return "correct" if a == "correct" and b == "correct" else (a if a != "correct" else b)


def stricter(r, cut=2):
    """The row with the stricter of the two grades (item 8, data only)."""
    s = dict(r)
    s["grades"] = {"grader": {"grade": strict_grade(r)}}
    return outcome(s, cut)


def retrieval(measure_txt: Path, main_ids: set) -> dict:
    v = []
    for line in Path(measure_txt).read_text().splitlines():
        m = LINE.match(line)
        if m and m[1] in main_ids:
            v.append((int(m[4]) if m[4] != "-" else None, m[5] == "yes", m[6] == "yes"))
    n = len(v)
    hit = lambda k: sum(1 for r, _, _ in v if r and r <= k)  # noqa: E731
    return {"n": n, "hit5": hit(5), "hit10": hit(10), "hit20": hit(20),
            "mrr": round(sum(1 / r for r, _, _ in v if r) / n, 4) if n else 0.0,
            "in_bundle": sum(1 for x in v if x[1]), "full": sum(1 for x in v if x[2])}


def mcnemar(a, b):
    return L.e2_parts()["mcnemar"](a, b)


def verdict(rows: dict, planned_main: list, apart_ids: list, dropped: bool) -> dict:
    n = len(planned_main)
    got = [rows[i] for i in planned_main if i in rows]
    missing = sorted(i for i in planned_main if i not in rows)
    o = {c: [outcome(r, c) for r in got] for c in (1, 2, 3)}
    right = sum(x["right"] for x in o[2])
    wrong = sum(x["wrong"] for x in o[2])
    b = L.bar(right, wrong, n)
    st = [stricter(r) for r in got]
    graded = [r for r in rows.values() if r.get("grades")]  # every graded row, the apart one too, as E2 counted
    agree = sum(1 for r in graded if (r["grades"].get("grader") or {}).get("grade") ==
                (r["grades"].get("check") or {}).get("grade"))
    full = {i: rows.get(i) for i in planned_main}
    rt = {c: [bool(rows[i] and outcome(rows[i], c)["right"]) if i in rows else False for i in planned_main]
          for c in (1, 2, 3)}
    apart = []
    for i in apart_ids:
        r = rows.get(i)
        apart.append({"run": r is not None, "right": bool(r and outcome(r, 2)["right"]),
                      "stopped_naming_id": bool(r and r.get("first_gaps_name_ids")), "dropped": dropped})
    return {"n": n, "bar": b, "missing": missing, "A1": sum(x["right"] for x in o[1]), "A3": sum(x["right"] for x in o[3]),
            "A2": right, "wrong": wrong, "correct": sum(x["correct"] for x in o[2]),
            "not_found": sum(x["nf"] for x in o[2]), "strict_right": sum(x["right"] for x in st),
            "strict_wrong": sum(x["wrong"] for x in st), "agree": agree, "graded": len(graded),
            "mcnemar_a1_a2": mcnemar(rt[1], rt[2]), "mcnemar_a2_a3": mcnemar(rt[2], rt[3]), "apart": apart,
            "search_failures": sum(r["search_failures"] for r in rows.values()),
            "search_failure_ids": sorted(r["id"] for r in rows.values() if r["search_failures"]),
            "citations_outside": sum(r["citations_outside"] for r in rows.values()),
            "right_only_outside": sum(1 for r in got if r.get("citation_right_only_outside")),
            "retried": sum(r.get("calls_retried", 0) for r in rows.values()),
            "no_grade": sum(1 for r in rows.values() if r.get("grades") and
                            not (r["grades"].get("grader") or {}).get("grade")),
            "errors": sum(1 for r in rows.values() if r["final_verdict"] == "error"), "_full": len(full)}


def show(v: dict, ret: dict | None, summary: dict) -> None:
    n, b = v["n"], v["bar"]
    lo, hi = L.exact_interval(v["A2"], n)
    wl, wh = L.wilson_interval(v["A2"], n)
    L.say("== THE VERDICT (K9; the judged condition only: window 4's pin, the pool on, today's bundle, search again "
          "once, A2)")
    L.say(f"right end to end: {v['A2']} of {n} ({L.pct(v['A2'], n)}; exact 95 % interval {100 * lo:.1f} to "
          f"{100 * hi:.1f} %; Wilson {100 * wl:.1f} to {100 * wh:.1f} %); wrong claims: {v['wrong']} of {n} "
          f"({L.pct(v['wrong'], n)})")
    L.say(f"the bar: at least {b['need_right']} right ({'met' if b['right_ok'] else 'NOT met'}) and at most "
          f"{b['max_wrong']} wrong claims ({'met' if b['wrong_ok'] else 'NOT met'}): "
          f"{'PASSES' if b['passes'] else 'MISSES'}; the target 95 % (at least {b['target_right']}): "
          f"{'reached' if b['target_ok'] else 'not reached'}")
    if v["missing"]:
        L.say(f"not run (counted as not right, never dropped): {len(v['missing'])}: {', '.join(v['missing'])}")
    L.say("== beside the verdict (data, not judged)")
    if ret:
        L.say(f"hit@5 {ret['hit5']} of {ret['n']} ({L.pct(ret['hit5'], ret['n'])}); hit@10 {ret['hit10']}; hit@20 "
              f"{ret['hit20']}; MRR {ret['mrr']}; in the first bundle {ret['in_bundle']}; full evidence {ret['full']}")
    L.say(f"answer correct, citation aside (A2): {v['correct']} of {n}; not found (A2): {v['not_found']}")
    L.say(f"the stricter of the two grades (A2): right {v['strict_right']} of {n}, wrong claims {v['strict_wrong']}")
    L.say(f"grader agreement: {v['agree']} of {v['graded']}; grades that never came (fail closed): {v['no_grade']}")
    g, l, pv = v["mcnemar_a1_a2"]
    L.say(f"A1 (one search; E3's one-call prompt) {v['A1']}; A3 {v['A3']}; A1 against A2: {g} gains, {l} losses, "
          f"exact McNemar p {pv:.4f}")
    for k, a in enumerate(v["apart"], 1):
        if a["dropped"]:
            L.say("the nonexistent-id question: DROPPED from every figure (its id now exists: item 6)")
        else:
            L.say(f"the nonexistent-id question (apart, DEC-1071 (5)): run {'yes' if a['run'] else 'no'}; right "
                  f"{'yes' if a['right'] else 'no'}; the product stopped with UNRESOLVED_IDS naming its id: "
                  f"{'yes' if a['stopped_naming_id'] else 'no'}")
    L.say(f"later searches that failed (item 17): {v['search_failures']}"
          + (f": {', '.join(v['search_failure_ids'])}" if v["search_failure_ids"] else ""))
    L.say(f"citations outside every item the reader received (item 18): {v['citations_outside']}; right only by such "
          f"a citation: {v['right_only_outside']}")
    L.say(f"calls run once more: {v['retried']}; reader errors: {v['errors']}; spent {summary.get('spent_usd')} USD "
          f"(projection {summary.get('projection_usd')}, brake {summary.get('brake_usd')}); stopped: "
          f"{summary.get('stopped') or 'no'}")


def data_table(p) -> None:
    L.say("== DATA ONLY, NOT JUDGED (FRESH-80-1 §3.4: no figure here chooses anything)")
    any_ = False
    for c in DATA:
        f = p["data"] / c / "summary.json"
        if not f.is_file():
            continue
        any_ = True
        s = json.loads(f.read_text())
        for line in s.get("lines", []):
            L.say(f"{c}: {line}")
    if not any_:
        L.say("(no data condition has run)")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--sets-root", required=True)
    a = ap.parse_args(argv)
    L.guard_root(a.sets_root)
    p = L.paths(a.sets_root)
    run = p["reader"]
    if not run.is_dir():
        raise SystemExit("REFUSED: the judged reader run has no rows yet")
    rows = {}
    for f in sorted(run.glob("*.json")):
        if f.name not in ("summary.json", "plan.json"):
            r = json.loads(f.read_text())
            rows[r["id"]] = r
    summary = json.loads((run / "summary.json").read_text()) if (run / "summary.json").is_file() else {}
    att = L.counting_attempt(a.sets_root)
    plan = json.loads((run / "plan.json").read_text())
    apart_ids = sorted(plan["apart"])
    measured = list(L.first_calls(att / "measure.txt"))
    if sorted(measured) != sorted(plan["main"] + plan["apart"]):
        L.say("note: the measured ids and the reader's plan differ")
    try:
        pre = json.loads(p["preflight"].read_text())
        dropped = (pre.get("item6") or {}).get("nowhere") is False
    except (OSError, ValueError):
        pre, dropped = {}, False
        L.say("note: no preflight.json: item 6's answer not read")
    if len(apart_ids) != 1:
        L.say(f"note: questions counted apart {len(apart_ids)} (1 expected)")
    planned = [i for i in plan["main"]]
    if len(planned) != 79:  # code review R10: the declared denominator
        raise SystemExit(f"REFUSED: the judged questions are {len(planned)}, not the declared 79")
    declared_digest = (pre.get("item1") or {}).get("sha256")  # readiness-7 F6: the result repeats the digest
    now = L.set_digest(a.sets_root)
    L.say(f"the set's digest now {now}; as at the pre-flight: {'yes' if now == declared_digest else 'NO'}")
    v = verdict(rows, planned, apart_ids, dropped)
    ret = retrieval(att / "measure.txt", set(planned))
    show(v, ret, summary)
    data_table(p)
    out = {k: x for k, x in v.items() if not k.startswith("_")}
    out["retrieval"] = ret
    L.write_row(p["runs"], "figures.json", out)
    return 0


if __name__ == "__main__":
    sys.exit(L.run_tool("figures", main))
