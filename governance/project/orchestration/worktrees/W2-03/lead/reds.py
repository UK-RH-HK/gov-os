"""List the failed and errored cases of a JUnit XML file, with the first lines of each message."""

import sys
import xml.etree.ElementTree as ET

root = ET.parse(sys.argv[1]).getroot()
lines = int(sys.argv[2]) if len(sys.argv) > 2 else 12
for case in root.iter("testcase"):
    for kind in ("failure", "error"):
        node = case.find(kind)
        if node is not None:
            print("==", kind.upper(), case.get("classname"), "::", case.get("name"), case.get("time"))
            text = (node.get("message") or "") + "\n" + (node.text or "")
            print("\n".join(text.strip().splitlines()[-lines:]))
