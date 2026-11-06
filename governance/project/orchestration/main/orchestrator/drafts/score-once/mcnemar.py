#!/usr/bin/env python3
"""DEC-1079 L1: two runs on the 138 (h24 and m60 apart), compared question by question on hit@5: gains, losses and an
exact two-sided McNemar test (binomial on the discordant pairs). Ids and counts only.

    mcnemar.py <80 base> <60 base> <80 cell> <60 cell>
"""
import math
import re
import sys

APART = {"h24", "m60"}


def hits(p80, p60):
    out = {}
    for prefix, path in (("", p80), ("v:", p60)):
        for line in open(path):
            m = re.match(r"(\S+) \((\w+)\): hit@5 (yes|no)", line)
            if m and m[1] not in APART:
                out[prefix + m[1]] = m[3] == "yes"
    return out


def exact_p(gains: int, losses: int) -> float:
    n = gains + losses
    if n == 0:
        return 1.0
    k = min(gains, losses)
    tail = sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n
    return min(1.0, 2 * tail)


a, b = hits(*sys.argv[1:3]), hits(*sys.argv[3:5])
assert set(a) == set(b), "the two runs do not cover the same questions"
gains = sum(1 for q in a if b[q] and not a[q])
losses = sum(1 for q in a if a[q] and not b[q])
print(f"against the base: {sum(b.values())} vs {sum(a.values())} of {len(a)}; gains {gains}, losses {losses}; "
      f"exact McNemar p {exact_p(gains, losses):.3f}")
