#!/usr/bin/env python3
"""DEC-1077 (c): the reranker's net contribution, from two runs' measure.txt pairs (with and without the reranker):
how many questions it lifts into the top 5, how many it pushes out, and the rank moves of the rest. Counts only.
    lift_push.py <with 80> <with 60> <without 80> <without 60>"""
import re, sys
def rows(p, pre=""):
    o = {}
    for l in open(p):
        x = re.match(r"(\S+) \((\w+)\): hit@5 (yes|no)(?: \(first gold rank (\d+)\))?", l)
        if x and x[1] not in ("h24", "m60"):
            o[pre + x[1]] = (x[3] == "yes", int(x[4]) if x[4] else None)
    return o
w = {**rows(sys.argv[1]), **rows(sys.argv[2], "v:")}; n = {**rows(sys.argv[3]), **rows(sys.argv[4], "v:")}
lift = sorted(k for k in w if w[k][0] and not n[k][0]); push = sorted(k for k in w if n[k][0] and not w[k][0])
up = sum(1 for k in w if w[k][1] and n[k][1] and w[k][1] < n[k][1]); down = sum(1 for k in w if w[k][1] and n[k][1] and w[k][1] > n[k][1])
print(f"questions {len(w)}: hit@5 with the reranker {sum(v[0] for v in w.values())}, without {sum(v[0] for v in n.values())}; "
      f"lifted into the top 5 {len(lift)}, pushed out {len(push)}; first gold rank better {up}, worse {down}")
