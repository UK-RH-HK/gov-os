#!/usr/bin/env python3
"""P2-AR-0039: normalised line diff of two probe outputs (scratch paths, hex digests >= 12 chars and UTC timestamps
normalised), so a before/after pair of runs of the same probe can be compared line by line.
Usage: normdiff.py <before.out> <after.out>"""
import difflib, re, sys
def norm(t):
    t = re.sub(r"/tmp/[^\s\"':,)\]]+", "<PATH>", t)
    t = re.sub(r"\b[0-9a-f]{12,}\b", "<HEX>", t)
    t = re.sub(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ", "<TS>", t)
    t = re.sub(r"\b(HDG|D|CIT|AUD|TASK)-\d{4}\b", r"\1-<N>", t)
    return t.splitlines()
a, b = norm(open(sys.argv[1]).read()), norm(open(sys.argv[2]).read())
d = list(difflib.unified_diff(a, b, fromfile=sys.argv[1], tofile=sys.argv[2], n=0, lineterm=""))
print(f"# {len(a)} lines before, {len(b)} after, {sum(1 for l in d if l.startswith(('+', '-')) and not l.startswith(('+++', '---')))} differing")
print("\n".join(d))
