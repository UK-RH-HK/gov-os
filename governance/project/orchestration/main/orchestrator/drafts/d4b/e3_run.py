#!/usr/bin/env python3
"""E3's five conditions (E3-E5-DESIGN §1, approved by DEC-1092): per question one reader call on each bundle:
  top5, top10, top20  the first call's ranked chunks 1-k with their own spans (lexical_chunk), text from E0's clone;
  bundle             the first call's bundle exactly as sent (E0's kept output: items, cuts, expansions);
  unranked40         calls 1 and 2's chunks (the pool's 40) with their own spans, shuffled with a seed per question.
No search-again here (the best two get it next). The reader and grader are E2's (the "may be incomplete" line kept;
a search_again verdict counts as not found). Citation by the measure's _match; nonexistent-id questions apart; the
runaway brake at twice the projection (DEC-1091 (2)). Counts and ids only on stdout. Run with the pin's python.
Usage: <pin python> e3_run.py <run folder> <projection usd> | <run folder> dry
"""
import json, math, random, re, sqlite3, subprocess, sys, threading, time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import yaml
from gov.retrieval import measure as M

HOME = Path.home()
SETS, CLONE = HOME / "gov-os-eval", HOME / "gov-os-runs/D4B/w4-e0/repo"
E0, KEPT = HOME / "gov-os-runs/D4B/w4-e0/out", HOME / "gov-os-eval/runs/w4-e0"
CLAUDE = str(HOME / ".local/bin/claude")
APART, WORKERS = {"h24", "m60"}, 4
CONDITIONS = ("top5", "top10", "top20", "bundle", "unranked40")
READER_SYS = (
    "You answer one question about a software repository, using only the search bundles you are given. Each bundle item "
    "has a path, a line range and the text of those lines. If the bundles answer the question, give the answer and cite "
    "the items (path, start_line, end_line) you rely on. If the bundles do not answer the question, give different search "
    "words in 'search' and set verdict to search_again. If you can tell your answer may be incomplete, search again for "
    "what is missing. If you judge the answer is not in the repository (an id that exists nowhere, say), answer "
    "not_found. Never answer beyond the bundles.")
UNRANKED_NOTE = " The bundle's items are in no particular order: weigh them yourself."
READER_SCHEMA = {"type": "object", "required": ["verdict", "answer", "citations", "search"], "properties": {
    "verdict": {"type": "string", "enum": ["answer", "search_again", "not_found"]}, "answer": {"type": "string"},
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
DB = sqlite3.connect(f"file:{CLONE}/.gov-runtime/store.db?mode=ro", uri=True, check_same_thread=False)


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
    u, cost = d.get("usage") or {}, d.get("total_cost_usd") or 0
    with lock:
        spent[0] += cost
    return {"wall_s": wall, "cost_usd": cost, "tokens": {k: u.get(k) for k in (
        "input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens", "output_tokens")}}, out


def first_calls(measure_txt):
    starts, n = {}, 1
    for line in Path(measure_txt).read_text().splitlines():
        m = re.match(r"(\S+) \((\w+)\):.*?; (\d+) calls?(?:;|$)", line)
        if m:
            starts[m[1]] = n
            n += int(m[3])
    return starts


def text_of(path, a, b):
    try:
        lines = (CLONE / path).read_text(errors="replace").splitlines(keepends=True)
    except OSError:
        return ""
    return "".join(lines[max(0, a - 1):b])


def own(e):
    """A ranked item with its chunk's own span (an expanded item goes back to its chunk)."""
    with lock:
        row = DB.execute("select path, start_line, end_line from lexical_chunk where chunk_id = ?", (e["chunk_id"],)).fetchone()
    path, a, b = row if row else (e["path"], int(e["start_line"]), int(e["end_line"]))
    return (path, int(a), int(b), text_of(path, int(a), int(b)))


def sent(e):
    return (e.get("path"), int(e.get("start_line")), int(e.get("end_line")), str(e.get("text", "")))


def bundles_of(q):
    c1 = json.loads(Path(q["first"]).read_text())["result"]["evidence"]
    c2 = json.loads(Path(q["second"]).read_text()).get("result", {}).get("evidence", []) if Path(q["second"]).is_file() else []
    ranked = [own(e) for e in c1]
    pool = ranked + [own(e) for e in c2]
    seen, uniq = set(), []
    for it in pool:
        if it[:3] not in seen:
            seen.add(it[:3]); uniq.append(it)
    random.Random(q["id"]).shuffle(uniq)
    return {"top5": ranked[:5], "top10": ranked[:10], "top20": ranked[:20], "bundle": [sent(e) for e in c1], "unranked40": uniq[:40]}


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
            q.update(gold=yaml.safe_load(f.read_text()).get("gold_answer"), kind="spent" if set_ == "memory-verdict" else part,
                     apart=q["id"] in APART, first=KEPT / kept / f"{starts[q['id']]:05d}.json",
                     second=KEPT / kept / f"{starts[q['id']] + 1:05d}.json")
            out.append(q)
    return out


def prompt_of(question, items):
    return "\n".join([f"Question: {question}", "\n=== Bundle 1 ==="] + [f"--- {p} lines {a}-{z}\n{t}" for p, a, z, t in items])


def one(q, cond, items, run, brake):
    if spent[0] > brake:
        stop_reason[0] = stop_reason[0] or f"the runaway brake: spend {spent[0]:.2f} USD passed {brake:.2f}"
        return None
    sys_ = READER_SYS + (UNRANKED_NOTE if cond == "unranked40" else "")
    meta, out = claude("claude-opus-5-5", sys_, READER_SCHEMA, prompt_of(q["question"], items), 1.5, run)
    verdict = (out or {}).get("verdict") or "error"
    if verdict == "search_again":
        verdict = "not_found"
    grades = {}
    if out and verdict in ("answer", "not_found"):
        said = out.get("answer") if verdict == "answer" else "Not found."
        gp = f"Question: {q['question']}\n\nGold answer: {q['gold']}\n\nAnswer to grade: {said}"
        for name, model in (("grader", "claude-opus-5-5"), ("check", "claude-sonnet-5-5")):
            gm, g = claude(model, GRADER_SYS, GRADER_SCHEMA, gp, 0.5, run)
            grades[name] = {**gm, "grade": (g or {}).get("grade")}
    cites = [(c.get("path"), int(c.get("start_line", 0)), int(c.get("end_line", 0))) for c in (out or {}).get("citations") or []]
    row = {"id": q["id"], "kind": q["kind"], "apart": q["apart"], "condition": cond, "verdict": verdict,
           "answer": (out or {}).get("answer"), "citations": (out or {}).get("citations"), "reader": meta, "grades": grades,
           "bundle_chars": sum(len(t) for *_, t in items), "items": len(items),
           "gold_in_bundle": any(hit(it, q) for it in items),
           "citation_right": (not q["apart"]) and any(hit((p, a, z, text_of(p, a, z)), q) for p, a, z in cites)}
    (Path(run) / f"{q['id']}.{cond}.json").write_text(json.dumps(row, indent=1))
    return row


def right(r):
    g = (r["grades"].get("grader") or {}).get("grade")
    if r["apart"]:
        return r["verdict"] == "not_found" or g == "correct"
    return r["verdict"] == "answer" and g == "correct" and r["citation_right"]


def mcnemar(a, b):
    g = sum(1 for x, y in zip(a, b) if y and not x); l = sum(1 for x, y in zip(a, b) if x and not y)
    n, k = g + l, min(g, l)
    return g, l, (min(1.0, 2 * sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n) if n else 1.0)


def main():
    run = Path(sys.argv[1]); qs = load()
    if sys.argv[2] == "dry":
        b = [bundles_of(q) for q in qs]
        print(json.dumps({"questions": len(qs), **{c: {"gold in bundle": sum(1 for q, x in zip(qs, b) if not q["apart"] and any(hit(i, q) for i in x[c])),
                                                       "chars median": sorted(sum(len(t) for *_, t in x[c]) for x in b)[len(b) // 2]} for c in CONDITIONS}}))
        return
    projection = float(sys.argv[2]); brake = 2 * projection; run.mkdir(parents=True, exist_ok=True)
    jobs = [(q, c, items) for q in qs for c, items in bundles_of(q).items()]
    t0 = time.time()
    with ThreadPoolExecutor(WORKERS) as pool:
        rows = [r for r in pool.map(lambda j: one(*j, run, brake), jobs) if r]
    rep = {"jobs_planned": len(jobs), "jobs_run": len(rows), "stopped": stop_reason[0], "projection_usd": projection,
           "brake_usd": brake, "spent_usd": round(spent[0], 2), "wall_min": round((time.time() - t0) / 60, 1)}
    by = {(r["id"], r["condition"]): r for r in rows}
    ids = [q["id"] for q in qs if not q["apart"] and all((q["id"], c) in by for c in CONDITIONS)]
    for c in CONDITIONS:
        for kind in ("visible", "hidden", "spent", "the 138"):
            rs = [by[(i, c)] for i in ids if kind == "the 138" or by[(i, c)]["kind"] == kind]
            rep[f"{c} {kind}"] = {"n": len(rs), "right": sum(map(right, rs)),
                                  "correct": sum(1 for r in rs if (r["grades"].get("grader") or {}).get("grade") == "correct" and r["verdict"] == "answer"),
                                  "citation_right": sum(r["citation_right"] for r in rs), "gold_in_bundle": sum(r["gold_in_bundle"] for r in rs),
                                  "wrong_claims": sum(1 for r in rs if r["verdict"] == "answer" and (r["grades"].get("grader") or {}).get("grade") != "correct"),
                                  "not_found": sum(1 for r in rs if r["verdict"] != "answer")}
        ap = [by[(q["id"], c)] for q in qs if q["apart"] and (q["id"], c) in by]
        rep[f"{c} nonexistent-id"] = {"n": len(ap), "right": sum(map(right, ap))}
        rs = [by[(i, c)] for i in ids]
        rep[f"{c} cost"] = {"usd": round(sum((r["reader"].get("cost_usd") or 0) + sum((g.get("cost_usd") or 0) for g in r["grades"].values()) for r in rs), 2),
                            "bundle chars median": sorted(r["bundle_chars"] for r in rs)[len(rs) // 2] if rs else None}
    base = [right(by[(i, "bundle")]) for i in ids]
    tests = {c: mcnemar(base, [right(by[(i, c)]) for i in ids]) for c in CONDITIONS if c != "bundle"}
    order = sorted(tests, key=lambda c: tests[c][2])
    for k, c in enumerate(order):  # Holm within the experiment
        g, l, p = tests[c]
        rep[f"mcnemar {c} vs bundle (gains, losses, p, Holm p)"] = (g, l, round(p, 5), round(min(1.0, p * (len(order) - k)), 5))
    rep["ranking by right on the 138"] = sorted(CONDITIONS, key=lambda c: -rep[f"{c} the 138"]["right"])
    rep["grader agreement"] = f"{sum(1 for r in rows if r['grades'] and r['grades']['grader'].get('grade') == r['grades']['check'].get('grade'))} of {sum(1 for r in rows if r['grades'])}"
    rep["errors"] = sum(1 for r in rows if r["verdict"] == "error")
    (run / "summary.json").write_text(json.dumps(rep, indent=1))
    print(json.dumps(rep, indent=1))


main()
