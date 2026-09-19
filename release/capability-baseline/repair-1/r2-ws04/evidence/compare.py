#!/usr/bin/env python3
"""P2-AR-0025 evidence tool: pair every verdict line of each probe output in before/ with after/.

Recognised verdict lines (the audit-of-record formats): delta-r `CHECK <id> PASS|FAIL ...`, zeta-r `OBS <id>: PASS|FAIL`,
synthesis `X <id> PASS|FAIL ...`, beta-r `[PASS|FAIL] <id>: ...`. Probes without verdict lines (alpha-r, gamma-r,
epsilon-r observation logs) are compared by reading the normalised diff (see 00-REPAIR-REPORT.md §7). Usage: compare.py [<family.probe> ...] (default: every file present in both dirs).
Prints FAIL->PASS, PASS->FAIL, lines present on one side only, and per-probe totals.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PAT = [
    re.compile(r"^CHECK (\S+) (PASS|FAIL)\b"),
    re.compile(r"^OBS (\S+?): (PASS|FAIL)\b"),
    re.compile(r"^X (\S+) (PASS|FAIL)\b"),
]
BRACKET = re.compile(r"^\[(PASS|FAIL)\] (\S+?):")


def verdicts(path):
    out = {}
    order = []
    with open(path, errors="replace") as f:
        for line in f:
            hit = None
            for p in PAT:
                m = p.match(line)
                if m:
                    hit = (m.group(1), m.group(2))
                    break
            if hit is None:
                m = BRACKET.match(line)
                if m:
                    hit = (m.group(2), m.group(1))
            if hit:
                k, v = hit
                if k not in out:
                    order.append(k)
                out[k] = v
    return out, order


def main():
    names = sys.argv[1:]
    if not names:
        b = {f[:-4] for f in os.listdir(os.path.join(HERE, "before")) if f.endswith(".out") and not f.startswith("RUN")}
        a = {f[:-4] for f in os.listdir(os.path.join(HERE, "after")) if f.endswith(".out") and not f.startswith("RUN")}
        names = sorted(b & a)
    tot = {"FAIL->PASS": 0, "PASS->FAIL": 0}
    for n in names:
        bv, _ = verdicts(os.path.join(HERE, "before", n + ".out"))
        av, order = verdicts(os.path.join(HERE, "after", n + ".out"))
        keys = order + [k for k in bv if k not in av]
        fp = [k for k in keys if bv.get(k) == "FAIL" and av.get(k) == "PASS"]
        pf = [k for k in keys if bv.get(k) == "PASS" and av.get(k) == "FAIL"]
        only_b = [k for k in keys if k in bv and k not in av]
        only_a = [k for k in keys if k in av and k not in bv]
        tot["FAIL->PASS"] += len(fp)
        tot["PASS->FAIL"] += len(pf)
        print(f"== {n}: before {sum(1 for v in bv.values() if v == 'PASS')}/{len(bv)} PASS, after {sum(1 for v in av.values() if v == 'PASS')}/{len(av)} PASS")
        for k in fp:
            print(f"   FAIL->PASS {k}")
        for k in pf:
            print(f"   PASS->FAIL {k}")
        for k in only_b:
            print(f"   before-only {k} ({bv[k]})")
        for k in only_a:
            print(f"   after-only  {k} ({av[k]})")
    print(f"TOTAL FAIL->PASS {tot['FAIL->PASS']}  PASS->FAIL {tot['PASS->FAIL']}")


if __name__ == "__main__":
    main()
