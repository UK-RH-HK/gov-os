"""Counts JUnit cases by classname prefix, and shows named cases' outcomes (lead, DAEO-u4oz review run)."""
import sys
import xml.etree.ElementTree as ET

path, prefixes, names = sys.argv[1], sys.argv[2].split(","), sys.argv[3:]
root = ET.parse(path).getroot()
counts = {p: {"passed": 0, "failed": 0, "skipped": 0} for p in prefixes}
for tc in root.iter("testcase"):
    cls, name = tc.get("classname", ""), tc.get("name", "")
    kind = "passed"
    if tc.find("failure") is not None or tc.find("error") is not None:
        kind = "failed"
    elif tc.find("skipped") is not None:
        kind = "skipped"
    for p in prefixes:
        if cls.startswith(p):
            counts[p][kind] += 1
    for n in names:
        if name.startswith(n):
            print("case", cls, name, kind)
for p, c in counts.items():
    print(p, c)
