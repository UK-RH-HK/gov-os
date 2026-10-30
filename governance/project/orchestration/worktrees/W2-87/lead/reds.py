"""The failed and erred cases of a JUnit XML file, with the first line of each message (W2-87 lead)."""
import sys
import xml.etree.ElementTree as ET

for case in ET.parse(sys.argv[1]).getroot().iter("testcase"):
    for kind in ("failure", "error"):
        node = case.find(kind)
        if node is not None:
            message = (node.get("message") or node.text or "").strip().splitlines()
            print(f"{kind.upper()} {case.get('classname')}::{case.get('name')} | {message[0][:300] if message else ''}")
