#!/usr/bin/env python3
"""DEC-1076 (4)'s figures from two measure.txt files (memory-retrieval's 80, memory-verdict's 60): the visible 40,
the hidden 39 (h24 apart), the spent 59 (m60 apart); hit@5, per cent and MRR of each; the 138 together; the spread
between the three sets (the highest per cent less the lowest). Counts only.

    score138.py <name> <measure 80> <measure 60>            one model's line
    score138.py --same <80 a> <60 a> <80 b> <60 b>          the ids whose hit@5 or first gold rank differ (T2's check)
"""
import re
import sys

APART = {"h24", "m60"}


def rows(path):
    out = {}
    for line in open(path):
        x = re.match(r"(\S+) \((\w+)\): hit@5 (yes|no)(?: \(first gold rank (\d+)\))?", line)
        if x and x[1] not in APART:
            out[x[1]] = (x[2], x[3] == "yes", int(x[4]) if x[4] else None)
    return out


def figures(r80, r60):
    sets = {"visible": [], "hidden": [], "spent": []}
    for qid, (part, hit, rank) in r80.items():
        sets[part].append((hit, rank))
    for qid, (part, hit, rank) in r60.items():
        sets["spent"].append((hit, rank))
    out = {}
    for k, v in sets.items():
        h = sum(1 for hit, _ in v if hit)
        mrr = sum(1 / rank for _, rank in v if rank) / len(v)
        out[k] = (h, len(v), 100 * h / len(v), mrr)
    allv = [x for v in sets.values() for x in v]
    total = (sum(1 for hit, _ in allv if hit), len(allv), sum(1 / r for _, r in allv if r) / len(allv))
    pcts = [out[k][2] for k in out]
    return out, total, max(pcts) - min(pcts)


if sys.argv[1] == "--same":
    a = {**rows(sys.argv[2]), **{"v:" + k: v for k, v in rows(sys.argv[3]).items()}}
    b = {**rows(sys.argv[4]), **{"v:" + k: v for k, v in rows(sys.argv[5]).items()}}
    diff = sorted(k for k in set(a) | set(b) if a.get(k, (None,))[1:] != b.get(k, (None,))[1:])
    print(f"questions compared: {len(set(a) | set(b))}; differing in hit@5 or first gold rank: {len(diff)}"
          + (f" ({', '.join(diff)})" if diff else ""))
    sys.exit(0 if not diff else 1)
name, p80, p60 = sys.argv[1:4]
s, t, spread = figures(rows(p80), rows(p60))
print(f"{name}: 138 {t[0]}/{t[1]} MRR {t[2]:.4f} | "
      + " | ".join(f"{k} {v[0]}/{v[1]} {v[2]:.1f}% MRR {v[3]:.4f}" for k, v in s.items())
      + f" | spread {spread:.1f}")
