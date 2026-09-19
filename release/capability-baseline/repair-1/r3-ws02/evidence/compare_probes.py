#!/usr/bin/env python3
"""P2-AR-0023: pair every marked verdict line of an audit-of-record probe run on the base binary with the same line on
the repaired binary. Marked lines: zeta-r `OBS <id>: PASS|FAIL`, delta-r `CHECK <id> PASS|FAIL`, synthesis
`X <id> PASS|FAIL`, beta-r `[PASS|FAIL] <id>:`. Unmarked families (alpha-r [F] lines, epsilon-r observations) are
compared line-for-line by `diff` in the report instead.

Usage: compare_probes.py <before-dir> <after-dir> [<before-dir> <after-dir> ...]  (pairs of label directories)
"""
import os
import re
import sys

PATS = [
    re.compile(r"^OBS (\S+): (PASS|FAIL)"),
    re.compile(r"^CHECK (\S+) (PASS|FAIL)"),
    re.compile(r"^X (\S+) (PASS|FAIL)"),
    re.compile(r"^\[(PASS|FAIL)\] (\S+?):"),
]


def marks(path):
    out = {}
    for line in open(path, errors="replace"):
        for i, p in enumerate(PATS):
            m = p.match(line)
            if m:
                a, b = m.group(1), m.group(2)
                k, v = (b, a) if i == 3 else (a, b)
                out.setdefault(k, v)  # first occurrence (verdict line; SUMMARY repeats it)
    return out


args = sys.argv[1:]
tot = {"FAIL->PASS": 0, "PASS->FAIL": 0, "PASS->PASS": 0, "FAIL->FAIL": 0, "only-before": 0, "only-after": 0}
for i in range(0, len(args), 2):
    bdir, adir = args[i], args[i + 1]
    for f in sorted(os.listdir(bdir)):
        if not f.endswith(".out") or not os.path.exists(os.path.join(adir, f)):
            continue
        b, a = marks(os.path.join(bdir, f)), marks(os.path.join(adir, f))
        if not b and not a:
            continue
        print(f"\n== {f}  ({os.path.basename(bdir)} -> {os.path.basename(adir)})")
        for k in sorted(set(b) | set(a)):
            bv, av = b.get(k, "-"), a.get(k, "-")
            if bv == "-":
                tot["only-after"] += 1
            elif av == "-":
                tot["only-before"] += 1
            else:
                tot[f"{bv}->{av}"] += 1
            flag = "" if bv == av else "   <== changed"
            print(f"  {k:70s} {bv:4s} -> {av:4s}{flag}")
print("\n# TOTAL " + ", ".join(f"{k}: {v}" for k, v in tot.items()))
