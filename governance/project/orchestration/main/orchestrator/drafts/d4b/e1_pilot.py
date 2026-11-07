#!/usr/bin/env python3
"""E1, the search-again pilot (D4B-SEARCH-AGAIN §7; DEC-1085 (4), DEC-1086 C, DEC-1087 (11); amended in
E1-DECLARATION.md: the product's bundles). Five visible questions. For each:
  attempt 1: the first call's bundle from E0's kept output (~/gov-os-eval/runs/w4-e0/r80/<n>.json);
  the reader (claude-opus-5-5, effort high, no tools, no transcript) returns answer | search_again | not_found;
  on search_again, the reader's own words are searched live with the pinned gov on E0's measure clone, and the first
  call's bundle is added; at most three attempts (A1 and A2 are A3's run cut after attempts 1 and 2);
  the final answer is graded by claude-opus-5-5 (counts) and claude-sonnet-5-5 (agreement), given the question, the
  gold answer and the reader's answer; the citation is checked by code against the gold sources' lines (re-anchored by
  heading in the clone). Every call's own usage and total_cost_usd are kept. Visible questions only.
Usage: e1_pilot.py <run folder> <qid>...
"""
import json, re, subprocess, sys, time
from pathlib import Path

import yaml

HOME = Path.home()
CLONE = HOME / "gov-os-runs/D4B/w4-e0/repo"
KEPT = HOME / "gov-os-eval/runs/w4-e0/r80"
MEASURE = HOME / "gov-os-runs/D4B/w4-e0/out/r80/measure.txt"
VIS = HOME / "gov-os-eval/fixtures/evaluation/memory-retrieval/visible"
GOV = str(HOME / ".local/bin/gov")
CLAUDE = str(HOME / ".local/bin/claude")
CAP = 3

READER_SYS = (
    "You answer one question about a software repository, using only the search bundles you are given. Each bundle item "
    "has a path, a line range and the text of those lines. If the bundles answer the question, give the answer and cite "
    "the items (path, start_line, end_line) you rely on. If the bundles do not answer the question, give different search "
    "words in 'search' and set verdict to search_again. If you judge the answer is not in the repository (an id that "
    "exists nowhere, say), answer not_found. Never answer beyond the bundles.")
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


def claude(model, system, schema, prompt, budget, cwd):
    t = time.monotonic()
    p = subprocess.run([CLAUDE, "-p", "--safe-mode", "--tools", "", "--no-session-persistence", "--output-format", "json",
                        "--model", model, "--effort", "high", "--max-budget-usd", str(budget), "--system-prompt", system,
                        "--json-schema", json.dumps(schema)], input=prompt, capture_output=True, text=True, cwd=cwd)
    wall = round(time.monotonic() - t, 1)
    try:
        d = json.loads(p.stdout)
    except ValueError:
        return {"error": (p.stderr or p.stdout)[-400:], "wall_s": wall}, None
    out = d.get("structured_output")
    if out is None:
        try:
            out = json.loads(d.get("result") or "")
        except ValueError:
            out = None
    u = d.get("usage") or {}
    meta = {"wall_s": wall, "cost_usd": d.get("total_cost_usd"), "is_error": d.get("is_error"),
            "tokens": {k: u.get(k) for k in ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens", "output_tokens")}}
    return meta, out


def first_calls():
    starts, n = {}, 1
    for line in MEASURE.read_text().splitlines():
        m = re.match(r"(\S+) \((\w+)\):.*?(\d+) calls?$", line)
        if m:
            starts[m[1]] = n
            n += int(m[3])
    return starts


def bundle(result):
    return [{"path": e.get("path"), "start_line": e.get("start_line"), "end_line": e.get("end_line"),
             "text": e.get("text", "")} for e in (result.get("evidence") or [])]


def search(words):
    env = {k: v for k, v in __import__("os").environ.items() if k not in ("GOV_STORE", "GOV_TICKET")}
    t = time.monotonic()
    p = subprocess.run([GOV, "retrieve", words, "--json"], capture_output=True, text=True, cwd=CLONE, env=env)
    wall = round(time.monotonic() - t, 2)
    try:
        return bundle(json.loads(p.stdout)["result"]), wall
    except (ValueError, KeyError):
        return [], wall


def gold_pieces(q):
    pieces = []
    for entry in q.get("sources") or []:
        for alt in (entry if isinstance(entry, list) else [entry]):
            a, b = alt["lines"]
            path = CLONE / alt["path"]
            head = (alt.get("heading") or "").strip()
            if head and path.is_file():
                for i, line in enumerate(path.read_text(errors="replace").splitlines(), 1):
                    if line.strip().startswith(head[:60]):
                        a, b = i, i + (b - a)
                        break
            pieces.append((alt["path"], a, b))
    return pieces


def cited_right(citations, pieces):
    return any(c.get("path") == p and c.get("start_line", 0) <= b and a <= c.get("end_line", 0)
               for c in citations for p, a, b in pieces)


def prompt_of(question, bundles):
    parts = [f"Question: {question}"]
    for k, b in enumerate(bundles, 1):
        parts.append(f"\n=== Bundle {k} ===")
        for it in b:
            parts.append(f"--- {it['path']} lines {it['start_line']}-{it['end_line']}\n{it['text']}")
    return "\n".join(parts)


def main():
    run, qids = Path(sys.argv[1]), sys.argv[2:]
    run.mkdir(parents=True, exist_ok=True)
    starts = first_calls()
    rows = []
    for qid in qids:
        q = yaml.safe_load(next(VIS.glob(f"[qQ]{qid[1:]}.yaml")).read_text())
        first = json.loads((KEPT / f"{starts[qid]:05d}.json").read_text())["result"]
        bundles, attempts, searches = [bundle(first)], [], []
        verdict, final = None, None
        for k in range(1, CAP + 1):
            meta, out = claude("claude-opus-5-5", READER_SYS, READER_SCHEMA, prompt_of(q["question"], bundles), 1.5, run)
            attempts.append({"attempt": k, **meta, "verdict": (out or {}).get("verdict")})
            if not out:
                verdict = "error"; break
            final, verdict = out, out["verdict"]
            if verdict != "search_again":
                break
            if k == CAP:
                verdict = "not_found"; break
            b, wall = search(out.get("search") or q["question"])
            searches.append({"words": out.get("search"), "wall_s": wall, "items": len(b)})
            bundles.append(b)
        pieces = gold_pieces(q)
        in_bundle = [any(cited_right([it], pieces) for it in b) for b in bundles]
        grades = {}
        if final and verdict in ("answer", "not_found"):
            gp = f"Question: {q['question']}\n\nGold answer: {q.get('gold_answer')}\n\nAnswer to grade: {final.get('answer') if verdict == 'answer' else 'Not found.'}"
            for name, model in (("grader", "claude-opus-5-5"), ("check", "claude-sonnet-5-5")):
                meta, g = claude(model, GRADER_SYS, GRADER_SCHEMA, gp, 0.5, run)
                grades[name] = {**meta, "grade": (g or {}).get("grade")}
        row = {"qid": qid, "final_verdict": verdict, "attempts": attempts, "searches": searches,
               "gold_in_bundle_by_attempt": in_bundle, "citation_right": bool(final and cited_right(final.get("citations") or [], pieces)),
               "grades": grades, "answer": (final or {}).get("answer"), "citations": (final or {}).get("citations")}
        rows.append(row)
        (run / f"{qid}.json").write_text(json.dumps(row, indent=1))
        print(json.dumps({k: row[k] for k in ("qid", "final_verdict", "gold_in_bundle_by_attempt", "citation_right")}
                         | {"grades": {k: v.get("grade") for k, v in grades.items()},
                            "reader_cost": round(sum(a.get("cost_usd") or 0 for a in attempts), 4),
                            "grader_cost": round(sum(v.get("cost_usd") or 0 for v in grades.values()), 4),
                            "attempts": len(attempts)}), flush=True)
    cost_r = sum(a.get("cost_usd") or 0 for r in rows for a in r["attempts"])
    cost_g = sum(v.get("cost_usd") or 0 for r in rows for v in r["grades"].values())
    summary = {"questions": len(rows), "reader_calls": sum(len(r["attempts"]) for r in rows),
               "reader_cost_usd": round(cost_r, 4), "grader_cost_usd": round(cost_g, 4),
               "per_question_usd": round((cost_r + cost_g) / max(1, len(rows)), 4),
               "projected_138_usd": round(138 * (cost_r + cost_g) / max(1, len(rows)), 2),
               "reader_wall_s_median": sorted(a["wall_s"] for r in rows for a in r["attempts"])[sum(len(r["attempts"]) for r in rows) // 2]}
    (run / "summary.json").write_text(json.dumps(summary, indent=1))
    print(json.dumps(summary))


main()
