"""Summarise a JUnit XML: totals, every non-pass case, and counts for named prefixes."""
import sys
import xml.etree.ElementTree as ET

root = ET.parse(sys.argv[1]).getroot()
prefixes = sys.argv[2:]
tot = {"pass": 0, "fail": 0, "error": 0, "skip": 0}
by = {p: dict(tot) for p in prefixes}
bad = []
for tc in root.iter("testcase"):
    name = tc.get("classname", "") + "::" + tc.get("name", "")
    kind = "pass"
    for child in tc:
        if child.tag in ("failure", "error", "skipped"):
            kind = {"failure": "fail", "error": "error", "skipped": "skip"}[child.tag]
            msg = (child.get("message") or "")[:200]
    tot[kind] += 1
    for p in prefixes:
        if name.startswith(p):
            by[p][kind] += 1
    if kind in ("fail", "error"):
        bad.append(f"{kind} {name} | {msg}")
print("totals:", tot)
for p in prefixes:
    print(p, by[p])
for b in bad:
    print(b)
