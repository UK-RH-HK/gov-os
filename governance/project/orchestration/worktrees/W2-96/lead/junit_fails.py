"""List the failed and errored cases of a JUnit XML file, with the first line of each message (marker-free)."""
import sys
import xml.etree.ElementTree as ET

root = ET.parse(sys.argv[1]).getroot()
for case in root.iter("testcase"):
    for kind in ("failure", "error"):
        node = case.find(kind)
        if node is not None:
            message = (node.get("message") or "").splitlines()[0][:220] if node.get("message") else ""
            print(kind.upper(), case.get("classname"), "::", case.get("name"), "|", case.get("time"), "|", message)
