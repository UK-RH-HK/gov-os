#!/usr/bin/env python3
"""DEC-1070 (6), the recall diagnosis, stage 1: from a measure's kept ranked outputs, no new search, no GPU.

    PYTHONPATH=<clone>/src python3 diag_recall.py <clone root> <sets root> <kept run dir> <measure.txt> [--json out]

For every question and every gold piece (an entry of its sources, the measure's own spans and matching rule):
  - where the gold first appears: in the 20 the first call gathered and reranked (its place after the rerank), in the
    fused list but cut from the first 20 (its fused position, 21 on), or in no route's list at all (ABSENT);
  - for an ABSENT piece: whether its span is in the lexical index and in the semantic index (the chunk table);
  - the stacked rank the measure scores, and the calls.
And for every first call: how many of the 20 the closure route alone brought, and how long the fused list was.

The hidden half: ids, stages, positions, counts and yes/no only. No question, gold answer, path, heading or line
of a hidden question is printed or written (DEC-820 (d), the hidden-half rule).
"""
import json
import os
import re
import sqlite3
import sys
from pathlib import Path

from gov.guard.reads import evaluation_sets
from gov.retrieval.measure import EVALUATION, _load, _Part

clone, sets_root, kept, mtxt = (Path(a) for a in sys.argv[1:5])
out_json = sys.argv[sys.argv.index("--json") + 1] if "--json" in sys.argv else None
SET = os.environ.get("DIAG_SET", "memory-retrieval")  # memory-verdict for the spent 60 (DEC-1074 (2)), counts only

entry = evaluation_sets(str(sets_root))[SET]
quoting = _Part("/q", [*entry.get("visible", []), *entry["hidden"], f"{EVALUATION}/**"], "")
questions = {}
for part in ("visible", "hidden"):
    for f in sorted((sets_root / EVALUATION / SET / part).glob("*.yaml")):
        q = _load(f, part, clone, quoting)
        questions[q["id"]] = q

order = []
for line in mtxt.read_text().splitlines():
    m = re.match(r"(\S+) \((visible|hidden)\): hit@5 (yes|no)(?: \(first gold rank (\d+)\))?.*; (\d+) calls", line)
    if m:
        order.append((m[1], m[3] == "yes", int(m[4]) if m[4] else None, int(m[5])))
files = sorted(kept.glob("*.json"))
assert sum(o[3] for o in order) == len(files), f"calls {sum(o[3] for o in order)} != kept files {len(files)}"

db = sqlite3.connect(clone / ".gov-runtime" / "store.db")
chunk_lines = {cid: (p, s, e) for cid, p, s, e in db.execute("select chunk_id, path, start_line, end_line from lexical_chunk")}
# a gathered chunk may be widened to its parent's span (the bundle's expansions), so a cut chunk counts by either
parent_lines = {cid: (p, s, e) for cid, p, s, e in db.execute(
    "select c.chunk_id, p.path, p.start_line, p.end_line from lexical_chunk c join lexical_parent p on c.parent_id = p.parent_id")}
embedded = {r[0] for r in db.execute("select chunk_id from semantic_vector")}
indexed_file = dict(db.execute("select path, indexed from lexical_file"))


def overlaps(path, s, e, alt):
    return path == alt[0] and s <= alt[2] and alt[1] <= e


def coverage(alts):
    """Whether any alternative's span has a chunk in the lexical index, and one embedded."""
    lex = sem = False
    for alt in alts:
        for cid, (p, s, e) in chunk_lines.items():
            if overlaps(p, s, e, alt):
                lex = True
                sem = sem or cid in embedded
        if lex and sem:
            break
    return lex, sem, any(bool(indexed_file.get(a[0])) for a in alts)


rows, closure_stats, i = [], [], 0
for qid, hit5, rank, ncalls in order:
    q = questions[qid]
    docs = [json.load(open(f))["result"] for f in files[i:i + ncalls]]
    i += ncalls
    first = docs[0]
    ev = first["evidence"]
    gaps = [g for g in first.get("gaps", []) if g.get("reason") == "NOT_GATHERED"]
    closure_stats.append({"id": qid, "part": q["part"], "fused_len": len(ev) + len(gaps),
                          "closure_only_in_20": sum(1 for e in ev if e.get("routes") == ["closure"]),
                          "closure_any_in_20": sum(1 for e in ev if "closure" in (e.get("routes") or []))})
    pieces = []
    for alts in q["sources"]:
        pos20 = next((n for n, e in enumerate(ev, 1)
                      if any(overlaps(e["path"], e["start_line"], e["end_line"], a) for a in alts)), None)
        routes = ev[pos20 - 1].get("routes") if pos20 else None
        fpos = fpos_parent = None
        if pos20 is None:  # in the cut list: the gold's own chunk, or (later widened) a sibling under its parent
            # the cut list starts after the reranked pool (20 in the product, 40 under v456)
            own = [n for n, g in enumerate(gaps, len(ev) + 1)
                   if any(overlaps(*chunk_lines.get(g["chunk_id"], ("", 0, -1)), a) for a in alts)]
            par = [n for n, g in enumerate(gaps, len(ev) + 1)
                   if any(overlaps(*parent_lines.get(g["chunk_id"], ("", 0, -1)), a) for a in alts)]
            fpos, fpos_parent = (own[0] if own else None), (par[0] if par else None)
        sib = None
        if pos20 is None:  # a chunk of the gold's parent section in the 20, not widened to the gold's lines
            sib = next((n for n, e in enumerate(ev, 1)
                        if any(overlaps(*parent_lines.get(e["chunk_id"], ("", 0, -1)), a) for a in alts)), None)
        stage = ("IN_20" if pos20 else "CUT" if fpos else "SIBLING_IN_20" if sib else
                 "SIBLING_CUT" if fpos_parent else "ABSENT")
        piece = {"stage": stage, "place_in_20": pos20, "fused_pos": fpos or fpos_parent, "routes": routes,
                 "sibling_place": sib}
        if stage != "IN_20":
            piece["lexical_indexed"], piece["embedded"], piece["file_indexed"] = coverage(alts)
        pieces.append(piece)
    rows.append({"id": qid, "part": q["part"], "hit5": hit5, "rank": rank, "calls": ncalls, "pieces": pieces})

if out_json:
    Path(out_json).write_text(json.dumps({"rows": rows, "closure": closure_stats}, indent=1))


def best(r):
    st = [p["stage"] for p in r["pieces"]]
    for s in ("IN_20", "CUT", "SIBLING_IN_20", "SIBLING_CUT"):
        if s in st:
            return s
    return "ABSENT"


for part in ("visible", "hidden"):
    rs = [r for r in rows if r["part"] == part]
    if not rs:
        continue
    print(f"== {part}: {len(rs)} questions, hit@5 {sum(r['hit5'] for r in rs)}")
    for r in rs:
        if r["hit5"]:
            continue
        ps = "; ".join(f"{p['stage']}" + (f" place {p['place_in_20']} via {'+'.join(p['routes'] or [])}" if p["place_in_20"] else "")
                       + (f" fused {p['fused_pos']}" if p["fused_pos"] else "")
                       + (f" sibling at place {p['sibling_place']}" if p.get("sibling_place") else "")
                       + (f" lex-indexed {'yes' if p['lexical_indexed'] else 'no'}, embedded {'yes' if p['embedded'] else 'no'},"
                          f" file indexed {'yes' if p['file_indexed'] else 'no'}" if p["stage"] != "IN_20" else "")
                       for p in r["pieces"])
        print(f"  MISS {r['id']}: stacked rank {r['rank']}, {r['calls']} calls; first-call stage {best(r)}; pieces: {ps}")
    allp = [p for r in rs for p in r["pieces"]]
    print(f"  all pieces ({len(allp)}): in the 20 {sum(p['stage']=='IN_20' for p in allp)}, "
          f"cut {sum(p['stage']=='CUT' for p in allp)}, sibling in the 20 {sum(p['stage']=='SIBLING_IN_20' for p in allp)}, sibling cut {sum(p['stage']=='SIBLING_CUT' for p in allp)}, "
          f"absent {sum(p['stage']=='ABSENT' for p in allp)}")
    cs = [c for c in closure_stats if c["part"] == part]
    n = len(cs)
    print(f"  first calls: fused list median {sorted(c['fused_len'] for c in cs)[n // 2]}, max {max(c['fused_len'] for c in cs)}; "
          f"closure-only chunks in the 20: mean {sum(c['closure_only_in_20'] for c in cs) / n:.1f}, "
          f"questions with >= 5: {sum(c['closure_only_in_20'] >= 5 for c in cs)}, with any: {sum(c['closure_only_in_20'] > 0 for c in cs)}")
    gold_routes = {}
    for p in allp:
        if p["routes"]:
            k = "+".join(sorted(p["routes"]))
            gold_routes[k] = gold_routes.get(k, 0) + 1
    print(f"  gold pieces in the 20, by route: {dict(sorted(gold_routes.items()))}")
