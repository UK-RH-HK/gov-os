import collections
import sys
import xml.etree.ElementTree as ET

root = ET.parse(sys.argv[1]).getroot()
prefix = sys.argv[2]
c = collections.Counter()
for case in root.iter("testcase"):
    cls = case.get("classname") or ""
    if not cls.startswith(prefix):
        continue
    key = cls
    state = "passed"
    for kind in ("failure", "error", "skipped"):
        if case.find(kind) is not None:
            state = kind
    c[(key, state)] += 1
tot = collections.Counter()
for (key, state), n in sorted(c.items()):
    print(key, state, n)
    tot[state] += n
print("TOTAL", dict(tot))
