#!/usr/bin/env python3
"""One question's ranked outputs in two runs, compared by chunk ids and places only (no text, no question): the
question's call range from each run's measure.txt (its lines in run order, each with "N calls"), then per call the
evidence ids in order, and where they differ.

    diff_one.py <qid> <measure.txt a> <kept folder a> <measure.txt b> <kept folder b>
"""
import json
import re
import sys
from pathlib import Path


def call_range(measure: str, qid: str):
    start = 1
    for line in open(measure):
        m = re.match(r"(\S+) \(\w+\): hit@5 .*?(\d+) calls?", line)
        if not m:
            continue
        n = int(m[2])
        if m[1] == qid:
            return list(range(start, start + n))
        start += n
    raise SystemExit(f"{qid} not in {measure}")


def ids(folder: str, n: int):
    """Per item: chunk id, path, line span and batch; then the expansions' spans (ids and line numbers only)."""
    data = json.loads((Path(folder) / f"{n:05d}.json").read_text())
    r = data.get("result") or {}
    items = [(e.get("chunk_id"), e.get("path"), e.get("start_line"), e.get("end_line"), e.get("batch"))
             for e in r.get("evidence", [])]
    exp = [(x.get("chunk_id"), x.get("parent_id"), x.get("start_line"), x.get("end_line")) for x in r.get("expansions", [])]
    return items + [("EXPANSIONS",)] + exp, (r.get("rerank") or {}).get("by")


qid, ma, ka, mb, kb = sys.argv[1:6]
ra, rb = call_range(ma, qid), call_range(mb, qid)
print(f"{qid}: calls a {ra[0]}-{ra[-1]}, b {rb[0]}-{rb[-1]}")
for i, (x, y) in enumerate(zip(ra, rb), 1):
    (ea, ba), (eb, bb) = ids(ka, x), ids(kb, y)
    same = ea == eb
    print(f"call {i}: {'same' if same else 'DIFFERENT'}; {len(ea)} vs {len(eb)} items; rerank {ba} / {bb}")
    if not same:
        sa, sb = set(ea), set(eb)
        print(f"  only in a: {len(sa - sb)}; only in b: {len(sb - sa)}; common {len(sa & sb)}")
        for p, (u, v) in enumerate(zip(ea, eb), 1):
            if u != v:
                print(f"  first difference at place {p}: {u} / {v}")
                break
        moved = [(c, ea.index(c) + 1, eb.index(c) + 1) for c in sa & sb if ea.index(c) != eb.index(c)]
        print(f"  common items at other places: {len(moved)}; e.g. {sorted(moved, key=lambda t: t[1])[:6]}")
