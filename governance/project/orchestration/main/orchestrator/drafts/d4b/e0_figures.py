#!/usr/bin/env python3
"""E0's figures (SEVEN-ANSWERS §7, DEC-1087 (11), DEC-1090 (1)) from two measure.txt files (memory-retrieval's 80,
memory-verdict's 60): per set (visible 40, hidden 39 with h24 apart, spent 59 with m60 apart) and the 138 together,
hit@5, hit@10, hit@20 (the first gold rank within the first call's ranked items), MRR of the first gold source, in the
bundle (the measure's own flag: a gold piece in an item of the first call, its line 391), and full evidence; the
spread between the three sets' hit@5. Counts only: the hidden set is read as figures, never as text.

    e0_figures.py <name> <measure 80> <measure 60>
"""
import re
import sys

APART = {"h24", "m60"}
LINE = re.compile(r"(\S+) \((\w+)\): hit@5 (yes|no) \(first gold rank (\d+|-)\), in the bundle (yes|no); "
                  r"full evidence (yes|no)")


def rows(path, spent):
    out = []
    for line in open(path):
        m = LINE.match(line)
        if m and m[1] not in APART:
            out.append(("spent" if spent else m[2], int(m[4]) if m[4] != "-" else None, m[5] == "yes", m[6] == "yes"))
    return out


def line(name, v):
    n = len(v)
    hit = lambda k: sum(1 for _, r, _, _ in v if r and r <= k)
    mrr = sum(1 / r for _, r, _, _ in v if r) / n
    return (f"{name} {n}: hit@5 {hit(5)} ({100 * hit(5) / n:.1f}%), hit@10 {hit(10)}, hit@20 {hit(20)}, MRR {mrr:.4f}, "
            f"in the bundle {sum(1 for x in v if x[2])}, full evidence {sum(1 for x in v if x[3])}"), 100 * hit(5) / n


name, p80, p60 = sys.argv[1:4]
allr = rows(p80, False) + rows(p60, True)
print(f"== {name}")
pcts = []
for part in ("visible", "hidden", "spent"):
    text, pct = line(part, [x for x in allr if x[0] == part])
    pcts.append(pct)
    print("  " + text)
print("  " + line("the 138", allr)[0] + f"; spread of hit@5 between the sets {max(pcts) - min(pcts):.1f} points")
