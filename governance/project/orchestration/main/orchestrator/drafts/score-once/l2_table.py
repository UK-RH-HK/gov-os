#!/usr/bin/env python3
"""DEC-1079 L2: for each miss of the full run (R0), its first gold rank at each stage (the reranker's own order, plus
the authority lift, plus routing's moves, the full pipeline), and the stage at which the answer left the top 5. Ids
and ranks only (h24 and m60 apart).

    l2_table.py <replays folder>   (expects l2a-own3, l2b-lift3, l2c-routing2, a-q06, each with r80/ and r60/; all on
                                    the labels re-anchored at e884675b, 12:42; the move off by the sentinel)
"""
import re
import sys
from collections import Counter
from pathlib import Path

APART = {"h24", "m60"}
STAGES = [("own", "l2a-own3"), ("+lift", "l2b-lift3"), ("+routing", "l2c-routing2"), ("full", "a-q06")]


def ranks(folder: Path):
    out = {}
    for prefix, part in (("", "r80"), ("v:", "r60")):
        for line in open(folder / part / "measure.txt"):
            m = re.match(r"(\S+) \(\w+\): hit@5 (yes|no)(?: \(first gold rank (\d+)\))?", line)
            if m and m[1] not in APART:
                out[prefix + m[1]] = int(m[3]) if m[3] else None
    return out


root = Path(sys.argv[1])
by = {name: ranks(root / folder) for name, folder in STAGES}
top5 = lambda r: r is not None and r <= 5
misses = [q for q, r in by["full"].items() if not top5(r)]
print(f"{len(misses)} misses of {len(by['full'])} in the full run; hit@5 by stage: "
      + ", ".join(f"{n} {sum(top5(r) for r in by[n].values())}" for n, _ in STAGES))
print("question | own | +lift | +routing | full | left the top 5 at")
left = Counter()
for q in sorted(misses):
    row = [by[n].get(q) for n, _ in STAGES]
    where = "never in it (ranked low by the reranker itself)"
    for (name, _), prev, cur in zip(STAGES[1:], row, row[1:]):
        if top5(prev) and not top5(cur):
            where = name
            break
    left[where] += 1
    print(f"{q} | " + " | ".join("-" if r is None else str(r) for r in row) + f" | {where}")
print("the misses by stage: " + "; ".join(f"{k}: {v}" for k, v in left.most_common()))
