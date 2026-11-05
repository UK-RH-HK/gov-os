#!/usr/bin/env python3
"""DEC-1071's figures from measure.txt files: the 79 (h24, the nonexistent-id question, apart), per half hit@5, %,
MRR, and the gap. Counts only."""
import re, sys
for p in sys.argv[1:]:
    r = {}
    for part in ("visible", "hidden"):
        h = n = 0; m = 0.0
        for l in open(p):
            x = re.match(r"(\S+) \((\w+)\): hit@5 (yes|no)(?: \(first gold rank (\d+)\))?", l)
            if x and x[2] == part and x[1] != "h24":
                n += 1; h += x[3] == "yes"; m += 1 / int(x[4]) if x[4] else 0
        r[part] = (h, n, m / n)
    v, d = r["visible"], r["hidden"]
    print(f"{p.replace('/home/usain/gov-os-runs/D4B/', '')}: 79 {v[0] + d[0]} | vis {v[0]}/{v[1]} {100 * v[0] / v[1]:.1f}% "
          f"MRR {v[2]:.4f} | hid {d[0]}/{d[1]} {100 * d[0] / d[1]:.1f}% MRR {d[2]:.4f} | gap {100 * v[0] / v[1] - 100 * d[0] / d[1]:.1f} | MRR79 {(v[2] * v[1] + d[2] * d[1]) / (v[1] + d[1]):.4f}")
