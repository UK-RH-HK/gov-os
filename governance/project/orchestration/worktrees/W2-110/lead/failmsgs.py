"""Group the failing cases of a JUnit file by suite and show one failure message per suite."""
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict

path = sys.argv[1]
groups = defaultdict(list)
for case in ET.parse(path).getroot().iter("testcase"):
    bad = case.find("failure")
    if bad is None:
        bad = case.find("error")
    if bad is None:
        continue
    cls = case.get("classname", "")
    key = ".".join(cls.split(".")[:3])
    groups[key].append((case.get("name"), (bad.get("message") or "")[:600]))
for key, items in sorted(groups.items()):
    print("==", key, len(items))
    seen = set()
    for name, msg in items:
        short = msg[:200]
        if short in seen:
            continue
        seen.add(short)
        print("   ", name, "::", msg.replace("\n", " ")[:600])
        if len(seen) >= 3:
            break
