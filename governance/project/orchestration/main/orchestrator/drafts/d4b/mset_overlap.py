#!/usr/bin/env python3
"""DEC-1070 (4): the new measurement set must not ask what a tuning question asks.

    python3 -I mset_overlap.py <new-set-folder> <other-folder> [<other-folder> ...]

Prints only the NEW set's ids whose main gold source (path, and a heading or overlapping lines) matches a gold
source of any question in the other folders, and a count. Nothing about the other folders' questions is printed:
neither their ids nor their text nor their sources, so the hidden half can be one of them.
"""
import glob
import os
import sys

import yaml


def spans(q):
    out = []
    for e in q.get("sources") or []:
        for s in e if isinstance(e, list) else [e]:
            if isinstance(s, dict) and s.get("path"):
                ln = s.get("lines") or [0, 0]
                out.append((s["path"], s.get("heading"), int(ln[0]), int(ln[-1])))
    return out


def same(a, b):
    if a[0] != b[0]:
        return False
    if a[1] and b[1]:
        return a[1] == b[1]
    return a[2] <= b[3] and b[2] <= a[3] and a[3] > 0 and b[3] > 0


def load(folder):
    out = []
    for f in sorted(glob.glob(os.path.join(folder, "*.yaml"))):
        q = yaml.safe_load(open(f)) or {}
        q.setdefault("id", os.path.basename(f)[:-5])
        out.append(q)
    return out


new = load(sys.argv[1])
others = [s for d in sys.argv[2:] for q in load(d) for s in spans(q)]
hits = [q["id"] for q in new if any(same(a, b) for a in spans(q) for b in others)]
print(f"new questions: {len(new)}; overlapping a tuning question's gold source: {len(hits)}"
      + (f" ({', '.join(hits)})" if hits else ""))
