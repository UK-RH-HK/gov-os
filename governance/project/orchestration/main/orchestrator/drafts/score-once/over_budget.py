#!/usr/bin/env python3
"""The first calls over the bundle budget, from kept runs (no GPU): per call, the budget's own fields and each item's
source, kind and size. Sizes, keys and paths only; no item text is printed. Item paths of hidden questions' gold are
not singled out (no gold is read).

    over_budget.py <run folder (r80/, r60/)> <kept r80 folder> <kept r60 folder> [limit]
"""
import json
import re
import sys
from pathlib import Path

run, k80, k60 = Path(sys.argv[1]), sys.argv[2], sys.argv[3]
limit = int(sys.argv[4]) if len(sys.argv) > 4 else 6000


def starts(measure):
    out, start = [], 1
    for line in open(measure):
        m = re.match(r"(\S+) \((\w+)\):.*?(\d+) calls?", line)
        if m:
            out.append((m[1], m[2], start))
            start += int(m[3])
    return out


keys_shown = False
for part, kept in (("r80", k80), ("r60", k60)):
    for qid, kind, start in starts(run / part / "measure.txt"):
        r = json.loads((Path(kept) / f"{start:05d}.json").read_text()).get("result") or {}
        b = r.get("budget") or {}
        used = (b.get("bundle") or {}).get("used") or 0
        if used <= limit:
            continue
        ev = r.get("evidence", [])
        if not keys_shown:
            print("budget keys:", json.dumps({k: (v if not isinstance(v, (list, str)) else type(v).__name__)
                                              for k, v in b.items()}))
            print("item keys:", sorted(ev[0].keys()) if ev else [])
            keys_shown = True
        print(f"== {part} {qid} ({kind}): used {used}; items {len(ev)}")
        for i, e in enumerate(ev, 1):
            t = str(e.get("text", ""))
            src = str(e.get("path") or e.get("source") or e.get("id"))
            if kind != "visible" or part != "r80":  # hidden-half rule: the file type only
                src = "*" + Path(src.split("#")[0]).suffix
            print(f"  {i:2d} {e.get('kind') or e.get('type')} {src} chars {len(t)} lines {t.count(chr(10)) + 1}"
                  f" tokens {e.get('tokens')} longest line {max((len(x) for x in t.split(chr(10))), default=0)}")
