#!/usr/bin/env python3
"""P2-AR-0026 — verdict-line comparison of the audit-of-record probe re-runs in ./base vs ./after (unedited) and
./base-shim vs ./after-shim (through gov-adapter.py), and of the derived X2 copy (../derived/<mode>/). Probes that
print verdict markers (zeta-r `OBS id: PASS`, delta-r `CHECK id PASS`, synthesis `X id PASS`, beta-r `[PASS] id`)
are compared line by line; a line present on one side only is reported as NOT REACHED on the other. Unmarked
probes (gamma-r, epsilon-r, alpha-r) are adjudicated in the report from the raw outputs.

Usage: python3 compare.py > COMPARE.out   (reads only)
"""
import os
import re
from collections import OrderedDict

HERE = os.path.dirname(os.path.abspath(__file__))
PATTERNS = [re.compile(r"^CHECK (\S+) (PASS|FAIL)\b"), re.compile(r"^X (\S+) (PASS|FAIL)\b"),
            re.compile(r"^OBS (\S+?): (PASS|FAIL)\b")]
BRACKET = re.compile(r"^\[(PASS|FAIL)\] (\S+)")


def verdicts(path):
    out = OrderedDict()
    if not os.path.exists(path):
        return None
    for line in open(path, errors="replace"):
        line = line.rstrip("\n")
        for p in PATTERNS:
            m = p.match(line)
            if m:
                out.setdefault(m.group(1), m.group(2))
                break
        else:
            m = BRACKET.match(line)
            if m:
                out.setdefault(m.group(2), m.group(1))
    return out


def compare(label, before, after):
    b, a = verdicts(before), verdicts(after)
    if b is None or a is None:
        return
    if not b and not a:
        return
    ids = list(OrderedDict.fromkeys(list(b.keys()) + list(a.keys())))
    rows = []
    counts = {"FAIL->PASS": 0, "PASS->FAIL": 0, "same": 0, "not-reached-after": 0, "not-reached-before": 0}
    for i in ids:
        x, y = b.get(i, "NOT_REACHED"), a.get(i, "NOT_REACHED")
        if x == y:
            counts["same"] += 1
            continue
        if y == "NOT_REACHED":
            counts["not-reached-after"] += 1
        elif x == "NOT_REACHED":
            counts["not-reached-before"] += 1
        else:
            counts[f"{x}->{y}"] += 1
        rows.append(f"    {i:70s} {x:12s} -> {y}")
    print(f"{label}: {counts}")
    for r in rows:
        print(r)


for before_mode, after_mode in (("base", "after"), ("base-shim", "after-shim")):
    print(f"\n=== {before_mode} -> {after_mode} ===")
    bd, ad = os.path.join(HERE, before_mode), os.path.join(HERE, after_mode)
    if not (os.path.isdir(bd) and os.path.isdir(ad)):
        continue
    for f in sorted(os.listdir(ad)):
        if f.endswith(".out"):
            compare(f[:-4], os.path.join(bd, f), os.path.join(ad, f))
dd = os.path.join(HERE, "..", "derived")
for before_mode, after_mode in (("base", "after"), ("base-shim", "after-shim")):
    print(f"\n=== derived X2 copy: {before_mode} -> {after_mode} ===")
    f = "AC16-X2-authority-gate-chain.derived.P2-AR-0026.out"
    compare(f[:-4], os.path.join(dd, before_mode, f), os.path.join(dd, after_mode, f))
