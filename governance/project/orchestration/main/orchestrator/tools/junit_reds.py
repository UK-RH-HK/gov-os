"""Print the failing and erroring cases of a JUnit XML file."""
import sys
import xml.etree.ElementTree as ET
for c in ET.parse(sys.argv[1]).iter("testcase"):
    for kind in ("failure", "error"):
        if c.find(kind) is not None:
            print(kind, c.get("classname"), c.get("name"), (c.find(kind).get("message") or "")[:120])
