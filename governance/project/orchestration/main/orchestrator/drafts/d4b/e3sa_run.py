#!/usr/bin/env python3
"""E3's search-again on the tied second place (E3-RESULT): top20 and unranked40, up to three attempts, E2's reader and
graders. The first bundle is the condition's (as in e3_run); each later search runs live with the pinned gov on E0's
clone and is built in the condition's own form (top20: the new search's ranked chunks 1-20 with their own spans;
unranked40: the unique chunks of its calls 1 and 2, own spans, shuffled with the question's id and the attempt as the
seed). A1 and A2 are A3's run cut, as in E2. Today's bundle with search-again is E2 itself (compared from its run
folder). Counts and ids only. The runaway brake at twice the projection. Run with the pin's python.
Usage: <pin python> e3sa_run.py <run folder> <projection usd>"""
import importlib.util, json, math, os, random, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

spec = importlib.util.spec_from_file_location("e3", Path(__file__).with_name("e3_run.py"))
src = Path(__file__).with_name("e3_run.py").read_text().replace("\nmain()\n", "\n")
E3 = type(sys)("e3"); exec(compile(src, "e3_run.py", "exec"), E3.__dict__)

GOV = str(Path.home() / ".local/bin/gov")
E2 = Path.home() / "gov-os-runs/D4B/search-again/e2"
CAP, CONDS = 3, ("top20", "unranked40")


def live(words, cond, seed):
    env = {k: v for k, v in os.environ.items() if k not in ("GOV_STORE", "GOV_TICKET", "PYTHONPATH")}
    def call(extra=()):
        p = subprocess.run([GOV, "retrieve", words, "--json", *extra], capture_output=True, text=True, cwd=E3.CLONE, env=env)
        try:
            return json.loads(p.stdout)["result"]
        except (ValueError, KeyError, TypeError):
            return {}
    r1 = call()
    ranked = [E3.own(e) for e in r1.get("evidence", [])]
    if cond == "top20":
        return ranked[:20]
    tok = r1.get("continuation")
    r2 = call(("--continue", tok)) if tok else {}
    seen, uniq = set(), []
    for it in ranked + [E3.own(e) for e in r2.get("evidence", [])]:
        if it[:3] not in seen:
            seen.add(it[:3]); uniq.append(it)
    random.Random(seed).shuffle(uniq)
    return uniq[:40]


def one(q, cond, run, brake):
    if E3.spent[0] > brake:
        E3.stop_reason[0] = E3.stop_reason[0] or f"the runaway brake: spend {E3.spent[0]:.2f} USD passed {brake:.2f}"
        return None
    sys_ = E3.READER_SYS + (E3.UNRANKED_NOTE if cond == "unranked40" else "")
    bundles = [E3.bundles_of(q)[cond]]
    attempts, final, verdict = [], None, None
    for k in range(1, CAP + 1):
        prompt = "\n".join([f"Question: {q['question']}"] + [f"\n=== Bundle {n} ===\n" + "\n".join(f"--- {p} lines {a}-{z}\n{t}" for p, a, z, t in b) for n, b in enumerate(bundles, 1)])
        meta, out = E3.claude("claude-opus-5-5", sys_, E3.READER_SCHEMA, prompt, 1.5, run)
        attempts.append({"attempt": k, **meta, "verdict": (out or {}).get("verdict")})
        if not out:
            verdict = "error"; break
        final, verdict = out, out["verdict"]
        if verdict != "search_again" or k == CAP:
            break
        bundles.append(live(out.get("search") or q["question"], cond, f"{q['id']}-{k}"))
    if verdict == "search_again":
        verdict = "not_found"
    grades = {}
    if final is not None and verdict in ("answer", "not_found"):
        said = final.get("answer") if verdict == "answer" else "Not found."
        gp = f"Question: {q['question']}\n\nGold answer: {q['gold']}\n\nAnswer to grade: {said}"
        for name, model in (("grader", "claude-opus-5-5"), ("check", "claude-sonnet-5-5")):
            gm, g = E3.claude(model, E3.GRADER_SYS, E3.GRADER_SCHEMA, gp, 0.5, run)
            grades[name] = {**gm, "grade": (g or {}).get("grade")}
    cites = [(c.get("path"), int(c.get("start_line", 0)), int(c.get("end_line", 0))) for c in (final or {}).get("citations") or []]
    row = {"id": q["id"], "kind": q["kind"], "apart": q["apart"], "condition": cond, "final_verdict": verdict,
           "answered_at": len(attempts) if verdict == "answer" else None, "attempts": attempts, "grades": grades,
           "gold_in_bundle": [any(E3.hit(it, q) for it in b) for b in bundles],
           "citation_right": (not q["apart"]) and any(E3.hit((p, a, z, E3.text_of(p, a, z)), q) for p, a, z in cites)}
    (Path(run) / f"{q['id']}.{cond}.json").write_text(json.dumps(row, indent=1))
    return row


def outcome(r, cut):
    grade = (r["grades"].get("grader") or {}).get("grade")
    answered = r["answered_at"] is not None and r["answered_at"] <= cut
    if r["apart"]:
        return (not answered) or grade == "correct"
    return answered and grade == "correct" and r["citation_right"]


def mcnemar(a, b):
    g = sum(1 for x, y in zip(a, b) if y and not x); l = sum(1 for x, y in zip(a, b) if x and not y)
    n, k = g + l, min(g, l)
    return g, l, (min(1.0, 2 * sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n) if n else 1.0)


def main():
    run, projection = Path(sys.argv[1]), float(sys.argv[2]); brake = 2 * projection; run.mkdir(parents=True, exist_ok=True)
    qs = E3.load(); t0 = time.time()
    with ThreadPoolExecutor(E3.WORKERS) as pool:
        rows = [r for r in pool.map(lambda j: one(*j, run, brake), [(q, c) for q in qs for c in CONDS]) if r]
    rep = {"jobs": len(rows), "stopped": E3.stop_reason[0], "projection_usd": projection, "brake_usd": brake,
           "spent_usd": round(E3.spent[0], 2), "wall_min": round((time.time() - t0) / 60, 1),
           "errors": sum(1 for r in rows if r["final_verdict"] == "error")}
    e2 = {}
    for f in E2.glob("*.json"):
        if f.name != "summary.json":
            r = json.loads(f.read_text()); e2[r["id"]] = r
    for c in CONDS:
        by = {r["id"]: r for r in rows if r["condition"] == c}
        ids = [q["id"] for q in qs if not q["apart"] and q["id"] in by and q["id"] in e2]
        for cut in (1, 2, 3):
            for kind in ("visible", "hidden", "spent", "the 138"):
                rs = [by[i] for i in ids if kind == "the 138" or by[i]["kind"] == kind]
                rep[f"{c} A{cut} {kind}"] = sum(outcome(r, cut) for r in rs)
            rep[f"{c} A{cut} wrong claims"] = sum(1 for i in ids if by[i]["answered_at"] and by[i]["answered_at"] <= cut
                                                 and (by[i]["grades"].get("grader") or {}).get("grade") != "correct")
        a1 = [outcome(by[i], 1) for i in ids]; a2 = [outcome(by[i], 2) for i in ids]
        rep[f"{c} mcnemar A1 vs A2 (gains, losses, p)"] = mcnemar(a1, a2)
        b2 = [E2_outcome(e2[i], 2) for i in ids]
        rep[f"{c} A2 vs today's bundle A2 (E2) (gains, losses, p)"] = mcnemar(b2, a2)
        rep[f"{c} searches"] = sum(len(by[i]["gold_in_bundle"]) - 1 for i in ids)
    (run / "summary.json").write_text(json.dumps(rep, indent=1))
    print(json.dumps(rep, indent=1))


def E2_outcome(r, cut):
    grade = (r["grades"].get("grader") or {}).get("grade")
    answered = r["answered_at"] is not None and r["answered_at"] <= cut
    return answered and grade == "correct" and r["citation_right"]


main()
