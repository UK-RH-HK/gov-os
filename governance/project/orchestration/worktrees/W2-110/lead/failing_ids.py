"""Write the failing node ids of a JUnit XML, one per line, for the W1-03, W1-46, W1-47 and W1-50 suites.
Usage: failing_ids.py <xml> <out file>"""
import sys
import xml.etree.ElementTree as ET

out = []
for case in ET.parse(sys.argv[1]).iter("testcase"):
    if case.find("failure") is None and case.find("error") is None:
        continue
    cls = case.get("classname", "")
    if not any(s in cls for s in ("W1-03", "W1-46", "W1-47", "W1-50")):
        continue
    parts = cls.split(".")
    path = "/".join(parts[:-1]) + "/" + parts[-1] + ".py"
    out.append(f"{path}::{case.get('name')}")
open(sys.argv[2], "w").write("\n".join(out) + "\n")
print(len(out), "ids")
