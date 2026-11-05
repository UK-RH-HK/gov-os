#!/usr/bin/env python3
"""DEC-1070 (6), stage 3: each route's list exactly as the product builds it (the m6 clone, unchanged), and where
the gold's own chunk is in it: per phrasing (30 each), and the route's phrasings fused (the meaning route cut to 30).

    cd <clone> && PYTHONPATH=src python3 diag_routes.py <clone root> <sets root> <out.json>

The hidden half: ids, ranks and counts only (DEC-820 (d)).
"""
import json
import sys
from pathlib import Path

from gov import records
from gov.guard.reads import evaluation_sets
from gov.retrieval import graph_route, lexical, retrieve, routing, semantic
from gov.retrieval.measure import EVALUATION, _load, _Part

clone, sets_root, out = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
SET = "memory-retrieval"
entry = evaluation_sets(str(sets_root))[SET]
quoting = _Part("/q", [*entry.get("visible", []), *entry["hidden"], f"{EVALUATION}/**"], "")
known = records.records(clone)


def rank(hits, alts):
    return next((n for n, h in enumerate(hits, 1)
                 if any(h["path"] == a[0] and h["start_line"] <= a[2] and a[1] <= h["end_line"] for a in alts)), None)


rows = []
for part in ("visible", "hidden"):
    for f in sorted((sets_root / EVALUATION / SET / part).glob("*.yaml")):
        q = _load(f, part, clone, quoting)
        asked = routing.phrasings(q["question"], graph_route.start_ids(clone, q["question"], known))
        lex_each = [lexical.search(clone, a, refresh=False) for a in asked]
        sem_each = [semantic.search(clone, a, refresh=False) for a in asked]
        lex_route = retrieve._phrased(lexical.search, clone, asked, "ranked")
        sem_route = retrieve._phrased(semantic.search, clone, asked, "hits", cut=semantic.TOP_K)
        lex_l = lex_route.get("ranked", lex_route["hits"])
        sem_l = sem_route["hits"]
        # the meaning route without the cut after the phrasings' fusion: every phrasing's 30, fused
        sem_uncut = routing.fused([s["hits"] for s in sem_each]) if len(sem_each) > 1 else sem_each[0]["hits"]
        rows.append({"id": q["id"], "part": part, "phrasings": len(asked),
                     "lex_len": len(lex_l), "sem_len": len(sem_l), "sem_uncut_len": len(sem_uncut),
                     "pieces": [{"lex_each": [rank(x.get("ranked", x["hits"]), alts) for x in lex_each],
                                 "sem_each": [rank(x["hits"], alts) for x in sem_each],
                                 "lex_route": rank(lex_l, alts), "sem_route": rank(sem_l, alts),
                                 "sem_uncut": rank(sem_uncut, alts)} for alts in q["sources"]]})
out.write_text(json.dumps({"rows": rows}, indent=1))
