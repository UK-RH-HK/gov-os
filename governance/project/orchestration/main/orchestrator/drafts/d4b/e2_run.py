#!/usr/bin/env python3
"""E2, search-again on the 138 (D4B-SEARCH-AGAIN; E1-DECLARATION and its amendment; DEC-1091). Run with the pin's
python so the measure's own loader and matcher are used (gold re-anchored at the clone's commit, source families).
Per question: the first call's bundle from E0's kept outputs; the reader (claude-opus-5-5, high, no tools, no
transcript) answers, searches again in its own words (the pinned gov on E0's clone, first call's bundle added) or
settles; at most three attempts; A1 and A2 are A3's run cut (a request for one more search at the cut is not found).
The final answer is graded once by claude-opus-5-5 (counts) and once by claude-sonnet-5-5 (agreement). The citation is
checked by the measure's _match. The nonexistent-id questions (h24, m60) are counted apart. The runaway brake
(DEC-1091 (2)): no new question starts once the run's measured spend passes twice its projection; the stop and its
cause are written. Hidden-half rule: the questions, answers and grades stay in the run folder; stdout and summary
carry counts and ids only.
Usage: <pin python> e2_run.py <run folder> <projection usd>
"""
import json, math, re, subprocess, sys, threading, time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import yaml
from gov.retrieval import measure as M

HOME = Path.home()
SETS = HOME / "gov-os-eval"
CLONE = HOME / "gov-os-runs/D4B/w4-e0/repo"
E0 = HOME / "gov-os-runs/D4B/w4-e0/out"
KEPT = HOME / "gov-os-eval/runs/w4-e0"
GOV = str(HOME / ".local/bin/gov")
CLAUDE = str(HOME / ".local/bin/claude")
CAP, WORKERS = 3, 4
APART = {"h24", "m60"}

READER_SYS = (
    "You answer one question about a software repository, using only the search bundles you are given. Each bundle item "
    "has a path, a line range and the text of those lines. If the bundles answer the question, give the answer and cite "
    "the items (path, start_line, end_line) you rely on. If the bundles do not answer the question, give different search "
    "words in 'search' and set verdict to search_again. If you can tell your answer may be incomplete, search again for "
    "what is missing. If you judge the answer is not in the repository (an id that exists nowhere, say), answer "
    "not_found. Never answer beyond the bundles.")
READER_SCHEMA = {"type": "object", "required": ["verdict", "answer", "citations", "search"], "properties": {
    "verdict": {"type": "string", "enum": ["answer", "search_again", "not_found"]},
    "answer": {"type": "string"},
    "citations": {"type": "array", "items": {"type": "object", "required": ["path", "start_line", "end_line"], "properties": {
        "path": {"type": "string"}, "start_line": {"type": "integer"}, "end_line": {"type": "integer"}}}},
    "search": {"type": "string"}}}
GRADER_SYS = (
    "You grade one answer to a question about a software repository against the gold answer. Return correct when the "
    "answer states the gold answer's facts and contradicts none of them; wrong when it contradicts them or misses their "
    "substance; not_found when it says the answer could not be found. For a question about an id that exists nowhere, "
    "correct means the answer says it was not found or does not exist.")
GRADER_SCHEMA = {"type": "object", "required": ["grade", "reason"], "properties": {
    "grade": {"type": "string", "enum": ["correct", "wrong", "not_found"]}, "reason": {"type": "string"}}}

lock, spent, stop_reason = threading.Lock(), [0.0], [None]


def claude(model, system, schema, prompt, budget, cwd):
    t = time.monotonic()
    p = subprocess.run([CLAUDE, "-p", "--safe-mode", "--tools", "", "--no-session-persistence", "--output-format", "json",
                        "--model", model, "--effort", "high", "--max-budget-usd", str(budget), "--system-prompt", system,
                        "--json-schema", json.dumps(schema)], input=prompt, capture_output=True, text=True, cwd=cwd)
    wall = round(time.monotonic() - t, 1)
    try:
        d = json.loads(p.stdout)
    except ValueError:
        return {"error": "unparsed output", "wall_s": wall}, None
    out = d.get("structured_output")
    if out is None:
        try:
            out = json.loads(d.get("result") or "")
        except ValueError:
            out = None
    u = d.get("usage") or {}
    cost = d.get("total_cost_usd") or 0
    with lock:
        spent[0] += cost
    return {"wall_s": wall, "cost_usd": cost, "is_error": d.get("is_error"),
            "tokens": {k: u.get(k) for k in ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens", "output_tokens")}}, out


def first_calls(measure_txt):
    starts, n = {}, 1
    for line in Path(measure_txt).read_text().splitlines():
        m = re.match(r"(\S+) \((\w+)\):.*?; (\d+) calls?(?:;|$)", line)
        if m:
            starts[m[1]] = n
            n += int(m[3])
    return starts


def items_of(result):
    return [(e.get("path"), int(e.get("start_line")), int(e.get("end_line")), str(e.get("text", "")))
            for e in (result.get("evidence") or [])]


def search(words):
    env = {k: v for k, v in __import__("os").environ.items() if k not in ("GOV_STORE", "GOV_TICKET", "PYTHONPATH")}
    p = subprocess.run([GOV, "retrieve", words, "--json"], capture_output=True, text=True, cwd=CLONE, env=env)
    try:
        return items_of(json.loads(p.stdout)["result"])
    except (ValueError, KeyError, TypeError):
        return []


def text_of(path, a, b):
    f = CLONE / path
    try:
        lines = f.read_text(errors="replace").splitlines(keepends=True)
    except OSError:
        return ""
    return "".join(lines[max(0, a - 1):b])


def hit(item, q):
    return any(M._match(item, e) for e in q["sources"])


def load():
    out = []
    for set_, part, kept in (("memory-retrieval", "visible", "r80"), ("memory-retrieval", "hidden", "r80"), ("memory-verdict", "hidden", "r60")):
        entry = M.evaluation_sets(str(SETS)).get(set_)
        quoting = M._Part("/q", [*entry.get("visible", []), *entry["hidden"], f"{M.EVALUATION}/**"], "")
        declared = M.families(SETS, CLONE)
        starts = first_calls(E0 / kept / "measure.txt")
        for f in sorted((SETS / M.EVALUATION / set_ / part).glob("*.yaml")):
            q = M._load(f, part, CLONE, quoting, declared, {})
            raw = yaml.safe_load(f.read_text())
            q.update(gold=raw.get("gold_answer"), kind="spent" if set_ == "memory-verdict" else part,
                     apart=q["id"] in APART, first=KEPT / kept / f"{starts[q['id']]:05d}.json")
            out.append(q)
    return out


def prompt_of(question, bundles):
    parts = [f"Question: {question}"]
    for k, b in enumerate(bundles, 1):
        parts.append(f"\n=== Bundle {k} ===")
        for path, a, z, text in b:
            parts.append(f"--- {path} lines {a}-{z}\n{text}")
    return "\n".join(parts)


def one(q, run, brake):
    if spent[0] > brake:
        if not stop_reason[0]:
            stop_reason[0] = f"the runaway brake: spend {spent[0]:.2f} USD passed {brake:.2f} (twice the projection)"
        return None
    bundles = [items_of(json.loads(Path(q["first"]).read_text())["result"])]
    attempts, final, verdict = [], None, None
    for k in range(1, CAP + 1):
        meta, out = claude("claude-opus-5-5", READER_SYS, READER_SCHEMA, prompt_of(q["question"], bundles), 1.5, run)
        attempts.append({"attempt": k, **meta, "verdict": (out or {}).get("verdict"),
                         "answer": (out or {}).get("answer"), "citations": (out or {}).get("citations")})
        if not out:
            verdict = "error"; break
        final, verdict = out, out["verdict"]
        if verdict != "search_again" or k == CAP:
            break
        bundles.append(search(out.get("search") or q["question"]))
    if verdict == "search_again":
        verdict = "not_found"
    grades = {}
    if final is not None and verdict in ("answer", "not_found"):
        said = final.get("answer") if verdict == "answer" else "Not found."
        gp = f"Question: {q['question']}\n\nGold answer: {q['gold']}\n\nAnswer to grade: {said}"
        for name, model in (("grader", "claude-opus-5-5"), ("check", "claude-sonnet-5-5")):
            meta, g = claude(model, GRADER_SYS, GRADER_SCHEMA, gp, 0.5, run)
            grades[name] = {**meta, "grade": (g or {}).get("grade")}
    cites = [(c.get("path"), int(c.get("start_line", 0)), int(c.get("end_line", 0))) for c in (final or {}).get("citations") or []]
    row = {"id": q["id"], "kind": q["kind"], "apart": q["apart"], "final_verdict": verdict, "attempts": attempts,
           "answered_at": len(attempts) if verdict == "answer" else None,
           "gold_in_bundle": [any(hit(it, q) for it in b) for b in bundles],
           "citation_right": (not q["apart"]) and any(hit((p, a, z, text_of(p, a, z)), q) for p, a, z in cites),
           "grades": grades}
    (Path(run) / f"{q['id']}.json").write_text(json.dumps(row, indent=1))
    return row


def mcnemar(a, b):
    g = sum(1 for x, y in zip(a, b) if y and not x); l = sum(1 for x, y in zip(a, b) if x and not y)
    n, k = g + l, min(g, l)
    return g, l, (min(1.0, 2 * sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n) if n else 1.0)


def outcome(r, cut):
    """Under condition A<cut>: right end to end, correct, wrong claim, not found."""
    grade = (r["grades"].get("grader") or {}).get("grade")
    answered = r["answered_at"] is not None and r["answered_at"] <= cut
    settled = r["final_verdict"] == "not_found" and len(r["attempts"]) <= cut
    if r["apart"]:
        nf = not answered  # cut before answering, or settled
        right = nf or (answered and grade == "correct")
        return {"right": right, "correct": right, "wrong": answered and grade != "correct", "nf": nf}
    if answered:
        return {"right": grade == "correct" and r["citation_right"], "correct": grade == "correct",
                "wrong": grade != "correct", "nf": False}
    return {"right": False, "correct": False, "wrong": False, "nf": True}  # cut before answering, or settled


def main():
    run = Path(sys.argv[1])
    qs = load()
    if sys.argv[2] == "dry":  # counts only: what would run, and whether every first bundle and gold loads
        firsts = [items_of(json.loads(Path(q["first"]).read_text())["result"]) for q in qs]
        print(json.dumps({"questions": len(qs), "by kind": {k: sum(1 for q in qs if q["kind"] == k) for k in ("visible", "hidden", "spent")},
                          "apart": sorted(q["id"] for q in qs if q["apart"]), "unresolved gold": sum(1 for q in qs if q["unresolved"]),
                          "first bundle holds gold": sum(1 for q, b in zip(qs, firsts) if not q["apart"] and any(hit(it, q) for it in b))}))
        return
    projection = float(sys.argv[2])
    run.mkdir(parents=True, exist_ok=True)
    brake = 2 * projection
    t0 = time.time()
    with ThreadPoolExecutor(WORKERS) as pool:
        rows = [r for r in pool.map(lambda q: one(q, run, brake), qs) if r]
    report = {"questions_planned": len(qs), "questions_run": len(rows), "stopped": stop_reason[0],
              "projection_usd": projection, "brake_usd": brake, "spent_usd": round(spent[0], 2), "wall_min": round((time.time() - t0) / 60, 1)}
    main_rows = [r for r in rows if not r["apart"]]
    for cut in (1, 2, 3):
        for kind in ("visible", "hidden", "spent", "the 138"):
            rs = [r for r in main_rows if kind == "the 138" or r["kind"] == kind]
            o = [outcome(r, cut) for r in rs]
            report[f"A{cut} {kind}"] = {"n": len(rs), "right": sum(x["right"] for x in o), "correct": sum(x["correct"] for x in o),
                                        "wrong_claims": sum(x["wrong"] for x in o), "not_found": sum(x["nf"] for x in o)}
        ap = [outcome(r, cut) for r in rows if r["apart"]]
        report[f"A{cut} nonexistent-id"] = {"n": len(ap), "right": sum(x["right"] for x in ap), "wrong_claims": sum(x["wrong"] for x in ap)}
    rt = {c: [outcome(r, c)["right"] for r in main_rows] for c in (1, 2, 3)}
    report["mcnemar A1 vs A2 (gains, losses, p)"] = mcnemar(rt[1], rt[2])
    report["mcnemar A2 vs A3 (gains, losses, p)"] = mcnemar(rt[2], rt[3])
    missed = [r for r in main_rows if not r["gold_in_bundle"][0]]
    report["retrieval misses (first bundle lacks gold)"] = len(missed)
    report["recovered at the retrieval level (a later bundle holds it)"] = sum(any(r["gold_in_bundle"][1:]) for r in missed)
    report["recovered at the answer level (A1 not right, A3 right)"] = sum(1 for a, b in zip(rt[1], rt[3]) if b and not a)
    report["recovered ids"] = sorted(r["id"] for r, a, b in zip(main_rows, rt[1], rt[3]) if b and not a)
    report["grader agreement"] = f"{sum(1 for r in rows if r['grades'] and r['grades']['grader'].get('grade') == r['grades']['check'].get('grade'))} of {sum(1 for r in rows if r['grades'])}"
    calls = [a for r in rows for a in r["attempts"]]
    walls = sorted(a["wall_s"] for a in calls)
    report["reader calls"] = len(calls)
    report["searches"] = sum(len(r["gold_in_bundle"]) - 1 for r in rows)
    report["reader wall s median, p90"] = (walls[len(walls) // 2], walls[int(0.9 * (len(walls) - 1))]) if walls else None
    tok = {}
    for r in rows:
        for c in r["attempts"] + list(r["grades"].values()):
            for k, v in (c.get("tokens") or {}).items():
                tok[k] = tok.get(k, 0) + (v or 0)
    report["tokens"] = tok
    report["errors"] = sum(1 for r in rows if r["final_verdict"] == "error")
    (run / "summary.json").write_text(json.dumps(report, indent=1))
    print(json.dumps(report, indent=1))


main()
