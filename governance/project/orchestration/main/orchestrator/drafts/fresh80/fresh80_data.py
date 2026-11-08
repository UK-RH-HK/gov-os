#!/usr/bin/env python3
"""The fresh 80's data conditions: DATA ONLY, NOT JUDGED (DEC-1097 (1)(c); FRESH-80-1 §3.1, §3.3, §3.4).

Every experiment of the 138 runs on the 80 for data, after the judged reader run and after the hold ends, so that no
fault of theirs can touch the judged figure. Each has its own projection (the 138's measured cost per question, times
80) and its own brake at twice it (DEC-1091 (2)), its own run folder (<sets root>/runs/fresh-80/data/<condition>,
derived here), a resume (a job with a row file is never run again), a call that returned nothing run once more, and
--dry (load, count, no call). Nothing here chooses anything; a data figure that beats the judged one is a finding
only (§3.4 item 4).

  e3    E3's other bundles, one reader call each: top 5, top 10, top 20 (the first call's ranked chunks with their own
        spans) and 40 unranked (calls 1 and 2's chunks, shuffled by the question's id); E3's reader and graders.
        Projection 36 USD (E3: 61.93 for 140), brake 72.
  e3sa  E3-SA: top 20 and 40 unranked with search again (up to three attempts; later searches live, in the
        condition's own form). Projection 19 (E3-SA: 31.70 for 280 runs), brake 38.
  e5    E5: one reader call on the 12,000-token bundle (a page of 40), from f80_e5_live.sh's second live retrieval.
        Projection 17 (E5: 29.50 for 140), brake 34.
  e4    E4: one reader call on today's bundle as M3 (zerank + gte) and as M1 (the 0.6B + gte) build it, from
        f80_e4_replays.sh. Projection 22 (E4: 37.33 for 280 runs), brake 44.
  e2g   E2G: E2's condition with the prototype glossary consulted at each search again (e2g_run.py's step).
        Projection 14 (E2G: 24.32 for 140), brake 28.
The one-call conditions are compared with the judged run's A1 (the same prompt as E3's one call); e3sa and e2g with
its A2 (exact McNemar). Counts and ids only.

    <pin python> fresh80_data.py <e3|e3sa|e5|e4|e2g> --sets-root ~/gov-os-eval [--dry] [--projection <usd>]
"""
import argparse
import json
import random
import sqlite3
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import f80lib as L  # noqa: E402
import fresh80_reader as RD  # noqa: E402

PROJECTIONS = {"e3": 36.0, "e3sa": 19.0, "e5": 17.0, "e4": 22.0, "e2g": 14.0}
WORKERS = 4
E3 = L.e3_parts()
E3_CONDS = ("top5", "top10", "top20", "unranked40")
SA_CONDS, SA_CAP = ("top20", "unranked40"), 3
CELLS = ("m3", "m1")
GLOSSARY = L.HOME / "gov-os-runs/D4B/glossary"
_db_lock = threading.Lock()


class Store:
    """The clone's store, read only, for a ranked item's own chunk span (e3_run.py's own())."""

    def __init__(self, clone: Path):
        self.clone = clone
        self.db = sqlite3.connect(f"file:{clone}/.gov-runtime/store.db?mode=ro", uri=True, check_same_thread=False)

    def own(self, e):
        with _db_lock:
            row = self.db.execute("select path, start_line, end_line from lexical_chunk where chunk_id = ?",
                                  (e.get("chunk_id"),)).fetchone()
        path, a, b = row if row else (e["path"], int(e["start_line"]), int(e["end_line"]))
        return (path, int(a), int(b), L.text_of(self.clone, path, int(a), int(b)))


def sent(e):
    return (e.get("path"), int(e.get("start_line")), int(e.get("end_line")), str(e.get("text", "")))


def unique_shuffled(items, seed, cap=40):
    seen, uniq = set(), []
    for it in items:
        if it[:3] not in seen:
            seen.add(it[:3])
            uniq.append(it)
    random.Random(seed).shuffle(uniq)
    return uniq[:cap]


def e3_bundles(q, kept: Path, start: tuple, store: Store) -> dict:
    """E3's four other bundles. The second call is taken only when the question made one (e3_run.py took the next
    file whatever it was; for a one-call question that is the next question's first call: fixed here)."""
    n, calls = start
    c1 = L.kept_doc(kept, n)["result"].get("evidence") or []
    c2 = (L.kept_doc(kept, n + 1).get("result") or {}).get("evidence") or [] if calls >= 2 else []
    ranked = [store.own(e) for e in c1]
    return {"top5": ranked[:5], "top10": ranked[:10], "top20": ranked[:20],
            "unranked40": unique_shuffled(ranked + [store.own(e) for e in c2], q["id"])}


def one_call(q, cond, items, run, clone, brake, ledger):
    """e3_run.py's one(), with resume, the call run once more, the ledger; a row per (question, condition)."""
    name = f"{q['id']}.{cond}.json"
    if (run / name).exists() or brake.passed():
        return None
    sys_ = E3["READER_SYS"] + (E3["UNRANKED_NOTE"] if cond == "unranked40" else "")
    meta, out = L.claude("claude-opus-5-5", sys_, RD.READER_SCHEMA, E3["prompt_of"](q["question"], items), 1.5, run,
                         ledger, f"{q['id']} {cond} reader")
    verdict = (out or {}).get("verdict") or "error"
    if verdict == "search_again":
        verdict = "not_found"
    grades = RD.grade(q, verdict, out, run, ledger) if out else {}
    cites = [(c.get("path"), int(c.get("start_line", 0)), int(c.get("end_line", 0)))
             for c in (out or {}).get("citations") or []]
    row = {"id": q["id"], "apart": q["apart"], "condition": cond, "verdict": verdict, "reader": meta,
           "grades": grades, "bundle_chars": sum(len(t) for *_, t in items), "items": len(items),
           "gold_in_bundle": any(L.hit(it, q) for it in items),
           "citation_right": (not q["apart"]) and any(L.hit((p, a, z, L.text_of(clone, p, a, z)), q)
                                                      for p, a, z in cites),
           "citations_outside": len(L.outside_citations(cites, [items]))}
    L.write_row(run, name, row)
    return row


def sa_one(q, cond, first, run, clone, brake, ledger, store):
    """e3sa_run.py's one(): later searches live, in the condition's own form, failures counted."""
    name = f"{q['id']}.{cond}.json"
    if (run / name).exists() or brake.passed():
        return None
    sys_ = E3["READER_SYS"] + (E3["UNRANKED_NOTE"] if cond == "unranked40" else "")
    bundles, attempts, final, verdict, fails = [first], [], None, None, 0
    for k in range(1, SA_CAP + 1):
        prompt = "\n".join([f"Question: {q['question']}"] + [
            f"\n=== Bundle {n} ===\n" + "\n".join(f"--- {p} lines {a}-{z}\n{t}" for p, a, z, t in b)
            for n, b in enumerate(bundles, 1)])
        meta, out = L.claude("claude-opus-5-5", sys_, RD.READER_SCHEMA, prompt, 1.5, run, ledger,
                             f"{q['id']} {cond} reader {k}")
        attempts.append({"attempt": k, **meta, "verdict": (out or {}).get("verdict")})
        if not out:
            verdict = "error"
            break
        final, verdict = out, out["verdict"]
        if verdict != "search_again" or k == SA_CAP:
            break
        words = out.get("search") or q["question"]
        r1, ok1, _, _ = L.search(words, clone)
        fails += not ok1
        ranked = [store.own(e) for e in r1.get("evidence", [])]
        if cond == "top20":
            bundles.append(ranked[:20])
            continue
        tok = r1.get("continuation")
        r2, ok2 = ({}, True)
        if tok:
            r2, ok2, _, _ = L.search(words, clone, ("--continue", tok))
            fails += not ok2
        bundles.append(unique_shuffled(ranked + [store.own(e) for e in r2.get("evidence", [])], f"{q['id']}-{k}"))
    if verdict == "search_again":
        verdict = "not_found"
    grades = RD.grade(q, verdict, final, run, ledger)
    cites = [(c.get("path"), int(c.get("start_line", 0)), int(c.get("end_line", 0)))
             for c in (final or {}).get("citations") or []]
    row = {"id": q["id"], "kind": "fresh", "apart": q["apart"], "condition": cond, "final_verdict": verdict,
           "answered_at": len(attempts) if verdict == "answer" else None, "attempts": attempts, "grades": grades,
           "gold_in_bundle": [any(L.hit(it, q) for it in b) for b in bundles], "search_failures": fails,
           "citation_right": (not q["apart"]) and any(L.hit((p, a, z, L.text_of(clone, p, a, z)), q)
                                                      for p, a, z in cites),
           "citations_outside": len(L.outside_citations(cites, bundles))}
    L.write_row(run, name, row)
    return row


def glossary_refine():
    """e2g_run.py's step: the prototype's top 30 for the question and the reader's words, one short call."""
    sys.path.insert(0, str(GLOSSARY))
    from lookup import lookup  # the prototype (DEC-1096 (4))
    g = L.e2g_parts()

    def refine(q, own_words, run, ledger, k):
        hits = lookup(str(GLOSSARY / "out"), f"{q['question']} {own_words}", 30)
        rp = (f"Question: {q['question']}\n\nYour search words were: {own_words}\n\n"
              "The repository's own terms, ids and code names that match:\n" + "\n".join(hits))
        meta, out = L.claude("claude-opus-5-5", g["REFINE_SYS"], g["REFINE_SCHEMA"], rp, 0.5, run, ledger,
                             f"{q['id']} refine {k}")
        words = ((out or {}).get("search") or own_words).strip()
        return words, {"attempt": k, **meta, "hits": len(hits), "changed": words != own_words.strip()}
    return refine


# ---- the judged run's rows, to compare with (read only)

def judged(p) -> dict:
    return RD.rows_of(p["reader"]) if p["reader"].is_dir() else {}


def right_e3(r):
    return E3["right"](r)


def summary_lines(cond, rows, qs, base, brake, ledger, t0) -> dict:
    main = [q["id"] for q in qs if not q["apart"]]
    apart = [q["id"] for q in qs if q["apart"]]
    lines, rep = [], {"condition": cond, "label": "data only, not judged", "projection_usd": brake.projection,
                      "brake_usd": brake.limit, "spent_usd": round(ledger.total, 2), "stopped": brake.reason,
                      "wall_min": round((time.time() - t0) / 60, 1)}
    if cond in ("e3sa", "e2g"):
        conds = SA_CONDS if cond == "e3sa" else ("e2g",)
        for c in conds:
            by = {r["id"]: r for r in rows if r.get("condition", "e2g") == c}
            ids = [i for i in main if i in by and i in base]
            right = {k: sum(RD.outcome(by[i], k)["right"] for i in ids) for k in (1, 2, 3)}
            wrong2 = sum(RD.outcome(by[i], 2)["wrong"] for i in ids)
            g, l, pv = RD.E2["mcnemar"]([RD.outcome(base[i], 2)["right"] for i in ids],
                                        [RD.outcome(by[i], 2)["right"] for i in ids])
            fails = sum(by[i].get("search_failures", 0) for i in by)
            lines.append(f"{c}: right A1 {right[1]}, A2 {right[2]}, A3 {right[3]} of {len(ids)}; wrong claims A2 "
                         f"{wrong2}; against the judged A2: {g} gains, {l} losses, p {pv:.4f}; failed searches {fails}; "
                         f"nonexistent-id right {sum(RD.outcome(by[i], 2)['right'] for i in apart if i in by)}")
            rep[c] = {"n": len(ids), "A1": right[1], "A2": right[2], "A3": right[3], "wrong_A2": wrong2,
                      "vs_judged_A2": (g, l, pv), "search_failures": fails}
    else:
        conds = {"e3": E3_CONDS, "e5": ("bundle12000",), "e4": CELLS}[cond]
        for c in conds:
            by = {r["id"]: r for r in rows if r["condition"] == c}
            ids = [i for i in main if i in by and i in base]
            right = sum(right_e3(by[i]) for i in ids)
            wrong = sum(1 for i in ids if by[i]["verdict"] == "answer" and
                        (by[i]["grades"].get("grader") or {}).get("grade") != "correct")
            g, l, pv = RD.E2["mcnemar"]([RD.outcome(base[i], 1)["right"] for i in ids], [right_e3(by[i]) for i in ids])
            gib = sum(by[i]["gold_in_bundle"] for i in ids)
            lines.append(f"{c}: right {right} of {len(ids)}; wrong claims {wrong}; gold in the bundle {gib}; against "
                         f"the judged A1: {g} gains, {l} losses, p {pv:.4f}; nonexistent-id right "
                         f"{sum(right_e3(by[i]) for i in apart if i in by)}")
            rep[c] = {"n": len(ids), "right": right, "wrong": wrong, "gold_in_bundle": gib, "vs_judged_A1": (g, l, pv)}
    errors = sum(1 for r in rows if (r.get("verdict") or r.get("final_verdict")) == "error")
    lines.append(f"spent {rep['spent_usd']} USD (projection {brake.projection}, brake {brake.limit}); stopped: "
                 f"{brake.reason or 'no'}; errors {errors}; rows {len(rows)}")
    rep["lines"] = lines
    return rep


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("condition", choices=tuple(PROJECTIONS))
    ap.add_argument("--sets-root", required=True)
    ap.add_argument("--clone", default=str(L.CLONE))
    ap.add_argument("--projection", type=float)
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args(argv)
    L.guard_root(a.sets_root)
    cond, clone, p = a.condition, Path(a.clone).resolve(), L.paths(a.sets_root)
    projection = a.projection if a.projection is not None else PROJECTIONS[cond]
    run = p["data"] / cond
    qs = L.load(a.sets_root, clone)
    base = judged(p)
    # the inputs each condition reads
    if cond == "e5":
        src = [(p["data"] / "e5" / "live", "bundle12000")]
    elif cond == "e4":
        src = [(p["data"] / "e4" / "replays" / c, c) for c in CELLS]
    else:
        src = [(L.counting_attempt(a.sets_root), None)]
    inputs_ok = all((d / "measure.txt").is_file() and (d / "kept").is_dir() for d, _ in src)
    if a.dry:
        jobs = len(qs) * {"e3": 4, "e3sa": 2, "e5": 1, "e4": 2, "e2g": 1}[cond]
        done = len([f for f in run.glob("*.json") if f.name != "summary.json"]) if run.is_dir() else 0
        L.say(f"dry {cond} (data only, not judged): questions {len(qs)}; jobs {jobs}; rows already {done}; inputs "
              f"present {'yes' if inputs_ok else 'no'}; judged rows {len(base)}; spent so far "
              f"{L.Ledger(run).total if run.is_dir() else 0:.2f} USD; projection {projection:.2f}, brake "
              f"{2 * projection:.2f}; no call made")
        return 0
    if not L.pinned():
        raise SystemExit("REFUSED: the fresh-80 files are not as reviewed and pinned (FRESH80-REVIEWED.sha256)")
    if L.hold_on():
        raise SystemExit("REFUSED: the hold is on: a data condition runs only after the hold ends (§3.2 step 10)")
    if len(base) != len(qs):
        raise SystemExit("REFUSED: the judged reader run is not finished: data conditions run after it")
    if not inputs_ok:
        raise SystemExit(f"REFUSED: {cond}'s inputs are not there (its live part or replays have not run)")
    run.mkdir(parents=True, exist_ok=True)
    ledger = L.Ledger(run)
    brake = L.Brake(projection, ledger)
    t0 = time.time()
    L.say(f"== {cond}: data only, not judged; projection {projection:.2f}, brake {brake.limit:.2f}; spent so far "
          f"{ledger.total:.2f}")
    store = Store(clone) if cond in ("e3", "e3sa") else None
    jobs = []
    refine = glossary_refine() if cond == "e2g" else None
    for d, label in src:
        starts = L.first_calls(d / "measure.txt")
        for q in qs:
            st = starts[q["id"]]
            if cond == "e3":
                for c, items in e3_bundles(q, d / "kept", st, store).items():
                    jobs.append(lambda q=q, c=c, items=items: one_call(q, c, items, run, clone, brake, ledger))
            elif cond == "e3sa":
                b = e3_bundles(q, d / "kept", st, store)
                for c in SA_CONDS:
                    jobs.append(lambda q=q, c=c, b=b: sa_one(q, c, b[c], run, clone, brake, ledger, store))
            elif cond in ("e5", "e4"):
                items = [sent(e) for e in L.kept_doc(d / "kept", st[0])["result"].get("evidence") or []]
                jobs.append(lambda q=q, label=label, items=items: one_call(q, label, items, run, clone, brake, ledger))
            else:  # e2g: the judged run's first bundles, the glossary at each search again
                first = L.kept_doc(d / "kept", st[0])["result"]
                jobs.append(lambda q=q, first=first, refine=refine: RD.one(q, first, run, clone, brake, ledger, refine))
    with ThreadPoolExecutor(WORKERS) as pool:
        list(pool.map(lambda j: j(), jobs))
    rows = [json.loads(f.read_text()) for f in sorted(run.glob("*.json")) if f.name not in ("summary.json",)]
    if cond == "e2g":
        for r in rows:
            r["condition"] = "e2g"
    rep = summary_lines(cond, rows, qs, base, brake, ledger, t0)
    L.write_row(run, "summary.json", rep)
    for line in rep["lines"]:
        L.say(f"{cond}: {line}")
    return 0


if __name__ == "__main__":
    sys.exit(L.run_tool("data", main))
