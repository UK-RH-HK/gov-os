#!/usr/bin/env python3
"""DEC-1070 (9)'s figures from a measure.txt: per half hit@5, full evidence and the MRR of the first gold source
(1/rank over the stacked ranks, 0 when not found). Counts only."""
import re, sys
for f in sys.argv[1:]:
    t = {"visible": [0, 0, 0.0, 0], "hidden": [0, 0, 0.0, 0]}
    for l in open(f):
        m = re.match(r"\S+ \((visible|hidden)\): hit@5 (yes|no)(?: \(first gold rank (\d+)\))?.*full evidence (yes|no)", l)
        if m:
            x = t[m[1]]; x[0] += m[2] == "yes"; x[1] += m[4] == "yes"; x[2] += 1 / int(m[3]) if m[3] else 0; x[3] += 1
    print(f, " | ".join(f"{p} hit@5 {v[0]}/{v[3]} full {v[1]} MRR {v[2] / max(v[3], 1):.4f}" for p, v in t.items()))
