#!/usr/bin/env python3
"""DEC-1070 (6), the recall diagnosis, stage 2: how deep each route ranks the gold, for all 80 questions.

    cd <clone> && PYTHONPATH=src python3 diag_depth.py <clone root> <sets root> <depth> <out.json>

The product's own route functions at the m6 clone, unchanged except the two routes' depth (lexical.TOP_K and
semantic.TOP_K raised to <depth> in this process only), with the product's three phrasings. For every gold piece:
its rank in the keyword route and the meaning route, per phrasing and as the route's phrasings fused (as the product
fuses them), by the chunk's own span or its parent's (an expansion). The query embedder is the live one, on the GPU.

The hidden half: ids, ranks and counts only (DEC-820 (d)). Nothing of a hidden question is printed or written.
"""
import json
import os
import sys
from pathlib import Path

from gov.guard.reads import evaluation_sets
from gov import records
from gov.retrieval import graph_route, lexical, routing, semantic
from gov.retrieval.measure import EVALUATION, _load, _Part

clone, sets_root, depth, out = Path(sys.argv[1]), Path(sys.argv[2]), int(sys.argv[3]), Path(sys.argv[4])
lexical.TOP_K = semantic.TOP_K = depth
SET = os.environ.get("DIAG_SET", "memory-retrieval")  # memory-verdict for the spent 60 (DEC-1074 (2))
entry = evaluation_sets(str(sets_root))[SET]
quoting = _Part("/q", [*entry.get("visible", []), *entry["hidden"], f"{EVALUATION}/**"], "")
known = records.records(clone)

import sqlite3
db = sqlite3.connect(clone / ".gov-runtime" / "store.db")
parent = {cid: (p, s, e) for cid, p, s, e in db.execute(
    "select c.chunk_id, p.path, p.start_line, p.end_line from lexical_chunk c join lexical_parent p on c.parent_id = p.parent_id")}


def rank(hits, alts, use_parent=False):
    """The first rank whose chunk's own span overlaps the gold (or, with use_parent, whose parent's span does)."""
    for n, h in enumerate(hits, 1):
        p, s, e = parent.get(h["chunk_id"], ("", 0, -1)) if use_parent else (h["path"], h["start_line"], h["end_line"])
        if any(p == a[0] and s <= a[2] and a[1] <= e for a in alts):
            return n, use_parent
    return None, False


rows = []
for part in ("visible", "hidden"):
    for f in sorted((sets_root / EVALUATION / SET / part).glob("*.yaml")):
        q = _load(f, part, clone, quoting)
        asked = routing.phrasings(q["question"], graph_route.start_ids(clone, q["question"], known))
        lex = [lexical.search(clone, a, refresh=False) for a in asked]
        sem = [semantic.search(clone, a, refresh=False) for a in asked]
        assert all(s.get("available", True) and not s.get("error") for s in sem), f"{q['id']}: the meaning route did not answer"
        lex_l = [x.get("ranked", x["hits"]) for x in lex]
        sem_l = [x["hits"] for x in sem]
        lex_f, sem_f = routing.fused(lex_l), routing.fused(sem_l)
        pieces = []
        for alts in q["sources"]:
            lr, sr = rank(lex_f, alts)[0], rank(sem_f, alts)[0]
            pieces.append({"lex_fused": lr, "sem_fused": sr,
                           "lex_parent": rank(lex_f, alts, True)[0], "sem_parent": rank(sem_f, alts, True)[0],
                           "lex_each": [rank(l, alts)[0] for l in lex_l], "sem_each": [rank(s, alts)[0] for s in sem_l],
                           "lex_len": len(lex_f), "sem_len": len(sem_f)})
        rows.append({"id": q["id"], "part": part, "pieces": pieces})
        print(q["id"], "done", flush=True)
out.write_text(json.dumps({"depth": depth, "rows": rows}, indent=1))
