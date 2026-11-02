"""List a JUnit XML's failed and errored cases with the first line of their message: junit_fail.py <xml>..."""
import sys
import xml.etree.ElementTree as ET

for path in sys.argv[1:]:
    root = ET.parse(path).getroot()
    for case in root.iter("testcase"):
        for kind in ("failure", "error"):
            node = case.find(kind)
            if node is not None:
                message = (node.get("message") or node.text or "").strip().splitlines()
                print(f"{kind}: {case.get('classname')}::{case.get('name')} | {(message or [''])[0][:220]}")
