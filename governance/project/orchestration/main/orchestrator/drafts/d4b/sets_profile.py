#!/usr/bin/env python3
"""DEC-1070 (12)'s blind phrasing audit, with the gold's structural traits, per set: aggregates only (no question,
no id, no per-question figure). Read, never used to choose or tune anything.

    cd <clone> && PYTHONPATH=src python3 sets_profile.py <sets root>
"""
import collections
import re
import sqlite3
import statistics
import sys
from pathlib import Path

from gov.guard.reads import evaluation_sets
from gov.retrieval.measure import EVALUATION, _load, _Part

root, sr = Path("."), Path(sys.argv[1])
STOP = set("a an the of to in on for and or is are was were be by with what which who how does do did can i my we our "
           "it its this that these those from at as when where why whose whom there their them they if not no any each "
           "should would will shall may must".split())
words = lambda s: {w for w in re.findall(r"[a-z0-9_]+", s.lower()) if w not in STOP and len(w) > 2}
db = sqlite3.connect(root / ".gov-runtime" / "store.db")
emb = {r[0] for r in db.execute("select chunk_id from semantic_vector")}
ch = collections.defaultdict(list)
for c in db.execute("select chunk_id, path, start_line, end_line, parent_id from lexical_chunk"):
    if c[0] in emb:
        ch[c[1]].append(c)
par = {p: s for p, s in db.execute("select parent_id, start_line from lexical_parent")}
cache = {}


def lines(p, s, e):
    if p not in cache:
        cache[p] = (root / p).read_text(errors="replace").splitlines()
    return cache[p][s - 1:e]


sets = [("memory-retrieval", "visible", "the tuning set"), ("memory-retrieval", "hidden", "the hidden check"),
        ("memory-verdict", "hidden", "the measurement set")]
for name, part, label in sets:
    e = evaluation_sets(str(sr))[name]
    qt = _Part("/q", [*e.get("visible", []), *e["hidden"], f"{EVALUATION}/**"], "")
    share, c, n = [], collections.Counter(), 0
    for f in sorted((sr / EVALUATION / name / part).glob("*.yaml")):
        q = _load(f, part, root, qt)
        p, s, e_ = q["sources"][0][0]
        gold = " ".join(lines(p, s, e_))
        qw = words(q["question"])
        if not qw:
            continue
        n += 1
        share.append(len(qw & words(gold)) / len(qw))
        first = (lines(p, s, s) or [""])[0].strip()
        hs = [x for x in ch.get(p, []) if x[2] <= e_ and s <= x[3]]
        c["answer a list item"] += bool(re.match(r"([-*] |\d+\. )", first))
        c["answer chunk without its heading"] += bool(hs) and hs[0][2] > par.get(hs[0][4], hs[0][2])
        c["gold in a .py file"] += p.endswith(".py")
        c["gold in the register"] += p == "docs/DECISION_REGISTER.md"
    q4 = statistics.quantiles(share, n=4)
    print(f"{label} ({n} questions): question words found in the gold span: median {statistics.median(share):.2f}, "
          f"quartiles {q4[0]:.2f} / {q4[2]:.2f}; under a third: {sum(x < 1 / 3 for x in share)}; "
          + "; ".join(f"{k}: {v} ({100 * v / n:.0f} %)" for k, v in c.items()))
