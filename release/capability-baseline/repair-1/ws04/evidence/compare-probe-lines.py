#!/usr/bin/env python3
"""P2-AR-0017: compare the SUMMARY lines ("<obs>: PASS|FAIL") of two zeta-r probe runs.

usage: compare-probe-lines.py <before-dir> <after-dir> [probe ...]
Prints, per probe, every observation whose outcome changed (FAIL->PASS, PASS->FAIL), observations only in one run,
and the totals. Exit status 0 always (this is a report, not a gate).
"""
import os
import re
import sys

LINE = re.compile(r"^(?P<obs>.+): (?P<res>PASS|FAIL)$")


def summary(path):
    out = {}
    if not os.path.exists(path):
        return out
    in_summary = False
    for ln in open(path, encoding="utf-8", errors="replace"):
        ln = ln.rstrip("\n")
        if ln.startswith("==== SUMMARY ===="):
            in_summary = True
            continue
        if not in_summary:
            continue
        m = LINE.match(ln)
        if m:
            out[m.group("obs")] = m.group("res")
    return out


def main():
    before, after = sys.argv[1], sys.argv[2]
    probes = sys.argv[3:] or sorted(f[:-4] for f in os.listdir(after) if f.endswith(".out"))
    grand = {"FAIL->PASS": 0, "PASS->FAIL": 0}
    for p in probes:
        b = summary(os.path.join(before, p + ".out"))
        a = summary(os.path.join(after, p + ".out"))
        fixed = [k for k in a if b.get(k) == "FAIL" and a[k] == "PASS"]
        regressed = [k for k in a if b.get(k) == "PASS" and a[k] == "FAIL"]
        still = [k for k in a if b.get(k) == "FAIL" and a[k] == "FAIL"]
        only_b = [k for k in b if k not in a]
        only_a = [k for k in a if k not in b]
        grand["FAIL->PASS"] += len(fixed)
        grand["PASS->FAIL"] += len(regressed)
        print(f"== {p}: before pass={sum(v == 'PASS' for v in b.values())}/{len(b)} after pass={sum(v == 'PASS' for v in a.values())}/{len(a)}")
        for k in fixed:
            print(f"   FAIL->PASS  {k}")
        for k in regressed:
            print(f"   PASS->FAIL  {k}")
        for k in still:
            print(f"   still FAIL  {k}")
        for k in only_b:
            print(f"   only before {k}: {b[k]}")
        for k in only_a:
            print(f"   only after  {k}: {a[k]}")
    print(f"TOTAL FAIL->PASS={grand['FAIL->PASS']} PASS->FAIL={grand['PASS->FAIL']}")


if __name__ == "__main__":
    main()
