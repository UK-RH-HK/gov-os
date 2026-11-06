#!/usr/bin/env python3
"""The grid's report (D4B-SCORE-ONCE §4): per cell, hit@5 and MRR on the 138 and per set, the spread, gains and
losses against B0 with an exact McNemar p, and a Holm-adjusted p for the 16 comparisons (shown, not part of the rule).
Ranked by the rule: hit@5 on the 138, then MRR; a cell whose spread is wider than B0's is marked. Counts only.

    grid_report.py <replays folder> <grid.txt>
"""
import importlib.util
import math
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("s138", HERE.parent / "d4b" / "score138.py")
src = (HERE.parent / "d4b" / "score138.py").read_text().split('\nif sys.argv[1] == "--same":')[0]
mod = {}
exec(compile(src, "score138.py", "exec"), mod)
APART = {"h24", "m60"}


def hits(folder: Path):
    out = {}
    for prefix, part in (("", "r80"), ("v:", "r60")):
        for line in open(folder / part / "measure.txt"):
            m = re.match(r"(\S+) \((\w+)\): hit@5 (yes|no)", line)
            if m and m[1] not in APART:
                out[prefix + m[1]] = m[3] == "yes"
    return out


def exact_p(g, l):
    n = g + l
    if n == 0:
        return 1.0
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(min(g, l) + 1)) / 2 ** n)


root, grid = Path(sys.argv[1]), Path(sys.argv[2])
cells = [line.split("\t")[0] for line in grid.read_text().splitlines() if line.strip()]
rows = {}
for c in cells:
    d = root / c
    if not (d / "r80" / "measure.txt").exists() or not (d / "r60" / "measure.txt").exists():
        rows[c] = None
        continue
    s, t, spread = mod["figures"](mod["rows"](d / "r80" / "measure.txt"), mod["rows"](d / "r60" / "measure.txt"))
    rows[c] = {"hit": t[0], "n": t[1], "mrr": t[2], "spread": spread, "sets": s, "hits": hits(d)}
b0 = rows.get("g-B0")
assert b0, "B0 is missing"
tests = []
for c in cells:
    r = rows[c]
    if r is None or c == "g-B0":
        continue
    g = sum(1 for q in b0["hits"] if r["hits"][q] and not b0["hits"][q])
    l = sum(1 for q in b0["hits"] if b0["hits"][q] and not r["hits"][q])
    r.update(gains=g, losses=l, p=exact_p(g, l))
    tests.append(c)
m = len(tests)  # Holm's step-down over the cells' p
order = sorted(tests, key=lambda c: rows[c]["p"])
running = 0.0
for i, c in enumerate(order):
    running = max(running, min(1.0, (m - i) * rows[c]["p"]))
    rows[c]["holm"] = running
print(f"B0: {b0['hit']}/{b0['n']} MRR {b0['mrr']:.4f} spread {b0['spread']:.1f} | "
      + " | ".join(f"{k} {v[0]}/{v[1]} MRR {v[3]:.4f}" for k, v in b0["sets"].items()))
print("cell | hit@5 /138 | MRR | visible | hidden | spent | spread | gains | losses | McNemar p | Holm p | note")
ranked = sorted([c for c in cells if rows[c] and c != "g-B0"], key=lambda c: (-rows[c]["hit"], -rows[c]["mrr"]))
for c in ranked:
    r = rows[c]
    note = "spread wider than B0" if r["spread"] > b0["spread"] + 1e-9 else ""
    print(f"{c} | {r['hit']} | {r['mrr']:.4f} | {r['sets']['visible'][0]} | {r['sets']['hidden'][0]} | "
          f"{r['sets']['spent'][0]} | {r['spread']:.1f} | {r['gains']} | {r['losses']} | {r['p']:.3f} | "
          f"{r['holm']:.3f} | {note}")
missing = [c for c in cells if rows[c] is None]
if missing:
    print("missing (not finished or failed): " + ", ".join(missing))
