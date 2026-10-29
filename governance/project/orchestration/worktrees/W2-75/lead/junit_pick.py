"""Print the outcome and time of JUnit cases whose name or class holds any of the given words."""
import sys
import xml.etree.ElementTree as ET

root = ET.parse(sys.argv[1]).getroot()
words = sys.argv[2:]
for case in root.iter("testcase"):
    name = case.get("classname", "") + "::" + case.get("name", "")
    if any(w in name for w in words):
        outcome = "passed"
        for tag in ("failure", "error", "skipped"):
            if case.find(tag) is not None:
                outcome = tag
        print(f"{outcome:8} {float(case.get('time', 0)):8.1f}s {name}")
