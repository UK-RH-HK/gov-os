#!/usr/bin/env python3
"""Every call over the bundle budget in kept runs: how far over, and whether one item of a single long line (over
4,000 characters) explains it. Counts only, no text or paths.

    over_budget_all.py <kept folder> [...]
"""
import json
import sys
from pathlib import Path

over = long_one = 0
excess, without = [], []
calls = 0
for folder in sys.argv[1:]:
    for f in sorted(Path(folder).glob("[0-9]*.json")):
        r = json.loads(f.read_text()).get("result") or {}
        b = (r.get("budget") or {}).get("bundle") or {}
        calls += 1
        if (b.get("used") or 0) <= (b.get("limit") or 10**9):
            continue
        over += 1
        ev = r.get("evidence", [])
        big = [e for e in ev if max((len(x) for x in str(e.get("text", "")).split("\n")), default=0) > 4000]
        long_one += bool(big)
        excess.append(b["used"] - b["limit"])
        rest = b["used"] - sum(-(-len(str(e.get("text", ""))) // 4) for e in big)
        without.append(rest)
print(f"calls {calls}; over the budget {over}; with an item of one line over 4,000 characters {long_one}")
print(f"excess tokens: {sorted(excess)}")
print(f"used without those items: max {max(without) if without else None}")
