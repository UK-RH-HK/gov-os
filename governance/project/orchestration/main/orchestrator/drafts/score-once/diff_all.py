#!/usr/bin/env python3
"""Every question's ranked outputs in two runs of one set, compared by ids, line spans and expansions only (no text,
no question): prints the count of questions and calls identical, and the ids of any that differ.

    diff_all.py <measure.txt a> <kept folder a> <measure.txt b> <kept folder b>
"""
import importlib.util
import re
import sys
from pathlib import Path

spec = importlib.util.spec_from_file_location("diff_one_mod", Path(__file__).with_name("diff_one.py"))
src = Path(__file__).with_name("diff_one.py").read_text().split("\nqid, ma, ka")[0]
mod = {}
exec(compile(src, "diff_one.py", "exec"), mod)

ma, ka, mb, kb = sys.argv[1:5]
qids = [m[1] for m in (re.match(r"(\S+) \(\w+\): hit@5", l) for l in open(ma)) if m]
same_q, diff_q, calls = 0, [], 0
for q in qids:
    ra, rb = mod["call_range"](ma, q), mod["call_range"](mb, q)
    if len(ra) != len(rb):
        diff_q.append(f"{q} (calls {len(ra)} vs {len(rb)})")
        continue
    ok = all(mod["ids"](ka, x)[0] == mod["ids"](kb, y)[0] for x, y in zip(ra, rb))
    calls += len(ra)
    if ok:
        same_q += 1
    else:
        diff_q.append(q)
print(f"questions {len(qids)}: identical {same_q}, different {len(diff_q)}; calls compared {calls}"
      + (f"; different: {', '.join(diff_q)}" if diff_q else ""))
sys.exit(0 if not diff_q else 1)
