"""List failed cases of a JUnit XML file: classname::name and the first line of the failure message."""
import sys
import xml.etree.ElementTree as ET
from collections import Counter

root = ET.parse(sys.argv[1]).getroot()
folders = Counter()
w2_81 = Counter()
for case in root.iter("testcase"):
    cls = case.get("classname", "")
    if "W2-81" in cls or "W2_81" in cls or "w2_81" in cls:
        state = "failed" if case.find("failure") is not None or case.find("error") is not None else (
            "skipped" if case.find("skipped") is not None else "passed")
        w2_81[state] += 1
    for tag in ("failure", "error"):
        node = case.find(tag)
        if node is not None:
            message = (node.get("message") or "").splitlines()
            print(f"{tag.upper()} {cls}::{case.get('name')}")
            print("    ", (message[0] if message else "")[:300])
print("W2-81 cases:", dict(w2_81))
