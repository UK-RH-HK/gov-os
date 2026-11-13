#!/usr/bin/env python3
"""The fresh 80's judged reader run (FRESH-80-1 §3.1, §3.2 step 9, §3.5; items 6, 8, 16, 17, 18, 19; DEC-1097 (1)(a)).

E2's condition on the 80, exactly as E2 ran it on the 138, so the 80's A2 compares with the 138's 128:
  - each question's first bundle from the counting attempt's kept outputs (run_measure.sh; COUNTS);
  - E2's reader (claude-opus-5-5, effort high, no tools, no transcript), its instruction with the "may be incomplete"
    line, its schema, its prompt form (prompt_of), its attempt cap (3) and its A1/A2/A3 cut (outcome): all read from
    drafts/d4b/e2_run.py by its syntax tree, byte for byte, the file pinned by sha256 (readiness review F6);
  - later searches live with the pinned gov on E0's clone; graded by claude-opus-5-5 (counts) and claude-sonnet-5-5
    (agreement), E2's grader; the citation by the measure's matcher (families on).
What the 80 adds (FRESH-80-1 §2):
  - resume (item 16): a question with a row file is never run again; rows are written whole (rename);
  - a reader or grader call that returned nothing is run once more, never a third time (§3.5);
  - the brake (DEC-1091 (2)): projection 15 USD, brake 30; the spend is kept in a ledger, so a resumed run starts
    from what was spent; no new question starts past the brake, and the stop and its cause are written;
  - a failed later search is counted and named by id (item 17), never silent; a later search answered without the
    shared reranker service (rerank.by not "service") or without a route (lexical or semantic missing or unavailable),
    or with the pool's rerank fallen back, is a failed search too (code review F1);
  - the citations outside every item the reader received are counted (item 18);
  - both graders' grades are kept, so the figures give the stricter grade as data (item 8);
  - the nonexistent-id question is found by its category, counted apart, and its first bundle's stopping_reason and
    gaps are read for DEC-1071 (5) (item 6); its id is never printed.
The run folder is <sets root>/runs/fresh-80/reader (derived here). Standard output: ids and counts only.

    <pin python> fresh80_reader.py --sets-root ~/gov-os-eval --dry
    <pin python> fresh80_reader.py --sets-root ~/gov-os-eval [--projection 15]
"""
import argparse
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import f80lib as L  # noqa: E402

PROJECTION = 15.0
WORKERS = 4
E2 = L.e2_parts()
READER_SYS, READER_SCHEMA = E2["READER_SYS"], E2["READER_SCHEMA"]
GRADER_SYS, GRADER_SCHEMA = E2["GRADER_SYS"], E2["GRADER_SCHEMA"]
CAP, prompt_of, outcome, items_of = E2["CAP"], E2["prompt_of"], E2["outcome"], E2["items_of"]


def grade(q, verdict, final, run, ledger):
    """E2's grading: the final answer (or "Not found.") by the grader and the check."""
    grades = {}
    if final is not None and verdict in ("answer", "not_found"):
        said = final.get("answer") if verdict == "answer" else "Not found."
        gp = f"Question: {q['question']}\n\nGold answer: {q['gold']}\n\nAnswer to grade: {said}"
        for name, model in (("grader", "claude-opus-5-5"), ("check", "claude-sonnet-5-5")):
            meta, g = L.claude(model, GRADER_SYS, GRADER_SCHEMA, gp, 0.5, run, ledger, f"{q['id']} {name}")
            grades[name] = {**meta, "grade": (g or {}).get("grade")}
    return grades


def one(q, first_result, run, clone, brake, ledger, refine=None):
    """E2's one(), with the 80's counts. ``refine`` (E2G only, data) turns the reader's words into the search."""
    if (run / f"{q['id']}.json").exists():
        return None  # resume: never run again
    if brake.passed():
        return None
    bundles = [items_of(first_result)]
    attempts, final, verdict, searches, consults = [], None, None, [], []
    for k in range(1, CAP + 1):
        meta, out = L.claude("claude-opus-5-5", READER_SYS, READER_SCHEMA, prompt_of(q["question"], bundles), 1.5,
                             run, ledger, f"{q['id']} reader {k}")
        attempts.append({"attempt": k, **meta, "verdict": (out or {}).get("verdict"),
                         "answer": (out or {}).get("answer"), "citations": (out or {}).get("citations")})
        if not out:
            verdict = "error"
            break
        final, verdict = out, out["verdict"]
        if verdict != "search_again" or k == CAP:
            break
        words = out.get("search") or q["question"]
        if refine is not None:
            words, c = refine(q, words, run, ledger, k)
            consults.append(c)
        result, ok, why, by = L.search(words, clone)  # a degraded answer is a failed search (code review F1)
        searches.append({"attempt": k, "ok": ok, "why": why, "rerank_by": by})
        bundles.append(items_of(result))
    if verdict == "search_again":
        verdict = "not_found"
    grades = grade(q, verdict, final, run, ledger)
    cites = [(c.get("path"), int(c.get("start_line", 0)), int(c.get("end_line", 0)))
             for c in (final or {}).get("citations") or []]
    outside = L.outside_citations(cites, bundles)
    inside = [c for c in cites if c not in outside]
    right_cite = (not q["apart"]) and any(L.hit((p, a, z, L.text_of(clone, p, a, z)), q) for p, a, z in cites)
    right_inside = (not q["apart"]) and any(L.hit((p, a, z, L.text_of(clone, p, a, z)), q) for p, a, z in inside)
    row = {"id": q["id"], "kind": "fresh", "apart": q["apart"], "final_verdict": verdict, "attempts": attempts,
           "answered_at": len(attempts) if verdict == "answer" else None,
           "gold_in_bundle": [any(L.hit(it, q) for it in b) for b in bundles],
           "citation_right": right_cite, "grades": grades,
           # the 80's additions
           "searches": searches, "search_failures": sum(1 for s in searches if not s["ok"]),
           "citations": len(cites), "citations_outside": len(outside),
           "citation_right_only_outside": right_cite and not right_inside,
           "calls_retried": sum(1 for a in attempts if a.get("retried")) +
                            sum(1 for g in grades.values() if g.get("retried")),
           "first_stopping_reason": first_result.get("stopping_reason"),
           "first_gaps_name_ids": L.gap_names_ids(first_result, q["question"]) if q["apart"] else None}
    if refine is not None:
        row["consults"] = consults
    L.write_row(run, f"{q['id']}.json", row)
    return row


def firsts(sets_root, qs):
    """Each question's first call's result, from the counting attempt."""
    att = L.counting_attempt(sets_root)
    starts = L.first_calls(att / "measure.txt")
    missing = [q["id"] for q in qs if q["id"] not in starts]
    if missing:
        raise SystemExit(f"REFUSED: {len(missing)} question(s) without a measured first call: {', '.join(missing)}")
    return {q["id"]: L.kept_doc(att / "kept", starts[q["id"]][0])["result"] for q in qs}


def rows_of(run: Path) -> dict:
    out = {}
    for f in sorted(run.glob("*.json")):
        if f.name not in ("summary.json", "plan.json"):
            r = json.loads(f.read_text())
            out[r["id"]] = r
    return out


def counts(rows: dict, planned: int, brake, ledger, t0) -> dict:
    rs = list(rows.values())
    main = [r for r in rs if not r["apart"]]
    rep = {"questions_planned": planned, "rows": len(rs), "stopped": brake.reason,
           "projection_usd": brake.projection, "brake_usd": brake.limit, "spent_usd": round(ledger.total, 2),
           "wall_min": round((time.time() - t0) / 60, 1), "errors": sum(1 for r in rs if r["final_verdict"] == "error"),
           "search_failures": sum(r["search_failures"] for r in rs),
           "search_failure_kinds": sorted({s["why"] for r in rs for s in r["searches"] if not s["ok"]}),
           "search_failure_ids": sorted(r["id"] for r in rs if r["search_failures"]),
           "citations_outside": sum(r["citations_outside"] for r in rs),
           "right_only_by_a_citation_outside": sum(1 for r in main if r["citation_right_only_outside"]),
           "calls_retried": sum(r["calls_retried"] for r in rs),
           "grader_no_grade": sum(1 for r in rs if r["grades"] and not (r["grades"].get("grader") or {}).get("grade")),
           "searches": sum(len(r["searches"]) for r in rs), "apart_rows": sum(1 for r in rs if r["apart"]),
           "main_rows": len(main)}
    return rep


def main(argv=None):  # run through L.run_tool: ACT-GUARD-SETS-1 checked first, standard error to the run folder
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--sets-root", required=True)
    ap.add_argument("--clone", default=str(L.CLONE))
    ap.add_argument("--projection", type=float, default=PROJECTION)
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args(argv)
    L.guard_root(a.sets_root)
    clone = Path(a.clone).resolve()
    p = L.paths(a.sets_root)
    qs = L.load(a.sets_root, clone)
    run = p["reader"]
    if a.dry:
        L.say(f"dry: questions {len(qs)}; apart by category {sum(q['apart'] for q in qs)}; "
              f"unresolved sources {sum(len(q['unresolved']) for q in qs)}")
        try:
            f = firsts(a.sets_root, qs)
            L.say(f"dry: first bundles loaded {len(f)}")
        except SystemExit as e:
            L.say(f"dry: first bundles not loaded ({e})")
        done = rows_of(run) if run.is_dir() else {}
        L.say(f"dry: rows already written {len(done)}; spent so far "
              f"{L.Ledger(run).total if run.is_dir() else 0:.2f} USD; projection {a.projection:.2f}, brake "
              f"{2 * a.projection:.2f}; no call made")
        return 0
    if not L.pinned():
        raise SystemExit("REFUSED: the fresh-80 files are not as reviewed and pinned (FRESH80-REVIEWED.sha256)")
    if not L.hold_on():
        raise SystemExit("REFUSED: the hold has not begun (log/act-in-progress.txt with FRESH-80 HOLD; item 13)")
    pre = json.loads(p["preflight"].read_text()) if p["preflight"].is_file() else {}
    if L.set_digest(a.sets_root) != (pre.get("item1") or {}).get("sha256"):
        raise SystemExit("REFUSED: the set's digest is not the pre-flight's (readiness-7 F6): to the owner")
    first = firsts(a.sets_root, qs)
    run.mkdir(parents=True, exist_ok=True)
    import fcntl
    lock = open(run / ".lock", "w")
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)  # one reader at a time (code review R3)
    except OSError:
        raise SystemExit("REFUSED: another reader run holds the lock")
    # the plan, in the run folder only (never printed): which ids are judged and which is apart, for the figures
    L.write_row(run, "plan.json", {"main": [q["id"] for q in qs if not q["apart"]],
                                   "apart": [q["id"] for q in qs if q["apart"]]})
    ledger = L.Ledger(run)
    brake = L.Brake(a.projection, ledger)
    before = len(rows_of(run))
    t0 = time.time()
    L.say(f"== the judged reader run: questions {len(qs)}; rows already written {before} (resumed, not run again); "
          f"spent so far {ledger.total:.2f} USD; brake {brake.limit:.2f}")
    with ThreadPoolExecutor(WORKERS) as pool:
        list(pool.map(lambda q: one(q, first[q["id"]], run, clone, brake, ledger), qs))
    rows = rows_of(run)
    rep = counts(rows, len(qs), brake, ledger, t0)
    rep["run_now"] = len(rows) - before
    L.write_row(run, "summary.json", rep)
    for k, v in rep.items():
        L.say(f"{k}: {v}")
    if brake.reason:
        L.say(f"STOPPED: {brake.reason}; the owner decides (FRESH-80-1 §3.5)")
    L.say("next: the hold ends; then fresh80_figures.py")
    return 0 if len(rows) == len(qs) else 1


if __name__ == "__main__":
    sys.exit(L.run_tool("reader", main))
