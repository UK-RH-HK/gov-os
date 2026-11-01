"""Print the failing or erroring node ids of a JUnit XML, one per line, with F or E.
Usage: allids.py <xml>"""
import sys
import xml.etree.ElementTree as ET

for case in ET.parse(sys.argv[1]).iter("testcase"):
    kind = "F" if case.find("failure") is not None else "E" if case.find("error") is not None else None
    if kind is None:
        continue
    parts = case.get("classname", "").split(".")
    print(kind, "/".join(parts[:-1]) + "/" + parts[-1] + ".py::" + case.get("name"))
