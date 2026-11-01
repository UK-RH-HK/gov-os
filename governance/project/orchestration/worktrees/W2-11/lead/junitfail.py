"""List the failed and errored cases of a JUnit XML file, each with the first line of its message."""
import sys
import xml.etree.ElementTree as ET

root = ET.parse(sys.argv[1]).getroot()
for case in root.iter("testcase"):
    for kind in ("failure", "error"):
        node = case.find(kind)
        if node is not None:
            msg = (node.get("message") or "").strip().splitlines()
            first = msg[0][:170] if msg else ""
            print(f"{kind.upper()} {case.get('classname')}::{case.get('name')} | {first}")
