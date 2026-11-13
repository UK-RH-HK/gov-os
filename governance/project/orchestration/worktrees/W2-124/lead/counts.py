import sys
import xml.etree.ElementTree as ET
from collections import Counter

root = ET.parse(sys.argv[1]).getroot()
counts = Counter()
for case in root.iter("testcase"):
    cls = case.get("classname") or ""
    if "W2-124" in cls or "test_w2_124" in cls:
        kind = "failed" if case.find("failure") is not None or case.find("error") is not None else (
            "skipped" if case.find("skipped") is not None else "passed")
        counts[kind] += 1
        if "s1_semantic" in cls and ("hung" in case.get("name") or "part-way" in case.get("name")):
            print(case.get("name"), case.get("time"), kind)
print(dict(counts))
