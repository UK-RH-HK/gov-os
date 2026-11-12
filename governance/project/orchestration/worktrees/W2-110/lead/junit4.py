"""Summarise a JUnit file: totals, failures/errors by id, and the state of named cases (substring match).
Usage: python3 junit4.py <xml> [substring ...]"""
import sys
import xml.etree.ElementTree as ET

root = ET.parse(sys.argv[1]).getroot()
cases = list(root.iter("testcase"))
state = {}
for c in cases:
    cid = c.get("classname", "") + "::" + c.get("name", "")
    s = "passed"
    for tag in ("failure", "error", "skipped"):
        if c.find(tag) is not None:
            s = tag
            break
    state[cid] = s
tot = {}
for s in state.values():
    tot[s] = tot.get(s, 0) + 1
print("totals", len(cases), tot)
for cid, s in sorted(state.items()):
    if s in ("failure", "error"):
        print(s.upper(), cid[:220])
for sub in sys.argv[2:]:
    hits = [(cid, s) for cid, s in state.items() if sub in cid]
    print("CASE", sub, "->", hits if hits else "NOT FOUND")
